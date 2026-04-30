from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "apps"))

# ── Security ────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-k2ur%-)e%vbo71o4ygxb4zxlcp6n6f)+0(%06j3jm8@th*i3qs'
)
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# ── Apps ─────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.accounts',
    'apps.core',
    'apps.media',
    'apps.database',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eventnest.urls'

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
                'apps.core.context_processors.global_context',   # ← global nav categories
            ],
        },
    },
]

WSGI_APPLICATION = 'eventnest.wsgi.application'

# ── Database ─────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
    # PostgreSQL (prod):
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME':     os.environ.get('DB_NAME', 'eventnest'),
    #     'USER':     os.environ.get('DB_USER', 'postgres'),
    #     'PASSWORD': os.environ.get('DB_PASSWORD', ''),
    #     'HOST':     os.environ.get('DB_HOST', 'localhost'),
    #     'PORT':     os.environ.get('DB_PORT', '5432'),
    # }
}

# ── Auth ──────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.CustomUser'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL            = '/accounts/login/'
LOGIN_REDIRECT_URL   = '/dashboard/'
LOGOUT_REDIRECT_URL  = '/accounts/login/'

# ── i18n ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Asia/Kolkata'
USE_I18N      = True
USE_TZ        = True

# ── Static & Media ────────────────────────────────────────────
STATIC_URL      = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT     = BASE_DIR / 'staticfiles'

MEDIA_URL  = '/media-files/'
MEDIA_ROOT = BASE_DIR / 'media_uploads'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Email (configure for prod) ────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# For prod:
# EMAIL_BACKEND   = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST      = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_PORT      = int(os.environ.get('EMAIL_PORT', 587))
# EMAIL_USE_TLS   = True
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
# DEFAULT_FROM_EMAIL = 'EventNest <noreply@eventnest.com>'
