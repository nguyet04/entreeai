#!/usr/bin/env bash

./build.sh

docker push gebizar/capstonegateway

export FLASKADDR="flask:80"
export ADDR=":4000"
export MONGOADDR="mongo:27017"

docker pull gebizar/capstonegateway
docker rm -f capstonegateway
docker rm -f mongo

docker network rm sharednetwork
docker network create sharednetwork 

docker run -d \
--name mongo \
--network sharednetwork \
mongo

docker run -d \
--network sharednetwork \
--name capstonegateway \
-p 80:80 \
-e FLASKADDR=$FLASKADDR \
-e MONGOADDR=$MONGOADDR \
-e ADDR=$ADDR \
gebizar/capstonegateway