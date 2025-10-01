from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.app.db.models import JobStatus


class JobResult(BaseModel):
    job_id: str
    status: JobStatus
    results: Optional[List[str]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True