#!/bin/bash

set -e

DOCKER_IMAGE="ghcr.io/bourquejulien/cqi-2024-gamer-server:latest"
BUILDX_CONTEXT="cqi"

docker buildx create --use --name $BUILDX_CONTEXT
docker buildx build --platform linux/amd64,linux/arm64 -t $DOCKER_IMAGE --push .
docker buildx rm $BUILDX_CONTEXT
