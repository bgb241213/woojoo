"""Photo lookup helpers.

Equipment photos are admin-managed ``EquipmentImage`` rows whose files live in
the default storage (local ``media/`` in dev, Cloudflare R2 in production).
The committed design photo library under ``static/images/`` acts as a
fallback so pages still render before ``import_design_photos`` has been run.

Sales-record photos keep using the static library (see
``records.SalesRecord.photo_urls`` for the admin-upload override).
"""
from functools import lru_cache

from django.conf import settings
from django.templatetags.static import static

_IMAGES_ROOT = settings.BASE_DIR / 'static' / 'images'
PLACEHOLDER = static('images/장비카드썸네일용.jpg')


def _sort_key(path):
    """Sort by the numeric filename stem (0.png, 1.png … 10.png)."""
    try:
        return (0, int(path.stem))
    except ValueError:
        return (1, path.name)


@lru_cache(maxsize=512)
def _scan(subdir, obj_id, ext):
    folder = _IMAGES_ROOT / subdir / str(obj_id)
    if not folder.is_dir():
        return ()
    files = sorted((p for p in folder.iterdir() if p.suffix.lower() == ext), key=_sort_key)
    return tuple(static(f'images/{subdir}/{obj_id}/{p.name}') for p in files)


def _db_photos(equipment_id, image_type):
    """URLs of admin-managed images for one equipment, ordered."""
    from .models import EquipmentImage
    urls = []
    qs = EquipmentImage.objects.filter(equipment_id=equipment_id, image_type=image_type)
    for img in qs.order_by('order', 'id'):
        try:
            urls.append(img.image.url)
        except ValueError:  # row without a file
            continue
    return urls


def rental_photos(equipment_id):
    """Rental gallery photos for an equipment id (may be empty)."""
    return _db_photos(equipment_id, 'rental') or list(_scan('rental', equipment_id, '.png'))


def sale_photos(equipment_id):
    """Sale gallery photos for an equipment id (may be empty)."""
    return _db_photos(equipment_id, 'sales') or list(_scan('sale', equipment_id, '.png'))


def record_photos(record_id):
    """Sales-record photos for a record id (may be empty)."""
    return list(_scan('records', record_id, '.jpg'))
