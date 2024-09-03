#!/bin/sh
if [ $# -eq 0 ]; then
    MODE=local
else
    MODE=$1
fi

if [ $# -eq 0 ]; then
    MODE=local
else
    MODE=$1
fi



if [ "$MODE" == "local" ]; then
    echo "Local mode"
    NETWORK=host docker-compose up client
else
    echo "Network mode"
    ADDRESS=$2 docker-compose up client 
fi
