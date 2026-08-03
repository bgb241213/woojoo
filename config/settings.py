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
    # Ordered by how often staff use them, not alphabetically: enquiries first
    # (checked daily), equipment next (changed occasionally), accounts last.
    'order_with_respect_to': [
        'quotes',
        'quotes.quoterequest',
        'quotes.callbackrequest',
        'equipment',
        'equipment.equipment',
        'records',
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
        'auth':                     'fas fa-users-cog',
        'auth.user':                'fas fa-user',
        'auth.group':               'fas fa-users',
    },
    # The tabbed change form hides fieldset descriptions behind clicks, which is
    # where the guidance for non-technical staff lives.
    'hide_models': ['equipment.equipmentimage'],
    'default_icon_parents':  'fas fa-chevron-circle-right',
    'default_icon_children': 'fas fa-circle',
    'related_modal_active': True,
    'show_ui_builder': False,
    # 'single' keeps every section — and its guidance text — on one scrollable
    # page. Tabs hid the descriptions behind clicks nobody made.
    'changeform_format': 'single',
    'language_chooser': False,
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
