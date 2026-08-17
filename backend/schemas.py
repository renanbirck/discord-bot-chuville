# Arquivo onde são definidos os 'schemas' a serem usados pela API.

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HeadlineSchema(BaseModel):
    """Formato de uma notícia devolvida pela API.

    Os nomes dos campos espelham as colunas de models.Headline (e não os
    nomes "amigáveis" que se poderia esperar de uma API pública) porque o
    bot já consome o JSON com esses nomes; from_attributes permite montar
    o schema diretamente a partir do objeto do SQLAlchemy.
    """

    model_config = ConfigDict(from_attributes=True)

    entry_id: int
    entry_title: str
    entry_publication_date: datetime
    entry_summary: str
    entry_link: str
    was_already_posted: bool


class EntrySchema(BaseModel):
    id: int
