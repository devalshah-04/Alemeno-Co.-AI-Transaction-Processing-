# FastAPI app: health check, db check, and CSV upload endpoint
import os
import shutil
import hashlib

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from tasks import process_job
from database import get_db
from models import Job
from schemas import JobCreateResponse

from typing import Optional, List
from models import Job
from schemas import (
    JobCreateResponse,
    JobStatusResponse,
    JobResultsResponse,
    JobListItem,
    JobSummaryOut,
    TransactionOut,
)

app = FastAPI()

# Folder where uploaded CSVs are saved (shared with the worker via a volume)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


@app.post("/jobs/upload", response_model=JobCreateResponse)
def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")

    contents = file.file.read()
    file_hash = hashlib.sha256(contents).hexdigest()

    # If this exact file content was uploaded before, return the existing job
    existing = db.query(Job).filter(Job.file_hash == file_hash).first()
    if existing:
        return JobCreateResponse(job_id=existing.id, status=existing.status, filename=existing.filename)

    job = Job(filename=file.filename, status="pending", file_hash=file_hash)
    db.add(job)
    db.commit()
    db.refresh(job)

    file_path = os.path.join(UPLOAD_DIR, f"{job.id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(contents)

    process_job.delay(job.id)

    return JobCreateResponse(job_id=job.id, status=job.status, filename=job.filename)

@app.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    summary = JobSummaryOut.model_validate(job.summary) if job.summary else None

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        filename=job.filename,
        row_count_raw=job.row_count_raw,
        row_count_clean=job.row_count_clean,
        created_at=job.created_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
        summary=summary,
    )


@app.get("/jobs/{job_id}/results", response_model=JobResultsResponse)
def get_job_results(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    transactions = [TransactionOut.model_validate(t) for t in job.transactions]
    summary = JobSummaryOut.model_validate(job.summary) if job.summary else None

    return JobResultsResponse(
        job_id=job.id,
        status=job.status,
        transactions=transactions,
        summary=summary,
    )


@app.get("/jobs", response_model=List[JobListItem])
def list_jobs(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status)
    jobs = query.order_by(Job.created_at.desc()).all()

    return [
        JobListItem(
            job_id=j.id,
            filename=j.filename,
            status=j.status,
            row_count_raw=j.row_count_raw,
            created_at=j.created_at,
        )
        for j in jobs
    ]