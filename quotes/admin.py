from django.contrib import admin
from .models import QuoteRequest, QuoteItem


class QuoteItemInline(admin.TabularInline):
    model         = QuoteItem
    extra         = 0
    readonly_fields = ('equipment', 'quantity')
    can_delete    = False


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    # ── 목록 ──────────────────────────────────────────
    list_display   = ('company_name', 'name', 'phone', 'status', 'created_at')
    list_filter    = ('status', 'created_at')
    list_editable  = ('status',)
    search_fields  = ('company_name', 'name', 'phone')
    ordering       = ('-created_at',)

    # ── 상세 폼 ───────────────────────────────────────
    readonly_fields = ('created_at',)
    inlines         = [QuoteItemInline]

    fieldsets = (
        ('고객 정보', {
            'fields': ('company_name', 'name', 'phone', 'email', 'business_number'),
        }),
        ('렌탈 정보', {
            'fields': ('start_date', 'end_date', 'delivery_address', 'budget', 'message'),
        }),
        ('처리 현황', {
            'fields': ('status', 'created_at'),
        }),
    )
