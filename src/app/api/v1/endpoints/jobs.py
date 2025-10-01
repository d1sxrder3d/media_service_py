from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from src.app.schemas.jobs import JobResult
from src.app.db import crud
from src.app.db.session import get_db

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)


@router.get("/{job_id}", response_model=JobResult)
async def get_job(job_id: str, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job