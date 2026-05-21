import requests
import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import time

# ==========================================
# PARAMETERS
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(SCRIPT_DIR, "stack.png")  # Provide a valid path to an image
PROMPT = "clothing"
BOX_THRESHOLD = 0.35
TEXT_THRESHOLD = 0.25
API_URL = "http://localhost:8000/predict_grounding_dino"
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

    print(f"Sending request to GroundingDINO API...")
    start_time = time.time()
    with open(IMAGE_PATH, "rb") as f:
        files = {"image": f}
        data = {
            "prompt": PROMPT,
            "box_threshold": BOX_THRESHOLD,
            "text_threshold": TEXT_THRESHOLD
        }
        response = requests.post(API_URL, files=files, data=data)
    end_time = time.time()
    print(f"Model prediction took {end_time - start_time:.3f} seconds.")

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        sys.exit(1)

    result = response.json()
    detections = result.get("detections", [])
    
    print(f"Found {len(detections)} detections.")

    # Visualization
    img = cv2.imread(IMAGE_PATH)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    for det in detections:
        bbox = det["bbox"]
        label = det["label"]
        conf = det["confidence"]

        x_min = int(bbox["x_min"])
        y_min = int(bbox["y_min"])
        x_max = int(bbox["x_max"])
        y_max = int(bbox["y_max"])

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
