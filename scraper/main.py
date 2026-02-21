import logging
from os import environ

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

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
async def get_new_headlines():
    """
    Lê o feed RSS e verifica se há novas notícias.
    """

    pass


@app.get("/post_headlines")
async def post_headlines(days: int = 3):
    """
    Retorna as notícias que ainda não foram postadas,
    nos últimos `days` dia (o padrão é 3)."""
    pass


@app.post("/mark_headline_as_read")
async def mark_headline_as_read(id):
    """Marca a manchete com o id especificado como lida,
    ou seja, ela não será postada novamente."""

    pass


### Inicialização do servidor, integrando com o logger do FastAPI.

logger = logging.getLogger("uvicorn.error")
logger.info("Inicializando o servidor!")
load_dotenv()

if __name__ == "__main__":
    uvicorn.run(app, log_level="trace")

### FIM.
