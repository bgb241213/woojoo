"""Import the committed design photo library into admin-managed storage.

Uploads every ``static/images/rental/<id>/*.png`` and
``static/images/sale/<id>/*.png`` into the default storage backend
(local ``media/`` when DEBUG, Cloudflare R2 in production) under a
deterministic path, and upserts the matching ``EquipmentImage`` row.

Idempotent: existing storage objects are not re-uploaded and existing rows
are not duplicated, so it is safe to run on every deploy.
"""
from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from equipment.models import Equipment, EquipmentImage

# (static subdir, EquipmentImage.image_type, storage subdir)
SOURCES = [
    ('rental', 'rental', 'rental'),
    ('sale', 'sales', 'sale'),
]


class Command(BaseCommand):
    help = 'Upload design photos to storage (R2 in production) and register EquipmentImage rows.'

    def handle(self, *args, **options):
        images_root = settings.BASE_DIR / 'static' / 'images'
        equipment_ids = set(Equipment.objects.values_list('id', flat=True))

        uploaded = rows_created = skipped = 0
        for static_sub, image_type, storage_sub in SOURCES:
            base = images_root / static_sub
            if not base.is_dir():
                continue
            for folder in sorted(base.iterdir(), key=lambda p: p.name):
                if not folder.is_dir() or not folder.name.isdigit():
                    continue
                eq_id = int(folder.name)
                if eq_id not in equipment_ids:
                    self.stdout.write(f'  ! skip photos for unknown equipment id {eq_id}')
                    continue
                files = sorted(
                    (p for p in folder.iterdir() if p.suffix.lower() == '.png'),
                    key=lambda p: int(p.stem) if p.stem.isdigit() else 99,
                )
                for order, path in enumerate(files):
                    name = f'equipment/design/{storage_sub}/{eq_id}/{path.name}'
                    if not default_storage.exists(name):
                        with path.open('rb') as fh:
                            default_storage.save(name, File(fh))
                        uploaded += 1
                    row, created = EquipmentImage.objects.get_or_create(
                        equipment_id=eq_id, image_type=image_type, image=name,
                        defaults={'order': order},
                    )
                    if created:
                        rows_created += 1
                    else:
                        skipped += 1
                        if row.order != order:
                            row.order = order
                            row.save(update_fields=['order'])

        self.stdout.write(self.style.SUCCESS(
            f'Design photos synced: {uploaded} files uploaded, '
            f'{rows_created} rows created, {skipped} rows already present. '
            f'Total EquipmentImage rows: {EquipmentImage.objects.count()}'
        ))
