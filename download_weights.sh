#!/bin/bash
# Root download weights orchestrator script
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting weights download..."
bash "${ROOT_DIR}/models/grounding_dino/download_weights.sh"
bash "${ROOT_DIR}/models/sam2/download_weights.sh"
bash "${ROOT_DIR}/models/dinov3/download_weights.sh"
echo "All weights downloaded successfully!"
