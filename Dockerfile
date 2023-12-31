# Dockerfile

# Python 3.11 이미지 사용
FROM python:3.11

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 Python 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# CRON 적용
RUN apt-get update && apt-get install -y cron vim dos2unix
RUN mkdir -p /tmp/log
COPY command.cron /etc/cron.d/command.cron
# 줄바꿈 이슈로 dos2unix 설치 후 실행
RUN dos2unix /etc/cron.d/command.cron
RUN chmod 0644 /etc/cron.d/command.cron
