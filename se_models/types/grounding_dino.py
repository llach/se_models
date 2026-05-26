from pydantic import BaseModel
from typing import List

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
