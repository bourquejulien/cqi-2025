#!/usr/bin/env python3

import os
import signal
import boto3
import docker
import time
import boto3.session
import base64
import logging
import docker
from docker import DockerClient
from docker.models.images import Image
from docker.models.containers import Container
from docker.models.networks import Network

from stop_token import StopToken
from match_runner import MatchRunner
from main_server_client import MainServerClient

GAME_SERVER_IMAGE_NAME = "ghcr.io/bourquejulien/cqi-2024-game-server"

def get_internal_key(session: boto3.session.Session) -> str:
    ecr_client = session.client(service_name="ecr", region_name="us-east-1")
    token = ecr_client.get_authorization_token()
    username, password = base64.b64decode(token["authorizationData"][0]["authorizationToken"]).decode().split(":")
    registry = token["authorizationData"][0]["proxyEndpoint"]

    return username, password, registry

def main() -> None:
    logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s%(module)s-%(funcName)s: %(message)s",
                    datefmt="%d-%m-%Y %H:%M:%S")
    # Grab secret from AWS Secrets Manager
    session = boto3.session.Session()
    secret_manager_client = session.client(service_name="secretsmanager", region_name="us-east-1")
    secret = secret_manager_client.get_secret_value(SecretId="internal_key")["SecretString"]

    docker_client: DockerClient = docker.from_env()

    username, password, registry = get_internal_key(session)
    docker_client.login(username=username, password=password, registry=registry)

    base_address = os.environ.get("SERVER_ADDRESS", "http://localhost:8000")
    main_server_client = MainServerClient(secret=secret, base_url=base_address)

    gameServerImage: Image = docker_client.images.pull(GAME_SERVER_IMAGE_NAME)

    match_runner = MatchRunner(game_server_image=gameServerImage, docker_client=docker_client)
    match_runner.cleanup()

    stop_token = StopToken()
    signal.signal(signal.SIGINT, stop_token.cancel)

    while not stop_token.is_canceled():
        # TODO - Evaluate how many games can run concurrently
        matches_to_run = main_server_client.get_next_matches(2)
        match_runner.run_matches(stop_token, matches_to_run)

        results = match_runner.get_results()
        for result in results:
            main_server_client.add_result(result)

        logging.info("Added %s results", len(results))
        stop_token.wait(5)

if __name__ == "__main__":
    main()
