#!/bin/bash
# Get the root directory of the repository
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WEIGHTS_DIR="${ROOT_DIR}/weights"

mkdir -p "${WEIGHTS_DIR}"
echo "Downloading Grounding DINO weights and config to ${WEIGHTS_DIR}..."

wget -O "${WEIGHTS_DIR}/groundingdino_swint_ogc.pth" -q --show-progress https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth
wget -O "${WEIGHTS_DIR}/GroundingDINO_SwinT_OGC.py" -q --show-progress https://raw.githubusercontent.com/IDEA-Research/GroundingDINO/main/groundingdino/config/GroundingDINO_SwinT_OGC.py

echo "Grounding DINO weights downloaded."
