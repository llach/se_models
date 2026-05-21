#!/bin/bash

# Get the root directory of the repository (parent of parent of script)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

DOCKER_USER=user
DOCKER_GID=$(id -g)
DOCKER_UID=$(id -u)
ROS_DISTRO=humble

CPU_ONLY_ARG=""
BASE_IMAGE_ARG="--build-arg BASE_IMAGE=nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04"
if [ "$(uname -s)" = "Darwin" ] || [ "$1" = "macos" ] || [ "$1" = "cpu" ]; then
    echo "Building for CPU only"
    CPU_ONLY_ARG="--build-arg CPU_ONLY=1"
    BASE_IMAGE_ARG="--build-arg BASE_IMAGE=ubuntu:22.04"
fi

echo "======================="
echo " Building docker image "
echo " IMAGE_TAG:   grounding_dino"
echo " DOCKER_USER: ${DOCKER_USER}"
echo " DOCKER_GID:  ${DOCKER_GID}"
echo " DOCKER_UID:  ${DOCKER_UID}"

docker rm -f grounding_dino 2>/dev/null
docker build --build-arg USERNAME="${DOCKER_USER}"\
             --build-arg ROS_DISTRO=${ROS_DISTRO}\
             --build-arg GID=${DOCKER_GID}\
             --build-arg UID=${DOCKER_UID}\
             ${BASE_IMAGE_ARG} \
             ${CPU_ONLY_ARG} \
             -f "${ROOT_DIR}/models/grounding_dino/Dockerfile" \
             -t "grounding_dino" "${ROOT_DIR}"
