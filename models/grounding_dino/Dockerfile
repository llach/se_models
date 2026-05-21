# Use a build argument to switch between GPU and CPU base images
ARG BASE_IMAGE=nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04
FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install minimal system dependencies required for building and running GroundingDINO
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3 \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy uv from the official image for fast dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ARG CPU_ONLY=0
ARG USERNAME=user
ARG UID=1000
ARG GID=1000

# Create a non-root user with bash shell
RUN groupadd -g ${GID} -o ${USERNAME} && \
    useradd -m -u ${UID} -g ${GID} -o -s /bin/bash ${USERNAME}

USER ${USERNAME}
WORKDIR /home/${USERNAME}/app

# Create virtual environment and activate it by adding to PATH
RUN uv venv /home/${USERNAME}/venv
ENV PATH="/home/${USERNAME}/venv/bin:${PATH}"
ENV PYTHONPATH="/home/${USERNAME}/app:${PYTHONPATH}"

# Install PyTorch using uv based on CPU_ONLY argument
RUN if [ "$CPU_ONLY" = "1" ] ; then \
        uv pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu ; \
    else \
        uv pip install --no-cache-dir torch torchvision torchaudio ; \
    fi

# Clone and install GroundingDINO
ENV CUDA_HOME=/usr/local/cuda
RUN git clone --depth 1 https://github.com/IDEA-Research/GroundingDINO.git && \
    cd GroundingDINO && \
    if [ "$CPU_ONLY" = "1" ] ; then export GROUNDINGDINO_BUILD_CUDA=0 ; fi && \
    uv pip install --no-cache-dir -e .

# Install FastAPI and server dependencies using uv
RUN uv pip install --no-cache-dir fastapi uvicorn pydantic python-multipart opencv-python-headless "transformers<4.37.0"

# Copy source/types and server code
COPY --chown=${USERNAME}:${GID} src/ /home/${USERNAME}/app/src/
COPY --chown=${USERNAME}:${GID} models/grounding_dino/api.py /home/${USERNAME}/app/api.py

# Download weights
RUN mkdir -p /home/${USERNAME}/app/weights && \
    cd /home/${USERNAME}/app/weights && \
    wget -q https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth && \
    wget -q https://raw.githubusercontent.com/IDEA-Research/GroundingDINO/main/groundingdino/config/GroundingDINO_SwinT_OGC.py

EXPOSE 8080
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
