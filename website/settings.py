"""Django settings for the Altay Engineering catalog."""

from pathlib import Path

import pymysql
from decouple import AutoConfig
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
# Только .env рядом с manage.py — не подхватываем секреты из родительских папок.
config = AutoConfig(search_path=BASE_DIR)

DEV_SECRET_KEY = "django-insecure-dev-only-change-me"
SECRET_KEY = config("SECRET_KEY", default=DEV_SECRET_KEY)
DEBUG = config("DEBUG", default=True, cast=bool)

if not DEBUG and SECRET_KEY == DEV_SECRET_KEY:
    raise ImproperlyConfigured(
        "Для запуска с DEBUG=False задайте уникальный SECRET_KEY в переменных окружения."
    )


def _csv(name: str, default: str) -> list[str]:
    return [item.strip() for item in config(name, default=default).split(",") if item.strip()]


ALLOWED_HOSTS = _csv("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = _csv("CSRF_TRUSTED_ORIGINS", "")

# Layero: production + preview-хосты (*.layero.app / *-main.layero.app).
# Префикс «.» — subdomain-wildcard Django (см. ALLOWED_HOSTS).
if not DEBUG and "*" not in ALLOWED_HOSTS and ".layero.app" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, ".layero.app"]
for _host in ALLOWED_HOSTS:
    if _host in {"*", "localhost", "127.0.0.1"} or _host.startswith("."):
        continue
    _origin = f"https://{_host}"
    if _origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS = [*CSRF_TRUSTED_ORIGINS, _origin]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "app.apps.CatalogConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "app.middleware.SecurityHeadersMiddleware",
    "app.middleware.RateLimitMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "website.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "app.context_processors.cart_count",
                "app.context_processors.public_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "website.wsgi.application"

DB_ENGINE = config("DB_ENGINE", default="sqlite").strip().lower()
if DB_ENGINE == "mysql":
    pymysql.install_as_MySQLdb()
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD", default=""),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="3306"),
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": config("SQLITE_PATH", default=str(BASE_DIR / "db.sqlite3")),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Novosibirsk"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_ROOT.mkdir(parents=True, exist_ok=True)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = config("EMAIL_HOST", default="smtp.mail.ru")
    EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
    EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or "webmaster@localhost"
SERVER_EMAIL = DEFAULT_FROM_EMAIL
# Куда слать PDF заявки. Пусто = письмо НЕ отправляется (заявка всё равно в БД).
# Не подставляем EMAIL_HOST_USER автоматически, чтобы случайно не слать на старый ящик.
ORDER_NOTIFICATION_EMAIL = config("ORDER_NOTIFICATION_EMAIL", default="").strip()
EMAIL_TIMEOUT = 10

# Ключ Яндекс.Карт виден в браузере, но не хранится в репозитории.
YANDEX_MAPS_API_KEY = config("YANDEX_MAPS_API_KEY", default="")

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "app": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
