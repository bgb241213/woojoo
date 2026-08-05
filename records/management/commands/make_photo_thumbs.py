"""Build display-sized copies of the sales-record photos.

The originals are phone shots — up to 2880x3840 and 1.9 MB each. They were
being served untouched into a 116px-wide marquee on the landing page and a
~220px grid on the records wall, so a single visit pulled tens of megabytes to
paint thumbnails. These derivatives are what the pages actually reference.

Two sizes because the two surfaces differ by a factor of two, and the landing
page loads ninety of them at once:

    _t.jpg   320px wide   landing marquee (116px display)
    _c.jpg   640px wide   records wall (220px display)

Idempotent: a derivative newer than its source is left alone, so re-running
after adding a few photos only processes those.
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageOps

# (suffix, target width, JPEG quality)
SIZES = [('_t', 320, 74), ('_c', 640, 78)]


class Command(BaseCommand):
    help = '판매 실적 사진의 표시용 축소본을 생성합니다.'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true',
                            help='Rebuild even when the derivative is up to date.')

    def handle(self, *args, **options):
        root = Path(settings.BASE_DIR) / 'static' / 'images' / 'records'
        if not root.is_dir():
            self.stdout.write(self.style.WARNING(f'{root} 없음 — 건너뜁니다.'))
            return

        sources = sorted(
            p for p in root.glob('*/*.jpg')
            if not any(p.stem.endswith(suffix) for suffix, _, _ in SIZES)
        )

        built = skipped = 0
        before = after = 0
        for src in sources:
            before += src.stat().st_size
            for suffix, width, quality in SIZES:
                out = src.with_name(f'{src.stem}{suffix}.jpg')
                if out.exists() and not options['force'] and out.stat().st_mtime >= src.stat().st_mtime:
                    after += out.stat().st_size
                    skipped += 1
                    continue
                with Image.open(src) as im:
                    # Phone photos carry orientation in EXIF; without this the
                    # thumbnail comes out rotated even though the original looks
                    # right in a viewer.
                    im = ImageOps.exif_transpose(im).convert('RGB')
                    if im.width > width:
                        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
                    im.save(out, 'JPEG', quality=quality, optimize=True, progressive=True)
                after += out.stat().st_size
                built += 1

        self.stdout.write(self.style.SUCCESS(
            f'원본 {len(sources)}장 · 생성 {built}개 · 유지 {skipped}개\n'
            f'원본 {before / 1048576:.1f} MB → 축소본 {after / 1048576:.1f} MB'
        ))
