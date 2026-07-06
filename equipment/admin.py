from django.contrib import admin
from django.utils.html import format_html
from .models import Equipment, EquipmentImage


class EquipmentImageInline(admin.TabularInline):
    model  = EquipmentImage
    extra  = 3
    fields = ['preview', 'image', 'image_type', 'order']
    readonly_fields = ['preview']

    @admin.display(description='미리보기')
    def preview(self, obj):
        if obj.pk and obj.image:
            try:
                return format_html(
                    '<img src="{}" style="height:72px; width:auto; border-radius:6px; '
                    'border:1px solid #dee2e6; background:#fff;" />',
                    obj.image.url,
                )
            except ValueError:
                pass
        return format_html('<span style="color:#999;">—</span>')


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    # ── 목록 ──────────────────────────────────────────
    list_display  = ('name', 'category', 'type', 'image_count', 'is_for_sale', 'is_active', 'created_at')
    list_filter   = ('category', 'type', 'is_for_sale', 'is_active')
    list_editable = ('is_for_sale', 'is_active')
    search_fields = ('name',)
    ordering      = ('category', 'name')

    # ── 상세 폼 ───────────────────────────────────────
    readonly_fields = ('created_at', 'image_preview')
    inlines = [EquipmentImageInline]

    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'category', 'type', 'image', 'image_preview', 'description'),
        }),
        ('스펙 정보', {
            'fields': (
                'max_work_height',
                'max_platform_height',
                'platform_size',
                'equipment_size',
                'equipment_weight',
                'max_load',
                'power_type',
            ),
        }),
        ('설정', {
            'fields': ('is_active', 'is_for_sale', 'created_at'),
        }),
    )

    # ── 커스텀 컬럼: 등록된 이미지 수 (렌탈/판매) ────
    @admin.display(description='이미지')
    def image_count(self, obj):
        rental = obj.images.filter(image_type='rental').count()
        sales = obj.images.filter(image_type='sales').count()
        return f'렌탈 {rental} · 판매 {sales}'

    # ── 커스텀 필드: 이미지 미리보기 ────────────────
    @admin.display(description='현재 사진 미리보기')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:220px; max-width:360px; '
                'border-radius:8px; border:1px solid #dee2e6; margin-top:6px;" />',
                obj.image.url,
            )
        return format_html('<span style="color:#999;">등록된 사진이 없습니다.</span>')

    # ── help_text를 위한 get_form 오버라이드 ─────────
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        helps = {
            'max_work_height':     '예: 7.62m',
            'max_platform_height': '예: 5.79m',
            'equipment_weight':    '예: 1,312kg',
            'max_load':            '예: 227kg',
            'equipment_size':      '예: 1.78 x 0.81 x 1.99m',
            'platform_size':       '예: 1.63 x 0.66m',
            'power_type':          '예: 배터리 / 디젤',
        }
        for field_name, help_text in helps.items():
            if field_name in form.base_fields:
                form.base_fields[field_name].help_text = help_text
        return form
