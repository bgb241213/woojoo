"""Enquiry admin.

These two tables are the only place customer personal data lives, so the
retention deadline is shown on every row rather than left implicit: staff can
see at a glance what is about to be destroyed under 개인정보보호법 §21 and act
on it before it goes. Deletion itself stays automatic (quotes/retention.py).
"""
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from . import retention
from .models import QuoteRequest, QuoteItem, CallbackRequest

STATUS_COLOURS = {
    'pending':   ('#b26a00', '#fff4e0'),
    'reviewing': ('#1F286F', '#e8eaf6'),
    'completed': ('#2e7d32', '#e8f5e9'),
    'cancelled': ('#9296a8', '#f1f2f6'),
}


def _pill(text, fg, bg):
    return format_html(
        '<span style="display:inline-block;padding:3px 10px;border-radius:999px;'
        'font-weight:700;font-size:12px;color:{};background:{};">{}</span>',
        fg, bg, text,
    )


def _retention_cell(created_at, years):
    """Days left before this record is destroyed, coloured as it runs out."""
    if not created_at:
        return '—'
    deadline = created_at + (timezone.now() - retention.cutoff(years))
    days = (deadline - timezone.now()).days
    stamp = timezone.localtime(deadline).strftime('%Y-%m-%d')
    if days <= 30:
        return format_html('<span style="color:#c62828;font-weight:700;">{} (D-{})</span>', stamp, days)
    return format_html('<span style="color:#6b7080;">{} (D-{})</span>', stamp, days)


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 0
    readonly_fields = ('equipment', 'quantity')
    can_delete = False
    verbose_name = '신청 장비'
    verbose_name_plural = '신청 장비 — 고객이 선택한 목록입니다 (수정 불가)'


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'company_name', 'name', 'phone',
                    'items_summary', 'inquiry_type', 'status_badge', 'expires_on')
    list_display_links = ('created_on', 'company_name')
    list_filter = ('status', 'inquiry_type', 'created_at')
    search_fields = ('company_name', 'name', 'phone', 'email')
    ordering = ('-created_at',)
    list_per_page = 30
    save_on_top = True
    date_hierarchy = 'created_at'

    # The consent timestamp is the evidence of lawful collection, so it must
    # never be editable after the fact.
    readonly_fields = ('created_at', 'privacy_agreed_at', 'expires_on')
    inlines = [QuoteItemInline]

    fieldsets = (
        ('처리 현황', {
            'fields': ('status',),
            'description': '연락을 마쳤으면 상태를 바꿔주세요. 목록에서 한눈에 구분됩니다.',
        }),
        ('고객 정보', {
            'fields': ('company_name', 'name', 'phone', 'email', 'business_number'),
        }),
        ('견적 내용', {
            'fields': ('inquiry_type', 'work_height_class', 'start_date', 'end_date',
                       'delivery_address', 'budget', 'message'),
        }),
        ('개인정보 관리', {
            'fields': ('privacy_agreed_at', 'created_at', 'expires_on'),
            'description': f'개인정보보호법에 따라 신청일로부터 '
                           f'{retention.QUOTE_RETENTION_YEARS}년이 지나면 자동으로 파기됩니다. '
                           '동의일시는 적법하게 수집했다는 증거이므로 수정할 수 없습니다.',
        }),
    )

    @admin.display(description='신청일', ordering='created_at')
    def created_on(self, obj):
        return timezone.localtime(obj.created_at).strftime('%Y-%m-%d %H:%M')

    @admin.display(description='상태', ordering='status')
    def status_badge(self, obj):
        fg, bg = STATUS_COLOURS.get(obj.status, ('#1a1a2e', '#eceff1'))
        return _pill(obj.get_status_display(), fg, bg)

    @admin.display(description='신청 장비')
    def items_summary(self, obj):
        items = list(obj.items.all())
        if not items:
            return format_html('<span style="color:#9296a8;">—</span>')
        head = ', '.join(f'{i.equipment.name}×{i.quantity}' for i in items[:2])
        return head if len(items) <= 2 else format_html('{} 외 {}건', head, len(items) - 2)

    @admin.display(description='파기 예정일')
    def expires_on(self, obj):
        return _retention_cell(obj.created_at, retention.QUOTE_RETENTION_YEARS)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items__equipment')


@admin.register(CallbackRequest)
class CallbackRequestAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'phone', 'short_message', 'called_badge', 'expires_on')
    list_display_links = ('created_on', 'phone')
    list_filter = ('is_called', 'created_at')
    search_fields = ('phone', 'message')
    ordering = ('-created_at',)
    list_per_page = 30
    save_on_top = True

    readonly_fields = ('created_at', 'privacy_agreed_at', 'expires_on')

    fieldsets = (
        ('처리 현황', {
            'fields': ('is_called',),
            'description': '전화를 드렸으면 체크해 주세요.',
        }),
        ('신청 내용', {
            'fields': ('phone', 'message'),
        }),
        ('개인정보 관리', {
            'fields': ('privacy_agreed_at', 'created_at', 'expires_on'),
            'description': f'개인정보보호법에 따라 신청일로부터 '
                           f'{retention.CALLBACK_RETENTION_YEARS}년이 지나면 자동으로 파기됩니다.',
        }),
    )

    actions = ['mark_called']

    @admin.display(description='신청일시', ordering='created_at')
    def created_on(self, obj):
        return timezone.localtime(obj.created_at).strftime('%Y-%m-%d %H:%M')

    @admin.display(description='문의 내용')
    def short_message(self, obj):
        if not obj.message:
            return format_html('<span style="color:#9296a8;">—</span>')
        return obj.message if len(obj.message) <= 40 else obj.message[:40] + '…'

    @admin.display(description='전화 완료', ordering='is_called')
    def called_badge(self, obj):
        return (_pill('완료', '#2e7d32', '#e8f5e9') if obj.is_called
                else _pill('대기', '#c62828', '#ffebee'))

    @admin.display(description='파기 예정일')
    def expires_on(self, obj):
        return _retention_cell(obj.created_at, retention.CALLBACK_RETENTION_YEARS)

    @admin.action(description='선택한 신청을 전화 완료로 표시')
    def mark_called(self, request, queryset):
        updated = queryset.update(is_called=True)
        self.message_user(request, f'{updated}건을 전화 완료로 표시했습니다.')
