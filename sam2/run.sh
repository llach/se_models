#!/bin/bash

REPOSITORY_NAME="$(basename "$(dirname -- "$( readlink -f -- "$0"; )")")"

RUNTIME_ARG="--runtime=nvidia"
NETWORK_ARGS="--net=host --ipc=host"
if [ "$(uname -s)" = "Darwin" ] || [ "$1" = "macos" ]; then
    echo "Running for macOS (CPU only)"
    RUNTIME_ARG=""
    NETWORK_ARGS=""
fi

# here you can append container creation arguments, such as volume creation etc.
DOCKER_ARGS="
--env=DISPLAY=$DISPLAY \
${RUNTIME_ARG} \
--mount source=$HOME/shared,target=/shared,type=bind \
--volume=/dev/shm:/dev/shm \
-p 8001:8001 \
"

# container neither running nor stopped? → create
if [[ -z "$(docker ps -a -q -f name=${REPOSITORY_NAME})" ]];
then
  echo "creating container"
  docker create --name ${REPOSITORY_NAME} \
                ${NETWORK_ARGS} \
                --hostname="$(hostname)" \
                --privileged  \
                ${DOCKER_ARGS} \
                ${REPOSITORY_NAME}
fi

# container not running? → start
if [[ -z  "$(docker ps -q -f name=${REPOSITORY_NAME})" ]];
then
  echo "starting container in background"
  docker container start $REPOSITORY_NAME
else
  echo "container is already running"
fi
