# CQI 2024 - Prog

# Requirements
- docker
- linux/mac

# Server

- To start the server in network mode (will be accessible across all devices in the same network) : `./server.sh`

- To start the server in local mode (will only be accessible across docker containers in same device) : `./server.sh local` 


# Client

- To start the client in network mode : 
  - `./client.sh network <IP ADDRESS of server>`

- To start the client in local mode (will look for the server in localhost:5001) : `./client.sh local` 



# TODO

- Windows version
