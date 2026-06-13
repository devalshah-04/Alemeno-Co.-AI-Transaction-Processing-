# Defines the response shapes for all API endpoints
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class JobCreateResponse(BaseModel):
    job_id: int
    status: str
    filename: str


# One transaction, as returned by /results
class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    txn_id: Optional[str] = None
    date: Optional[str] = None
    merchant: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    account_id: Optional[str] = None
    is_anomaly: bool
    anomaly_reason: Optional[str] = None
    llm_category: Optional[str] = None
    llm_failed: bool


# The AI-generated summary for a job
class JobSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_spend_inr: Optional[float] = None
    total_spend_usd: Optional[float] = None
    top_merchants: Optional[list] = None
    anomaly_count: Optional[int] = None
    narrative: Optional[str] = None
    risk_level: Optional[str] = None


# Response for GET /jobs/{job_id}/status
class JobStatusResponse(BaseModel):
    job_id: int
    status: str
    filename: str
    row_count_raw: Optional[int] = None
    row_count_clean: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    summary: Optional[JobSummaryOut] = None


# Response for GET /jobs/{job_id}/results
class JobResultsResponse(BaseModel):
    job_id: int
    status: str
    transactions: List[TransactionOut]
    summary: Optional[JobSummaryOut] = None


# One row in GET /jobs
class JobListItem(BaseModel):
    job_id: int
    filename: str
    status: str
    row_count_raw: Optional[int] = None
    created_at: datetime