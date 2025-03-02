import os
import time

from celery import Celery
from services.utils import Utils
from services.image_processing import ImageProcessor

utils = Utils()
celery = Celery(__name__)
celery.conf.broker_url = utils.config.celery.celery_broker_url
celery.conf.result_backend = utils.config.celery.celery_result_backend


@celery.task(name="image_processing_task")
def image_processing_task(image_path):
    processor = ImageProcessor(image_path)
    return processor.get_metadata()