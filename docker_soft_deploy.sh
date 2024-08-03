#!/bin/sh

# Check Docker Network
NETWORK_NAME="common_network"

# Search from Docker Network List
network_exists=$(docker network ls | grep -w $NETWORK_NAME)

# If the network does not exist, create it
if [ -z "$network_exists" ]; then
    echo "Network '$NETWORK_NAME' is not exists. Creating..."
    docker network create $NETWORK_NAME
fi

DATA_COMPOSE_FILE=docker-compose-data.yml
data_services="database pgadmin cache"

# Check if all data services are running
data_all_services_up=true

for service in $data_services; do
    # Check service by 'docker-compose ps'
    if ! docker-compose -f $DATA_COMPOSE_FILE ps | grep -q $service; then
        echo "$service service is not running."
        data_all_services_up=false
        break
    fi
done

# If one or more services are not running, build and run
if [ "$data_all_services_up" = "false" ]; then
    echo "One or more services are not running. Starting build and run..."
    docker-compose -f $DATA_COMPOSE_FILE down
    docker-compose -f $DATA_COMPOSE_FILE up -d --build
fi

WEB_COMPOSE_FILE=docker-compose-web.yml
web_services="web_server celery_monitor"

# Check if all web services are running
web_all_services_up=true

for service in $web_services; do
    # Check service by 'docker-compose ps'
    if ! docker-compose -f $WEB_COMPOSE_FILE ps | grep -q $service; then
        echo "$service service is not running."
        web_all_services_up=false
        break
    fi
done

# If one or more services are not running, build and run
if [ "$web_all_services_up" = "false" ]; then
    echo "One or more services are not running. Starting build and run..."
    docker-compose -f $WEB_COMPOSE_FILE down
    docker-compose -f $WEB_COMPOSE_FILE up -d --build
fi

# Application Deployment
BLUE_APP_COMPOSE_FILE=docker-compose-app-blue.yml
GREEN_APP_COMPOSE_FILE=docker-compose-app-green.yml

blue_app_services="web_blue cron_blue celery_blue"
green_app_services="web_green cron_green celery_green"

app_blue_services_up=true
app_green_services_up=true

# Check if all blue app services are running
for service in $blue_app_services; do
    if ! docker-compose -f $BLUE_APP_COMPOSE_FILE ps | grep -q $service; then
        echo "$service service is not running."
        app_blue_services_up=false
        break
    fi
done

# Check if all green app services are running
for service in $green_app_services; do
    if ! docker-compose -f $GREEN_APP_COMPOSE_FILE ps | grep -q $service; then
        echo "$service service is not running."
        app_green_services_up=false
        break
    fi
done

# Deployment logic
if [ "$app_blue_services_up" = "false" ] && [ "$app_green_services_up" = "false" ]; then
    echo "Both blue and green servers are not running. Starting build blue and run..."
    docker-compose -f $BLUE_APP_COMPOSE_FILE up -d
    docker exec web_server /bin/sh -c '/etc/nginx/conf.d/nginx_update_blue.sh'
    echo "Nginx setting to blue environment"
elif [ "$app_blue_services_up" = "true" ]; then
    echo "Deploying green server."
    docker-compose -f $GREEN_APP_COMPOSE_FILE up -d
    docker exec web_server /bin/sh -c '/etc/nginx/conf.d/nginx_update_green.sh'
    echo "Nginx setting to green environment."
    docker-compose -f $BLUE_APP_COMPOSE_FILE down
    echo "Remove blue environment."
elif [ "$app_green_services_up" = "true" ]; then
    echo "Deploying blue server."
    docker-compose -f $BLUE_APP_COMPOSE_FILE up -d
    docker exec web_server /bin/sh -c '/etc/nginx/conf.d/nginx_update_blue.sh'
    echo "Nginx setting to blue environment."
    docker-compose -f $GREEN_APP_COMPOSE_FILE down
    echo "Remove green environment."
fi

docker rmi $(docker images -f "dangling=true" -q) 2> /dev/null
