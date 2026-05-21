#!/bin/bash

REPOSITORY_NAME="$(basename "$(dirname -- "$( readlink -f -- "$0"; )")")"

DOCKER_USER=user
DOCKER_GID=$(id -g)
DOCKER_UID=$(id -u)
ROS_DISTRO=humble

MACOS_ARG=""
BASE_IMAGE_ARG="--build-arg BASE_IMAGE=nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04"
if [ "$(uname -s)" = "Darwin" ] || [ "$1" = "macos" ]; then
    echo "Building for macOS (CPU only)"
    MACOS_ARG="--build-arg MACOS=1"
    BASE_IMAGE_ARG="--build-arg BASE_IMAGE=ubuntu:22.04"
fi

echo "======================="
echo " Building docker image "
echo " IMAGE_TAG:   ${REPOSITORY_NAME}"
echo " DOCKER_USER: ${DOCKER_USER}"
echo " DOCKER_GID:  ${DOCKER_GID}"
echo " DOCKER_UID:  ${DOCKER_UID}"

docker rm -f $REPOSITORY_NAME
docker build ${DOCKER_FILE_PATH} --build-arg USERNAME="${DOCKER_USER}"\
                                 --build-arg ROS_DISTRO=${ROS_DISTRO}\
                                 --build-arg GID=${DOCKER_GID}\
                                 --build-arg UID=${DOCKER_UID}\
                                 ${BASE_IMAGE_ARG} \
                                 ${MACOS_ARG} \
                                 -f Dockerfile \
                                 -t "${REPOSITORY_NAME}" .
