from pydantic import BaseModel
from typing import List

class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float

class SegmentationResult(BaseModel):
    mask_base64: str
    confidence: float

class SegmentationResponse(BaseModel):
    results: List[SegmentationResult]
