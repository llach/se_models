FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

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

ARG USERNAME=user
ARG UID=1000
ARG GID=1000

# Create user with bash shell
RUN groupadd -g ${GID} -o ${USERNAME} && \
    useradd -m -u ${UID} -g ${GID} -o -s /bin/bash ${USERNAME}

USER ${USERNAME}
WORKDIR /home/${USERNAME}/app

# Clone SAM2 and install
ENV CUDA_HOME=/usr/local/cuda
RUN git clone --depth 1 https://github.com/facebookresearch/segment-anything-2.git && \
    cd segment-anything-2 && \
    pip install --no-cache-dir --no-build-isolation .

# Install FastAPI and other reqs 
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"
RUN pip install --no-cache-dir fastapi uvicorn pydantic python-multipart opencv-python-headless

# Create empty weights directory as placeholder/mountpoint
RUN mkdir -p /home/${USERNAME}/app/weights

# Copy source/types and server code
COPY --chown=${USERNAME}:${GID} src/ /home/${USERNAME}/app/src/
COPY --chown=${USERNAME}:${GID} models/sam2/api.py /home/${USERNAME}/app/api.py

EXPOSE 8080
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
