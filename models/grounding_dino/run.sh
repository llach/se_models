#!/bin/bash

RUNTIME_ARG="--runtime=nvidia"
NETWORK_ARGS="--net=host --ipc=host"
if [ "$(uname -s)" = "Darwin" ] || [ "$1" = "macos" ]; then
    echo "Running for macOS (CPU only)"
    RUNTIME_ARG=""
    NETWORK_ARGS=""
fi

# Load .env variables if present
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "${SCRIPT_DIR}/../../.env" ]; then
    export $(grep -v '^#' "${SCRIPT_DIR}/../../.env" | xargs)
fi

PORT="${GROUNDING_DINO_PORT:-8000}"

# here you can append container creation arguments, such as volume creation etc.
DOCKER_ARGS="
--env=DISPLAY=$DISPLAY \
${RUNTIME_ARG} \
--mount source=$HOME/shared,target=/shared,type=bind \
--volume=${SCRIPT_DIR}/../../weights:/home/user/app/weights \
--volume=/dev/shm:/dev/shm \
-p ${PORT}:8080 \
"

# container neither running nor stopped? → create
if [[ -z "$(docker ps -a -q -f name=grounding_dino)" ]];
then
  echo "creating container"
  docker create -i -t --name grounding_dino \
                ${NETWORK_ARGS} \
                --hostname="$(hostname)" \
                --privileged  \
                ${DOCKER_ARGS} \
                grounding_dino
fi

# container not running? → start
if [[ -z  "$(docker ps -q -f name=grounding_dino)" ]];
then
  echo "starting container in background"
  docker container start grounding_dino
else
  echo "container is already running"
fi
