"""Staff-only screens for linking the KakaoTalk alert account.

Kakao's authorisation has to be granted by a person in a browser, so this is a
small three-step flow rather than a settings value: a status page, a redirect
out to Kakao, and the callback that stores the tokens.

Every view is behind staff_member_required — the callback writes credentials,
and the test button sends a real message.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from . import kakao
from .models import KakaoAccount

STAFF_ONLY = method_decorator(staff_member_required, name='dispatch')


def _redirect_uri(request):
    """Must match the URI registered on the Kakao app exactly."""
    return request.build_absolute_uri(reverse('quotes:kakao_callback'))


@STAFF_ONLY
class KakaoStatusView(View):
    template_name = 'quotes/kakao_status.html'

    def get(self, request):
        return render(request, self.template_name, {
            'configured': kakao.is_configured(),
            'account': KakaoAccount.current(),
            'redirect_uri': _redirect_uri(request),
            'message': request.GET.get('m', ''),
            'error': request.GET.get('e', ''),
        })


@STAFF_ONLY
class KakaoConnectView(View):
    def get(self, request):
        if not kakao.is_configured():
            return redirect(reverse('quotes:kakao_status') + '?e=' + 'KAKAO_REST_API_KEY가 설정되지 않았습니다.')
        return HttpResponseRedirect(kakao.authorize_url(_redirect_uri(request)))


@STAFF_ONLY
class KakaoCallbackView(View):
    def get(self, request):
        status = reverse('quotes:kakao_status')
        if request.GET.get('error'):
            reason = request.GET.get('error_description') or request.GET['error']
            return redirect(f'{status}?e=카카오 연결이 취소되었습니다 — {reason}')
        code = request.GET.get('code')
        if not code:
            return redirect(f'{status}?e=인증 코드를 받지 못했습니다.')
        try:
            account = kakao.complete_connection(code, _redirect_uri(request))
        except kakao.KakaoError as exc:
            return redirect(f'{status}?e=연결 실패 — {exc}')
        return redirect(f'{status}?m={account.nickname or "카카오 계정"} 연결이 완료되었습니다.')


@STAFF_ONLY
class KakaoTestView(View):
    """Sends a real message so staff get an immediate yes/no answer."""

    def post(self, request):
        status = reverse('quotes:kakao_status')
        ok = kakao.send_to_me(
            '[우주렌탈] 알림 연결 테스트\n이 메시지가 보이면 정상입니다.',
            link_url=request.build_absolute_uri('/admin/'),
            button_title='관리자 열기',
        )
        if ok:
            return redirect(f'{status}?m=테스트 메시지를 보냈습니다. 카카오톡을 확인해 주세요.')
        account = KakaoAccount.current()
        detail = account.last_error if account and account.last_error else '계정이 연결되지 않았습니다.'
        return redirect(f'{status}?e=발송 실패 — {detail}')
