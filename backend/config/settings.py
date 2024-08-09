import logging
from datetime import timedelta

from dotenv import load_dotenv

from .side_settings import *

# Environment
BASE_DIR = Path(__file__).resolve().parent.parent
env = os.environ.get
dotenv_path = os.path.join(BASE_DIR, './.env')
load_dotenv(dotenv_path=dotenv_path)

# Project
SECRET_KEY = env('SECRET_KEY')
DEBUG = bool(int(env('DEBUG')))
DEV = bool(int(env('DEV')))
DOCKER = bool(int(env('DOCKER')))

HTTPS = bool(int(env('HTTPS')))
SITE_ID = int(env('SITE_ID'))
MAIN_DOMAIN = env('MAIN_DOMAIN', '127.0.0.1')
DOMAIN_URL = f'http{"s" if HTTPS else ""}://{MAIN_DOMAIN}{":8000" if DEV else ""}'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'web', MAIN_DOMAIN] + env('ALLOWED_HOSTS', '').split(',')

ROOT_URLCONF = 'apps.core.routes.root'
AUTH_USER_MODEL = 'core.User'

LANGUAGE_CODE = 'ru-ru'
LOCALE_PATHS = (BASE_DIR / 'locale',)
TIME_ZONE = env('TZ', 'Europe/Moscow')
USE_I18N = True
USE_L10N = True
USE_TZ = True
WSGI_APPLICATION = None
ASGI_APPLICATION = 'config.asgi.application'

MINIO_USE = bool(int(env('MINIO_USE')))
POSTGRES_USE = bool(int(env('POSTGRES_USE')))

REDIS_HOST = env('REDIS_HOST') if not DOCKER else 'redis'
REDIS_PORT = int(env('REDIS_PORT'))
REDIS_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
REDIS_CACHE_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'

LOGIN_URL = 'signin'
LOGIN_REDIRECT_URL = 'signin'

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [f'http{"s" if not DEV else ""}://{MAIN_DOMAIN}']
CORS_ORIGIN_ALLOW_ALL = True

INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'corsheaders',

    'django_redis',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'polymorphic',
    'django_celery_beat',
    'django_extensions',

    'apps.core',
    'apps.endpoints',
]
if DOCKER: INSTALLED_APPS.append('django_minio_backend')

# Database
if POSTGRES_USE:
    DATABASES = {
        'default': {
            'ENGINE': env('DB_ENGINE'),
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST'),
            'PORT': env('DB_PORT'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [(REDIS_HOST, REDIS_PORT)], },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        # 'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',
        'user': '120/minute'
    }
}
REST_USE_JWT = True
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=40 if DEV else 60 * 24 * 2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_CACHE_URL,
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient', }
    }
}
USER_AGENTS_CACHE = 'default'

CORS_ALLOWED_ORIGINS = (
    'http://127.0.0.1:8000',
    'http://127.0.0.1:3000',
    'http://localhost:8000',
    'http://localhost:3000',
)

# Static | Media
STATICFILES_DIRS = (
    BASE_DIR.parent / 'frontend' / 'build' / 'static',
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
MINIO_EXTERNAL_ENDPOINT_USE_HTTPS = True
MINIO_USE_HTTPS = False
if DEV and not MINIO_USE:
    STATIC_ROOT = BASE_DIR.parent / 'static'
    MEDIA_ROOT = BASE_DIR.parent / 'media'
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
else:
    STATIC_ROOT = None
    MEDIA_ROOT = None
    STATIC_URL = f'{DOMAIN_URL}/static/'
    MEDIA_URL = f'{DOMAIN_URL}/media/'

    MINIO_ENDPOINT = 'minio:9000'
    MINIO_EXTERNAL_ENDPOINT = f'{MAIN_DOMAIN}'  # For external access use Docker hostname and MinIO port
    MINIO_ACCESS_KEY = env('MINIO_ROOT_USER')
    MINIO_SECRET_KEY = env('MINIO_ROOT_PASSWORD')
    MINIO_EXTERNAL_ENDPOINT_USE_HTTPS = bool(int(env('MINIO_EXTERNAL_ENDPOINT_USE_HTTPS') or 0))
    MINIO_USE_HTTPS = bool(int(env('MINIO_USE_HTTPS') or 0))
    MINIO_URL_EXPIRY_HOURS = timedelta(days=1)
    MINIO_CONSISTENCY_CHECK_ON_START = True
    MINIO_PRIVATE_BUCKETS = [
        'django-backend-dev-private',
    ]
    MINIO_PUBLIC_BUCKETS = [
        'static',
        'media',
    ]
    MINIO_POLICY_HOOKS: list[tuple[str, dict]] = []
    MINIO_STATIC_FILES_BUCKET = 'static'  # Just bucket name may be 'my-static-files'?
    MINIO_MEDIA_FILES_BUCKET = 'media'  # Just bucket name may be 'media-files'?
    MINIO_BUCKET_CHECK_ON_SAVE = True  # Default: True // Creates a cart if it doesn't exist, then saves it
    MINIO_PUBLIC_BUCKETS.append(MINIO_STATIC_FILES_BUCKET)
    MINIO_PUBLIC_BUCKETS.append(MINIO_MEDIA_FILES_BUCKET)
    MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
    MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True
    DEFAULT_FILE_STORAGE = 'django_minio_backend.models.MinioBackend'
    STATICFILES_STORAGE = 'django_minio_backend.models.MinioBackendStatic'
    FILE_UPLOAD_MAX_MEMORY_SIZE = 65536


# GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID')
# GOOGLE_CLIENT_SECRET = env('GOOGLE_CLIENT_SECRET')
# GOOGLE_REDIRECT_URI = f'{DOMAIN_URL}/google-callback/'
#
# DISCORD_CLIENT_ID = env('DISCORD_CLIENT_ID')
# DISCORD_CLIENT_SECRET = env('DISCORD_CLIENT_SECRET')
# DISCORD_REDIRECT_URI = f'{DOMAIN_URL}/discord-callback/'
#
# YANDEX_RECAPTCHA_SECRET_KEY = env('YANDEX_RECAPTCHA_SECRET_KEY')


# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django_sendmail_backend.backends.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = int(env('EMAIL_PORT'))
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_SSL = True
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Celery
timezone = TIME_ZONE
broker_url = REDIS_BROKER_URL
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 86400 * 30}
result_backend = REDIS_BROKER_URL
accept_content = ['application/json']
task_serializer = 'json'
result_serializer = 'json'
task_default_queue = 'default'
broker_connection_retry_on_startup = True
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = True

# Logging configuration
logs_base_dir = os.path.join(BASE_DIR.parent, 'logs')
log_dirs = {
    'base': os.path.join(logs_base_dir, 'base'),
    'payment': os.path.join(logs_base_dir, 'payment'),
    'order': os.path.join(logs_base_dir, 'order'),
}
for path in log_dirs.values():
    os.makedirs(path, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'base_formatter': {
            'format': '{levelname} {asctime}: {message}',
            'style': '{',
            'datefmt': '%m-%d %H:%M:%S',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'base_formatter',
        },
    },
    'loggers': {
        'base': {
            'handlers': ['console', 'base_file'],
            'level': 'DEBUG' if DEBUG else 'DEBUG',
            'propagate': True,
        },
        'payment': {
            'handlers': ['console', 'payment_file'],
            'level': 'DEBUG' if DEBUG else 'DEBUG',
            'propagate': True,
        },
        'order': {
            'handlers': ['console', 'order_file'],
            'level': 'DEBUG' if DEBUG else 'DEBUG',
            'propagate': True,
        },
        'console': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'DEBUG',
            'propagate': True,
        },
    }
}

for logger_name, log_dir in log_dirs.items():
    log_file_handler = {
        'level': 'DEBUG' if DEBUG else 'WARNING',
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'filename': os.path.join(log_dir, f'{logger_name}.log'),
        'when': 'midnight',
        'backupCount': 30,  # How many days to keep logs
        'formatter': 'base_formatter',
        'encoding': 'utf-8',
    }
    LOGGING['handlers'][f'{logger_name}_file'] = log_file_handler
    LOGGING['loggers'][logger_name]['handlers'].append(f'{logger_name}_file')


log = logging.getLogger('base')
log.info('#####################################')
log.info('########## Server Settings ##########')
log.info('#####################################')
log.info(f'{BASE_DIR=}')
log.info(f'{MAIN_DOMAIN=}')
log.info(f'{DOMAIN_URL=}')
log.info(f'{HTTPS=}')
log.info(f'{POSTGRES_USE=}')
log.info(f'{MINIO_USE=}')
log.info(f'{MINIO_EXTERNAL_ENDPOINT_USE_HTTPS=}')
log.info(f'{MINIO_USE_HTTPS=}')
log.info(f'{ALLOWED_HOSTS=}')
log.info(f'{DEBUG=}')
log.info(f'{DEV=}')
log.info(f'{ASGI_APPLICATION=}')
log.info(f'{WSGI_APPLICATION=}')
log.info(f'{STATIC_URL=}')
log.info(f'{MEDIA_URL=}')
log.info(f'{STATIC_ROOT=}')
log.info(f'{MEDIA_ROOT=}')
log.info('#####################################')
log.info('#####################################')
log.info('#####################################')
