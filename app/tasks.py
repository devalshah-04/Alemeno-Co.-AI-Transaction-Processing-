# Background tasks executed by the Celery worker
import time
from celery_app import celery_app
from database import SessionLocal
from models import Job


@celery_app.task(name="process_job")
def process_job(job_id: int):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return

        job.status = "processing"
        db.commit()

        # Placeholder for the real pipeline (steps a-e) — added in later steps
        time.sleep(5)

        job.status = "completed"
        db.commit()
    finally:
        db.close()