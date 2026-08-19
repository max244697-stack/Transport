from .base import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

INSTALLED_APPS += [
    "storages",
]

# WhiteNoise should be inserted right after SecurityMiddleware.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + MIDDLEWARE[1:]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('SECRET_KEY environment variable is not set')

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')
AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN', '').removeprefix(
    'https://'
).removeprefix('http://').rstrip('/')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'auto')
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

if AWS_S3_CUSTOM_DOMAIN:
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'


# CSRF trusted origins for Railway
raw_csrf_trusted_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = []
if raw_csrf_trusted_origins:
    for origin in raw_csrf_trusted_origins.split(','):
        origin = origin.strip()
        if not origin:
            continue
        if origin.startswith(('http://', 'https://')):
            CSRF_TRUSTED_ORIGINS.append(origin)
        else:
            CSRF_TRUSTED_ORIGINS.append(f'https://{origin}')

# Email settings for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


# Security settings for production
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'


# Photos (CompletedOrder) go to Cloudflare R2. CSS/JS stay on the app via WhiteNoise.
_s3_options = {
    "access_key": AWS_ACCESS_KEY_ID,
    "secret_key": AWS_SECRET_ACCESS_KEY,
    "bucket_name": AWS_STORAGE_BUCKET_NAME,
    "endpoint_url": AWS_S3_ENDPOINT_URL,
    "region_name": AWS_S3_REGION_NAME,
    "default_acl": AWS_DEFAULT_ACL,
    "querystring_auth": AWS_QUERYSTRING_AUTH,
    "file_overwrite": AWS_S3_FILE_OVERWRITE,
    "object_parameters": AWS_S3_OBJECT_PARAMETERS,
    "addressing_style": "path",
    "signature_version": "s3v4",
}
if AWS_S3_CUSTOM_DOMAIN:
    _s3_options["custom_domain"] = AWS_S3_CUSTOM_DOMAIN

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": _s3_options,
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        "OPTIONS": {},
    },
}

