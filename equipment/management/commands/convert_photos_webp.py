"""Re-encode equipment photos as WebP.

The design library arrived as ~1200px PNGs averaging 360KB, and the rental
list shows every machine's gallery, so that page pulled 43MB of images. The
photos are studio shots on white, which WebP compresses to roughly 7% of the
PNG at a quality no one can tell apart on a phone.

Rows are updated with ``queryset.update()`` rather than ``instance.save()`` on
purpose: saving re-runs wheel-line detection (see EquipmentImage.save), which
reads every file back out of R2 and would overwrite ``baseline_detected`` from
a lossily re-encoded copy. The geometry is unchanged by the re-encode, so the
existing baselines stay correct.
"""
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from equipment.imaging import MAX_EDGE, QUALITY, encode_webp, webp_name
from equipment.models import EquipmentImage


class Command(BaseCommand):
    help = '장비 사진을 WebP로 변환해 용량을 줄입니다.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='변환하지 않고 예상 절감량만 출력합니다.')
        parser.add_argument('--quality', type=int, default=QUALITY)
        parser.add_argument('--max-edge', type=int, default=MAX_EDGE)
        parser.add_argument('--keep-originals', action='store_true',
                            help='변환 후 원본 파일을 지우지 않습니다.')

    def handle(self, *args, **options):
        dry = options['dry_run']
        quality = options['quality']
        max_edge = options['max_edge']

        rows = EquipmentImage.objects.exclude(image='').order_by('equipment_id', 'order', 'id')
        before = after = 0
        converted = skipped = failed = 0

        for row in rows:
            name = row.image.name
            if name.lower().endswith('.webp'):
                skipped += 1
                continue
            try:
                with row.image.open('rb') as fh:
                    original = fh.read()
                data, size = encode_webp(original, quality, max_edge)
            except Exception as exc:  # noqa: BLE001 — one bad file must not stop the run
                failed += 1
                self.stderr.write(self.style.WARNING(f'  건너뜀 {name}: {exc}'))
                continue

            before += len(original)
            after += len(data)
            converted += 1
            self.stdout.write(
                f'  {name}  {len(original) // 1024}KB → {len(data) // 1024}KB  {size[0]}x{size[1]}'
            )
            if dry:
                continue

            new_name = default_storage.save(webp_name(name), ContentFile(data))
            EquipmentImage.objects.filter(pk=row.pk).update(image=new_name)
            if not options['keep_originals']:
                default_storage.delete(name)

        self.stdout.write('')
        verb = '변환 예정' if dry else '변환 완료'
        self.stdout.write(self.style.SUCCESS(
            f'{verb}: {converted}장 | 이미 WebP: {skipped}장 | 실패: {failed}장'
        ))
        if before:
            self.stdout.write(self.style.SUCCESS(
                f'{before / 1048576:.1f}MB → {after / 1048576:.1f}MB '
                f'({after / before * 100:.0f}%, {(before - after) / 1048576:.1f}MB 절감)'
            ))
