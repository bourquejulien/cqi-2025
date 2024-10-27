#!/bin/env python3

import logging
import asyncio
import json
import os
import sys
import logging
import threading

from typing import Callable, Iterable, TypeVar
from aiohttp import web
from aiohttp.web import Response, json_response, Application, Request


ENV_PORT = "PORT"
ENV_MODE = "MODE"
DEFAULT_PORT = 5001


async def start(request: Request):
    data = request.json
    if data["is_offense"] == True:
        ...
    else:
        ...

    return Response(
        text="OK",
        status=200
    )


async def next_move(request: Request):
    return Response(
        text="OK",
        status=200
    )


async def end_game(request: Request):
    return Response(
        text="OK",
        status=200
    )


def setup_web_server(is_debug: bool) -> Application:
    extra_format = " %(module)s-%(funcName)s:" if is_debug else ":"
    logging.basicConfig(level=logging.DEBUG if is_debug else logging.INFO,
                        format=f"%(asctime)s %(levelname)s{
                            extra_format} %(message)s",
                        datefmt="%d-%m-%Y %H:%M:%S"
                        )

    app = web.Application(logger=logging.getLogger())

    app.router.add_get("/start", start)
    app.router.add_post("/next_move", next_move)
    app.router.add_post("/end_game", end_game)

    return app


def main() -> None:
    port = int(os.environ[ENV_PORT]) \
        if ENV_PORT in os.environ \
        else DEFAULT_PORT
    is_debug = ENV_MODE not in os.environ or os.environ[ENV_MODE] == "debug"

    app = setup_web_server(is_debug=is_debug)

    host = "0.0.0.0"
    app.logger.info("Starting bot on %s", f"{host}:{port}")
    web.run_app(app, host=host, port=port)


if __name__ == "__main__":
    main()
