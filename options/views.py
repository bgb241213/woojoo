from django.views.generic import TemplateView

from .models import OptionDevice


class OptionsView(TemplateView):
    template_name = 'options/list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # 칸과 그 사진까지 한 번에. columns() 가 칸을 돌며 사진을 꺼내므로
        # 여기서 photos 만 당겨두면 정작 쓰이지 않고, 섹션·칸마다 조회가
        # 따로 나간다 — 로컬에서는 티가 안 나도 운영 DB 는 왕복마다 값을 치른다.
        ctx['devices'] = (OptionDevice.objects
                          .filter(is_active=True)
                          .prefetch_related('columns_set__photos'))
        return ctx
