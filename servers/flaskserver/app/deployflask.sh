#!/usr/bin/env bash

export SQLADDR="sql:3306"
export FLASKADDR="flask:5000"
export MYSQL_ROOT_PASSWORD="lol"


# cd ../databases
# ./builddb.sh

# cd ../app
./buildflask.sh

# docker push gebizar/flaskapp
# docker pull gebizar/flaskapp
# docker pull gebizar/flaskdb

docker rm -f flaskapp
# docker rm -f flaskdb

# docker network rm sharednetwork
# docker network create sharednetwork

# docker run -d \
# --name flaskdb \
# --network sharednetwork \
# -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD \
# -e MYSQL_DATABASE=schema \
# -p 3306:3306 \
# gebizar/flaskdb

docker run -d \
--name flaskapp \
--network sharednetwork \
-e FLASKADDR=$FLASKADDR \
-e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD \
-e SQLADDR=$SQLADDR \
gebizar/flaskapp
