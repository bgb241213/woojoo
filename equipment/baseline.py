"""Wheel-line (ground-line) detection for equipment photos.

The compare page stacks machines side by side and scales each one against the
tallest in its row.  For that comparison to read correctly every machine's
wheels must sit on one horizontal line.

The photos are manufacturer spec drawings: the machine is centred on a white
square canvas with a *dimension band* (the black ``2.48 [m]`` arrows) printed
below the wheels.  That band's height varies per file, so anchoring the canvas
bottom — which is what CSS does by default — anchors the band, not the wheels.

Detection exploits the one property every drawing shares: the machine is drawn
in colour (orange/blue) or mid grey, while the dimension band is pure black.
Scanning up from the bottom for the lowest *vertically thick* run of machine
pixels finds the wheels; the thickness requirement is what keeps the thin
dimension arrows — and their anti-aliased grey fringes — from being mistaken
for a wheel.
"""
from PIL import Image, ImageChops

# Pixel classification thresholds, validated against the current photo library.
WHITE = 242   # luminance at or above this is page background
BLACK = 65    # luminance at or below this is dimension-band ink
SAT   = 40    # saturation above this is machine paintwork regardless of luminance

# Run/thickness requirements scale with the image so a 555px drawing is not
# held to the same pixel counts as a 1153px one.
RUN_RATIO   = 0.017
THICK_RATIO = 0.010


def _machine_mask(im):
    """Bilevel mask: 255 where a pixel belongs to the machine, 0 elsewhere."""
    r, g, b = im.split()
    mx = ImageChops.lighter(ImageChops.lighter(r, g), b)
    mn = ImageChops.darker(ImageChops.darker(r, g), b)
    sat = ImageChops.subtract(mx, mn)
    lum = im.convert('L')

    not_white = lum.point(lambda v: 255 if v < WHITE else 0)
    not_black = lum.point(lambda v: 255 if v > BLACK else 0)
    coloured  = sat.point(lambda v: 255 if v > SAT else 0)

    # not_white AND (not_black OR coloured)
    return ImageChops.darker(not_white, ImageChops.lighter(not_black, coloured))


def detect_baseline(path):
    """Height of the wheel line above the bottom of the *cell* it renders in.

    Returns a 0–1 fraction, or ``None`` when no machine could be found.

    The value is expressed relative to the rendered cell rather than the source
    image because the compare page draws these with ``background-size: contain``
    in a square cell: a portrait or square image is scaled to fill the cell's
    height, but a landscape one is not.
    """
    with Image.open(path) as src:
        im = src.convert('RGB')
        w, h = im.size
        mask = _machine_mask(im)

    run_len = max(8, round(w * RUN_RATIO))
    thick = max(5, round(h * THICK_RATIO))

    # A row counts as "machine" when it holds `run_len` consecutive mask pixels.
    # Searching the packed bytes keeps this fast without numpy.
    data = mask.tobytes()
    needle = b'\xff' * run_len

    consecutive = 0
    lowest = None
    for y in range(h):
        if data[y * w:(y + 1) * w].find(needle) >= 0:
            consecutive += 1
            if consecutive >= thick:
                lowest = y
        else:
            consecutive = 0

    if lowest is None:
        return None

    # `contain` fits by height only when the image is at least as tall as wide.
    displayed = min(1.0, h / w)
    return (h - 1 - lowest) / h * displayed


def detect_percent_for_file(fieldfile):
    """Wheel line of an uploaded photo, as a percentage, or ``None``.

    Wraps :func:`detect_baseline` for ``EquipmentImage.image``: the file is read
    through the storage backend (R2 in production), so it is pulled into memory
    first rather than handed to Pillow as a lazily-seeking remote stream.

    Never raises. A photo the detector cannot read — a plan view, a real
    photograph with no clean ground line, a corrupt upload — must not stop staff
    from saving the record; the compare page just falls back to the view median
    and the value can be typed in by hand.
    """
    import io
    import logging

    try:
        fieldfile.open('rb')
        try:
            data = fieldfile.read()
        finally:
            fieldfile.close()
        fraction = detect_baseline(io.BytesIO(data))
    except Exception:
        logging.getLogger(__name__).warning(
            'Baseline detection failed for %s', getattr(fieldfile, 'name', '?'), exc_info=True
        )
        return None

    return None if fraction is None else round(fraction * 100, 2)
