import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_PATH

DATABASE_URL = "sqlite:///" + DATABASE_PATH

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 15})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa (estilo SQLAlchemy 2.0) para os modelos do app."""


def get_db():
    logging.info("O banco de dados está em %s.", DATABASE_URL)

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
