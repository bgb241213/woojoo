from django.views.generic import TemplateView

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
                tiles.append({'src': src, 'model': model, 'date': date})
        ctx['tiles'] = tiles
        ctx['record_count'] = records.count()
        ctx['photo_count'] = len(tiles)
        return ctx
