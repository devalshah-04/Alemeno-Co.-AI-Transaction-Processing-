# Background tasks executed by the Celery worker
import os
import math
from datetime import datetime

import pandas as pd

from celery_app import celery_app
from database import SessionLocal
from models import Job, Transaction
from pipeline.cleaning import clean_dataframe
from pipeline.anomalies import detect_anomalies

UPLOAD_DIR = "uploads"


def find_upload_path(job_id: int) -> str:
    """Locate the uploaded file for this job (saved as '<job_id>_<filename>')."""
    for filename in os.listdir(UPLOAD_DIR):
        if filename.startswith(f"{job_id}_"):
            return os.path.join(UPLOAD_DIR, filename)
    raise FileNotFoundError(f"No uploaded file found for job {job_id}")


def none_if_nan(value):
    """Convert pandas NaN (from blank CSV cells) to None for database storage."""
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


@celery_app.task(name="process_job")
def process_job(job_id: int):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return

        job.status = "processing"
        db.commit()

        try:
            # Read the raw CSV
            file_path = find_upload_path(job.id)
            df_raw = pd.read_csv(file_path)
            job.row_count_raw = len(df_raw)

            # Step a: clean the data
            df_clean = clean_dataframe(df_raw)
            job.row_count_clean = len(df_clean)

            # Step b: detect anomalies
            df_clean = detect_anomalies(df_clean)

            # Save each cleaned row as a Transaction
            for _, row in df_clean.iterrows():
                txn = Transaction(
                    job_id=job.id,
                    txn_id=none_if_nan(row["txn_id"]),
                    date=row["date"],
                    merchant=row["merchant"],
                    amount=row["amount"],
                    currency=row["currency"],
                    status=row["status"],
                    category=row["category"],
                    account_id=row["account_id"],
                    is_anomaly=bool(row["is_anomaly"]),
                    anomaly_reason=row["anomaly_reason"],
                )
                db.add(txn)

            job.status = "completed"
            job.completed_at = datetime.utcnow()
            db.commit()

        except Exception as e:
            # If anything in the pipeline fails, record it instead of crashing silently
            job.status = "failed"
            job.error_message = str(e)
            db.commit()

    finally:
        db.close()