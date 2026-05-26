#!/bin/bash
# Get the root directory of the repository
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WEIGHTS_DIR="${ROOT_DIR}/weights"

mkdir -p "${WEIGHTS_DIR}"
echo "Downloading SAM2 weights and config to ${WEIGHTS_DIR}..."

wget -O "${WEIGHTS_DIR}/sam2.1_hiera_large.pt" -q --show-progress https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt
wget -O "${WEIGHTS_DIR}/sam2.1_hiera_l.yaml" -q --show-progress https://raw.githubusercontent.com/facebookresearch/sam2/refs/heads/main/sam2/configs/sam2.1/sam2.1_hiera_l.yaml

echo "SAM2 weights downloaded."
