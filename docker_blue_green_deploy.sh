#!/bin/bash


# app-blue 또는 app-green 중 하나가 실행 중인지 확인
APP_BLUE_RUNNING=$(docker ps --filter "name=app-blue" --format "{{.Names}}")
APP_GREEN_RUNNING=$(docker ps --filter "name=app-green" --format "{{.Names}}")

if [ -z "$APP_BLUE_RUNNING" ] && [ -z "$APP_GREEN_RUNNING" ]; then
    echo "app-blue 와 app-green이 실행 중이지 않습니다. 최초 둘 다 실행합니다."

    docker-compose up -d app-blue  # app-blue 컨테이너 시작
    sleep 10  # 컨테이너가 완전히 시작될 시간을 줌
    APP_BLUE_RUNNING=$(docker ps --filter "name=app-blue" --format "{{.Names}}")
    if [ -z "$APP_BLUE_RUNNING" ]; then
        echo "Error: app-blue 컨테이너를 시작하지 못했습니다. 스크립트를 종료합니다."
        exit 1
    fi

    docker-compose up -d app-green  # app-green 컨테이너 시작
    sleep 10  # 컨테이너가 완전히 시작될 시간을 줌
    APP_GREEN_RUNNING=$(docker ps --filter "name=app-green" --format "{{.Names}}")
    if [ -z "$APP_GREEN_RUNNING" ]; then
        echo "Error: app-green 컨테이너를 시작하지 못했습니다. 스크립트를 종료합니다."
        exit 1
    fi
fi


# Nginx 컨테이너가 실행 중인지 확인
NGINX_CONTAINER=$(docker ps --filter "name=nginx" --format "{{.Names}}")

if [ -z "$NGINX_CONTAINER" ]; then
    echo "Nginx 컨테이너가 실행 중이지 않습니다. Nginx 컨테이너를 시작합니다."
    docker-compose up -d nginx  # Nginx 컨테이너 시작
    sleep 10  # 컨테이너가 완전히 시작될 시간을 줌

    # Nginx 컨테이너가 제대로 시작되지 않았는지 다시 확인
    NGINX_CONTAINER=$(docker ps --filter "name=nginx" --format "{{.Names}}")
    if [ -z "$NGINX_CONTAINER" ]; then
        echo "Error: Nginx 컨테이너를 시작하지 못했습니다. 스크립트를 종료합니다."
        exit 1
    fi
fi

# 현재 사용 중인 환경을 확인
CURRENT_ENV=$(docker exec nginx cat etc/nginx/nginx.conf | grep server | grep -o 'blue\|green')

# 트래픽을 전환할 새로운 환경 설정
if [ "$CURRENT_ENV" == "blue" ]; then
    NEW_ENV="green"
    NEW_PORT="8082"
    CURRENT_PORT="8081"
else
    NEW_ENV="blue"
    NEW_PORT="8081"
    CURRENT_PORT="8082"
fi

echo "현재 환경: $CURRENT_ENV, 새 환경: $NEW_ENV"

# 새로운 환경의 컨테이너를 시작
docker-compose up -d app-$NEW_ENV

# 헬스체크 (새 환경이 정상적으로 동작하는지 확인)
HEALTHY=false
RE_TRY=60
for i in $(seq 1 $RE_TRY)
do
    STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$NEW_PORT)
    if [ "$STATUS_CODE" == "200" ]; then
        docker exec app-${CURRENT_ENV} sh -c "celery -A config control shutdown"
        docker exec app-${NEW_ENV} sh -c "celery -A config worker --loglevel=info -D"
        HEALTHY=true
        break
    fi
    echo "새 환경이 준비되지 않았습니다. 재시도 중... ($i/$RE_TRY)"
    sleep 5
done

if [ "$HEALTHY" = true ]; then
    # Nginx 설정 파일을 업데이트하여 트래픽을 새 환경으로 전환
    if [[ "$OSTYPE" == "darwin"* ]]; then
      # macOS의 경우
      sed -i '' "s/app-${CURRENT_ENV}/app-${NEW_ENV}/g" nginx.conf
      sed -i '' "s/${CURRENT_PORT}/${NEW_PORT}/" nginx.conf
    else
      # Linux의 경우
      sed -i "s/app-${CURRENT_ENV}/app-${NEW_ENV}/g" nginx.conf
      sed -i "s/${CURRENT_PORT}/${NEW_PORT}/" nginx.conf
    fi

    docker exec nginx sh -c "nginx -s reload"
    echo "트래픽이 $NEW_ENV 환경으로 전환되었습니다."

    # 이전 환경의 컨테이너를 종료
    docker-compose stop app-$CURRENT_ENV
else
    echo "새 환경이 정상적으로 준비되지 않았습니다. 배포를 중단합니다."
    exit 1
fi


CRON_APP_RUNNING=$(docker ps --filter "name=cron-app" --format "{{.Names}}")

if [ -z "$CRON_APP_RUNNING" ]; then
    echo "Cron 컨테이너가 실행 중이지 않습니다. Cron 컨테이너를 시작합니다."
    docker-compose up -d cron-app  # Cron 컨테이너 시작
    sleep 10  # 컨테이너가 완전히 시작될 시간을 줌

    # Cron 컨테이너가 제대로 시작되지 않았는지 다시 확인
    CRON_APP_RUNNING=$(docker ps --filter "name=cron-app" --format "{{.Names}}")
    if [ -z "$CRON_APP_RUNNING" ]; then
        echo "Error: Cron 컨테이너를 시작하지 못했습니다. 스크립트를 종료합니다."
        exit 1
    fi
else
    docker exec cron-app sh -c "fab2 update-crontab"
    docker exec cron-app sh -c "dos2unix command.cron"
    docker exec cron-app sh -c "chmod 0644 command.cron"
    docker exec cron-app sh -c "cat command.cron | crontab -"
    docker exec cron-app sh -c "service cron restart"
    echo "Cron 작업이 업데이트되었습니다."
fi
