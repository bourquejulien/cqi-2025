#!/bin/bash

set -e
set -u
set -o pipefail

ECR_NAME="481665101132.dkr.ecr.us-east-1.amazonaws.com"
BUILDER_NAME="cqi-builder"

if [[ -z ${TEAM_NAME+x} ]]; then
    read -p "Enter team name: " TEAM_NAME
fi

if [[ -z ${BUILD_DIR+x} ]]; then
    read -p "Enter build directory ('.' if current directory): " BUILD_DIR
fi

docker buildx ls | grep "$BUILDER_NAME" || docker buildx create --name "$BUILDER_NAME"
docker buildx use "$BUILDER_NAME"

docker buildx build --platform linux/amd64 -t "$ECR_NAME/$TEAM_NAME" --push "$BUILD_DIR"
