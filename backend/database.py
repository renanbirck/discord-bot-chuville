from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_PATH

# O main.py já loga DATABASE_PATH uma única vez na inicialização; não repetimos
# o mesmo dado aqui (antes, get_db() logava a URL do banco em toda requisição).
DATABASE_URL = "sqlite:///" + DATABASE_PATH

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 15})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa (estilo SQLAlchemy 2.0) para os modelos do app."""


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
