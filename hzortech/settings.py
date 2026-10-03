import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    "hzortech.com",
    "www.hzortech.com",
    "0.0.0.0",
    "127.0.0.1",
    "localhost",
]

CSRF_TRUSTED_ORIGINS = [
    "https://hzortech.com",
    "https://www.hzortech.com",
]

SITE_URL = os.environ.get('SITE_URL', 'https://hzortech.com')

INSTALLED_APPS = [
    'business_page',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'business_page.middleware.SecurityHeadersMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Cloudflare Turnstile (get keys at dash.cloudflare.com → Turnstile)
TURNSTILE_SITE_KEY   = os.environ.get('TURNSTILE_SITE_KEY', '')
TURNSTILE_SECRET_KEY = os.environ.get('TURNSTILE_SECRET_KEY', '')

# Meta Pixel — only ever loaded after the visitor accepts analytics cookies.
META_PIXEL_ID = os.environ.get('META_PIXEL_ID', '1301979234631773')

# Higgsfield — server-side only. HF_KEY is read from the environment by
# business_page.higgsfield; it is never exposed to templates.
HIGGSFIELD_WEBHOOK_TOKEN = os.environ.get('HIGGSFIELD_WEBHOOK_TOKEN', '')
HIGGSFIELD_OUTPUT_DIR = BASE_DIR / 'assets' / 'generated'

ROOT_URLCONF = 'hzortech.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'business_page.context_processors.site',
                'business_page.context_processors.seo',
            ],
        },
    },
]

WSGI_APPLICATION = 'hzortech.wsgi.application'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Database — PostgreSQL in production, SQLite for local dev fallback
if os.environ.get('POSTGRES_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'hzortech'),
            'USER': os.environ.get('POSTGRES_USER', 'hzortech'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
            'HOST': os.environ.get('POSTGRES_HOST', 'postgres'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
            'CONN_MAX_AGE': 60,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

CACHES = {
    'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'hzortech'},
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Yerevan'
USE_I18N = True
USE_TZ = True


# ── Static files ──────────────────────────────────────────────────────────────
# `frontend/dist` is the Vite build output (hashed filenames + manifest). It is
# served under /static/dist/. Built in the Docker image's node stage; locally
# via `npm run build` (or proxied from the Vite dev server when
# VITE_DEV_SERVER is set).
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
VITE_DIST_DIR = BASE_DIR / 'frontend' / 'dist'
VITE_DEV_SERVER = os.environ.get('VITE_DEV_SERVER', '') if DEBUG else ''
STATICFILES_DIRS = [('dist', VITE_DIST_DIR)] if VITE_DIST_DIR.exists() else []

# Django ≥5.1 ignores the old STATICFILES_STORAGE setting — STORAGES is the
# only way to enable hashed + compressed static files.
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}
if os.environ.get('DJANGO_TEST_STATIC') == 'simple':
    STORAGES['staticfiles'] = {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}

WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = [
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'avif', 'zip', 'gz', 'tgz', 'bz2', 'tbz',
    'xz', 'br', 'swf', 'flv', 'woff', 'woff2',
    'mp4', 'webm', 'mov',
]
_VITE_HASHED = re.compile(r'/dist/assets/.+-[A-Za-z0-9_-]{8}\.\w+$')


def WHITENOISE_IMMUTABLE_FILE_TEST(path, url):
    # Django-manifest hashed names (name.0123456789ab.ext) and Vite-hashed
    # names (name-AbCd1234.ext) never change content → cache forever.
    # Scroll sequences live in directories versioned by their source request
    # id (seq/forge-<id>/…), so they are immutable by path.
    return bool(re.match(r'^.+\.[0-9a-f]{12}\..+$', url) or _VITE_HASHED.search(url) or '/seq/' in url)


# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_TIMEOUT = 15
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'contact@hzortech.com')
CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'contact@hzortech.com')


# ── Security ──────────────────────────────────────────────────────────────────
# Cloudflare (Flexible SSL) → nginx sets X-Forwarded-Proto: https on every
# proxied request, so Django can trust it for request.is_secure().
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'
# SECURE_SSL_REDIRECT was briefly enabled on the (incorrect) assumption that
# nginx's hardcoded `X-Forwarded-Proto: https` guarantees request.is_secure()
# is always true in production. In the real Cloudflare → nginx → Django
# chain it was not — the live site 301-redirected to itself in a loop
# (caught and reverted within minutes; see git history). Root cause wasn't
# chased under live-incident pressure — it needs reproducing against the
# real proxy chain (not a local simulation) before re-enabling. Cloudflare's
# own edge TLS/"Always Use HTTPS" is what actually protects visitors here;
# this was defense-in-depth, not load-bearing, so leaving it off is safe.
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0

SITEMAP_PROTOCOL = 'https'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {
        'business_page': {'handlers': ['console'], 'level': 'INFO'},
        'django.request': {'handlers': ['console'], 'level': 'WARNING'},
    },
}
