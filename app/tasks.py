# Background tasks executed by the Celery worker
import os
import math
from datetime import datetime

import pandas as pd

from celery_app import celery_app
from database import SessionLocal
from models import Job, Transaction, JobSummary
from pipeline.cleaning import clean_dataframe
from pipeline.anomalies import detect_anomalies
from pipeline.categorization import categorize_transactions
from pipeline.narrative import generate_summary

UPLOAD_DIR = "uploads"


def find_upload_path(job_id: int) -> str:
    for filename in os.listdir(UPLOAD_DIR):
        if filename.startswith(f"{job_id}_"):
            return os.path.join(UPLOAD_DIR, filename)
    raise FileNotFoundError(f"No uploaded file found for job {job_id}")


def none_if_nan(value):
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
            file_path = find_upload_path(job.id)
            df_raw = pd.read_csv(file_path)
            job.row_count_raw = len(df_raw)

            df_clean = clean_dataframe(df_raw)
            job.row_count_clean = len(df_clean)

            df_clean = detect_anomalies(df_clean)
            df_clean = categorize_transactions(df_clean)

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
                    llm_category=none_if_nan(row["llm_category"]),
                    llm_failed=bool(row["llm_failed"]),
                )
                db.add(txn)

            # Step d: narrative summary
            summary_data = generate_summary(df_clean)
            job_summary = JobSummary(
                job_id=job.id,
                total_spend_inr=summary_data["total_spend_inr"],
                total_spend_usd=summary_data["total_spend_usd"],
                top_merchants=summary_data["top_merchants"],
                anomaly_count=summary_data["anomaly_count"],
                narrative=summary_data["narrative"],
                risk_level=summary_data["risk_level"],
            )
            db.add(job_summary)

            job.status = "completed"
            job.completed_at = datetime.utcnow()
            db.commit()

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()

    finally:
        db.close()