import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------
# Environment
# ---------------------------------------------------------------
PROD = os.environ.get("DJANGO_PRODUCTION") == "1"  # set DJANGO_PRODUCTION=1 on the live server
DEBUG = not PROD
if not PROD and os.environ.get("DJANGO_HOSTS"):
    # DJANGO_HOSTS is only set on a real server. If it is set but DJANGO_PRODUCTION is not 1,
    # refuse to start instead of running the live site with DEBUG=True.
    raise RuntimeError("DJANGO_HOSTS is set but DJANGO_PRODUCTION != 1 - refusing to run with DEBUG on a server")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or ("dev-only-insecure-key-" + "x" * 40)
if PROD and not os.environ.get("DJANGO_SECRET_KEY"):
    raise RuntimeError("Set DJANGO_SECRET_KEY on the server")

ALLOWED_HOSTS = ['*']


# ---------------------------------------------------------------
# Admin / login URLs
# ---------------------------------------------------------------
ADMIN_URL = "admin-chyakan/"  # not the default /admin/ (harder to guess)
LOGIN_URL = "/" + ADMIN_URL + "login/"
LOGIN_REDIRECT_URL = "/" + ADMIN_URL
LOGOUT_REDIRECT_URL = "/"

# ---------------------------------------------------------------
# Apps & middleware
# ---------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.SecurityHeaders",
    "core.middleware.AdminLoginThrottle",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------
# Templates
# ---------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context.stats",
            ],
        },
    }
]

# ---------------------------------------------------------------
# Database
# ---------------------------------------------------------------
DB_PASSWORD = os.environ.get("DB_PASSWORD")
if DB_PASSWORD:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "chyakan"),
            "USER": os.environ.get("DB_USER", "chyakan_user"),
            "PASSWORD": DB_PASSWORD,
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }
elif PROD:
    raise RuntimeError("Set DB_PASSWORD (and DB_HOST / DB_NAME / DB_USER if needed) on the server")
else:
    # local development without DB_PASSWORD: a throw-away SQLite file.
    # To use your local PostgreSQL instead, set DB_PASSWORD in your terminal before runserver.
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# ---------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation." + name}
    for name in (
        "UserAttributeSimilarityValidator",
        "MinimumLengthValidator",
        "CommonPasswordValidator",
        "NumericPasswordValidator",
    )
]

# ---------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------
LANGUAGE_CODE = "ckb"
TIME_ZONE = "Asia/Baghdad"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG

TRUSTED_PROXY_COUNT = int(os.environ.get("TRUSTED_PROXY_COUNT", "1"))  # proxies between the visitor and Django (Render/nginx = 1)

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedStaticFilesStorage"
            if PROD
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        )
    },
}

# ---------------------------------------------------------------
# Security
# ---------------------------------------------------------------
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
DATA_UPLOAD_MAX_MEMORY_SIZE = 12 * 1024 * 1024

if PROD:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    CSRF_TRUSTED_ORIGINS = [
        o.strip() for o in os.environ.get("DJANGO_ORIGINS", "").split(",") if o.strip()
    ]

# ---------------------------------------------------------------
# Private CV files (NOT public) + optional e-mail notifications
# ---------------------------------------------------------------
PRIVATE_ROOT = BASE_DIR / "private_files"   # never served directly; only staff can download via the admin
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "")   # your e-mail: gets a short notice for each new message / CV
if os.environ.get("EMAIL_HOST"):
    EMAIL_HOST = os.environ["EMAIL_HOST"]; EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", ""); EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = True; DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
