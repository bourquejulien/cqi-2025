#!/bin/bash

set -e

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root" >&2
  exit 1
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "GITHUB_TOKEN is not set. Please export it before running this script." >&2
    exit 1
fi

echo "Updating system..."
apt-get update > /dev/null && apt-get -y upgrade > /dev/null

echo "Installing dependencies..."
apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl \
    python3 \
    python3-venv \
    libaugeas0 \
    > /dev/null

echo "Installing Docker..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list

apt-get update > /dev/null && apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin > /dev/null

# Test installation
docker run hello-world
echo $GITHUB_TOKEN | docker login ghcr.io -u bourquejulien --password-stdin
