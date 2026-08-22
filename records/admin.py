"""판매 실적 어드민.

한 행이 사진 한 장이다 — 사진을 고르고, 그 사진에 붙는 모델명을 적고,
저장하면 끝이다. 쓰는 사람이 개발자가 아니라는 전제로 파일명 대신 사진을
보여주고 칸마다 어디에 어떻게 나오는지 적었다.
"""
from django.contrib import admin
from django.utils.html import format_html

from equipment.admin_actions import RowActionsMixin

from .models import SalesRecord

_THUMB = ('height:{}px;width:auto;border-radius:6px;border:1px solid #dee2e6;'
          'background:#fff;object-fit:cover;')


def _thumb(url, height):
    return format_html('<img src="{}" style="' + _THUMB.format(height) + '" />', url)


def _muted(text):
    return format_html('<span style="color:#9296a8;">{}</span>', text)


@admin.register(SalesRecord)
class SalesRecordAdmin(RowActionsMixin, admin.ModelAdmin):
    list_display = ('thumb', 'model_name_or_default', 'shipped_date', 'active_toggle', 'row_delete')
    list_display_links = ('thumb', 'model_name_or_default')
    list_filter = ('is_active', 'shipped_date')
    search_fields = ('model_name',)
    ordering = ('-shipped_date', '-id')
    list_per_page = 40
    save_on_top = True
    date_hierarchy = 'shipped_date'

    readonly_fields = ('preview', 'created_at', 'photo_key')

    fieldsets = (
        ('사진', {
            'fields': ('preview', 'image'),
            'description': '사진 한 장이 판매 실적 페이지의 타일 하나가 됩니다. '
                           '여러 장을 올리시려면 실적을 여러 건 등록해 주세요. '
                           '큰 사진을 올리셔도 저장할 때 자동으로 줄어듭니다.',
        }),
        ('사진 정보', {
            'fields': ('model_name', 'shipped_date'),
            'description': '모델명은 사진 위에 뜹니다. 비워두면 "고소작업대"로 나옵니다. '
                           '출고일은 화면에 나오지 않고 정리용으로만 씁니다.',
        }),
        ('노출 설정', {
            'fields': ('is_active',),
            'description': '끄면 이 사진이 판매 실적 페이지에서 사라집니다.',
        }),
        ('기록', {
            'fields': ('photo_key', 'created_at'),
            'classes': ('collapse',),
            'description': '처음 사진을 불러온 폴더 번호입니다. 신경 쓰지 않으셔도 됩니다.',
        }),
    )

    @admin.display(description='지금 등록된 사진')
    def preview(self, obj):
        url = obj.photo_url() if obj.pk else None
        if url:
            return _thumb(url, 220)
        return _muted('아래에서 사진을 고르고 저장하면 여기에 보입니다')

    @admin.display(description='사진')
    def thumb(self, obj):
        url = obj.photo_url()
        if url:
            return _thumb(url, 52)
        return _muted('없음')

    @admin.display(description='모델명', ordering='model_name')
    def model_name_or_default(self, obj):
        return obj.model_name or _muted('고소작업대')
