import requests
import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import json
import base64
import time

# ==========================================
# PARAMETERS
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(SCRIPT_DIR, "stack.png")  # Provide a valid path to an image
API_URL = "http://localhost:8001/predict_sam2"
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

    print(f"Sending request to SAM2 API (with {len(BBOXES)} bounding boxes)...")
    
    start_time = time.time()
    with open(IMAGE_PATH, "rb") as f:
        files = {"image": f}
        data = {
            "bboxes_json": json.dumps(BBOXES)
        }
        response = requests.post(API_URL, files=files, data=data)
    end_time = time.time()
    print(f"Model prediction took {end_time - start_time:.3f} seconds.")

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        sys.exit(1)

    result = response.json()
    segmentations = result.get("results", [])
    
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
        conf = seg["confidence"]
        mask_b64 = seg["mask_base64"]
        
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
