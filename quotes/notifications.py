"""Emails the office when a customer submits an enquiry.

Sending is best-effort by design. The enquiry is already committed to the
database before any of this runs, so a refused SMTP login or a mail server
timeout must never surface as an error to the customer — they would resubmit,
or worse, assume the company never got it. Failures are logged and swallowed;
the admin list stays the source of truth.

Formatting is plain text on purpose: it renders identically in Daum, Naver and
mobile clients, and there is nothing here that HTML would make clearer.
"""
import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

logger = logging.getLogger(__name__)

_LINE = '─' * 34


def _fmt(value, empty='-'):
    """Blank fields print as a dash so the columns stay readable."""
    if value is None or value == '':
        return empty
    return str(value)


def _when(dt):
    return timezone.localtime(dt).strftime('%Y-%m-%d %H:%M') if dt else '-'


def _rows(pairs):
    """Left-pad the labels so the values line up in a monospaced client."""
    width = max((len(k) for k, _ in pairs), default=0)
    return '\n'.join(f'  {k.ljust(width)}   {v}' for k, v in pairs)


def _section(title, pairs):
    return f'■ {title}\n{_rows(pairs)}'


def _admin_link(path):
    base = (settings.SITE_BASE_URL or '').rstrip('/')
    return f'{base}{path}' if base else None


def _send(subject, body, reply_to=None):
    recipients = settings.ENQUIRY_NOTIFICATION_EMAILS
    if not recipients:
        logger.info('Enquiry notification skipped: no recipient configured.')
        return False
    try:
        EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
            # Lets staff hit Reply and reach the customer directly.
            reply_to=[reply_to] if reply_to else None,
        ).send(fail_silently=False)
        return True
    except Exception:
        logger.exception('Enquiry notification failed (subject=%s)', subject)
        return False


def send_quote_notification(quote):
    """Notify the office about a new 견적 신청."""
    who = ' '.join(x for x in (quote.company_name, quote.name) if x) or quote.phone
    subject = f'[우주렌탈] 견적 신청 - {who}'

    period = '-'
    if quote.start_date or quote.end_date:
        period = f'{_fmt(quote.start_date)} ~ {_fmt(quote.end_date)}'

    parts = [
        f'홈페이지에서 견적 신청이 접수되었습니다.\n{_LINE}',
        _section('접수 정보', [
            ('접수일시', _when(quote.created_at)),
            ('구분', quote.get_inquiry_type_display() or '-'),
        ]),
        # business_number is admin-only — the public form never collects it, so
        # listing it would print a permanent dash.
        _section('고객 정보', [
            ('회사명', _fmt(quote.company_name)),
            ('담당자', _fmt(quote.name)),
            ('연락처', _fmt(quote.phone)),
            ('이메일', _fmt(quote.email)),
        ]),
        _section('요청 내용', [
            ('필요 작업고', _fmt(quote.work_height_class)),
            ('사용 기간', period),
            ('현장 주소', _fmt(quote.delivery_address)),
            ('예산', f'{quote.budget:,}원' if quote.budget else '-'),
        ]),
    ]

    items = list(quote.items.select_related('equipment'))
    if items:
        listed = '\n'.join(f'  · {i.equipment.name} × {i.quantity}대' for i in items)
        parts.append(f'■ 신청 장비\n{listed}')

    if quote.message:
        parts.append(f'■ 추가 요청사항\n  {quote.message}')

    parts.append(_section('개인정보 동의', [('동의일시', _when(quote.privacy_agreed_at))]))

    link = _admin_link(f'/admin/quotes/quoterequest/{quote.pk}/change/')
    if link:
        parts.append(f'{_LINE}\n관리자 페이지에서 보기\n{link}')

    return _send(subject, '\n\n'.join(parts), reply_to=quote.email or None)


def send_callback_notification(callback):
    """Notify the office about a new 콜백 신청 (left outside business hours)."""
    subject = f'[우주렌탈] 콜백 신청 - {callback.phone}'

    parts = [
        f'영업시간 외 콜백 신청이 접수되었습니다.\n다음 영업일에 연락이 필요합니다.\n{_LINE}',
        _section('신청 내용', [
            ('접수일시', _when(callback.created_at)),
            ('연락처', callback.phone),
        ]),
    ]

    if callback.message:
        parts.append(f'■ 남긴 내용\n  {callback.message}')

    parts.append(_section('개인정보 동의', [('동의일시', _when(callback.privacy_agreed_at))]))

    link = _admin_link(f'/admin/quotes/callbackrequest/{callback.pk}/change/')
    if link:
        parts.append(f'{_LINE}\n관리자 페이지에서 보기\n{link}')

    return _send(subject, '\n\n'.join(parts))
