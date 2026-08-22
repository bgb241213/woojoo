from pathlib import Path
import os

import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
ALLOWED_HOSTS += ['.railway.app', 'woojoorental.co.kr', 'www.woojoorental.co.kr']

# Railway terminates TLS at its edge and forwards to gunicorn over plain HTTP,
# so without this Django believes every request is insecure and builds http://
# absolute URLs — which is what made Kakao reject the OAuth redirect (KOE006).
# Only trusted behind that proxy; locally there is no such header to honour.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://woojoorental.co.kr',
    'https://www.woojoorental.co.kr',
]

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'django_browser_reload',
    'equipment',
    'quotes',
    'pages',
    'sales',
    'records',
    'options',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Destroys enquiries past their retention period (개인정보보호법 §21).
    'quotes.middleware.RetentionPurgeMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'quotes.context_processors.retention_periods',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ---------------------------------------------------------------------------
# Database
#
# Railway rebuilds the container on every deploy, so a SQLite file inside the
# project directory is wiped each time — which is how the equipment list once
# came back empty and why customer enquiries could not survive a release.
# Production therefore runs on Postgres, injected as DATABASE_URL by Railway.
# Without that variable (i.e. local development) it falls back to SQLite.
# ---------------------------------------------------------------------------
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,          # reuse connections instead of one per request
        conn_health_checks=True,   # drop connections the DB has already closed
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Email — enquiry notifications
#
# Credentials come from the environment so they never reach the repository.
# Without EMAIL_HOST_USER nothing is configured, and mail is printed to the
# console instead: local development and a misconfigured deploy both keep
# working, they simply do not deliver.
# ---------------------------------------------------------------------------
EMAIL_HOST          = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_SSL       = os.environ.get('EMAIL_USE_SSL', 'False') == 'True'
EMAIL_USE_TLS       = not EMAIL_USE_SSL and os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
# A hung SMTP connection would hold the customer's request open; fail fast and
# let quotes.notifications log it.
EMAIL_TIMEOUT       = 10

# Railway blocks outbound SMTP (see quotes/email_backends.py), so the API route
# is preferred whenever a key is present. SMTP stays available for a host that
# allows it — a self-managed server, or local testing.
BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')

if BREVO_API_KEY:
    EMAIL_BACKEND = 'quotes.email_backends.BrevoAPIBackend'
elif EMAIL_HOST_USER:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Notifications stay silent until one of the two routes is actually configured.
EMAIL_ENABLED = bool(BREVO_API_KEY or EMAIL_HOST_USER)

# Many providers reject a From: that is not the authenticated mailbox.
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL') or EMAIL_HOST_USER or 'noreply@woojoorental.co.kr'

ENQUIRY_NOTIFICATION_EMAILS = [
    addr.strip() for addr in
    os.environ.get('ENQUIRY_NOTIFICATION_EMAILS', 'woojoo66666@daum.net').split(',')
    if addr.strip()
]

# Used to build the "open in admin" link inside notification emails.
SITE_BASE_URL = os.environ.get('SITE_BASE_URL', 'https://woojoorental.co.kr')

# KakaoTalk "나에게 보내기" alerts. Only the app key lives here — the per-account
# authorisation is granted in a browser and stored in quotes.KakaoAccount.
KAKAO_REST_API_KEY = os.environ.get('KAKAO_REST_API_KEY', '')
# Kakao enables 클라이언트 시크릿 by default on new REST API keys; leave blank
# only if it has been switched off on the app.
KAKAO_CLIENT_SECRET = os.environ.get('KAKAO_CLIENT_SECRET', '')

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# ---------------------------------------------------------------------------
# Media & Storage
# Django 4.2+ uses STORAGES dict (DEFAULT_FILE_STORAGE is deprecated)
# Local dev  → filesystem (media/ folder)
# Production → Cloudflare R2 via django-storages S3Boto3Storage
# ---------------------------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

if not DEBUG:
    # --- Cloudflare R2 credentials (read by django-storages via AWS_* names) ---
    AWS_ACCESS_KEY_ID        = os.environ.get('R2_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY    = os.environ.get('R2_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME  = os.environ.get('R2_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL      = os.environ.get('R2_ENDPOINT_URL')
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_FILE_OVERWRITE    = False
    AWS_QUERYSTRING_AUTH     = False
    # R2 does not support S3 ACLs — set bucket public access via R2 dashboard
    AWS_DEFAULT_ACL          = None

    _r2_domain = (
        os.environ.get('R2_CUSTOM_DOMAIN', '')
        .replace('https://', '')
        .replace('http://', '')
        .rstrip('/')
    )
    if _r2_domain:
        AWS_S3_CUSTOM_DOMAIN = _r2_domain
        MEDIA_URL = f"https://{_r2_domain}/"

    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }

# ---------------------------------------------------------------------------
# django-jazzmin
# ---------------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    'site_title': '우주렌탈 관리자',
    'site_header': '우주렌탈 관리자',
    'site_brand': '우주렌탈',
    'welcome_sign': '우주렌탈 관리자 페이지에 오신 것을 환영합니다',
    'copyright': '우주렌탈',
    'show_sidebar': True,
    'navigation_expanded': True,
    'custom_links': {
        'quotes': [{
            'name': '카카오톡 알림 연결',
            'url': 'quotes:kakao_status',
            'icon': 'fas fa-comment-dots',
            'permissions': ['quotes.view_quoterequest'],
        }],
    },
    # Ordered by how often staff use them, not alphabetically: enquiries first
    # (checked daily), equipment next (changed occasionally), accounts last.
    'order_with_respect_to': [
        'quotes',
        'quotes.quoterequest',
        'quotes.callbackrequest',
        'equipment',
        'equipment.equipment',
        'records',
        'records.salesrecord',
        'options',
        'options.optiondevice',
        'auth',
    ],
    'icons': {
        'quotes':                   'fas fa-file-invoice',
        'quotes.quoterequest':      'fas fa-file-alt',
        'quotes.callbackrequest':   'fas fa-phone-volume',
        'equipment':                'fas fa-truck',
        'equipment.equipment':      'fas fa-truck-loading',
        'equipment.equipmentimage': 'fas fa-image',
        'records':                  'fas fa-clipboard-check',
        'records.salesrecord':      'fas fa-clipboard-list',
        'options':                  'fas fa-shield-alt',
        'options.optiondevice':     'fas fa-toolbox',
        'options.optionphoto':      'fas fa-image',
        'auth':                     'fas fa-users-cog',
        'auth.user':                'fas fa-user',
        'auth.group':               'fas fa-users',
    },
    # The tabbed change form hides fieldset descriptions behind clicks, which is
    # where the guidance for non-technical staff lives.
    # 사진은 장비·실적·옵션 안에서만 다룬다. 사진만 따로 모아 놓은 화면은
    # 어느 장비 사진인지 알 수 없어 직원에게 도움이 되지 않는다.
    'hide_models': ['equipment.equipmentimage', 'options.optionphoto',
                    'options.optioncolumn'],
    'default_icon_parents':  'fas fa-chevron-circle-right',
    'default_icon_children': 'fas fa-circle',
    'related_modal_active': True,
    'show_ui_builder': False,
    # 'single' keeps every section — and its guidance text — on one scrollable
    # page. Tabs hid the descriptions behind clicks nobody made.
    'changeform_format': 'single',
    'language_chooser': False,
    # 안내문·사진·삭제 체크만 손본 얇은 CSS. static/css/admin.css 참고.
    'custom_css': 'css/admin.css',
    # 목록의 노출 버튼을 눌렀을 때 그 자리에서 저장되게 한다.
    'custom_js': 'js/admin.js',
}

JAZZMIN_UI_TWEAKS = {
    'navbar_small_text': False,
    'footer_small_text': False,
    'body_small_text': False,
    'brand_small_text': False,
    'brand_colour': 'navbar-primary',
    'accent': 'accent-primary',
    'navbar': 'navbar-dark',
    'no_navbar_border': True,
    'navbar_fixed': False,
    'layout_boxed': False,
    'footer_fixed': False,
    'sidebar_fixed': True,
    'sidebar': 'sidebar-dark-primary',
    'sidebar_nav_small_text': False,
    'sidebar_disable_expand': False,
    'sidebar_nav_child_indent': True,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_flat_style': False,
    'theme': 'default',
    'dark_mode_theme': None,
    'button_classes': {
        'primary':   'btn-primary',
        'secondary': 'btn-secondary',
        'info':      'btn-info',
        'warning':   'btn-warning',
        'danger':    'btn-danger',
        'success':   'btn-success',
    },
}
