FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime
ARG DEBIAN_FRONTEND=noninteractive

ENV CUDA_HOME=/usr/local/cuda \
    TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0 7.5 8.0 8.6+PTX" \
    SETUPTOOLS_USE_DISTUTILS=stdlib \
    PATH=/usr/local/cuda/bin:$PATH

# Combine system dependencies, install Libmamba solver, install CUDA, and clean caches in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
         wget \
         build-essential \
         git \
         python3-opencv \
         ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    conda \
        config --set solver libmamba && \
    conda \
        install -y -c "nvidia/label/cuda-12.1.1" cuda && \
    conda \
        clean -afy

ARG USERNAME=user
ARG UID=1000
ARG GID=1000

# Create user with bash shell
RUN groupadd -g ${GID} -o ${USERNAME} && \
    useradd -m -u ${UID} -g ${GID} -o -s /bin/bash ${USERNAME}

USER ${USERNAME}
WORKDIR /home/${USERNAME}/app
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

# Clone repository in a separate layer to leverage caching if dependencies change
ENV LD_LIBRARY_PATH=/opt/conda/lib/python3.10/site-packages/torch/lib:$LD_LIBRARY_PATH
RUN git clone https://github.com/IDEA-Research/GroundingDINO.git

# Set CUDA path relative to active Conda env for library compilation
ENV CUDA_HOME=$CONDA_PREFIX

RUN python -m pip install --no-cache-dir "numpy<2" "transformers==4.38.2" fastapi uvicorn pydantic python-multipart

RUN cd GroundingDINO && python -m pip install --no-cache-dir .

RUN python -c "import groundingdino._C"

# Create empty weights directory as placeholder/mountpoint
RUN mkdir -p /home/${USERNAME}/app/weights

# Copy source/types and server code
COPY --chown=${USERNAME}:${GID} src/ /home/${USERNAME}/app/src/
COPY --chown=${USERNAME}:${GID} models/grounding_dino/api.py /home/${USERNAME}/app/api.py

EXPOSE 8080
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]