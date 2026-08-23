"""WebP encoding for site photos.

Every photo the site serves passes through here, so none of them can reach
storage at their original size:

* ``import_design_photos`` encodes the committed library on upload — ~1200px
  PNGs averaging 360KB, studio shots on white that WebP takes to about 7%.
* ``convert_photos_webp`` re-encodes what is already in storage, for the
  photos uploaded before this module existed.
* ``compress_upload`` runs from the admin, where phone photos arrive at
  several megabytes each.

One encoder for all three keeps the output identical whichever path a photo
took, and keeps the stored filename predictable.
"""
import io

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

# Tiles render at ~150px on a phone and the lightbox at ~1100px, so anything
# above this is detail no one ever sees.
MAX_EDGE = 1000
QUALITY = 82


def webp_name(name):
    """The storage path this photo takes once encoded."""
    return name.rsplit('.', 1)[0] + '.webp'


def encode_webp(payload, quality=QUALITY, max_edge=MAX_EDGE):
    """(bytes, (w, h)) — WebP for one image, downscaled to fit max_edge."""
    im = Image.open(io.BytesIO(payload))
    # Phone cameras record portrait shots as landscape plus an EXIF rotation
    # flag. Re-encoding drops the flag, so the rotation has to be baked into
    # the pixels here or admin uploads come out lying on their side.
    im = ImageOps.exif_transpose(im)
    # Palette images can hide an alpha channel; flattening those to RGB would
    # turn transparent margins black behind the white card.
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
        im = im.convert('RGBA')
    else:
        im = im.convert('RGB')
    im.thumbnail((max_edge, max_edge), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=quality, method=6)
    return buf.getvalue(), im.size


def probe_size(field_file):
    """(가로, 세로) — 아직 저장 전인 업로드 파일을 메모리에서 잰다."""
    field_file.open('rb')
    with Image.open(io.BytesIO(field_file.read())) as im:
        return ImageOps.exif_transpose(im).size


def compress_upload(field_file):
    """Re-encode a just-uploaded image as WebP before it reaches storage.

    Admin uploads come straight off a phone — several megabytes each — and
    would otherwise be served at full size. 변환했으면 (가로, 세로) 를, 이미
    WebP 라 손대지 않았으면 None 을 돌려준다 — 부르는 쪽이 그 값을 그대로
    저장해 두면 화면에서 파일을 다시 열 일이 없다.

    Only safe for a file that is new or replaced: saving routes the name back
    through the field's ``upload_to``, so calling this for a file already in
    storage would nest the directory prefix. Callers detect the change first.
    """
    name = (field_file.name or '').rsplit('/', 1)[-1]
    if not name or name.lower().endswith('.webp'):
        return None
    field_file.open('rb')
    data, size = encode_webp(field_file.read())
    field_file.save(webp_name(name), ContentFile(data), save=False)
    return size
