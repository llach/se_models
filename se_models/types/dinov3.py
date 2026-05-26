from pydantic import BaseModel
from typing import List

class EmbeddingResponse(BaseModel):
    embeddings: List[float]
    shape: List[int]
    h_patches: int
    w_patches: int
