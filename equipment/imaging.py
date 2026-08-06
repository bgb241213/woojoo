"""WebP encoding for equipment photos.

The design library is committed as ~1200px PNGs averaging 360KB. They are
studio shots on white, which WebP compresses to roughly 7% of the PNG at a
quality indistinguishable on a phone.

Shared by ``import_design_photos`` (which encodes on upload) and
``convert_photos_webp`` (which re-encodes what is already in storage) so both
produce byte-identical output and agree on the stored filename.
"""
import io

from PIL import Image

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
