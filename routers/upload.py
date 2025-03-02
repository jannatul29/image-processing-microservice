from fastapi import APIRouter, UploadFile, File, Depends
import tifffile as tiff
import numpy as np
from sqlalchemy.orm import Session
from database.setup import SessionLocal, get_db
from database.models import ImageMetadata

router = APIRouter(tags=["Image Upload & Metadata"])

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

@router.post("/upload")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    with open(f"data/{file.filename}", "wb") as f:
        f.write(contents)

    image = tiff.imread(f"data/{file.filename}")
    t, z, y, x, c = image.shape

    metadata = ImageMetadata(
        filename=file.filename, width=x, height=y, depth=z, time_frames=t, channels=c
    )
    db.add(metadata)
    db.commit()

    return {"message": "File uploaded", "metadata": metadata}
