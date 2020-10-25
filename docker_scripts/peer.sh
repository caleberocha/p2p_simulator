#!/bin/bash

cd $(dirname $0)/..
NAME=peer-$RANDOM$RANDOM
docker build -f Dockerfile_peer --rm -t p2p_simulator_peer .
docker run --network p2p --name $NAME -it p2p_simulator_peer python -m peer
docker container rm $NAME
