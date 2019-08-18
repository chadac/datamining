#!/bin/bash

docker run -it \
       -v $PWD/mongod.conf:/etc/mongod.conf \
       -e MONGO_INITDB_ROOT_USERNAME=root \
       -e MONGO_INITDB_ROOT_PASSWORD=root \
       -p 27017:27017 \
       mongo:latest \
       mongod --bind_ip_all -f /etc/mongod.conf
