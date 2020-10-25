#!/bin/bash

cd $(dirname $0)/..
docker build -f Dockerfile_server --rm -t p2p_simulator_server .
docker network create --driver bridge p2p
docker run --network p2p --name p2pserver -it p2p_simulator_server python -m server
docker container rm p2pserver
docker network rm p2p
