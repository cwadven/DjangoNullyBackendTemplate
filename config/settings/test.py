from .base import * # noqa


SECRET_KEY = 'development_secret_key'

KAKAO_API_KEY = 'development_KAKAO_API_KEY'
KAKAO_SECRET_KEY = 'development_KAKAO_SECRET_KEY'
KAKAO_REDIRECT_URL = 'development_KAKAO_REDIRECT_URL'
KAKAO_PAY_CID = 'TC0ONETIME'
KAKAO_PAY_SECRET_KEY = 'development_KAKAO_PAY_SECRET_KEY'

NAVER_API_KEY = 'development_NAVER_API_KEY'
NAVER_SECRET_KEY = 'development_NAVER_SECRET_KEY'
NAVER_REDIRECT_URL = 'development_NAVER_REDIRECT_URL'

GOOGLE_CLIENT_ID = 'development_GOOGLE_CLIENT_ID'
GOOGLE_SECRET_KEY = 'development_GOOGLE_SECRET_KEY'
GOOGLE_REDIRECT_URL = 'development_GOOGLE_REDIRECT_URL'

AWS_IAM_ACCESS_KEY = 'development_AWS_IAM_ACCESS_KEY'
AWS_IAM_SECRET_ACCESS_KEY = 'development_AWS_IAM_SECRET_ACCESS_KEY'
AWS_S3_BUCKET_NAME = 'bucket_name'

AWS_SQS_URL = 'development_AWS_SQS_URL'

EMAIL_HOST_USER = 'TESTTESTTEST'
EMAIL_HOST_PASSWORD = 'TESTTESTTEST'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "nully",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
        "TEST": {
            "NAME": "nully_test"
        }
    },
}

# CELERY SETTINGS
timezone = 'Asia/Seoul'
CELERY_BROKER_URL = 'redis://localhost:6379/2'
result_backend = 'redis://localhost:6379/2'
accept_content = ["json"]
task_serializer = "json"
result_serializer = "json"

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

KAKAO_PAY_BASE_DOMAIN = 'http://127.0.0.1:8000'
OPENAI_API_KEY = 'development_OPENAI_API_KEY'
