#!/bin/bash
# Get the root directory of the repository
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WEIGHTS_DIR="${ROOT_DIR}/weights"

mkdir -p "${WEIGHTS_DIR}"
echo "Downloading DINOv3 weights to ${WEIGHTS_DIR}..."

wget -O "${WEIGHTS_DIR}/dinov3_vitl16_pretrain_lvd1689m-8aa4cbdd.pth" -q --show-progress https://huggingface.co/jaychempan/dinov3/resolve/main/dinov3_vitl16_pretrain_lvd1689m-8aa4cbdd.pth

echo "DINOv3 weights downloaded."
