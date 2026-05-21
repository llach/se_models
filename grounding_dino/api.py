# pyrefly: ignore [missing-import]
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List
# pyrefly: ignore [missing-import]
import torch
import io
from PIL import Image

# GroundingDINO imports
from groundingdino.util.inference import load_model, predict
import groundingdino.datasets.transforms as T

app = FastAPI(title="GroundingDINO API")

# Load model weights
CONFIG_PATH = "weights/GroundingDINO_SwinT_OGC.py"
WEIGHTS_PATH = "weights/groundingdino_swint_ogc.pth"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Loading model on {DEVICE}...")
model = load_model(CONFIG_PATH, WEIGHTS_PATH)
model = model.to(DEVICE)
print("Model loaded successfully!")

# Define Python types for FastAPI integration
class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float

class DetectionResult(BaseModel):
    label: str
    confidence: float
    bbox: BoundingBox

class DetectionResponse(BaseModel):
    detections: List[DetectionResult]

def load_image_from_bytes(image_bytes: bytes):
    transform = T.Compose([
        T.RandomResize([800], max_size=1333),
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    
    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_transformed, _ = transform(pil_img, None)
    width, height = pil_img.size
    
    return image_transformed, width, height

@app.post("/predict_grounding_dino", response_model=DetectionResponse)
async def predict_endpoint(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    box_threshold: float = Form(0.35),
    text_threshold: float = Form(0.25)
):
    try:
        contents = await image.read()
        image_transformed, w, h = load_image_from_bytes(contents)
        
        # Run prediction
        boxes, logits, phrases = predict(
            model=model,
            image=image_transformed,
            caption=prompt,
            box_threshold=box_threshold,
            text_threshold=text_threshold,
            device=DEVICE
        )
        
        # GroundingDINO returns boxes in format: cx, cy, w, h (normalized)
        detections = []
        for box, logit, phrase in zip(boxes, logits, phrases):
            cx, cy, bw, bh = box.tolist()
            x_min = (cx - bw / 2) * w
            y_min = (cy - bh / 2) * h
            x_max = (cx + bw / 2) * w
            y_max = (cy + bh / 2) * h
            
            detections.append(DetectionResult(
                label=phrase,
                confidence=float(logit),
                bbox=BoundingBox(
                    x_min=float(x_min),
                    y_min=float(y_min),
                    x_max=float(x_max),
                    y_max=float(y_max)
                )
            ))
            
        return DetectionResponse(detections=detections)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "device": DEVICE}
