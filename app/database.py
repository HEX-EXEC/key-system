import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]

max_retries = 5
retry_delay = 5
for attempt in range(max_retries):
    try:
        engine = create_engine(DATABASE_URL)
        logger.info("Successfully connected to the database")
        break
    except Exception as e:
        logger.error(f"Failed to connect to database (attempt {attempt + 1}/{max_retries}): {str(e)}")
        if attempt == max_retries - 1:
            raise
        time.sleep(retry_delay)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()