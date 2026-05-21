import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import time

# Support importing from the project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Load .env variables if present to get local port mapping
if os.path.exists(os.path.join(ROOT_DIR, ".env")):
    with open(os.path.join(ROOT_DIR, ".env")) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val

from src.grounding_dino_client import GroundingDinoClient

# ==========================================
# PARAMETERS
# ==========================================
IMAGE_PATH = os.path.join(SCRIPT_DIR, "stack.png")
PROMPT = "clothing"
BOX_THRESHOLD = 0.35
TEXT_THRESHOLD = 0.25

PORT = os.getenv("GROUNDING_DINO_PORT", "8000")
API_URL = f"http://localhost:{PORT}"
# ==========================================

def create_dummy_image():
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(img, (100, 100), (300, 400), (0, 0, 255), -1)  # Red rectangle
    cv2.circle(img, (500, 200), 50, (0, 255, 0), -1)             # Green circle
    cv2.imwrite(IMAGE_PATH, img)
    return img

def main():
    if not os.path.exists(IMAGE_PATH):
        print(f"Creating a dummy image at {IMAGE_PATH} since it doesn't exist.")
        create_dummy_image()

    print(f"Initializing GroundingDINO client at {API_URL}...")
    try:
        client = GroundingDinoClient(API_URL)
    except Exception as e:
        print(f"Failed to initialize client: {e}")
        print("Ensure that the GroundingDINO server is running.")
        sys.exit(1)

    print(f"Sending request via GroundingDinoClient...")
    start_time = time.time()
    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()
        
    try:
        response = client.predict(
            image_bytes=image_bytes,
            prompt=PROMPT,
            box_threshold=BOX_THRESHOLD,
            text_threshold=TEXT_THRESHOLD
        )
    except Exception as e:
        print(f"Prediction failed: {e}")
        sys.exit(1)
        
    end_time = time.time()
    print(f"Model prediction took {end_time - start_time:.3f} seconds.")

    detections = response.detections
    print(f"Found {len(detections)} detections.")

    # Visualization
    img = cv2.imread(IMAGE_PATH)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    for det in detections:
        bbox = det.bbox
        label = det.label
        conf = det.confidence

        x_min = int(bbox.x_min)
        y_min = int(bbox.y_min)
        x_max = int(bbox.x_max)
        y_max = int(bbox.y_max)

        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
        
        # Put text inside the box (downwards) to avoid cutoff, with a black outline for readability
        text = f"{label} {conf:.2f}"
        text_y = y_min + 20 if y_min + 20 < y_max else y_min - 10
        cv2.putText(img, text, (x_min + 5, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
        cv2.putText(img, text, (x_min + 5, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    plt.figure(figsize=(10, 8))
    plt.imshow(img)
    plt.title("GroundingDINO Output")
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    main()
