import requests
from se_models.types.dinov3 import EmbeddingResponse

class Dinov3Client:
    def __init__(self, api_url: str = "http://localhost:8002"):
        """
        Initialize the Dinov3Client and run a health check.
        """
        self.api_url = api_url.rstrip('/')
        
        # Health check during initialization
        try:
            resp = requests.get(f"{self.api_url}/health", timeout=5.0)
            if resp.status_code != 200 or resp.json().get("status") != "healthy":
                raise RuntimeError(
                    f"DINOv3 API health check failed: status {resp.status_code}, response: {resp.text}"
                )
        except Exception as e:
            raise RuntimeError(f"Failed to connect to DINOv3 API at {self.api_url}/health: {e}")

    def get_embeddings(self, image_bytes: bytes) -> EmbeddingResponse:
        """
        Extract features/embeddings from the DINOv3 API.
        """
        files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
        resp = requests.post(f"{self.api_url}/predict_embeddings", files=files)
        resp.raise_for_status()
        
        return EmbeddingResponse(**resp.json())
