"""Photo lookup helpers.

The Claude Design photo library is committed under ``static/images/`` keyed by
equipment / record id (e.g. ``static/images/rental/6/0.png``). These helpers scan
those folders and return ready-to-use static URLs, so templates can render photo
carousels/galleries without a per-image DB row.

Results are cached per-process; the photo set only changes on deploy.
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


def rental_photos(equipment_id):
    """Rental gallery photos for an equipment id (may be empty)."""
    return list(_scan('rental', equipment_id, '.png'))


def sale_photos(equipment_id):
    """Sale gallery photos for an equipment id (may be empty)."""
    return list(_scan('sale', equipment_id, '.png'))


def record_photos(record_id):
    """Sales-record photos for a record id (may be empty)."""
    return list(_scan('records', record_id, '.jpg'))
