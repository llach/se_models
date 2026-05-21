import requests
from src.types.grounding_dino import DetectionResponse

class GroundingDinoClient:
    def __init__(self, api_url: str = "http://localhost:8000"):
        """
        Initialize the GroundingDinoClient and run a health check.
        """
        self.api_url = api_url.rstrip('/')
        
        # Health check during initialization
        try:
            resp = requests.get(f"{self.api_url}/health", timeout=5.0)
            if resp.status_code != 200 or resp.json().get("status") != "healthy":
                raise RuntimeError(
                    f"GroundingDINO API health check failed: status {resp.status_code}, response: {resp.text}"
                )
        except Exception as e:
            raise RuntimeError(f"Failed to connect to GroundingDINO API at {self.api_url}/health: {e}")

    def predict(
        self,
        image_bytes: bytes,
        prompt: str,
        box_threshold: float = 0.35,
        text_threshold: float = 0.25
    ) -> DetectionResponse:
        """
        Perform detection query on the GroundingDINO API.
        """
        files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
        data = {
            'prompt': prompt,
            'box_threshold': box_threshold,
            'text_threshold': text_threshold
        }
        
        resp = requests.post(f"{self.api_url}/predict_grounding_dino", files=files, data=data)
        resp.raise_for_status()
        
        return DetectionResponse(**resp.json())
