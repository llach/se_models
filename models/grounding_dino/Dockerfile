FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-devel
ARG DEBIAN_FRONTEND=noninteractive

# Architecture support and compiler configs
ENV TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0 7.5 8.0 8.6+PTX" \
    SETUPTOOLS_USE_DISTUTILS=stdlib

# Install only necessary system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
         git \
         libgl1-mesa-glx \
         libglib2.0-0 \
         ca-certificates && \
    rm -rf /var/lib/apt/lists/*

ARG USERNAME=user
ARG UID=1000
ARG GID=1000

# Create user matching host UID/GID for correct file sharing
RUN groupadd -g ${GID} -o ${USERNAME} && \
    useradd -m -u ${UID} -g ${GID} -o -s /bin/bash ${USERNAME}

USER ${USERNAME}
WORKDIR /home/${USERNAME}/app
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"
ENV LD_LIBRARY_PATH=/opt/conda/lib/python3.10/site-packages/torch/lib:$LD_LIBRARY_PATH

# Clone with depth=1 to save space
RUN git clone --depth 1 https://github.com/IDEA-Research/GroundingDINO.git

# Install packages (using opencv-python-headless to keep image lean)
RUN python -m pip install --no-cache-dir "numpy<2" "transformers==4.38.2" "opencv-python-headless<4.10" fastapi uvicorn pydantic python-multipart

# Compile and install Grounding DINO using the pre-installed CUDA toolkit compiler (nvcc)
RUN cd GroundingDINO && python -m pip install --no-cache-dir .

# Force downgrade numpy to <2 to override any upgrades during the Grounding DINO install
RUN python -m pip install --no-cache-dir "numpy<2"

# Verify C extensions compiled correctly
RUN python -c "import groundingdino._C"

RUN mkdir -p /home/${USERNAME}/app/weights

# Copy code
COPY --chown=${USERNAME}:${GID} src/ /home/${USERNAME}/app/src/
COPY --chown=${USERNAME}:${GID} models/grounding_dino/api.py /home/${USERNAME}/app/api.py

EXPOSE 8080
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]