import io
import os
import uuid
import logging
from pathlib import Path
from celery import Celery, group
from PIL import Image
import boto3

from src.core.config import settings
from src.db.session import SessionLocal
from src.db import crud, models

# --- Celery app ---
celery_app = Celery("image_worker")

celery_app.conf.broker_url = settings.redis_url
celery_app.conf.result_backend = settings.redis_url

# --- Logger ---
logger = logging.getLogger(__name__)

# --- S3 client ---
s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    region_name=settings.S3_REGION,
)


RESOLUTIONS = {
    "320": 320,
    "480": 480,
    "720": 720,
    "1080": 1080,
    "2k": 2048,   
    "original": None,  
}


def resize_and_convert(image_bytes: bytes, resolution: str) -> bytes:

    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")

    if resolution not in RESOLUTIONS:
        raise ValueError(f"Unsupported resolution: {resolution}")

    target_width = RESOLUTIONS[resolution]

    if target_width:  
        w_percent = target_width / float(img.size[0])
        target_height = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((target_width, target_height), Image.LANCZOS)

    output = io.BytesIO()
    img.save(output, format="WEBP", quality=90)
    output.seek(0)
    return output.read()


@celery_app.task(name="process_single_image", bind=True)
def process_single_image(self, path: str, entity_id: str, image_bytes: bytes, resolution: str) -> dict:
    try:
        processed_bytes = resize_and_convert(image_bytes, resolution)
 
        new_filename = f"{uuid.uuid4()}.webp"
        key = f"{path}/{entity_id}/{new_filename}"
 
        s3_client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=processed_bytes,
            ContentType="image/webp",
        )
 
        url = f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET}/{key}"
        return {"status": "success", "url": url}
 
    except Exception as exc:
        logger.error(f"Failed to process image for entity {entity_id}: {exc}", exc_info=True)
       
        return {"status": "failure", "error": str(exc)}

@celery_app.task(name="finalize_job")
def finalize_job(results: list, job_id: str):
    db = SessionLocal()
    try:
        successful_urls = []
        errors = []
        for result in results:
            if result["status"] == "success":
                successful_urls.append(result["url"])
            else:
                errors.append(result["error"])

        if not errors:
            final_status = models.JobStatus.done
        elif errors and not successful_urls:
            final_status = models.JobStatus.failed
        else:
            final_status = models.JobStatus.partial_success

        error_message = ", ".join(errors) if errors else None
        crud.update_job_status(db, job_id, final_status, results=successful_urls, error=error_message)
    finally:
        db.close()


@celery_app.task(name="process_images_job", bind=True)
def process_images_job(self, job_id: str, path: str, entity_id: str, image_contents_list: list, resolution: str):
    db = SessionLocal()
    try:
        crud.update_job_status(db, job_id, models.JobStatus.processing)

        callback = finalize_job.s(job_id=job_id)
        header = group(
            process_single_image.s(path, entity_id, image_bytes, resolution)
            for image_bytes in image_contents_list
        )
        (header | callback).apply_async()
    finally:
        db.close()
