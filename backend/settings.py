"""
Django settings for backend project.
"""

from dateutil import tz
import os

import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATICFILES_FINDERS = \
    ('django.contrib.staticfiles.finders.FileSystemFinder',
     'django.contrib.staticfiles.finders.AppDirectoriesFinder')

# Disable debugging in production.
DEBUG = bool(int(os.environ.get('VOTER_VALIDATION_DEBUG', '0')))

SECRET_KEY = os.environ['VOTER_VALIDATION_DJANGO_SECRET_KEY']  # required

# For HTTPS deployment
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31556926  # one year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    CSRF_COOKIE_HTTPONLY = True
    X_FRAME_OPTIONS = "DENY"

# Site-related settings

# Allowed hosts (Heroku recommendation).
ALLOWED_HOSTS = ["*"]

# S3/Cloudfront settings for serving static files (production only). See
# http://condopilot.com/blog/web/how-setup-gzip-compressor-and-aws-s3-django/
if not DEBUG:
    CLOUDFRONT_DOMAIN = os.environ['CLOUDFRONT_DOMAIN']
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    AWS_S3_SECURE_URLS = True
    AWS_S3_URL_PROTOCOL = 'https:'
    AWS_S3_CUSTOM_DOMAIN = CLOUDFRONT_DOMAIN
    STATICFILES_LOCATION = "static"  # Where static files are stored in bucket
    STATIC_URL = "https://%s/%s/" % (CLOUDFRONT_DOMAIN, STATICFILES_LOCATION)
    ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"
    AWS_PRELOAD_METADATA = True  # for Collectfast
    COLLECTFAST_ENABLED = True

    # Compression of S3 files
    STATICFILES_FINDERS += (
        'compressor.finders.CompressorFinder',  # look for compressed versions
    )
    AWS_IS_GZIPPED = True
    GZIP_CONTENT_TYPES = (
        'text/css',
        'application/javascript',
        'application/x-javascript',
        'text/javascript'
    )
    COMPRESS_ENABLED = True
    COMPRESS_URL = STATIC_URL
    COMPRESS_ROOT = STATIC_ROOT
    COMPRESS_CSS_FILTERS = ["compressor.filters.css_default.CssAbsoluteFilter",
                            "compressor.filters.cssmin.CSSMinFilter"]
    COMPRESS_JS_FILTERS = ["compressor.filters.jsmin.JSMinFilter"]
    COMPRESS_STORAGE = 'backend.storage.CachedS3BotoStorage'
    STATICFILES_STORAGE = COMPRESS_STORAGE
else:
    STATIC_URL = '/static/'
    COLLECTFAST_ENABLED = False
    COMPRESS_ENABLED = False

# Application definition

INSTALLED_APPS = [
    'collectfast',  # for a faster collectstatic (when deploying to S3)
    'voter_validation.apps.VoterValidationConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.redirects',  # for redirecting herokuapp to custom domain
    'compressor',
    'hide_herokuapp',
    'storages',  # for S3 storage of static files with django-storages and boto
]

MIDDLEWARE_CLASSES = [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'voter_validation.middleware.ActiveUserMiddleware',
    'hide_herokuapp.middleware.HideHerokuappFromRobotsMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': (
                ('django.template.loaders.cached.Loader', (
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                )),
            )
        },
    },
]

# For redirecting herokuapp to custom domain.
if not DEBUG:
    SITE_ID = os.environ['SITE_ID']
else:
    SITE_ID = 1

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'voter_validation_test_db',
            'USER': 'voter_validation_test',
            'PASSWORD': 'voter_validation_test_pass',
            'HOST': 'localhost',
            'PORT': '',
        }
    }
else:
    # Heroku
    DATABASES = {'default': dj_database_url.config()}

    # Max connection age in seconds. Used to avoid reopening new
    # connections. Note that we can only have up to 20  connections to the
    # DB, and some may end up in a bad state, so this limits the number of
    # dynos we can spin up.
    DATABASES['default']['CONN_MAX_AGE'] = 500

# Logging support
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(process)d] [%(levelname)s] '
                      ' %(module)s: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'voter_validation': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'
SERVER_TIME_ZONE = tz.gettz(TIME_ZONE)

USE_I18N = True

USE_L10N = True

USE_TZ = True
