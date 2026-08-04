from django.urls import path

from . import kakao_views, views

app_name = 'quotes'

urlpatterns = [
    path('', views.QuoteCreateView.as_view(), name='form'),
    path('complete/', views.QuoteCompleteView.as_view(), name='complete'),
    path('callback/', views.CallbackCreateView.as_view(), name='callback'),

    # Staff-only: linking the KakaoTalk account that enquiry alerts go to.
    path('kakao/', kakao_views.KakaoStatusView.as_view(), name='kakao_status'),
    path('kakao/connect/', kakao_views.KakaoConnectView.as_view(), name='kakao_connect'),
    path('kakao/callback/', kakao_views.KakaoCallbackView.as_view(), name='kakao_callback'),
    path('kakao/test/', kakao_views.KakaoTestView.as_view(), name='kakao_test'),
]
