from fastapi import APIRouter, UploadFile, File, Depends
import tifffile as tiff
import numpy as np
from sqlalchemy.orm import Session
from database.setup import get_db
from database.models import Images
from services.image_processing import ImageProcessor

router = APIRouter(tags=["Image Upload & meta_data"])


@router.post("/upload")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        image_filepath = f"data/dynamic/{file.filename}"
        contents = await file.read()
        with open(image_filepath, "wb") as f:
            f.write(contents)

        processor = ImageProcessor(image_filepath)
        image_attributes = processor.get_image_attributes()
        image_obj = Images(**image_attributes)
        db.add(image_obj)
        db.commit()

        return {"message": "File uploaded"}
    except Exception as error:
        return {"error": str(error)}
