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

# Install ROS 2, MoveIt, build tools, and development/compilation dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-${ROS_DISTRO}-desktop \
    ros-${ROS_DISTRO}-moveit \
    ros-${ROS_DISTRO}-ur \
    ros-${ROS_DISTRO}-diagnostic-updater \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    python3-pip \
    git \
    build-essential \
    sudo \
    libssl-dev \
    libusb-1.0-0-dev \
    pkg-config \
    libgtk-3-dev \
    libglfw3-dev \
    libglu1-mesa-dev \
    freeglut3-dev \
    nodejs \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

# Initialize rosdep (run as root)
RUN rosdep init

# Clone, build, and install librealsense v2.54.2 with RSUSB (libusb) backend
# (This allows L515 support and bypasses host kernel/udev restrictions inside Docker)
RUN git clone --depth 1 -b v2.54.2 https://github.com/IntelRealSense/librealsense.git /tmp/librealsense \
    && cd /tmp/librealsense \
    && mkdir build && cd build \
    && cmake .. \
       -DCMAKE_BUILD_TYPE=Release \
       -DFORCE_RSUSB_BACKEND=false \
       -DBUILD_WITH_CUDA=false \
    && make -j$(nproc) \
    && make install \
    && rm -rf /tmp/librealsense

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

# Clone the realsense-ros wrapper v4.54.1 (matching librealsense v2.54.2 for L515 support)
# and build the colcon workspace
RUN mkdir -p /home/ros/ws/src && \
    git clone --depth 1 -b 4.54.1 https://github.com/IntelRealSense/realsense-ros.git /home/ros/ws/src/realsense-ros && \
    cd /home/ros/ws && \
    . /opt/ros/${ROS_DISTRO}/setup.sh && \
    colcon build --symlink-install


RUN pip install sounddevice requests dynamixel-sdk ur_rtde piper-tts

# Copy functions.sh and configure auto-sourcing in .bashrc
COPY --chown=ros:ros ros2_interface/functions.sh /home/ros/.functions.sh
RUN echo "source /home/ros/.functions.sh" >> /home/ros/.bashrc

# Download Piper voice models (both .onnx and .onnx.json) to the ros user's home directory
RUN curl -L https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx -o /home/ros/es_ES-davefx-medium.onnx \
    && curl -L https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json -o /home/ros/es_ES-davefx-medium.onnx.json \
    && curl -L https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/high/en_US-lessac-high.onnx -o /home/ros/en_US-lessac-high.onnx \
    && curl -L https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/high/en_US-lessac-high.onnx.json -o /home/ros/en_US-lessac-high.onnx.json

# Default entry point
CMD ["/bin/bash"]
