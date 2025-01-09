#!/bin/bash

set -e

IMAGE_NAME_EASY="ghcr.io/bourquejulien/cqi-2025-easy-bot:latest"
IMAGE_NAME_MEDIUM="ghcr.io/bourquejulien/cqi-2025-easy-medium:latest"

AWS_ECR_NAME="481665101132.dkr.ecr.us-east-1.amazonaws.com"

NAMES=$(aws secretsmanager get-secret-value \
    --secret-id user_secrets \
    --query "SecretString" \
    --output text \
    | jq "keys[]" -r)

docker pull $IMAGE_NAME
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin "$AWS_ECR_NAME"

for NAME in $NAMES; do
    echo "Pushing $NAME"
    NAME="${AWS_ECR_NAME}/${NAME}"
    docker tag $IMAGE_NAME "$NAME"
    docker push "$NAME"
done
