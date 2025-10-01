
from typing import List
import tempfile

from fastapi import APIRouter, UploadFile, File, Form
from fastapi import Depends
from sqlalchemy.orm import Session

import uuid
from pathlib import Path

from src.app.schemas.process import ProcessResponse
from src.app import worker
from src.app.db import crud
from src.app.db.session import get_db

router = APIRouter(
    prefix="/process",
    tags=["process"]
)

@router.post("", response_model=ProcessResponse)
async def process_job(
    path: str = Form(...),
    entity_id: str = Form(..., alias="id"),
    resolution: str = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """ 
    form-data:
    - path: куда сохраняем (например 'products')
    - entity_id: идентификатор сущности (UUID продукта)
    - images: список файлов
    - db: БД
    """
    job_id = str(uuid.uuid4())


    crud.create_job(db, job_id, path, entity_id, resolution)

    image_contents_list = []
    for img in images:
        contents = await img.read()
        image_contents_list.append(contents)

    worker.process_images_job.delay(job_id, path, entity_id, image_contents_list, resolution)

    return ProcessResponse(job_id=job_id, status="queued")