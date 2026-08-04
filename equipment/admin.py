"""Equipment admin.

Written for staff who are not developers: every column and field is labelled in
Korean, photos are shown rather than described by filename, and the machine-only
concepts (wheel line, ordering) are either automated or explained inline.
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import Equipment, EquipmentImage

_THUMB = ('height:{}px;width:auto;border-radius:6px;border:1px solid #dee2e6;'
          'background:#fff;object-fit:contain;')


def _thumb(url, height):
    return format_html('<img src="{}" style="' + _THUMB.format(height) + '" />', url)


def _muted(text):
    return format_html('<span style="color:#9296a8;">{}</span>', text)


class EquipmentImageInline(admin.TabularInline):
    model = EquipmentImage
    extra = 3
    fields = ['preview', 'image', 'image_type', 'order', 'baseline_status', 'baseline']
    readonly_fields = ['preview', 'baseline_status']
    verbose_name = '사진'
    verbose_name_plural = '사진 — 파일을 고르고 용도만 지정하면 됩니다'

    @admin.display(description='미리보기')
    def preview(self, obj):
        if obj.pk and obj.image:
            try:
                return _thumb(obj.image.url, 78)
            except ValueError:
                pass
        return _muted('저장하면 보입니다')

    @admin.display(description='바퀴선 인식')
    def baseline_status(self, obj):
        """Says in words what the detector did, so the number beside it makes sense."""
        if not obj.pk or not obj.image:
            return _muted('—')
        if obj.baseline is not None:
            return format_html(
                '<span style="color:#1F286F;font-weight:700;">직접 지정 {}%</span>', obj.baseline
            )
        if obj.baseline_detected is not None:
            return format_html(
                '<span style="color:#2e7d32;">자동 인식 {}%</span>', obj.baseline_detected
            )
        return format_html(
            '<span style="color:#b26a00;">인식 실패 — 비교 페이지에서 어긋나 보이면 '
            '오른쪽에 숫자를 넣어주세요</span>'
        )


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('thumb', 'name', 'category', 'type', 'photo_summary',
                    'exposure', 'is_active')
    list_display_links = ('thumb', 'name')
    list_filter = ('is_active', 'is_for_rent', 'is_for_sale', 'category', 'type')
    list_editable = ('is_active',)
    search_fields = ('name',)
    ordering = ('category', 'name')
    list_per_page = 30
    save_on_top = True

    readonly_fields = ('created_at',)
    inlines = [EquipmentImageInline]

    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'category', 'type', 'description'),
            'description': '장비명은 목록과 견적서에 그대로 나옵니다. '
                           '미터급은 장비 렌탈 페이지의 탭 구분에 쓰입니다.',
        }),
        ('스펙', {
            'fields': ('max_work_height', 'max_platform_height', 'platform_size',
                       'equipment_size', 'equipment_weight', 'max_load', 'power_type'),
            'description': '홈페이지 장비 목록과 비교 페이지에 그대로 표시됩니다. '
                           '단위(m, kg)까지 함께 적어주세요.',
        }),
        ('노출 설정', {
            'fields': ('is_active', 'is_for_rent', 'is_for_sale', 'is_flagship'),
            'description': '노출 여부를 끄면 홈페이지 어디에도 나오지 않습니다. '
                           '렌탈과 판매는 각각 독립이라 둘 다 켤 수 있습니다. '
                           '대표장비는 해당 미터급 목록 맨 위에 고정됩니다.',
        }),
        ('기록', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    # The legacy single `image` field is deliberately absent from the fieldsets
    # above: nothing on the site renders it. Its last reference is in
    # equipment/detail.html, and that template is dead too — EquipmentDetailView
    # is a RedirectView that sends /equipment/<id>/ to the list anchor instead of
    # rendering anything. Offering it alongside the photo inline only made staff
    # wonder which of the two inputs actually mattered.
    #
    # The column stays: dropping it would orphan the three files still stored in
    # R2 and buys nothing, since the field is now unreachable from the UI.

    @admin.display(description='사진')
    def thumb(self, obj):
        first = obj.images.order_by('order', 'id').first()
        for candidate in (first.image if first else None, obj.image):
            if candidate:
                try:
                    return _thumb(candidate.url, 44)
                except ValueError:
                    continue
        return _muted('없음')

    @admin.display(description='등록 사진')
    def photo_summary(self, obj):
        rental = obj.images.filter(image_type='rental').count()
        sales = obj.images.filter(image_type='sales').count()
        if not rental and not sales:
            return format_html('<span style="color:#c62828;">없음</span>')
        return format_html('렌탈 <b>{}</b> · 판매 <b>{}</b>', rental, sales)

    @admin.display(description='노출')
    def exposure(self, obj):
        """One column instead of three checkboxes — faster to scan down a list."""
        if not obj.is_active:
            return format_html('<span style="color:#c62828;">숨김</span>')
        tags = [label for flag, label in
                ((obj.is_for_rent, '렌탈'), (obj.is_for_sale, '판매'), (obj.is_flagship, '대표'))
                if flag]
        return ' · '.join(tags) or _muted('어디에도 노출 안 됨')

    def get_queryset(self, request):
        # photo_summary/thumb hit the image table for every row.
        return super().get_queryset(request).prefetch_related('images')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        helps = {
            'name':                '예: LGMG AS1413E',
            'max_work_height':     '예: 15.8m',
            'max_platform_height': '예: 13.8m',
            'equipment_weight':    '예: 3,570kg',
            'max_load':            '예: 320kg',
            'equipment_size':      '가로 x 세로 x 높이 — 예: 2.8 x 1.3 x 2.74m',
            'platform_size':       '가로 x 세로 — 예: 2.64 x 1.12m',
            'power_type':          '예: 배터리 / 디젤',
            'description':         '장비 상세에 들어갈 설명입니다. 비워두어도 됩니다.',
        }
        for name, text in helps.items():
            if name in form.base_fields:
                form.base_fields[name].help_text = text
        return form
