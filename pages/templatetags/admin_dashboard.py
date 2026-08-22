"""관리자 첫 화면에 쓰는 숫자들.

기본 첫 화면은 모델 목록만 늘어놓아서, 로그인한 직원이 "오늘 내가 뭘 해야
하는지"를 알 수 없었다. 답을 해야 하는 건수를 먼저 보여주려고 만든 태그다.

숫자는 전부 COUNT 한 번씩이고 첫 화면에서만 쓰인다.
"""
from django import template
from django.urls import reverse
from django.utils import timezone

register = template.Library()


@register.simple_tag
def admin_todo():
    """답을 기다리는 건수. [(제목, 건수, 링크, 급함 여부)] 순서대로 나온다."""
    from quotes.models import CallbackRequest, QuoteRequest

    today = timezone.localdate()

    pending = QuoteRequest.objects.filter(status='pending').count()
    today_quotes = QuoteRequest.objects.filter(created_at__date=today).count()
    waiting_calls = CallbackRequest.objects.filter(is_called=False).count()

    quote_url = reverse('admin:quotes_quoterequest_changelist')
    call_url = reverse('admin:quotes_callbackrequest_changelist')

    return [
        {'label': '연락 안 드린 견적', 'count': pending,
         'url': f'{quote_url}?status__exact=pending',
         'hint': '고객이 답을 기다리는 중입니다',
         'urgent': pending > 0},
        {'label': '전화 못 드린 콜백', 'count': waiting_calls,
         'url': f'{call_url}?is_called__exact=0',
         'hint': '영업시간 외에 번호를 남긴 분들입니다',
         'urgent': waiting_calls > 0},
        {'label': '오늘 들어온 견적', 'count': today_quotes,
         'url': quote_url,
         'hint': '오늘 하루 접수된 전체 건수입니다',
         'urgent': False},
    ]


@register.simple_tag
def admin_shortcuts():
    """자주 하는 일로 바로 가는 버튼들."""
    return [
        {'label': '판매 실적 사진 올리기', 'icon': 'fas fa-camera',
         'url': reverse('admin:records_salesrecord_add'),
         'hint': '사진 한 장에 실적 한 건입니다'},
        {'label': '장비 정보 고치기', 'icon': 'fas fa-truck-loading',
         'url': reverse('admin:equipment_equipment_changelist'),
         'hint': '스펙·사진·노출 여부'},
        {'label': '옵션 장치 고치기', 'icon': 'fas fa-toolbox',
         'url': reverse('admin:options_optiondevice_changelist'),
         'hint': '보호장치·협착방지장치·라인빔'},
        {'label': '견적 신청 보기', 'icon': 'fas fa-file-alt',
         'url': reverse('admin:quotes_quoterequest_changelist'),
         'hint': '접수된 문의 전체'},
    ]
