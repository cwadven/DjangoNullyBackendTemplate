#!/bin/bash

# web-app 실행 중인지 확인
WEB_APP_RUNNING=$(docker ps --filter "name=web-app" --format "{{.Names}}")

# gunicorn을 재시작하기 위해 컨테이너가 실행 중인지 확인합니다.
if [ -z "$WEB_APP_RUNNING" ]; then
    echo "web-app 실행 중이 아닙니다. web-app 컨테이너를 시작합니다."
    docker-compose up -d web-app  # web-app 컨테이너 시작
    sleep 10  # 컨테이너가 완전히 시작될 시간을 줌
    WEB_APP_RUNNING=$(docker ps --filter "name=web-app" --format "{{.Names}}")
    if [ -z "$WEB_APP_RUNNING" ]; then
        echo "Error: web-app 컨테이너를 시작하지 못했습니다. 스크립트를 종료합니다."
        exit 1
    fi
else
    echo "web-app 컨테이너가 이미 실행 중입니다."
    echo "web-app 마이그레이션 및 정적 파일을 업데이트합니다."
    docker exec web-app sh -c "cd /app &&
         pip install --no-cache-dir -r requirements.txt &&
         python manage.py migrate &&
         python manage.py collectstatic --noinput"
    echo "gunicorn 프로세스를 종료합니다."
    docker exec web-app sh -c "pkill -f gunicorn"
    sleep 10
    echo "gunicorn 프로세스를 재시작합니다."
    docker exec web-app sh -c "gunicorn config.wsgi:application --bind 0.0.0.0:8000 --access-logfile /var/log/gunicorn/access.log --error-logfile /var/log/gunicorn/error.log --daemon"
fi

# Nginx 컨테이너가 실행 중인지 확인
NGINX_CONTAINER=$(docker ps --filter "name=nginx" --format "{{.Names}}")

if [ -z "$NGINX_CONTAINER" ]; then
    echo "Nginx 컨테이너가 실행 중이지 않습니다. Nginx 컨테이너를 시작합니다."
    docker-compose up -d nginx  # Nginx 컨테이너 시작
    sleep 10  # 컨테이너가 완전히 시작될 시간을 줌

    # Nginx 컨테이너가 제대로 시작됐는지 다시 확인
    NGINX_CONTAINER=$(docker ps --filter "name=nginx" --format "{{.Names}}")
    if [ -z "$NGINX_CONTAINER" ]; then
        echo "Error: Nginx 컨테이너를 시작하지 못했습니다. 스크립트를 종료합니다."
        exit 1
    fi
fi

# 헬스체크 (web-app 환경이 정상적으로 동작하는지 확인)
HEALTHY=false
RE_TRY=60
for i in $(seq 1 $RE_TRY)
do
    STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000)
    if [ "$STATUS_CODE" == "200" ]; then
        HEALTHY=true
        echo "web-app 환경이 정상적으로 준비되었습니다."
        # Celery worker 재시작
        echo "Celery worker를 재시작합니다."
        # Celery worker 가 실행 중이라면 graceful 후 재시작
        docker exec web-app sh -c "celery -A config control shutdown"
        docker exec web-app sh -c "celery -A config worker --loglevel=info --loglevel=info -D --logfile=/var/log/celery/worker.log"
        echo "Celery worker가 재시작되었습니다."
        break
    fi
    echo "web-app 환경이 준비되지 않았습니다. 재시도 중... ($i/$RE_TRY)"
    sleep 5
done

if [ "$HEALTHY" = false ]; then
    echo "web-app 환경이 준비되지 않아 스크립트를 종료합니다."
    exit 1
fi

# Nginx 재실행
echo "Nginx를 재시작합니다."
docker exec nginx sh -c "nginx -s reload"
echo "Nginx가 재시작되었습니다."

# Cron job 서비스 실행 확인
CRON_APP_RUNNING=$(docker ps --filter "name=cron-app" --format "{{.Names}}")

if [ -z "$CRON_APP_RUNNING" ]; then
    echo "Cron 컨테이너가 실행 중이지 않습니다. Cron 컨테이너를 시작합니다."
    docker-compose up -d cron-app  # Cron 컨테이너 시작
    sleep 10  # 컨테이너가 완전히 시작될 시간을 줌

    # Cron 컨테이너가 제대로 시작됐는지 다시 확인
    CRON_APP_RUNNING=$(docker ps --filter "name=cron-app" --format "{{.Names}}")
    if [ -z "$CRON_APP_RUNNING" ]; then
        echo "Error: Cron 컨테이너를 시작하지 못했습니다. 스크립트를 종료합니다."
        exit 1
    fi
else
    echo "Cron 작업을 업데이트합니다."
    docker exec cron-app sh -c "fab2 update-crontab"
    docker exec cron-app sh -c "dos2unix command.cron"
    docker exec cron-app sh -c "chmod 0644 command.cron"
    docker exec cron-app sh -c "cat command.cron | crontab -"
    docker exec cron-app sh -c "service cron restart"
    echo "Cron 작업이 업데이트되었습니다."
fi
