"""옵션 장치 어드민 — equipment 쪽과 같은 방식으로, 개발자가 아닌 직원 기준."""
from django.contrib import admin
from django.utils.html import format_html

from .models import OptionDevice, OptionPhoto

_THUMB = ('height:{}px;width:auto;border-radius:6px;border:1px solid #dee2e6;'
          'background:#fff;object-fit:contain;')


def _thumb(url, height):
    return format_html('<img src="{}" style="' + _THUMB.format(height) + '" />', url)


def _muted(text):
    return format_html('<span style="color:#9296a8;">{}</span>', text)


class OptionPhotoInline(admin.TabularInline):
    model = OptionPhoto
    extra = 2
    fields = ['preview', 'image', 'column_label', 'column_tag', 'caption', 'order']
    readonly_fields = ['preview']
    verbose_name = '사진'
    verbose_name_plural = '사진 — 칸 이름이 같은 사진끼리 한 칸에 묶여 나옵니다'

    @admin.display(description='미리보기')
    def preview(self, obj):
        if obj.pk and obj.image:
            try:
                return _thumb(obj.image.url, 78)
            except ValueError:
                pass
        return _muted('없음')


@admin.register(OptionDevice)
class OptionDeviceAdmin(admin.ModelAdmin):
    list_display = ['thumb', 'title', 'column_summary', 'order', 'is_active']
    list_display_links = ['thumb', 'title']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'lead']
    ordering = ['order', 'id']
    save_on_top = True
    inlines = [OptionPhotoInline]

    fieldsets = (
        ('내용', {
            'fields': ('title', 'lead', 'note'),
            'description': '장치명은 섹션 제목으로, 설명은 그 아래 한 줄로 나갑니다. '
                           '보조 문구는 비워두셔도 됩니다.',
        }),
        ('노출 설정', {
            'fields': ('order', 'is_active'),
            'description': '순서가 작을수록 페이지 위쪽에 나옵니다. '
                           '노출을 끄면 페이지에서 사라집니다.',
        }),
    )

    @admin.display(description='사진')
    def thumb(self, obj):
        first = obj.photos.order_by('order', 'id').first()
        if first and first.image:
            try:
                return _thumb(first.image.url, 44)
            except ValueError:
                pass
        return _muted('없음')

    @admin.display(description='칸 구성')
    def column_summary(self, obj):
        cols = obj.columns()
        if not cols:
            return format_html('<span style="color:#c62828;">사진 없음</span>')
        return ' · '.join(f'{c["label"]} ({len(c["photos"])}장)' for c in cols)

    def get_queryset(self, request):
        # column_summary/thumb 가 행마다 사진 테이블을 두드리지 않도록.
        return super().get_queryset(request).prefetch_related('photos')
