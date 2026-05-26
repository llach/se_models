import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import json
import base64
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

from se_models.sam2_client import Sam2Client

# ==========================================
# PARAMETERS
# ==========================================
IMAGE_PATH = os.path.join(SCRIPT_DIR, "stack.png")
PORT = os.getenv("SAM2_PORT", "8001")
API_URL = f"http://localhost:{PORT}"
# Empty list means run automatic mask generation
BBOXES = [] 
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

    print(f"Initializing SAM2 client at {API_URL}...")
    try:
        client = Sam2Client(API_URL)
    except Exception as e:
        print(f"Failed to initialize client: {e}")
        print("Ensure that the SAM2 server is running.")
        sys.exit(1)

    print(f"Sending request via Sam2Client (with {len(BBOXES)} bounding boxes)...")
    
    start_time = time.time()
    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()
        
    try:
        response = client.predict(
            image_bytes=image_bytes,
            bboxes_json=json.dumps(BBOXES)
        )
    except Exception as e:
        print(f"Prediction failed: {e}")
        sys.exit(1)
        
    end_time = time.time()
    print(f"Model prediction took {end_time - start_time:.3f} seconds.")

    segmentations = response.results
    print(f"Found {len(segmentations)} segmentations.")

    # Visualization
    img = cv2.imread(IMAGE_PATH)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Plot original
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    axes[0].imshow(img)
    axes[0].set_title("Original Image")
    axes[0].axis("off")

    # Plot masks overlay
    overlay = img.copy()
    for seg in segmentations:
        conf = seg.confidence
        mask_b64 = seg.mask_base64
        
        # Decode base64 PNG mask
        mask_bytes = base64.b64decode(mask_b64)
        mask_arr = np.frombuffer(mask_bytes, dtype=np.uint8)
        mask_img = cv2.imdecode(mask_arr, cv2.IMREAD_GRAYSCALE)
        
        # Colorize mask with random color
        color = np.random.randint(0, 255, size=(3,), dtype=np.uint8)
        bool_mask = mask_img > 128
        
        # Blend overlay
        alpha = 0.5
        overlay[bool_mask] = overlay[bool_mask] * (1 - alpha) + color * alpha

    axes[1].imshow(overlay)
    axes[1].set_title(f"SAM2 Output ({len(segmentations)} masks)")
    axes[1].axis("off")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
