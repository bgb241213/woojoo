import random

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
            for src in r.photo_urls():
                # The wall renders these ~220px wide; the originals are up to
                # 2880px. `full` stays for the lightbox.
                tiles.append({
                    'src': display_variant(src, '_c'),
                    'full': src,
                    'model': model,
                })
        # 출고일 순으로 두면 같은 날 나간 장비가 뭉쳐 벽 한 구역이 비슷한 사진만
        # 채운다. 섞어서 전체가 고르게 보이도록 하고, 다시 들어와도 같은 그림이
        # 아니게 한다. 매 요청마다 섞이므로 새로고침하면 배열이 달라진다.
        random.shuffle(tiles)
        ctx['tiles'] = tiles
        ctx['record_count'] = records.count()
        ctx['photo_count'] = len(tiles)
        return ctx
