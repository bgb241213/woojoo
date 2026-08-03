"""Precompute the wheel-line position of every equipment photo.

Scanning 100 drawings is far too slow to do per request, so the detected
values are written to ``equipment/data/photo_baselines.json`` and committed.
Re-run this whenever the photo library changes.

Detection is good but not infallible — plan-view drawings and real
photographs have no ground line to find.  Review ``--contact-sheet`` output
and correct any strays from the admin (장비 이미지 → 바퀴선 위치), which
always wins over the value stored here.
"""
import json
import statistics

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

from equipment.baseline import detect_baseline
from equipment.photos import BASELINE_PATH

# static/images subdirectories holding per-equipment photo folders.
SOURCES = ['rental', 'sale']

# Photo indices the compare page actually renders (0.png is unused there).
VIEW_INDICES = [1, 2, 3]

# Flag anything this far from its view's median for human review.
OUTLIER_MARGIN = 0.08


class Command(BaseCommand):
    help = 'Detect the wheel line in every equipment photo and cache it to JSON.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--contact-sheet',
            metavar='PATH',
            help='Also write a QA image with the detected line drawn on every photo.',
        )

    def handle(self, *args, **options):
        images_root = settings.BASE_DIR / 'static' / 'images'

        detected = {}   # {source: {equipment_id: {index: fraction}}}
        by_view = {}    # {index: [fraction, ...]} — for the median fallback
        failures = []
        scanned = []    # (path, fraction) for the contact sheet

        for source in SOURCES:
            base = images_root / source
            if not base.is_dir():
                continue
            for folder in sorted(base.iterdir(), key=lambda p: p.name):
                if not folder.is_dir() or not folder.name.isdigit():
                    continue
                for index in VIEW_INDICES:
                    path = folder / f'{index}.png'
                    if not path.is_file():
                        continue
                    value = detect_baseline(path)
                    if value is None:
                        failures.append(f'{source}/{folder.name}/{index}.png')
                        continue
                    detected.setdefault(source, {}).setdefault(folder.name, {})[str(index)] = round(value, 4)
                    by_view.setdefault(index, []).append(value)
                    scanned.append((path, value))

        if not scanned:
            self.stdout.write(self.style.ERROR('No photos found under static/images/.'))
            return

        payload = {'_defaults': {
            str(index): round(statistics.median(values), 4)
            for index, values in sorted(by_view.items())
        }}
        payload.update({source: detected[source] for source in SOURCES if source in detected})

        BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
        BASELINE_PATH.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')

        self.stdout.write(self.style.SUCCESS(
            f'Wrote {len(scanned)} baselines to '
            f'{BASELINE_PATH.relative_to(settings.BASE_DIR)}'
        ))
        for index, values in sorted(by_view.items()):
            self.stdout.write(
                f'  view {index}: n={len(values)} '
                f'min={min(values) * 100:.1f}% '
                f'median={statistics.median(values) * 100:.1f}% '
                f'max={max(values) * 100:.1f}%'
            )

        self._report_review(by_view, detected, failures)

        if options['contact_sheet']:
            self._contact_sheet(scanned, options['contact_sheet'])

    def _report_review(self, by_view, detected, failures):
        """List everything a human should eyeball before trusting the output."""
        for path in failures:
            self.stdout.write(self.style.WARNING(f'  ! no wheel line found: {path}'))

        medians = {index: statistics.median(values) for index, values in by_view.items()}
        strays = []
        for source, folders in detected.items():
            for equipment_id, views in folders.items():
                for index, value in views.items():
                    drift = abs(value - medians[int(index)])
                    if drift > OUTLIER_MARGIN:
                        strays.append((drift, f'{source}/{equipment_id}/{index}.png', value))

        for drift, path, value in sorted(strays, reverse=True):
            self.stdout.write(self.style.WARNING(
                f'  ? unusual: {path} at {value * 100:.1f}% '
                f'({drift * 100:.1f}%p from view median) — check the drawing'
            ))

        if failures or strays:
            self.stdout.write(
                '  Correct any of the above from the admin: '
                '장비 → 장비 이미지 → 바퀴선 위치(%)'
            )

    def _contact_sheet(self, scanned, out_path):
        """Grid of every photo with its detected wheel line drawn in red."""
        cell, columns = 220, 8
        rows = (len(scanned) + columns - 1) // columns
        sheet = Image.new('RGB', (cell * columns, cell * rows), 'white')
        draw = ImageDraw.Draw(sheet)

        for i, (path, value) in enumerate(scanned):
            x, y = (i % columns) * cell, (i // columns) * cell
            with Image.open(path) as src:
                thumb = src.convert('RGB')
                thumb.thumbnail((cell, cell))
            # Bottom-align so the drawn line matches how the page anchors these.
            top = y + cell - thumb.height
            sheet.paste(thumb, (x, top))
            line_y = top + thumb.height - 1 - round(value * thumb.height)
            draw.line([(x, line_y), (x + thumb.width, line_y)], fill='red', width=2)
            draw.text((x + 3, y + 3), '/'.join(path.parts[-3:]), fill='#0055cc')

        sheet.save(out_path)
        self.stdout.write(self.style.SUCCESS(f'Contact sheet written to {out_path}'))
