#!/bin/env python3

import logging
import asyncio
import json
import os
import sys
import logging
import threading

from typing import Callable, Coroutine, Iterable, TypeVar
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
    return json_response({"status": status})


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


async def force_end_game(request: Request):
    game_running = await run_async(game_runner.force_end_game)
    if not game_running:
        return Response(text="No game running", status=400)

    return json_response({"status": "stopped"}, status=200)


def initialize(app: Application) -> None:
    global game_runner, handler_thread
    game_runner = Runner(app.logger)
    handler_thread = threading.Thread(target=game_runner.run, args=())
    handler_thread.start()


def stop() -> None:
    print("Stopping...")
    game_runner.stop()
    handler_thread.join()


def setup_web_server(is_debug: bool) -> Application:
    extra_format = " %(module)s-%(funcName)s:" if is_debug else ":"
    logging.basicConfig(level=logging.DEBUG if is_debug else logging.INFO,
                        format=f"%(asctime)s %(levelname)s{extra_format} %(message)s",
                        datefmt="%d-%m-%Y %H:%M:%S"
                        )

    app = web.Application(logger=logging.getLogger())

    app.router.add_get("/status", get_status)
    app.router.add_post("/run_game", run_game)
    app.router.add_post("/force_end_game", force_end_game)

    return app


def main() -> None:
    port = int(os.environ[ENV_PORT]) \
        if ENV_PORT in os.environ \
        else DEFAULT_PORT
    is_debug = ENV_MODE not in os.environ or os.environ[ENV_MODE] == "debug"

    app = setup_web_server(is_debug=is_debug)
    initialize(app)

    host = "0.0.0.0"
    try:
        app.logger.info("Starting game server on %s", f"{host}:{port}")
        web.run_app(app, host=host, port=port)
    finally:
        stop()


if __name__ == "__main__":
    main()
