import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON
from sqlalchemy.sql import func

from src.app.db.session import Base


class JobStatus(str, enum.Enum):
    queued = "queued"
    processing = "processing"
    done = "done"
    failed = "failed"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    path = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    resolution = Column(String, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.queued, nullable=False)
    results = Column(JSON, nullable=True)  
    error = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
