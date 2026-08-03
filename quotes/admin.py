from django.contrib import admin
from .models import QuoteRequest, QuoteItem, CallbackRequest


class QuoteItemInline(admin.TabularInline):
    model         = QuoteItem
    extra         = 0
    readonly_fields = ('equipment', 'quantity')
    can_delete    = False


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    # ── 목록 ──────────────────────────────────────────
    list_display   = ('company_name', 'name', 'phone', 'inquiry_type', 'status', 'created_at')
    list_filter    = ('status', 'inquiry_type', 'created_at')
    list_editable  = ('status',)
    search_fields  = ('company_name', 'name', 'phone')
    ordering       = ('-created_at',)

    # ── 상세 폼 ───────────────────────────────────────
    # The consent timestamp is the evidence of lawful collection, so it must
    # never be editable after the fact.
    readonly_fields = ('created_at', 'privacy_agreed_at')
    inlines         = [QuoteItemInline]

    fieldsets = (
        ('고객 정보', {
            'fields': ('company_name', 'name', 'phone', 'email', 'business_number'),
        }),
        ('견적 정보', {
            'fields': ('inquiry_type', 'work_height_class', 'start_date', 'end_date', 'delivery_address', 'budget', 'message'),
        }),
        ('처리 현황', {
            'fields': ('status', 'created_at'),
        }),
        ('개인정보 동의', {
            'fields': ('privacy_agreed_at',),
            'description': '견적 신청 시 개인정보 수집·이용에 동의한 일시입니다. 수정할 수 없습니다.',
        }),
    )


@admin.register(CallbackRequest)
class CallbackRequestAdmin(admin.ModelAdmin):
    list_display   = ('phone', 'message', 'is_called', 'created_at')
    list_editable  = ('is_called',)
    list_filter    = ('is_called', 'created_at')
    ordering       = ('-created_at',)
    readonly_fields = ('created_at', 'privacy_agreed_at')
