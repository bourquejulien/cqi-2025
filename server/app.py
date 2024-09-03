from gevent import monkey
monkey.patch_all()

import os
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
# Patch before importing anything else

print(f'Server initialization started, network mode : {os.environ.get('NETWORK', 'Not defined')}')

# Flask application
APP = Flask(__name__)
# In order to accept external requests
CORS(APP)
APP.config['SECRET_KEY'] = 'dev'

# Socketio instance to communicate with frontend

SOCKETIO = SocketIO(APP,
                    async_mode='gevent',
                    cors_allowed_origins='*',
                    logger=False)

players = set([])

@APP.route('/')
def test():
    return 'Server is running !'

@SOCKETIO.on('disconnect', namespace='/leaveGame')
def disconnect():
    print('A player disconnected from the server')
    id = request.sid
    
    if id in players:
        players.remove(id)

    return ''


@SOCKETIO.on('connect', namespace='/newGame')
def mission_connect():
    id = request.sid

    print(f'A new player connected to the server : {id}')
    players.add(id)
    
    return ''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f'Server is starting on port {port}')
    SOCKETIO.run(APP, debug=False, host='0.0.0.0', port=port, log_output=True)

