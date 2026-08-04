"""KakaoTalk "나에게 보내기" alerts for new enquiries.

Kakao will not let a server send messages unprompted: someone has to authorise
the app once, and the site then holds a refresh token on their behalf. That is
what quotes.views.KakaoConnectView sets up and what KakaoAccount stores.

Everything here is best-effort. An expired authorisation or a Kakao outage must
not surface to the customer submitting the form — the enquiry is already saved,
and the email plus the admin list remain the record.

Uses urllib rather than requests: the two calls involved are simple form posts
and the project has no HTTP client dependency to justify adding one.
"""
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

AUTHORIZE_URL = 'https://kauth.kakao.com/oauth/authorize'
TOKEN_URL = 'https://kauth.kakao.com/oauth/token'
SEND_URL = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'
PROFILE_URL = 'https://kapi.kakao.com/v2/user/me'

SCOPE = 'talk_message'
TIMEOUT = 10

# Kakao's default text template caps the body at 200 characters; anything longer
# is rejected outright rather than trimmed, so trim it here.
TEXT_LIMIT = 200


class KakaoError(Exception):
    pass


def is_configured():
    return bool(settings.KAKAO_REST_API_KEY)


def _request(url, data=None, headers=None):
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode('utf-8') or '{}')
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', 'replace')[:400]
        raise KakaoError(f'HTTP {exc.code}: {detail}') from exc
    except Exception as exc:
        raise KakaoError(str(exc)) from exc


def authorize_url(redirect_uri):
    params = {
        'client_id': settings.KAKAO_REST_API_KEY,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': SCOPE,
    }
    return f'{AUTHORIZE_URL}?{urllib.parse.urlencode(params)}'


def _token_request(data):
    """Kakao turns 클라이언트 시크릿 on by default for new REST API keys, and
    then rejects every token call that omits it. Sent only when configured so
    an app with the feature switched off still works."""
    if settings.KAKAO_CLIENT_SECRET:
        data = {**data, 'client_secret': settings.KAKAO_CLIENT_SECRET}
    return _request(TOKEN_URL, data)


def _store_tokens(account, payload):
    """Persist a token response. Kakao only returns a refresh token when it
    issues a new one, so the existing value must be kept otherwise."""
    account.access_token = payload.get('access_token', '')
    expires_in = int(payload.get('expires_in') or 0)
    account.access_expires_at = timezone.now() + timedelta(seconds=max(expires_in - 60, 0))
    if payload.get('refresh_token'):
        account.refresh_token = payload['refresh_token']
    return account


def complete_connection(code, redirect_uri):
    """Exchange the one-time code for tokens and save them. Returns the account."""
    from .models import KakaoAccount

    payload = _token_request({
        'grant_type': 'authorization_code',
        'client_id': settings.KAKAO_REST_API_KEY,
        'redirect_uri': redirect_uri,
        'code': code,
    })
    if not payload.get('refresh_token'):
        raise KakaoError('카카오가 갱신 토큰을 주지 않았습니다. 동의 항목을 확인해 주세요.')

    account = KakaoAccount.current() or KakaoAccount(refresh_token='')
    _store_tokens(account, payload)
    account.last_error = ''
    try:
        me = _request(PROFILE_URL, headers={'Authorization': f'Bearer {account.access_token}'})
        account.nickname = (me.get('properties') or {}).get('nickname', '')
    except KakaoError:
        pass  # Nickname is cosmetic; a failure here must not block the connection.
    account.save()
    return account


def _valid_access_token(account):
    if account.access_token and account.access_expires_at and account.access_expires_at > timezone.now():
        return account.access_token
    payload = _token_request({
        'grant_type': 'refresh_token',
        'client_id': settings.KAKAO_REST_API_KEY,
        'refresh_token': account.refresh_token,
    })
    _store_tokens(account, payload)
    account.save()
    return account.access_token


def send_to_me(text, link_url=None, button_title=None):
    """Push one message to the linked account. Returns True when Kakao accepted it."""
    from .models import KakaoAccount

    if not is_configured():
        return False
    account = KakaoAccount.current()
    if not account or not account.refresh_token:
        logger.info('Kakao alert skipped: no account linked.')
        return False

    if len(text) > TEXT_LIMIT:
        text = text[:TEXT_LIMIT - 1] + '…'

    template = {'object_type': 'text', 'text': text}
    # `link` is required even when empty. A url is only included when the site
    # address is known, because Kakao rejects domains not registered on the app.
    template['link'] = (
        {'web_url': link_url, 'mobile_web_url': link_url} if link_url else {}
    )
    if link_url and button_title:
        template['button_title'] = button_title

    try:
        token = _valid_access_token(account)
        _request(
            SEND_URL,
            {'template_object': json.dumps(template, ensure_ascii=False)},
            {'Authorization': f'Bearer {token}'},
        )
    except KakaoError as exc:
        logger.warning('Kakao alert failed: %s', exc)
        KakaoAccount.objects.filter(pk=account.pk).update(
            last_error=f'{timezone.localtime():%Y-%m-%d %H:%M} · {exc}'[:500]
        )
        return False

    KakaoAccount.objects.filter(pk=account.pk).update(last_sent_at=timezone.now(), last_error='')
    return True
