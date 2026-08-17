import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .config import DATABASE_PATH, RSS_URL
from .database import engine, get_db

# Configura o logging para integrar com o Uvicorn/FastAPI
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Criar as tabelas é um efeito colateral do início do serviço, não da
    # importação do módulo (que também acontece em testes, ferramentas, etc.).
    models.Base.metadata.create_all(bind=engine)
    logger.info("Inicializando o servidor!")
    logger.info("Irei ler o feed de %s.", RSS_URL)
    logger.info("Os dados lidos serão escritos no BD %s.", DATABASE_PATH)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    """
    A 'página principal' da API.

    TODO: Ver o que o bot pode retornar quando for feita uma chamada
    na raiz. Ele pode retornar, por exemplo, a data da última notícia.
    """
    return {"status": 200}


@app.get("/fetch_headlines")
async def get_new_headlines(db: Session = Depends(get_db)):
    """
    Lê o feed RSS e verifica se há novas notícias, retornando um objeto JSON com o número
    de novas entradas.
    """
    logger.info("Lendo o feed.")
    try:
        num_new_entries = crud.get_latest_headlines_from_feed(db, RSS_URL)
    except crud.FeedUnavailableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "num_new_entries": num_new_entries,
    }


@app.get("/get_unposted_headlines", response_model=list[schemas.HeadlineSchema])
async def get_unposted_headlines(db: Session = Depends(get_db), days: int | None = 3):
    """
    Retorna as notícias que ainda não foram postadas,
    nos últimos `days` dia (o padrão é 3)."""
    logger.info("Lendo as notícias com menos de %d dias.", days)
    return crud.get_unposted_headlines(db, days)  # pyright:ignore[reportArgumentType]


@app.post("/mark_headline_as_read")
async def mark_headline_as_read(
    entry: schemas.EntrySchema, db: Session = Depends(get_db)
):
    """Marca a manchete com o id especificado como lida,
    ou seja, ela não será postada novamente."""

    try:
        crud.mark_headline_as_read(db, entry.id)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="A notícia com o id especificado não existe!"
        )

    return entry


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8820, log_level="info")
