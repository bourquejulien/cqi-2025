#!/bin/bash

set -e
set -o pipefail
set -u

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 481665101132.dkr.ecr.us-east-1.amazonaws.com

CURRENT_DIR=$(pwd)
AWS_ECR_NAME="481665101132.dkr.ecr.us-east-1.amazonaws.com"
OUTPUT_DIR_NAME="remise"
OUTPUT_DIR="$CURRENT_DIR/$OUTPUT_DIR_NAME"

NAMES=$(aws secretsmanager get-secret-value \
    --secret-id user_secrets \
    --query "SecretString" \
    --output text \
| jq "keys[]" -r)

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

for NAME in $NAMES; do
    IMAGE_NAME="${AWS_ECR_NAME}/${NAME}:latest"
    SIMPLE_NAME="cqiprog-remise-$NAME"
    
    if docker pull "$IMAGE_NAME" ; then
        docker tag "$IMAGE_NAME" "$SIMPLE_NAME"
        docker save "$SIMPLE_NAME" > "$OUTPUT_DIR/$SIMPLE_NAME.tar"
    else
        echo "Image $IMAGE_NAME not found"
    fi
done

ARCHIVE_NAME="ecr_remise.tar.gz"
echo "Creating archive $ARCHIVE_NAME"
tar -C "$CURRENT_DIR" -czf "$ARCHIVE_NAME" "$OUTPUT_DIR_NAME"
rm -rf "$OUTPUT_DIR"
