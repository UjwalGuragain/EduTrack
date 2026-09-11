"""
Django production settings for the student_management_system project.

Selected in production by setting:

    DJANGO_SETTINGS_MODULE=student_management_system.settings_production

This module inherits the base project settings and overrides only the
values that must be hardened in production. All sensitive values are read
from the environment and the application fails fast if a critical
security setting is missing or unsafe.
"""
import os

from .settings import *  # noqa: F401,F403

# --- Core security ---

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError(
        "DJANGO_SECRET_KEY must be set in the environment when running "
        "with settings_production."
    )

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'false').lower() in ('true', '1', 'yes')
if DEBUG:
    raise RuntimeError(
        "DJANGO_DEBUG must not be enabled with settings_production."
    )

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')
    if host.strip()
]
if not ALLOWED_HOSTS:
    raise RuntimeError(
        "DJANGO_ALLOWED_HOSTS must be set (comma-separated) when running "
        "with settings_production."
    )


# --- HTTPS / secure cookies ---

# Redirect all non-HTTPS requests to HTTPS.
SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', 'true').lower() in ('true', '1', 'yes')

# HTTP Strict Transport Security: tell browsers to only use HTTPS for a year.
SECURE_HSTS_SECONDS = int(os.getenv('DJANGO_SECURE_HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Only send session and CSRF cookies over HTTPS.
SESSION_COOKIE_SECURE = os.getenv('DJANGO_SESSION_COOKIE_SECURE', 'true').lower() in ('true', '1', 'yes')
CSRF_COOKIE_SECURE = os.getenv('DJANGO_CSRF_COOKIE_SECURE', 'true').lower() in ('true', '1', 'yes')

# Prevent browsers from MIME-sniffing responses.
SECURE_CONTENT_TYPE_NOSNIFF = True

# Protect against clickjacking.
X_FRAME_OPTIONS = 'DENY'

# Site privacy: only send the origin as a referrer when leaving the site.
SECURE_REFERRER_POLICY = 'same-origin'

# WhiteNoise: serve compressed, far-future-cached static files.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}