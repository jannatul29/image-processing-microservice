from fastapi import APIRouter
from services.image_processing import ImageProcessor

router = APIRouter(tags=["Image Processing"])

@router.get("/metadata")
def get_metadata(filename: str):
    processor = ImageProcessor(f"data/{filename}")
    return processor.get_metadata()

@router.get("/slice")
def get_slice(filename: str, time: int, z: int, channel: int):
    processor = ImageProcessor(f"data/{filename}")
    return {"slice": processor.extract_slice(time, z, channel).tolist()}

@router.post("/analyze")
def analyze_image(filename: str):
    processor = ImageProcessor(f"data/{filename}")
    return {"pca_result": processor.apply_pca(n_components=3).tolist()}

@router.get("/statistics")
def get_statistics(filename: str):
    processor = ImageProcessor(f"data/{filename}")
    return {"statistics": processor.compute_statistics()}
