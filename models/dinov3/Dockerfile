FROM pytorch/pytorch:2.4.1-cuda12.1-cudnn9-devel

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

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

# Clone DINOv3 repository and install dependencies
RUN git clone --depth 1 https://github.com/facebookresearch/dinov3.git /home/${USERNAME}/app/dinov3 && \
    cd /home/${USERNAME}/app/dinov3 && \
    pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH="/home/${USERNAME}/app/dinov3:${PYTHONPATH}"

ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"
RUN pip install --no-cache-dir fastapi uvicorn pydantic python-multipart opencv-python-headless torchvision

RUN mkdir -p /home/${USERNAME}/app/weights

COPY --chown=${USERNAME}:${GID} se_models/ /home/${USERNAME}/app/se_models/
COPY --chown=${USERNAME}:${GID} models/dinov3/api.py /home/${USERNAME}/app/api.py

EXPOSE 8080
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
