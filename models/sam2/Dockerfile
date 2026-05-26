ARG BASE_IMAGE=nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04
FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
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

# Copy uv for fast dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ARG CPU_ONLY=0
ARG USERNAME=user
ARG UID=1000
ARG GID=1000

# Create user with bash shell
RUN groupadd -g ${GID} -o ${USERNAME} && \
    useradd -m -u ${UID} -g ${GID} -o -s /bin/bash ${USERNAME}

USER ${USERNAME}
WORKDIR /home/${USERNAME}/app

# Create virtual environment and activate it by adding to PATH
RUN uv venv /home/${USERNAME}/venv
ENV PATH="/home/${USERNAME}/venv/bin:/usr/local/cuda/bin:${PATH}"
ENV PYTHONPATH="/home/${USERNAME}/app:${PYTHONPATH}"

# Install python dependencies based on CPU_ONLY argument using uv
RUN if [ "$CPU_ONLY" = "1" ] ; then \
        uv pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu ; \
    else \
        uv pip install --no-cache-dir torch torchvision torchaudio ; \
    fi && \
    uv pip install --no-cache-dir "setuptools<82" wheel

# Clone SAM2 and install using uv
ENV CUDA_HOME=/usr/local/cuda
RUN git clone --depth 1 https://github.com/facebookresearch/segment-anything-2.git && \
    cd segment-anything-2 && \
    uv pip install --no-cache-dir --no-build-isolation .

# Install FastAPI and other reqs using uv
RUN uv pip install --no-cache-dir fastapi uvicorn pydantic python-multipart opencv-python-headless

# Create empty weights directory as placeholder/mountpoint
RUN mkdir -p /home/${USERNAME}/app/weights

# Copy source/types and server code
COPY --chown=${USERNAME}:${GID} src/ /home/${USERNAME}/app/src/
COPY --chown=${USERNAME}:${GID} models/sam2/api.py /home/${USERNAME}/app/api.py

EXPOSE 8080
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
