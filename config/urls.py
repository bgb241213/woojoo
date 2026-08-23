from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('equipment/', include('equipment.urls')),
    path('quote/', include('quotes.urls')),
    path('options/', include('options.urls')),
    path('sales/', include('sales.urls')),
    path('records/', include('records.urls')),
    # 영업용 판매 카탈로그. 같은 화면을 메뉴만 걷어낸 껍데기로 다시 낸다.
    path('catalog/', include('catalog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__reload__/', include('django_browser_reload.urls'))]
