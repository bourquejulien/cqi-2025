#! /bin/bash

set -e

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <AWS_ACCESS_KEY_ID> <AWS_SECRET_ACCESS_KEY>"
    exit 1
fi

export AWS_ACCESS_KEY_ID=$1
export AWS_SECRET_ACCESS_KEY=$2

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 481665101132.dkr.ecr.us-east-1.amazonaws.com
