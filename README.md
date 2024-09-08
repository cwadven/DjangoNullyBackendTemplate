# Nully's Django Backend API Template

Nully's Django Backend API Template


## Features

### Social Login
![KakaoTalk](https://img.shields.io/badge/kakaotalk-ffcd00.svg?style=for-the-badge&logo=kakaotalk&logoColor=000000) <br>
![Google](https://img.shields.io/badge/google-4285F4?style=for-the-badge&logo=google&logoColor=white)<br>
**Naver**

## Requirements

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) Version 3.11 <br>
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) Version 14 (Docker file based) <br>
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white) (Celery, Cache) <br>
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) (Optional) <br>

## CI/CD

![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white) <br>

## Getting Started

```shell
# Clone the repository

# Create a virtual environment in the root directory
python -m venv venv

# Activate the virtual environment
# Windows
source venv/Scripts/activate
# Linux
source venv/bin/activate

# Install the requirements
pip install -r requirements.txt

# Define .django_env file
fab2 generate-env

-- Below is the example of .django_env file creating --

-----------------0----------------------
- Input CSRF_TRUSTED_ORIGIN:
----------------------------------------
For use CSRF_TRUSTED_ORIGINS, you need to set the host ip.

"CSRF_TRUSTED_ORIGIN" Example: "http://127.0.0.1"
----------------------------------------
 
-----------------1----------------------
- Input SECRET_KEY:
----------------------------------------
This is a secret key for Django. 
You can generate it here: https://djecrety.ir/

"SECRET_KEY" Example: "django-insecure-......test..."
----------------------------------------

----------------2-----------------------
- Input KAKAO_API_KEY:
- Input KAKAO_SECRET_KEY:
- Input KAKAO_REDIRECT_URL:
----------------------------------------
You can get it here: https://developers.kakao.com/

[ More Explain ]
"KAKAO_API_KEY" Example: "4df48d962f....."
"KAKAO_SECRET_KEY" Example: "sdfaefse....."
"KAKAO_REDIRECT_URL" Example: "http://...."
----------------------------------------

----------------3-----------------------
- Input KAKAO_PAY_CID:
- Input KAKAO_PAY_SECRET_KEY:
----------------------------------------
For Kakao Pay, you need to get a separate key.
"KAKAO_PAY_CID" Example: "TC0ONETIME"
"KAKAO_PAY_SECRET_KEY" Example: "897a....."
----------------------------------------

---------------4------------------------
- Input NAVER_API_KEY:
- Input NAVER_SECRET_KEY:
- Input NAVER_REDIRECT_URL:
----------------------------------------
You can get it here: https://developers.naver.com/main/
"NAVER_API_KEY" Example: "4df48d962f....."
"NAVER_SECRET_KEY" Example: "sdfaefse....."
"NAVER_REDIRECT_URL" Example: "http://...."
----------------------------------------

----------------5-----------------------
- Input GOOGLE_CLIENT_ID:
- Input GOOGLE_SECRET_KEY:
- Input GOOGLE_REDIRECT_URL:
----------------------------------------
You can get it here: https://console.cloud.google.com/apis/credentials

"GOOGLE_CLIENT_ID" Example: "346021117315-ikur0p9aeup3i....."
"GOOGLE_SECRET_KEY" Example: "GOCSPX-i....."
"GOOGLE_REDIRECT_URL" Example: "http://127.0.0.1:8000/account/login"
----------------------------------------

----------------6-----------------------
- Input CHANNEL_HOST:
- Input CHANNEL_PORT:
----------------------------------------
Channels uses Redis as a channel layer.

"CHANNEL_HOST" Example: 127.0.0.1 (if you use docker, you need to set docker container name example 'redis')
"CHANNEL_PORT" Example: 6379
----------------------------------------

----------------7-----------------------
- Input CELERY_BROKER_URL:
- Input result_backend:
----------------------------------------
Celery uses Redis as a message broker.
Need to install Redis: https://redis.io/

"CELERY_BROKER_URL" Example: redis://localhost:6379/2  (if you use docker, you need to set docker container name example 'redis')
"result_backend" Example: redis://localhost:6379/2
----------------------------------------

----------------8-----------------------
- Input CACHEOPS_REDIS_HOST:
- Input CACHEOPS_REDIS_PORT:
- Input CACHEOPS_REDIS_DB:
----------------------------------------
Cacheops uses Redis as a cache.

"CACHEOPS_REDIS_HOST" Example: localhost  (if you use docker, you need to set docker container name example 'redis')
"CACHEOPS_REDIS_PORT" Example: 6379
"CACHEOPS_REDIS_DB" Example: 10
(redis db number)
----------------------------------------

----------------9-----------------------
- Input CACHES_LOCATION:
----------------------------------------
Cache uses location.

"CACHES_LOCATION" Example: redis://localhost:6379/1  (if you use docker, you need to set docker container name example 'redis')
----------------------------------------

-----------------10----------------------
- Input DB_ENGINE:
- Input DB_NAME:
- Input DB_USER:
- Input DB_PASSWORD:
- Input DB_HOST:
- Input DB_PORT:
- Input DB_TEST_NAME:
----------------------------------------
Database settings.

"DB_ENGINE" Example: django.db.backends.postgresql
"DB_NAME" Example: nully
"DB_USER" Example: postgres
"DB_PASSWORD" Example: postgres
"DB_HOST" Example: localhost  (if you use docker, you need to set docker container name 'postgresql14')
"DB_PORT" Example: 5432
"DB_TEST_NAME" Example: nully_test
----------------------------------------

------------------11---------------------
- Input EMAIL_HOST_USER:
- Input EMAIL_HOST_PASSWORD:
----------------------------------------
Host email settings.
Default Gmail if you want to use other email services, you need to change the settings.

"EMAIL_HOST_USER" Example: nully@gmail.com
"EMAIL_HOST_PASSWORD" Example: 1234
----------------------------------------

-----------------12---------------------
- Input AWS_IAM_ACCESS_KEY:
- Input AWS_IAM_SECRET_ACCESS_KEY:
- Input AWS_S3_BUCKET_NAME:
- Input AWS_SQS_URL:
----------------------------------------
AWS settings.

"AWS_IAM_ACCESS_KEY" Example: AKIAYXZ223G...
"AWS_IAM_SECRET_ACCESS_KEY" Example: AKIAYXZ223G...
"AWS_S3_BUCKET_NAME" Example: nully
"AWS_SQS_URL" Example: https://sqs.ap-northeast-2.amazonaws.com/1234/nully
----------------------------------------

-----------------13---------------------
- Input CRONTAB_PREFIX_COMMAND:
----------------------------------------
"CRONTAB_PREFIX_COMMAND" 
Example:
source venv/bin/activate && python manage.py
or
cd /app && newrelic-admin run-program python manage.py
----------------------------------------


-----------------14---------------------
- Input OPENAI_API_KEY:
----------------------------------------
openai api key https://platform.openai.com/settings/profile?tab=api-keys

"OPENAI_API_KEY"
----------------------------------------


-----------------15---------------------
- Input SENTRY_DSN:
----------------------------------------
sentry dns for sentry.io of your project

SENTRY_DSN
----------------------------------------


-----------------16---------------------
- Input SENTRY_ENV:
----------------------------------------
sentry environment for sentry.io of your project

SENTRY_ENV
----------------------------------------

# Define settings file
# local, development, production
export DJANGO_SETTINGS_MODULE=XXXX.settings.local

# Migrate the database
python manage.py migrate

# Run the server
python manage.py runserver

# Run the celery worker
celery -A config worker -l INFO -P solo
```

## Testing

Local Testing
```shell
python manage test --keepdb
```

## CI/CD Setting

### Deploying (self-hosted)

.github/workflows/deploy_staging.yml

1. Edit `DJANGO_SETTINGS_MODULE`
2. `/var/www/ProjectName/` file directory of your project
3. Set well celery directory or remove celery part
```
name: celery restart
run: |
sudo /etc/init.d/celeryd restart
```

### Testing (Github action, When PR to `code-review` name branch)

- GitHub Actions (.github/workflows/test.yml)
- GitHub Actions (.github/workflows/lint.yml)

## Database

### Postgres

```shell
# Set gin index for extension 
psql -U postgres -d database_name -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

## Setting CRON

Need to use by django command

`command.cron`

**[ Example ]**

By Local

```cronexp
30 * * * * . /var/www/ProjectName/bin/activate && cd /var/www/ProjectName && python manage.py django_commands >> /var/log/django_commands.log 2>&1
```

---

## Getting Start By Docker
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
### 1. Set env file

```shell
-- Set .django_env file
fab2 generate-env
```

### 2. `docker-compose.yml` file change `environment` for your `DJANGO_SETTINGS_MODULE`

### 3. Run docker-compose

Create `.env` file at root directory

```shell
# 1.
# Before you start, you need set .env and .django_env files at root directory
# .env file is for docker-compose environment variables
# Need
# POSTGRES_DB
# POSTGRES_USER
# POSTGRES_PASSWORD
# PGADMIN_DEFAULT_EMAIL
# PGADMIN_DEFAULT_PASSWORD
# FLOWER_USER
# FLOWER_PASSWORD

# 2.
# .django_env file is for django settings
# .django_env can be generated by fab2 generate-env

# 3.
# Run deploy script
chmod +x ./deploy.sh
./deploy.sh
```

### 4. Setting CRON

Update crontab.j2 file
- add `prefix_command` for your cron command

```cronexp
PATH=/usr/local/bin:/usr/bin:/bin
MAILTO=""
* * * * * {{ prefix_command }} check >> /tmp/log/django_commands.log 2>&1
```

If you want to see CRON log

```shell
# Check docker container id (find ...cron...)
docker ps

# Ensure the container is running
docker exec -it docker_container_id bash

# Check log
tail -f /tmp/log/django_commands.log
```


## Extra

### Git Hooks

- **pre-commit**: Run flake8
- **pre-push**: Push with master branch version tag

```
cd project_root

chmod +x ./scripts/set_git_hooks.sh
./scripts/set_git_hooks.sh
```
