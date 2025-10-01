from pydantic import BaseModel


class ProcessResponse(BaseModel):
    job_id: str
    status: str  

