import logging
from os import environ

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()
DATABASE_URL = "sqlite:///" + environ["DATABASE_PATH"]

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 15})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    logging.info("O banco de dados está em %s.", DATABASE_URL)

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
