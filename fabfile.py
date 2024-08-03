import json
import os

from fabric2 import task


@task
def generate_env(c):
    """
    Generate local env file
    """
    from config.settings.base import BASE_DIR
    from pathlib import Path
    import json

    env_file_path = Path(BASE_DIR) / '.django_env'

    env_local = {
        'CSRF_TRUSTED_ORIGIN': _get_or_set_environment('CSRF_TRUSTED_ORIGIN'),
        'SECRET_KEY': _get_or_set_environment('SECRET_KEY'),
        'KAKAO_API_KEY': _get_or_set_environment('KAKAO_API_KEY'),
        'KAKAO_SECRET_KEY': _get_or_set_environment('KAKAO_SECRET_KEY'),
        'KAKAO_REDIRECT_URL': _get_or_set_environment('KAKAO_REDIRECT_URL'),
        'KAKAO_PAY_CID': _get_or_set_environment('KAKAO_PAY_CID'),
        'KAKAO_PAY_SECRET_KEY': _get_or_set_environment('KAKAO_PAY_SECRET_KEY'),
        'NAVER_API_KEY': _get_or_set_environment('NAVER_API_KEY'),
        'NAVER_SECRET_KEY': _get_or_set_environment('NAVER_SECRET_KEY'),
        'NAVER_REDIRECT_URL': _get_or_set_environment('NAVER_REDIRECT_URL'),
        'GOOGLE_CLIENT_ID': _get_or_set_environment('GOOGLE_CLIENT_ID'),
        'GOOGLE_SECRET_KEY': _get_or_set_environment('GOOGLE_SECRET_KEY'),
        'GOOGLE_REDIRECT_URL': _get_or_set_environment('GOOGLE_REDIRECT_URL'),
        'CHANNEL_LAYERS': {
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {
                    'hosts': [(_get_or_set_environment('CHANNEL_HOST'), int(_get_or_set_environment('CHANNEL_PORT')))],
                },
            },
        },
        'CELERY_BROKER_URL': _get_or_set_environment('CELERY_BROKER_URL'),
        'result_backend': _get_or_set_environment('result_backend'),
        'CACHEOPS_REDIS': {
            'host': _get_or_set_environment('CACHEOPS_REDIS_HOST'),
            'port': int(_get_or_set_environment('CACHEOPS_REDIS_PORT')),
            'db': int(_get_or_set_environment('CACHEOPS_REDIS_DB')),
        },
        'CACHEOPS': {},
        'CACHES_LOCATION': _get_or_set_environment('CACHES_LOCATION'),
        'DATABASE': {
            'ENGINE': _get_or_set_environment('DB_ENGINE'),
            'NAME': _get_or_set_environment('DB_NAME'),
            'USER': _get_or_set_environment('DB_USER'),
            'PASSWORD': _get_or_set_environment('DB_PASSWORD'),
            'HOST': _get_or_set_environment('DB_HOST'),
            'PORT': _get_or_set_environment('DB_PORT'),
            'TEST': {
                'NAME': _get_or_set_environment('DB_TEST_NAME')
            },
        },
        'EMAIL_HOST_USER': _get_or_set_environment('EMAIL_HOST_USER'),
        'EMAIL_HOST_PASSWORD': _get_or_set_environment('EMAIL_HOST_PASSWORD'),
        'AWS_IAM_ACCESS_KEY': _get_or_set_environment('AWS_IAM_ACCESS_KEY'),
        'AWS_IAM_SECRET_ACCESS_KEY': _get_or_set_environment('AWS_IAM_SECRET_ACCESS_KEY'),
        'AWS_S3_BUCKET_NAME': _get_or_set_environment('AWS_S3_BUCKET_NAME'),
        'AWS_SQS_URL': _get_or_set_environment('AWS_SQS_URL'),
        'CRONTAB_PREFIX_COMMAND': _get_or_set_environment('CRONTAB_PREFIX_COMMAND'),
        'OPENAI_API_KEY': _get_or_set_environment('OPENAI_API_KEY'),
        'SENTRY_DSN': _get_or_set_environment('SENTRY_DSN'),
        'SENTRY_ENV': _get_or_set_environment('SENTRY_ENV').lower() if os.environ.get('SENTRY_DSN') else None,
    }

    with open(env_file_path, 'w', encoding='utf-8') as f:
        json.dump(env_local, f, ensure_ascii=False, indent=4)


def _get_or_set_environment(environment_key):
    if os.environ.get(environment_key) is None:
        return input(f'Input {environment_key}: ')
    return os.environ[environment_key]


@task
def update_crontab(c):
    from jinja2 import Template
    from pathlib import Path

    django_env_str = Path('.django_env').read_text()
    if not django_env_str:
        raise Exception('.django_env file not found')
    django_env = json.loads(django_env_str)
    try:
        prefix_command = django_env['CRONTAB_PREFIX_COMMAND']
    except KeyError:
        raise Exception('CRONTAB_PREFIX_COMMAND not found in .django_env file')

    template = Template(Path('crontab.j2').read_text())
    rendered = template.render(
        prefix_command=prefix_command,
    )
    rendered += '\n'

    Path('command.cron').write_text(rendered)
