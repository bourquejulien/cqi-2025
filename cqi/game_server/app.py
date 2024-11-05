#!/bin/env python3

from dataclasses import asdict
import logging
import asyncio
import os
import time
import signal
import threading

from typing import Callable, Iterable, TypeVar
from threading import Thread
from aiohttp import web
from aiohttp.web import Response, json_response, Application, Request

from src.game_runner import Runner

game_runner: Runner
handler_thread: Thread

T = TypeVar("T")


ENV_PORT = "PORT"
ENV_MODE = "MODE"
DEFAULT_PORT = 5000


async def run_async(func: Callable[[Iterable], T], *args) -> T:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args)


async def get_status(request: Request):
    status = await run_async(game_runner.status)
    return json_response({"status": asdict(status)})


async def run_game(request: Request):
    OFFENSE = "offense_url"
    DEFENSE = "defense_url"
    query_param = request.rel_url.query

    if OFFENSE not in query_param or DEFENSE not in query_param:
        return Response(text="Wrong parameters", status=400)

    offense_bot_url = request.rel_url.query[OFFENSE]
    defense_bot_url = request.rel_url.query[DEFENSE]

    await run_async(game_runner.launch_game, offense_bot_url, defense_bot_url)

    return json_response({"status": "started"}, status=200)


async def end_game(request: Request):
    game_running = await run_async(game_runner._force_end_game)
    if not game_running:
        return Response(text="No game running", status=400)

    return json_response({"status": "stopped"}, status=200)


def initialize(is_debug: bool) -> None:
    global game_runner, handler_thread

    extra_format = " %(module)s-%(funcName)s:" if is_debug else ":"
    logging.basicConfig(level=logging.DEBUG if is_debug else logging.INFO,
                        format=f"%(asctime)s %(levelname)s{
                            extra_format} %(message)s",
                        datefmt="%d-%m-%Y %H:%M:%S")

    game_runner = Runner()
    handler_thread = threading.Thread(target=game_runner.run, args=())
    handler_thread.start()


def stop() -> None:
    logging.info("Stopping...")
    game_runner.stop()
    handler_thread.join()


def setup_web_server() -> Application:
    app = web.Application(logger=logging.getLogger())

    app.router.add_get("/status", get_status)
    app.router.add_post("/run_game", run_game)
    app.router.add_post("/force_end_game", end_game)

    return app


def test() -> None:
    bot_1_url = os.environ["BOT_1_URL"]
    bot_2_url = os.environ["BOT_2_URL"]

    global should_stop
    should_stop = False

    def stop(*_):
        global should_stop
        should_stop = True
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    game_runner.launch_game(bot_1_url, bot_2_url)

    DURATION = 15
    for _ in range(DURATION):
        if should_stop or game_runner.status().is_over or not game_runner.status().is_running:
            break
        time.sleep(1)

    if not game_runner.status().is_over:
        logging.warning("Game not over")


def run() -> None:
    port = int(os.environ[ENV_PORT]) \
        if ENV_PORT in os.environ \
        else DEFAULT_PORT
    host = "0.0.0.0"

    app = setup_web_server()
    logging.info("Starting game server on %s", f"{host}:{port}")
    web.run_app(app, host=host, port=port)


def main() -> None:
    mode = "debug" if ENV_MODE not in os.environ else os.environ[ENV_MODE]
    is_debug = mode in ["debug", "test"]

    initialize(is_debug)

    launch = test if mode == "test" else run
    try:
        launch()
    finally:
        stop()


if __name__ == "__main__":
    main()
