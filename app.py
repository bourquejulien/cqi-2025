#!/bin/env python3

from flask import Flask, Response, request
from flask_caching import Cache
import json
from game import Game
from player import Move
from piece import Piece
import random
import bot

cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
app: Flask = Flask(__name__)
cache.init_app(app)

@app.route("/health", methods=["GET"])
def get_health():
    return Response(
        response="ok", 
        status=200
    )

@app.route("/start_game", methods=["POST"])
def start_game():
    game: Game = None

    # Check if a game is already running
    if cache.has("game") and not cache.get("game").game_over:
        return Response(
            response="The game is already running", 
            status=400
        )

    # Create a new game
    game = Game()
       
    # Make the bots play
    game.play_turn(0, 0, Piece.Orientation.UP, random.randint(0, 20)) # Player 1
    game.next_turn()
    game.play_turn(15, 0, Piece.Orientation.UP, random.randint(0, 20)) # Player 2
    game.next_turn()
    game.play_turn(0, 17, Piece.Orientation.UP, random.randint(15, 20)) # Player 3
    game.next_turn()

    # Save the game in the cache
    cache.set("game", game)

    return Response(
        response= json.dumps({
            "color": "#FFFF00",
            "board": game.board.to_img_64().decode()
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
    move: Move = None
    try:
        move: Move = Move.from_request(**request.json)
        # TODO - Validate parameters
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
    game.play_move(move)
    game.next_turn()

    # Check if the game is over for the player
    if not game.real_player.playing:
        cache.set("game", game)
        return GameResponse(game, "Wrong move, game is over")
    
    # Check if the game is over
    if game.game_over:
        cache.set("game", game)
        return GameResponse(game, "Game is over, you lose")
    
    # Make the bots play
    # Player 1 is random
    x, y, orientation, piece_id = bot.random_play(game.players[0], game.board)
    game.play_turn(x, y, Piece.Orientation(orientation), piece_id)
    game.next_turn()

    # Player 2 is random
    x, y, orientation, piece_id = bot.random_play(game.players[1], game.board)
    game.play_turn(x, y, Piece.Orientation(orientation), piece_id)
    game.next_turn()

    # Player 3 is greedy
    x, y, orientation, piece_id = bot.greedy_play(game.players[2], game.board)
    game.play_turn(x, y, Piece.Orientation(orientation), piece_id)
    game.next_turn()
    
    cache.set("game", game)
    return GameResponse(game, "Valid move")

@app.route("/end_game", methods=["POST"])
def end_game():
    game: Game = None

    # Check if a game is already running
    try:
        game = cache.get("game")
        cache.delete("game")
        if game.game_over:
            return Response(
                response="The game is already over", 
                status=400
            )
        
        return GameResponse(game, "Game ended manually")
    except:
        return Response(
            response="No game is running", 
            status=400
        )

def GameResponse(game: Game, message: str = ""):
        return Response(
            response= json.dumps({
                "game_over": game.game_over,
                "score": game.real_player.score,
                "message": message,
                "board": game.board.to_img_64().decode()
            }),
            status=200,
            headers={
                "Content-Type": "application/json"
            }
        )

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
