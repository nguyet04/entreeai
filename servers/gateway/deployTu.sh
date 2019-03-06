#!/usr/bin/env bash

./buildTu.sh

docker push nguyet04/capstonegateway

export FLASKADDR="FLASK:80"
export ADDR=":80"

docker pull nguyet04/capstonegateway
docker rm -f capstonegateway

docker network rm sharednetwork
docker network create sharednetwork 

docker run -d \
--network sharednetwork \
--name capstonegateway \
-p 80:80 \
-e FLASKADDR=$FLASKADDR \
-e ADDR=$ADDR \
nguyet04/capstonegateway