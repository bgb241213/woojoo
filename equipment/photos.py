"""Photo lookup helpers.

Equipment photos are admin-managed ``EquipmentImage`` rows whose files live in
the default storage (local ``media/`` in dev, Cloudflare R2 in production).
The committed design photo library under ``static/images/`` acts as a
fallback so pages still render before ``import_design_photos`` has been run.

Sales-record photos keep using the static library (see
``records.SalesRecord.photo_urls`` for the admin-upload override).
"""
import json
from functools import lru_cache

from django.conf import settings
from django.templatetags.static import static

_IMAGES_ROOT = settings.BASE_DIR / 'static' / 'images'
PLACEHOLDER = static('images/장비카드썸네일용.jpg')

# Wheel-line positions produced by the ``compute_photo_baselines`` command.
BASELINE_PATH = settings.BASE_DIR / 'equipment' / 'data' / 'photo_baselines.json'


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


def _db_images(equipment_id, image_type):
    """[(url, row)] of admin-managed images that have a file, ordered.

    Photo URLs and baseline overrides are both indexed off this one sequence —
    building them separately lets their indices drift apart the moment a row
    is missing its file.
    """
    from .models import EquipmentImage
    qs = EquipmentImage.objects.filter(equipment_id=equipment_id, image_type=image_type)
    images = []
    for img in qs.order_by('order', 'id'):
        try:
            url = img.image.url
        except ValueError:  # row without a file
            continue
        images.append((url, img))
    return images


def _db_photos(equipment_id, image_type):
    """URLs of admin-managed images for one equipment, ordered."""
    return [url for url, _ in _db_images(equipment_id, image_type)]


def rental_photos(equipment_id):
    """Rental gallery photos for an equipment id (may be empty)."""
    return _db_photos(equipment_id, 'rental') or list(_scan('rental', equipment_id, '.png'))


def sale_photos(equipment_id):
    """Sale gallery photos for an equipment id (may be empty)."""
    return _db_photos(equipment_id, 'sales') or list(_scan('sale', equipment_id, '.png'))


def record_photos(record_id):
    """Sales-record photos for a record id (may be empty)."""
    return list(_scan('records', record_id, '.jpg'))


@lru_cache(maxsize=1)
def _baselines():
    """Cached contents of the precomputed wheel-line table."""
    try:
        return json.loads(BASELINE_PATH.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def _admin_baselines(equipment_id, image_type):
    """{index: fraction} for admin-managed photos.

    Covers both the value detected when the photo was uploaded and any manual
    correction typed over it — ``effective_baseline`` picks the winner. Photos
    added through the admin therefore need no separate command run.
    """
    result = {}
    for index, (_, row) in enumerate(_db_images(equipment_id, image_type)):
        value = row.effective_baseline
        if value is not None:
            result[index] = value / 100
    return result


def photo_baselines(equipment_id, kind, count):
    """Wheel-line fraction per photo, index-aligned with the photo URL list.

    ``kind`` is the ``static/images`` subdirectory ('rental' or 'sale').
    An admin correction wins over the precomputed value, which in turn wins
    over the median for that view.
    """
    table = _baselines()
    detected = table.get(kind, {}).get(str(equipment_id), {})
    defaults = table.get('_defaults', {})
    image_type = 'sales' if kind == 'sale' else kind
    overrides = _admin_baselines(equipment_id, image_type)

    values = []
    for index in range(count):
        value = overrides.get(index)
        if value is None:
            value = detected.get(str(index), defaults.get(str(index), 0.0))
        values.append(round(value, 4))
    return values
