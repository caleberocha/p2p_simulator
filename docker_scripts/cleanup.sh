#!/bin/bash

docker network rm p2p
docker container rm $(docker container ls -a -f "ancestor=p2p_simulator_server" -q)
docker container rm $(docker container ls -a -f "ancestor=p2p_simulator_peer" -q)
docker rmi -f $(docker images p2p_simulator_* -q)
