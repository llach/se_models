from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List
import torch
import io
import json
from PIL import Image
import numpy as np
import cv2
import base64

# SAM2 imports
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator

# Import Pydantic schemas from shared src package
from src.types.sam2 import BoundingBox, SegmentationResult, SegmentationResponse

app = FastAPI(title="SAM2 API")

# Load model weights
CHECKPOINT = "/home/user/app/weights/sam2.1_hiera_large.pt"
CONFIG = "//home/user/app/weights/sam2.1_hiera_l.yaml"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Loading SAM2 on {DEVICE}...")
sam2_model = build_sam2(CONFIG, CHECKPOINT, device=DEVICE)
predictor = SAM2ImagePredictor(sam2_model)
mask_generator = SAM2AutomaticMaskGenerator(sam2_model)
print("SAM2 loaded successfully!")

def encode_mask_to_base64(mask: np.ndarray):
    mask_img = (mask * 255).astype(np.uint8)
    _, buffer = cv2.imencode('.png', mask_img)
    return base64.b64encode(buffer).decode('utf-8')

@app.post("/predict_sam2", response_model=SegmentationResponse)
async def predict_endpoint(
    image: UploadFile = File(...),
    bboxes_json: str = Form("[]") # json string of list of boxes
):
    try:
        contents = await image.read()
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
        image_np = np.array(pil_img)
        
        boxes = json.loads(bboxes_json)
        results = []
        
        if len(boxes) == 0:
            auto_masks = mask_generator.generate(image_np)
            for m in auto_masks:
                b64_mask = encode_mask_to_base64(m['segmentation'])
                results.append(SegmentationResult(
                    mask_base64=b64_mask,
                    confidence=float(m['predicted_iou'])
                ))
            return SegmentationResponse(results=results)
        
        predictor.set_image(image_np)

        input_boxes = []
        for b in boxes:
            input_boxes.append([b['x_min'], b['y_min'], b['x_max'], b['y_max']])
        input_boxes = np.array(input_boxes)
        
        masks, scores, logits = predictor.predict(
            point_coords=None,
            point_labels=None,
            box=input_boxes,
            multimask_output=False,
        )
        
        for i in range(len(boxes)):
            mask = masks[i, 0]
            score = scores[i, 0]
            
            b64_mask = encode_mask_to_base64(mask)
            results.append(SegmentationResult(
                mask_base64=b64_mask,
                confidence=float(score)
            ))
            
        return SegmentationResponse(results=results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "device": DEVICE}
