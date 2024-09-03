import socketio
import time
import os

print('Client launched')

# # Initialize the Socket.IO client
sio = socketio.Client()

# # Server IP and port
network_mode = os.environ.get('NETWORK', 'local')
print(f'Network mode : {network_mode}')
if network_mode == 'host':
    SERVER_IP = 'localhost' # Replace with your server's IP address
else:
    SERVER_IP = os.environ.get('ADDRESS', 'ERROR').replace('"', '') # Replace with your server's IP address

SERVER_PORT = 5001

# # Full server URL
SERVER_URL = f'http://{SERVER_IP}:{SERVER_PORT}'

@sio.event(namespace='/newGame')
def connect():
    print('Connected to newGame namespace')

@sio.event
def connect_error(data):
    print('Connection failed!')

@sio.event
def disconnect():
    print('Disconnected from the server')

def join_game():
    try:
        sio.connect(SERVER_URL + '/newGame', namespaces=['/newGame'])
        print(f'Connected to /newGame namespace 2 ')
    except socketio.exceptions.ConnectionError as e:
        print(f'Failed to connect to /newGame namespace: {str(e)}')


def main():
    try:
        print(f'Connecting to {SERVER_URL}')
        # Connect to the server
        sio.connect(SERVER_URL)
        
        # time.sleep(1)

        # join_game()

        # Keep the client running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Client is shutting down...")
    finally:
        # Disconnect from the server
        if sio.connected:
            sio.disconnect()

if __name__ == '__main__':
    main()
