import logging
from os import environ

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import engine, get_db

# Configura o logging para integrar com o Uvicorn/FastAPI
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)

# Precisa vir no começo, para a API já inicializar em um estado conhecido.
load_dotenv()

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.get("/")
async def root():
    """
    A 'página principal' da API.

    TODO: Ver o que o bot pode retornar quando for feita uma chamada
    na raiz. Ele pode retornar, por exemplo, a data da última notícia.
    """
    return {"status": 200}
    pass


@app.get("/fetch_headlines")
async def get_new_headlines(db: Session = Depends(get_db)):
    """
    Lê o feed RSS e verifica se há novas notícias, retornando um objeto JSON com o número
    de novas entradas.
    """
    logging.info("Lendo o feed.")
    num_new_entries = crud.get_latest_headlines_from_feed(db, environ["RSS_URL"])

    return {
        "num_new_entries": num_new_entries,
    }


@app.get("/get_unposted_headlines")
async def get_unposted_headlines(db: Session = Depends(get_db), days: int | None = 3):
    """
    Retorna as notícias que ainda não foram postadas,
    nos últimos `days` dia (o padrão é 3)."""
    logging.info("Lendo as notícias com menos de %d dias.", days)
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


# Inicialização do servidor


logging.info("Inicializando o servidor!")

try:
    logging.info("Irei ler o feed de %s.", environ["RSS_URL"])
    logging.info("Os dados lidos serão escritos no BD %s.", environ["DATABASE_PATH"])
except KeyError:
    logging.error(
        "Você precisa de um arquivo .env com DATABASE_PATH e RSS_URL configurados! Leia o README.md."
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8820, log_level="info")

# FIM.
