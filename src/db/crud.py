from sqlalchemy.orm import Session
from src.app.db import models


def create_job(db: Session, job_id: str, path: str, entity_id: str, resolution: str):
    job = models.Job(
        job_id=job_id,
        path=path,
        entity_id=entity_id,
        resolution=resolution,
        status=models.JobStatus.queued,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_job_status(db: Session, job_id: str, status: models.JobStatus, results=None, error=None):
    job = db.query(models.Job).filter(models.Job.job_id == job_id).first()
    if not job:
        return None
    job.status = status
    if results is not None:
        job.results = results
    if error is not None:
        job.error = error
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: str):
    return db.query(models.Job).filter(models.Job.job_id == job_id).first()
