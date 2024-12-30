import base64
import shutil
from boto3 import session
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

def get_internal_key(session: session.Session) -> str:
    secret_manager_client = session.client(service_name="secretsmanager", region_name="us-east-1")
    return secret_manager_client.get_secret_value(SecretId="internal_key")["SecretString"]

def get_ecr_login(session: session.Session) -> str:
    ecr_client = session.client(service_name="ecr", region_name="us-east-1")
    token = ecr_client.get_authorization_token()
    username, password = base64.b64decode(token["authorizationData"][0]["authorizationToken"]).decode().split(":")
    registry = token["authorizationData"][0]["proxyEndpoint"].replace("https://", "")
    return username, password, registry

def login_to_ecr(session: session.Session, docker_client: docker.DockerClient) -> None | Exception:
    try:
        username, password, registry = get_ecr_login(session)
        docker_client.login(username=username, password=password, registry=registry)
    except Exception as e:
        return e
    
    return None
