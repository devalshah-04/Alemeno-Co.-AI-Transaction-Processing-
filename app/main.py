# FastAPI app with health check and database connection check
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Confirms the API container can actually reach and query the database
@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "connected"}