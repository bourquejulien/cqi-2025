#!/bin/env python3

import logging
import random
import json

from flask import Flask, Response, request
from flask_caching import Cache

import src.bot as bot
from src.game import Game
from src.player import Move

cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
app: Flask = Flask(__name__)
cache.init_app(app)

def GameResponse(game: Game, message: str = ""):
        response = {
            "game_over": game.game_over,
            "score": game.real_player.score,
            "message": message,
        }
        app.logger.info("%s", response)

        response["board"] = game.to_img_64().decode()
        return Response(
            response= json.dumps(response),
            status=200,
            headers={
                "Content-Type": "application/json"
            }
        )

@app.route("/status", methods=["GET"])
def get_status():
    if not cache.has("game"):
        return Response(
            response="No game available",
            status=400
        )
    
    return GameResponse(cache.get("game"))

@app.route("/start_game", methods=["POST"])
def start_game():
    # Check if a game is already running
    if cache.has("game") and not cache.get("game").game_over:
        return Response(
            response="The game is already running", 
            status=400
        )

    # Create a new game
    player_idx = random.randint(0, 3)
    game = Game(player_idx)
       
    for _ in range(player_idx):
        move = bot.bot_play(game.current_player, game.board)
        game.play_move(move)

    # Save the game in the cache
    cache.set("game", game)

    app.logger.info("Game started, player id: %d, color: %s", game.real_player.id, game.real_player.color)
    return Response(
        response= json.dumps({
            "color": game.real_player.color,
            "board": game.to_img_64().decode(),
            "pieces": game.real_player.get_pieces_summary()
        }),
        status=200,
        headers={
            "Content-Type": "application/json"
        }
    )

@app.route("/send_move", methods=["POST"])
def move():
    if request.headers["Content-Type"] != "application/json":
        return Response(
            response="Content-Type must be application/json", 
            status=400
        )
    
    # Get the parameters
    move: Move | None = None
    try:
        move: Move = Move.from_request(**request.json)
    except:
        return Response(
            response="Invalid parameters", 
            status=400
        )

    # Check if a game exists
    if not cache.has("game"):
        return Response(
            response="The game is not running",
            status=400
        )
    
    # Check if the game is over
    if cache.get("game").game_over:
        return Response(
            response="The game is over",
            status=400
        )

    game: Game = cache.get("game")

    # Play the move for the player
    app.logger.info("Bot played: %s", move)
    game.play_move(move)

    # Check if the game is over
    if game.game_over:
        cache.set("game", game)
        return GameResponse(game, "You lost, game is over" if game.real_player.playing else "Wrong move, game is over")

    # Make the bots play
    for _ in range(len(game.players) - 1):
        move = bot.bot_play(game.current_player, game.board)
        game.play_move(move)

    if game.game_over:
        cache.set("game", game)
        return GameResponse(game, "You won, other player are unable to play.")
    
    cache.set("game", game)
    return GameResponse(game, "Valid move")

@app.route("/end_game", methods=["POST"])
def end_game():
    # Check if a game is already ended
    if not cache.has("game") or cache.get("game").game_over:
        return Response(
            response="No game currently running", 
            status=400
        )
    
    game: Game = cache.get("game")
    game.force_end_game()
    cache.set("game", game)

    return GameResponse(game, "Game ended manually")

def start_gunicorn():
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    return app

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
