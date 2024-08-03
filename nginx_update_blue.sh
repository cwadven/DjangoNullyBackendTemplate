#!/bin/sh

NEW_CONFIG="server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://web_blue:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias /app/static/;
    }

    location /media/ {
        alias /app/media/;
    }
}"

echo "> Health Check Start!"

for RETRY_COUNT in $(seq 1 100)
do
  RESPONSE=$(curl -s http://web_blue:8000/)

  if [ -n "$RESPONSE" ]
  then
    echo "> Health check 성공"
    echo "$NEW_CONFIG" > /etc/nginx/conf.d/default.conf
    nginx -s reload
    break
  else
    echo "> Health check의 응답을 알 수 없거나 혹은 실행 상태가 아닙니다."
    echo "> Health check: ${RESPONSE}"
  fi

  if [ ${RETRY_COUNT} -eq 100 ] # RETRY_COUNT 내에서 성공하지 못한 경우
  then
    echo "> Health check 실패"
    echo "> 엔진엑스에 연결하지 않고 배포를 종료합니다."
    exit 1
  fi

  echo "> Health check 연결 실패. 재시도..."
  sleep 5
done
