#!/bin/bash

set -e

LETSENCRYPT_BACKUP="s3://cqi-persisted/letsencrypt/backup.tar.gz"

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

snap install aws-cli --classic > /dev/null

echo "Installing dependencies..."
apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl \
    python3 \
    python3-venv \
    libaugeas0 \
    nginx
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

# Allow to run as non-root
# gpasswd -a $USER docker
# newgrp docker

# Test installation
docker run hello-world
echo $GITHUB_TOKEN | docker login ghcr.io -u bourquejulien --password-stdin

echo "Installing certbot..."
python3 -m venv /opt/certbot/ && \
            /opt/certbot/bin/pip install --upgrade pip > /dev/null && \
            /opt/certbot/bin/pip install certbot certbot-nginx > /dev/null && \
            ln -s /opt/certbot/bin/certbot /usr/bin/certbot

if aws s3 ls $LETSENCRYPT_BACKUP ; then
    echo "Downloading and extracting letsencrypt backup..."
    rm -rf /etc/letsencrypt
    aws s3 cp $LETSENCRYPT_BACKUP - | sudo tar -xzf - -C /etc
else
    echo "No letsencrypt backup found."
fi

certbot certonly --nginx --non-interactive --agree-tos --domains server.cqiprog.info --email cqiprog@fastmail.com

echo "Configuring nginx..."
mv ./default.conf /etc/nginx/sites-available/default.conf
ln -s /etc/nginx/sites-available/default.conf /etc/nginx/sites-enabled/default.conf
nginx -t && nginx -s reload

# Automatically renew certificates
echo "0 0,12 * * * root /opt/certbot/bin/python -c 'import random; import time; time.sleep(random.random() * 3600)' && sudo certbot renew -q" | sudo tee -a /etc/crontab > /dev/null

# Push the updated files to S3
tar -czf - -C /etc letsencrypt | aws s3 cp - $LETSENCRYPT_BACKUP --acl bucket-owner-full-control

# Start the server
docker compose up -d
