from celery import Celery
from services.utils import Utils
from services.image_processing import ImageProcessor
from sqlalchemy.orm import Session
from database.setup import get_db
from database.models import Images
from fastapi import Depends

utils = Utils()
celery = Celery(__name__)
celery.conf.broker_url = utils.config.celery.celery_broker_url
celery.conf.result_backend = utils.config.celery.celery_result_backend


@celery.task(name="image_processing_task")
def image_processing_task(image_path, db: Session = Depends(get_db)):
    processor = ImageProcessor(image_path)
    image_attributes = processor.get_image_attributes()
    image_obj = Images(**image_attributes)
    db.add(image_obj)
    db.commit()

    return {"message": "File uploaded"}
