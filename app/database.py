# Sets up the database connection and provides sessions for talking to it
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Connection string: read from environment variable, with a fallback default
# Format: postgresql://<user>:<password>@<host>:<port>/<database_name>
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://alemeno:alemeno_pass@postgres:5432/transactions_db"
)

# The engine manages the actual low-level connection to Postgres
engine = create_engine(DATABASE_URL)

# SessionLocal creates a new "conversation" with the database for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class our table models will inherit from
Base = declarative_base()

# Used by FastAPI to give each request its own database session, and close it afterward
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()