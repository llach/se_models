FROM ubuntu:22.04

# Prevent interactive prompts during installation
ARG DEBIAN_FRONTEND=noninteractive

# Set build argument for ROS distro (defaulting to humble)
ARG ROS_DISTRO=humble
ENV ROS_DISTRO=${ROS_DISTRO}

# Set up locales and UTF-8
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    && locale-gen en_US en_US.UTF-8 \
    && update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*
ENV LANG=en_US.UTF-8

# Setup timezone (non-interactively)
ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install setup keys and repositories for ROS 2
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    ca-certificates \
    && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null \
    && rm -rf /var/lib/apt/lists/*

# Install ROS 2, MoveIt, and development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-${ROS_DISTRO}-desktop \
    ros-${ROS_DISTRO}-moveit \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    python3-pip \
    git \
    build-essential \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Initialize rosdep (run as root)
RUN rosdep init

# Create the non-root 'ros' user with sudo privileges matching GID/UID
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} -o ros && \
    useradd -m -u ${UID} -g ${GID} -o -s /bin/bash ros && \
    echo "ros ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to the non-root user
USER ros
WORKDIR /home/ros/ws

# Initialize rosdep for the user
RUN rosdep update

# Create the colcon workspace under ~/ws and build it once to generate setup.bash
RUN mkdir -p /home/ros/ws/src && \
    cd /home/ros/ws && \
    . /opt/ros/${ROS_DISTRO}/setup.sh && \
    colcon build


# Copy functions.sh and configure auto-sourcing in .bashrc
COPY --chown=ros:ros ros2_interface/functions.sh /home/ros/.functions.sh
RUN echo "source /home/ros/.functions.sh" >> /home/ros/.bashrc

# Default entry point
CMD ["/bin/bash"]
