# Defines the response shape returned by the upload endpoint
from pydantic import BaseModel


class JobCreateResponse(BaseModel):
    job_id: int
    status: str
    filename: str