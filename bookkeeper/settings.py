"""
Django settings for bookkeeper project.

Generated by 'django-admin startproject' using Django 4.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from pathlib import Path

import django_stubs_ext
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

django_stubs_ext.monkeypatch()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = bool(os.environ.get("DEBUG", False))
if DEBUG:
    load_dotenv(BASE_DIR / ".env-dev", override=True)
else:
    load_dotenv(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

if not "SECRET_KEY" in os.environ:
    raise ImproperlyConfigured("You need to set the 'SECRET_KEY' environment variable")
SECRET_KEY = os.environ["SECRET_KEY"]


ALLOWED_HOSTS = [".localhost", "127.0.0.1", "[::1]"]
if "UPSTREAM_HOST" in os.environ:
    HOSTNAME = os.environ["UPSTREAM_HOST"]
    ALLOWED_HOSTS.append(HOSTNAME)
    CSRF_TRUSTED_ORIGINS = [f"https://{HOSTNAME}"]

INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "widget_tweaks",
    "bookkeeping",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "bookkeeper.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["bookkeeper/templates/"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "bookkeeping.context_processors.years_processor",
            ],
        },
    },
]

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar", "django_browser_reload"]
    MIDDLEWARE += [
        "django_browser_reload.middleware.BrowserReloadMiddleware",
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

WSGI_APPLICATION = "bookkeeper.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
if not "APP_DATA_LOCATION" in os.environ:
    raise ImproperlyConfigured("You need to set the 'APP_DATA_LOCATION' environment variable")

APP_DATA_LOCATION = Path(os.environ["APP_DATA_LOCATION"])
DB_PATH = APP_DATA_LOCATION / "db/db.sqlite3"
DB_PATH.parent.mkdir(exist_ok=True)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_PATH,
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
AUTH_USER_MODEL = "bookkeeping.User"

import locale

LANGUAGE_CODE = "de-DE"
locale.setlocale(locale.LC_ALL, LANGUAGE_CODE.replace("-", "_"))
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS: list[str | tuple[str, str]] = ["bookkeeper/static"]
STATIC_ROOT = "/var/www/bookkeeper/static/"

if DEBUG:
    MEDIA_URL = "./static/media/"
    MEDIA_ROOT = APP_DATA_LOCATION / "media"
    STATICFILES_DIRS += [("media", str(APP_DATA_LOCATION / "media"))]
else:
    MEDIA_URL = "media/"
    MEDIA_ROOT = APP_DATA_LOCATION / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "/"
