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

# Add path and pythonpath
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"
ENV PYTHONPATH="/home/${USERNAME}/app:${PYTHONPATH}"

# Install python dependencies based on MACOS argument
RUN if [ "$MACOS" = "1" ] ; then \
        pip3 install --user --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu ; \
    else \
        pip3 install --user --no-cache-dir torch torchvision torchaudio ; \
    fi

# Clone GroundingDINO
ENV CUDA_HOME=/usr/local/cuda
RUN git clone https://github.com/IDEA-Research/GroundingDINO.git && \
    cd GroundingDINO && \
    if [ "$MACOS" = "1" ] ; then export GROUNDINGDINO_BUILD_CUDA=0 ; fi && \
    pip3 install --user -e .

# Install FastAPI and other reqs (force older transformers to avoid BertModel get_head_mask error)
RUN pip3 install --user --no-cache-dir fastapi uvicorn pydantic python-multipart opencv-python-headless "transformers<4.37.0"

# Copy source/types and server code (build context is root)
COPY --chown=${USERNAME}:${GID} src/ /home/${USERNAME}/app/src/
COPY --chown=${USERNAME}:${GID} models/grounding_dino/api.py /home/${USERNAME}/app/api.py

# Download weights
RUN mkdir -p /home/${USERNAME}/app/weights && \
    cd /home/${USERNAME}/app/weights && \
    wget -q https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth && \
    wget -q https://raw.githubusercontent.com/IDEA-Research/GroundingDINO/main/groundingdino/config/GroundingDINO_SwinT_OGC.py

EXPOSE 8080
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
