import json

from .base import *  # noqa


with open(Path(BASE_DIR) / '.django_env', 'r') as file:  # noqa
    data = json.load(file)


DEBUG = False

ALLOWED_HOSTS = ['*']

SECRET_KEY = data['SECRET_KEY']

KAKAO_API_KEY = data['KAKAO_API_KEY']
KAKAO_SECRET_KEY = data['KAKAO_SECRET_KEY']
KAKAO_REDIRECT_URL = data['KAKAO_REDIRECT_URL']
KAKAO_PAY_CID = data['KAKAO_PAY_CID']
KAKAO_PAY_SECRET_KEY = data['KAKAO_PAY_SECRET_KEY']

NAVER_API_KEY = data['NAVER_API_KEY']
NAVER_SECRET_KEY = data['NAVER_SECRET_KEY']
NAVER_REDIRECT_URL = data['NAVER_REDIRECT_URL']

GOOGLE_CLIENT_ID = data['GOOGLE_CLIENT_ID']
GOOGLE_SECRET_KEY = data['GOOGLE_SECRET_KEY']
GOOGLE_REDIRECT_URL = data['GOOGLE_REDIRECT_URL']

AWS_IAM_ACCESS_KEY = data['AWS_IAM_ACCESS_KEY']
AWS_IAM_SECRET_ACCESS_KEY = data['AWS_IAM_SECRET_ACCESS_KEY']
AWS_S3_BUCKET_NAME = data['AWS_S3_BUCKET_NAME']

AWS_SQS_URL = data['AWS_SQS_URL']

EMAIL_HOST_USER = data['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = data['EMAIL_HOST_PASSWORD']
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

DATABASES = {
    'default': data['DATABASE']
}

# CacheOps
CACHEOPS_REDIS = data['CACHEOPS_REDIS']
CACHEOPS_DEFAULTS = {
    'timeout': 60 * 15
}
CACHEOPS = data['CACHEOPS']

# CELERY SETTINGS
timezone = 'Asia/Seoul'
CELERY_BROKER_URL = data['CELERY_BROKER_URL']
result_backend = data['result_backend']
accept_content = ["json"]
task_serializer = "json"
result_serializer = "json"

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': data['CACHES_LOCATION'],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

KAKAO_PAY_BASE_DOMAIN = 'http://127.0.0.1:8000'

CSRF_TRUSTED_ORIGINS = [data.get('CSRF_TRUSTED_ORIGIN', 'http://127.0.0.1')]

OPENAI_API_KEY = data['OPENAI_API_KEY']

if data['SENTRY_DSN']:
    import sentry_sdk
    sentry_sdk.init(
        dsn=data['SENTRY_DSN'],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
        environment=data['SENTRY_ENV'],
    )
