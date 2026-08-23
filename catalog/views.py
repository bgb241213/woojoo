"""판매 카탈로그 — 영업 상황에서 링크 하나로 건네는 화면.

판매 장비와 판매 실적만 보여주고 홈페이지의 나머지로는 나갈 수 없다. 화면
자체는 기존 두 페이지를 그대로 쓴다. 같은 내용을 두 벌로 두면 한쪽만 고쳐지고
언젠가 서로 어긋나기 때문이다 — 다른 것은 껍데기(base_catalog.html)뿐이다.
"""
from records.views import RecordsListView
from sales.views import SalesListView

CATALOG_BASE = 'base_catalog.html'


class CatalogSalesView(SalesListView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['base_template'] = CATALOG_BASE
        return ctx


class CatalogRecordsView(RecordsListView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['base_template'] = CATALOG_BASE
        return ctx
