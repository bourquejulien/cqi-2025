import base64
import logging
import shutil
import boto3
import docker
import requests

DEFAULT_TIMEOUT = 2

def get_aws_metadata_token():
    url = "http://169.254.169.254/latest/api/token"
    headers = {"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
    response = requests.put(url, headers=headers, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    return response.text.strip()

def is_running_on_ec2():
    try:
        get_aws_metadata_token()
        return True
    except:
        return False

def get_disk_usage() -> float:
    total, used, _ = shutil.disk_usage("/")
    return used / total

def get_internal_key(session: boto3.session.Session) -> str:
    ecr_client = session.client(service_name="ecr", region_name="us-east-1")
    token = ecr_client.get_authorization_token()
    username, password = base64.b64decode(token["authorizationData"][0]["authorizationToken"]).decode().split(":")
    registry = token["authorizationData"][0]["proxyEndpoint"]
    return username, password, registry
