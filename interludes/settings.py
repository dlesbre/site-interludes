"""
Django settings for interludes project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from typing import Any, List

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

try:
    from . import secret
except ImportError:
    raise ImportError("The interludes/secret.py file is missing.\nRun 'make secret' to generate a secret.") from None


def import_secret(name: str) -> Any:
    """
    Shorthand for importing a value from the secret module and raising an
    informative exception if a secret is missing.
    """
    try:
        return getattr(secret, name)
    except AttributeError:
        raise RuntimeError("Secret missing: {}".format(name)) from None


SECRET_KEY = import_secret("SECRET_KEY")

DB_NAME = import_secret("DB_NAME")

ADMINS = import_secret("ADMINS")

SERVER_EMAIL = import_secret("SERVER_EMAIL")
DEFAULT_FROM_EMAIL = import_secret("DEFAULT_FROM_EMAIL")
EMAIL_HOST = import_secret("EMAIL_HOST")
EMAIL_PORT = import_secret("EMAIL_PORT")
EMAIL_HOST_USER = import_secret("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = import_secret("EMAIL_HOST_PASSWORD")

EMAIL_USE_SSL = True

# FIXME - set to False in production
DEBUG = True

# FIXME - set hosts in production
ALLOWED_HOSTS: List[str] = []

if DEBUG:
    # This will display emails in Console.
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_PRELOAD = True

    SECURE_REFERRER_POLICY = "same-origin"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "home.apps.HomeConfig",
    "admin_pages.apps.AdminPagesConfig",
    "accounts.apps.AccountsConfig",
    "site_settings.apps.SiteSettingsConfig",
    "pages.apps.PagesConfig",
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

ROOT_URLCONF = "interludes.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "interludes", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "site_settings.context_processors.settings",
            ],
        },
    },
]

WSGI_APPLICATION = "interludes.wsgi.application"

# Auto primary key type
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, DB_NAME),
    }
}

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_USER_MODEL = "accounts.EmailUser"
AUTH_PROFILE_MODULE = "home.ParticipantModel"

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

# Session time in seconds
SESSION_COOKIE_AGE = 3600

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "CET"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "profile"

# Prefix to mails to admins
EMAIL_SUBJECT_PREFIX = "[DJANGO WEBLUDES] "

# Signature to mails to admins
EMAIL_SIGNATURE = "-- Site Interludes (mail généré automatiquement)"

# Prefix to mails to users
USER_EMAIL_SUBJECT_PREFIX = "[interludes] "
