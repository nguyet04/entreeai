#!/usr/bin/env bash

./build.sh

docker push gebizar/capstonegateway

export FLASKADDR="FLASK:80"
export ADDR=":80"

docker pull gebizar/capstonegateway
docker rm -f capstonegateway

docker network rm sharednetwork
docker network create sharednetwork 

docker run -d \
--network sharednetwork \
--name capstonegateway \
-p 80:80 \
-e FLASKADDR=$FLASKADDR \
-e ADDR=$ADDR \
gebizar/capstonegateway