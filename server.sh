#!/bin/sh

if [ $# -eq 0 ]; then
    MODE=network
else
    MODE=$1
fi

echo Container started in mode : $MODE

if [ "$MODE" == "local" ]; then
    NETWORK=host docker-compose up server
else
    echo Server running on address $(ifconfig | grep "inet 192"||"inet 10")
    docker-compose up server
fi
