#!/bin/bash

set -e

function getArchitecture() {
    INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=game_runner_0" \
    --query "Reservations[*].Instances[*].InstanceId" \
    --output text)

    ARCHITECTURE=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --query "Reservations[*].Instances[*].Architecture" \
    --output text)

    echo $ARCHITECTURE
}

IMAGE_NAME_EASY="ghcr.io/bourquejulien/cqi-2025-easy-bot:latest"
IMAGE_NAME_MEDIUM="ghcr.io/bourquejulien/cqi-2025-medium-bot:latest"
PLATFORM="linux/$(getArchitecture)"

AWS_ECR_NAME="481665101132.dkr.ecr.us-east-1.amazonaws.com"

NAMES=$(aws secretsmanager get-secret-value \
    --secret-id user_secrets \
    --query "SecretString" \
    --output text \
    | jq "keys[]" -r)

echo "Pulling images using platform: $PLATFORM"

docker pull --platform "$PLATFORM"  "$IMAGE_NAME_EASY"
docker pull --platform "$PLATFORM"  "$IMAGE_NAME_MEDIUM"

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin "$AWS_ECR_NAME"

i=0
for NAME in $NAMES; do
    if (( $((i % 2)) == 0 )); then
        IMAGE_NAME=$IMAGE_NAME_EASY
    else
        IMAGE_NAME=$IMAGE_NAME_MEDIUM
    fi

    i=$((i + 1))

    NAME="${AWS_ECR_NAME}/${NAME}"
    echo "Image: "$IMAGE_NAME" to: $NAME"
    docker tag "$IMAGE_NAME" "$NAME"
    docker push "$NAME"
done
