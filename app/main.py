# FastAPI app: health check, db check, and CSV upload endpoint
import os
import shutil

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from tasks import process_job
from database import get_db
from models import Job
from schemas import JobCreateResponse

app = FastAPI()

# Folder where uploaded CSVs are saved (shared with the worker via a volume)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "connected"}


@app.post("/jobs/upload", response_model=JobCreateResponse)
def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Basic validation: only accept .csv files
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")

    # Create the Job record first, so we get an id to name the saved file with
    job = Job(filename=file.filename, status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)

    # Save the uploaded file to disk, named with the job id to avoid clashes
    file_path = os.path.join(UPLOAD_DIR, f"{job.id}_{file.filename}")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Hand off to the background worker — returns immediately, doesn't wait
    process_job.delay(job.id)

    return JobCreateResponse(job_id=job.id, status=job.status, filename=job.filename)

