#!/usr/bin/env python3

import os
import signal
import boto3
import boto3.session
import docker
import boto3.session
import logging
import docker
from docker import DockerClient
from docker.models.images import Image

from interfaces import Match
from helpers import *
from stop_token import StopToken
from match_runner import MatchRunner
from main_server_client import MainServerClient

GAME_SERVER_IMAGE_NAME = "ghcr.io/bourquejulien/cqi-2025-game-server"
MAX_DISK_USAGE = 0.9

def prune_images(docker_client: docker.DockerClient) -> None:
    if not is_running_on_ec2():
        logging.warning("Not running on EC2, skipping cleanup")
        return
    
    logging.warning("Pruning images...")
    docker_client.images.prune()
    logging.warning(f"Done pruning images, new disck usage: {get_disk_usage()}")


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s => %(module)s-%(funcName)s: %(message)s",
                    datefmt="%d-%m-%Y %H:%M:%S")

    session = boto3.session.Session()
    docker_client: DockerClient = docker.from_env()

    internal_key = get_internal_key(session)
    if ex := login_to_ecr(session, docker_client):
        raise ex

    base_address = os.environ.get("SERVER_ADDRESS", "http://localhost:8000")
    main_server_client = MainServerClient(secret=internal_key, base_url=base_address)

    gameServerImage: Image = docker_client.images.pull(GAME_SERVER_IMAGE_NAME)

    match_runner = MatchRunner(game_server_image=gameServerImage, docker_client=docker_client)
    match_runner.cleanup()

    stop_token = StopToken()
    signal.signal(signal.SIGINT, stop_token.cancel)

    while not stop_token.is_canceled():
        disk_usage = get_disk_usage()

        matches_to_run: list[Match] = []
        if disk_usage < MAX_DISK_USAGE:
            matches_to_run = main_server_client.get_next_matches(match_runner.currently_running)
        else:
            logging.warning(f"Disk usage is too high ({disk_usage})")
            prune_images(docker_client)
        
        match_runner.run_matches(stop_token, matches_to_run)
        results = match_runner.get_results()

        for result in results:
            main_server_client.add_result(result)

        logging.info("Sent %s results", len(results))
        
        if e := login_to_ecr(session, docker_client):
            logging.warning(f"Failed to login to ECR: {e}")
        
        stop_token.wait(5)

if __name__ == "__main__":
    main()
