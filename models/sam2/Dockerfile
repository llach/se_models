FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-devel

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install only necessary build/runtime utilities (removed redundant python3 system packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    build-essential \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

ARG USERNAME=user
ARG UID=1000
ARG GID=1000

# Create user matching host UID/GID for correct file sharing
RUN groupadd -g ${GID} -o ${USERNAME} && \
    useradd -m -u ${UID} -g ${GID} -o -s /bin/bash ${USERNAME}

USER ${USERNAME}
WORKDIR /home/${USERNAME}/app

# Clone and compile SAM2 with custom CUDA operators (now compiles correctly since nvcc is present)
RUN git clone --depth 1 https://github.com/facebookresearch/segment-anything-2.git && \
    cd segment-anything-2 && \
    pip install --no-cache-dir --no-build-isolation .

ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"
RUN pip install --no-cache-dir fastapi uvicorn pydantic python-multipart opencv-python-headless

RUN mkdir -p /home/${USERNAME}/app/weights

COPY --chown=${USERNAME}:${GID} src/ /home/${USERNAME}/app/src/
COPY --chown=${USERNAME}:${GID} models/sam2/api.py /home/${USERNAME}/app/api.py

EXPOSE 8080
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
