import requests
from src.types.sam2 import SegmentationResponse

class Sam2Client:
    def __init__(self, api_url: str = "http://localhost:8001"):
        """
        Initialize the Sam2Client and run a health check.
        """
        self.api_url = api_url.rstrip('/')
        
        # Health check during initialization
        try:
            resp = requests.get(f"{self.api_url}/health", timeout=5.0)
            if resp.status_code != 200 or resp.json().get("status") != "healthy":
                raise RuntimeError(
                    f"SAM2 API health check failed: status {resp.status_code}, response: {resp.text}"
                )
        except Exception as e:
            raise RuntimeError(f"Failed to connect to SAM2 API at {self.api_url}/health: {e}")

    def predict(
        self,
        image_bytes: bytes,
        bboxes_json: str = "[]"
    ) -> SegmentationResponse:
        """
        Perform segmentation query on the SAM2 API.
        """
        files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
        data = {
            'bboxes_json': bboxes_json
        }
        
        resp = requests.post(f"{self.api_url}/predict_sam2", files=files, data=data)
        resp.raise_for_status()
        
        return SegmentationResponse(**resp.json())
