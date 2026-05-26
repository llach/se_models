import cv2
import numpy as np
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

from se_models.dinov3_client import Dinov3Client

IMAGE_PATH = os.path.join(SCRIPT_DIR, "stack.png")
PORT = os.getenv("DINOV3_PORT", "8002")
API_URL = f"http://localhost:{PORT}"

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

    print(f"Initializing DINOv3 client at {API_URL}...")
    try:
        client = Dinov3Client(API_URL)
    except Exception as e:
        print(f"Failed to initialize client: {e}")
        print("Ensure that the DINOv3 server is running.")
        sys.exit(1)

    print("Sending request via Dinov3Client...")
    start_time = time.time()
    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()
        
    try:
        response = client.get_embeddings(image_bytes)
    except Exception as e:
        print(f"Prediction failed: {e}")
        sys.exit(1)
        
    end_time = time.time()
    print(f"Model prediction took {end_time - start_time:.3f} seconds.")
    print(f"Success! Embedded features received.")
    print(f"Shape of features: {response.shape}")
    print(f"Patch resolution: h_patches={response.h_patches}, w_patches={response.w_patches}")
    print(f"Number of flattened values: {len(response.embeddings)}")
    
    # Simple validation: num_patches * dim == len(embeddings)
    expected_len = response.shape[0] * response.shape[1]
    if len(response.embeddings) == expected_len:
        print("Verification PASSED: Flattened length matches tensor dimensions!")
    else:
        print(f"Verification FAILED: Flattened length is {len(response.embeddings)}, but expected {expected_len}")

if __name__ == "__main__":
    main()
