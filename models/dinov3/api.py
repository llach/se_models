from fastapi import FastAPI, UploadFile, File, HTTPException
import torch
import torchvision.transforms.functional as TF
from PIL import Image
import io
import numpy as np

# Import the response type from se_models
from se_models.types.dinov3 import EmbeddingResponse

app = FastAPI(title="DINOv3 API")

PATCH_SIZE = 16
IMAGE_SIZE = 768

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

MODEL_NAME = "dinov3_vitl16"
DINOV3_LOCATION = "/home/user/app/dinov3"
VITL_WEIGHTS = "/home/user/app/weights/dinov3_vitl16_pretrain_lvd1689m-8aa4cbdd.pth"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_N_LAYERS = 24

print(f"Loading DINOv3 model on {DEVICE}...")
dinov3_model = torch.hub.load(
    repo_or_dir=DINOV3_LOCATION,
    model=MODEL_NAME,
    source="local",
    weights=VITL_WEIGHTS
)
dinov3_model.to(DEVICE)
dinov3_model.eval()
print("DINOv3 model loaded successfully!")

def resize_transform(
    mask_image: Image,
    image_size: int = IMAGE_SIZE,
    patch_size: int = PATCH_SIZE,
) -> torch.Tensor:
    w, h = mask_image.size
    h_patches = int(image_size / patch_size)
    w_patches = int((w * image_size) / (h * patch_size))
    return TF.to_tensor(TF.resize(mask_image, (h_patches * patch_size, w_patches * patch_size)))

@app.post("/predict_embeddings", response_model=EmbeddingResponse)
async def predict_embeddings(
    image: UploadFile = File(...)
):
    try:
        contents = await image.read()
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Preprocess
        test_image_resized = resize_transform(pil_img)
        test_image_normalized = TF.normalize(test_image_resized, mean=IMAGENET_MEAN, std=IMAGENET_STD)
        
        # Calculate patch shapes
        h_patches, w_patches = [int(d / PATCH_SIZE) for d in test_image_resized.shape[1:]]
        
        with torch.inference_mode():
            # Match the device configuration
            input_tensor = test_image_normalized.unsqueeze(0).to(DEVICE)
            if DEVICE == "cuda":
                with torch.autocast(device_type='cuda', dtype=torch.float32):
                    feats = dinov3_model.get_intermediate_layers(input_tensor, n=range(MODEL_N_LAYERS), reshape=True, norm=True)
            else:
                feats = dinov3_model.get_intermediate_layers(input_tensor, n=range(MODEL_N_LAYERS), reshape=True, norm=True)
            
            x = feats[-1].squeeze().detach().cpu()
            dim = x.shape[0]
            x = x.view(dim, -1).permute(1, 0) # shape: (num_patches, dim)
            
            shape = list(x.shape) # e.g. [num_patches, dim]
            # Flatten features to 1D list
            embeddings_list = x.flatten().numpy().tolist()
            
        return EmbeddingResponse(
            embeddings=embeddings_list,
            shape=shape,
            h_patches=h_patches,
            w_patches=w_patches
        )
    except Exception as e:
        print(f"Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "device": DEVICE}
