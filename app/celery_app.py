# Creates and configures the Celery application
# This file is imported by both the API (to send tasks) and the worker (to run them)
import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "worker",
    broker=REDIS_URL,   # where tasks are queued
    backend=REDIS_URL,  # where task results/state are stored
    include=["tasks"],  # tells the worker to import tasks.py so its tasks get registered
)