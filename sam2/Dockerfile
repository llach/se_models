ARG BASE_IMAGE=nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04
FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    sudo \
    zsh \
    python3 \
    python3-pip \
    python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

ARG MACOS=0
ARG USERNAME=user
ARG UID=1000
ARG GID=1000

# Create user
RUN groupadd -g ${GID} -o ${USERNAME} && \
    useradd -m -u ${UID} -g ${GID} -o -s /bin/zsh ${USERNAME} && \
    usermod -aG sudo ${USERNAME} && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER ${USERNAME}
WORKDIR /home/${USERNAME}/app

ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

# Install python dependencies based on MACOS argument
RUN if [ "$MACOS" = "1" ] ; then \
    pip3 install --user --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu ; \
    else \
    pip3 install --user --no-cache-dir torch torchvision torchaudio ; \
    fi

# Clone SAM2
ENV CUDA_HOME=/usr/local/cuda
RUN git clone https://github.com/facebookresearch/segment-anything-2.git && \
    cd segment-anything-2 && \
    pip3 install --user .

# Install FastAPI and other reqs
RUN pip3 install --user --no-cache-dir fastapi uvicorn pydantic python-multipart opencv-python-headless

# Download weights
RUN mkdir -p /home/${USERNAME}/app/weights && \
    cd /home/${USERNAME}/app/weights && \
    wget -q https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt && \
    wget -q https://raw.githubusercontent.com/facebookresearch/sam2/refs/heads/main/sam2/configs/sam2.1/sam2.1_hiera_l.yaml

# Copy server code
COPY --chown=${USERNAME}:${GID} api.py /home/${USERNAME}/app/api.py

EXPOSE 8001
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]
