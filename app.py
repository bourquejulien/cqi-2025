from flask import Flask, Response, request, session
from flask_caching import Cache
import json
from game import Game
from piece import Piece
import base64
from dataclasses import dataclass

# Setup Flask
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
app: Flask = Flask(__name__)
cache.init_app(app)

@dataclass
class Move:
    x: int
    y: int
    orientation: int
    peice_id: int

@app.route('/end_game', methods=["GET"])
def end_game():
    game: Game = None

    # Check if a game is already running
    try:
        game = cache.get('game')
        if game.game_over:
            return Response(
                response="The game is already over", 
                status=400
            )
        
        cache.delete('game')
        return Response(
            response=json.dumps({
                "message": "The game was ended",
                "score": game.players[game.real_player_id].score
            })
        )
    except:
        return Response(
            response="No game is running", 
            status=200
        )

@app.route('/start_game', methods=["GET"])
def start_game():
    game: Game = None

    # Check if a game is already running
    try:
        game = cache.get('game')
        if not game.game_over:
            return Response(
                response="The game is already running", 
                status=400
            )
    except:
        # Create a new game
        game = Game()
       
    # Make the bots play
    game.play_turn(0, 0, Piece.Orientation.UP, 5) # Player 1
    game.setup_turn()
    game.play_turn(17, 0, Piece.Orientation.UP, 19) # Player 2
    game.setup_turn()
    game.play_turn(0, 16, Piece.Orientation.DOWN, 10) # Player 3

    # Save the game in the cache
    cache.set('game', game)

    return Response(
        response= json.dumps({
            "color": "yellow",
            "board": game.board.to_img_64().decode()
        }),
        status=200,
        headers={
            "Content-Type": "application/json"
        }
    )

@app.route('/send_move', methods=["POST"])
def move():
    game: Game = None

    try:
        game = cache.get('game')
        if game.game_over:
            return Response(
                response="The game is over", 
                status=400
            )
    except:
        return Response(
            response="The game is not running", 
            status=400
        )

    if request.headers['Content-Type'] != 'application/json':
        return Response(
            response="Content-Type must be application/json", 
            status=400
        )

    # Get the parameters
    move: Move = None
    try:
        move: Move = Move(**request.json)
        # TODO - Validate parameters
    except:
        return Response(
            response="Invalid parameters", 
            status=400
        )

    # Play the move for the player
    game.setup_turn()
    game.play_turn(move.x, move.y, Piece.Orientation(move.orientation), move.peice_id)
    player_score = game.players[game.player_playing].score

    # Check if the game is over for the player
    if not game.players[game.player_playing].playing:
        cache.set('game', game)
        return Response(
                response= json.dumps({
                    "game_over": True,
                    "score": player_score,
                    "board": game.board.to_img_64().decode()
                }),
            status=200,
            headers={
                "Content-Type": "application/json"
            }
        )
    
    # Setup the next turn
    game.setup_turn()

    # Check if the game is over
    if game.game_over:
        cache.set('game', game)
        return Response(
                response= json.dumps({
                    "game_over": True,
                    "score": player_score,
                    "board": game.board.to_img_64().decode()
                }),
            status=200,
            headers={
                "Content-Type": "application/json"
            }
        )

    # TODO - Make the bots play
    # Make the bots play
    game.play_turn(3, 2, Piece.Orientation.UP, 2) # Player 1
    game.setup_turn()
    game.play_turn(15, 1, Piece.Orientation.UP, 5) # Player 2
    game.setup_turn()
    game.play_turn(17, 4, Piece.Orientation.UP, 10) # Player 3
    
    cache.set('game', game)
    return Response(
        response= json.dumps({
            "game_over": False,
            "score": player_score,
            "board": game.board.to_img_64().decode()
        }),
        status=200,
        headers={
            "Content-Type": "application/json"
        }
    )

if __name__ == "__main__":
    app.run(debug=True)