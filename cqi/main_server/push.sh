#!/bin/bash

set -e

DOCKER_HUB_IMAGE="brqu/server"
BUILDX_CONTEXT="cqi"

docker buildx create --use --name $BUILDX_CONTEXT
docker buildx build --platform linux/amd64,linux/arm64 -t $DOCKER_HUB_IMAGE --push .
docker buildx rm $BUILDX_CONTEXT
