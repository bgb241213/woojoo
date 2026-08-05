from django.views.generic import TemplateView

from equipment.photos import display_variant

from .models import SalesRecord


class RecordsListView(TemplateView):
    template_name = 'records/list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        records = SalesRecord.objects.filter(is_active=True).prefetch_related('images')
        # Flatten to one tile per photo — the wall shows every shipment photo.
        tiles = []
        for r in records:
            model = r.model_name or '고소작업대'
            date = r.shipped_date.strftime('%Y.%m.%d')
            for src in r.photo_urls():
                # The wall renders these ~220px wide; the originals are up to
                # 2880px. `full` stays for the lightbox.
                tiles.append({
                    'src': display_variant(src, '_c'),
                    'full': src,
                    'model': model,
                    'date': date,
                })
        ctx['tiles'] = tiles
        ctx['record_count'] = records.count()
        ctx['photo_count'] = len(tiles)
        return ctx
