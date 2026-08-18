from django.views.generic import TemplateView

from .models import OptionDevice


class OptionsView(TemplateView):
    template_name = 'options/list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # 사진까지 한 번에 — 섹션마다 칸을 다시 묶느라 행별 조회가 나가면 안 된다.
        ctx['devices'] = (OptionDevice.objects
                          .filter(is_active=True)
                          .prefetch_related('photos'))
        return ctx
