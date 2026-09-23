# Arquivo onde são definidos os 'schemas' a serem usados pela API.

from datetime import datetime, timezone
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict


def _as_utc(value: datetime) -> datetime:
    """O SQLite não guarda o fuso horário, então as datas voltam do BD sem
    ele; como o backend sempre as grava em UTC, é só marcá-las como UTC."""
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


# Data em UTC, que no JSON sai com o fuso explícito (ex.: 2026-09-22T13:00:00Z),
# para não ser confundida com o horário local de quem consulta o status.
UTCDatetime = Annotated[datetime, AfterValidator(_as_utc)]


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


class PostingErrorSchema(EntrySchema):
    """O erro que o bot teve ao tentar postar a notícia `id`."""

    error: str


class LastHeadlineSchema(BaseModel):
    """A notícia mais recente, como aparece no status (/). Os nomes dos campos
    seguem o mesmo padrão de HeadlineSchema."""

    model_config = ConfigDict(from_attributes=True)

    entry_id: int
    entry_title: str
    entry_publication_date: UTCDatetime
    was_already_posted: bool
    # None se o bot não relatou erro (a notícia já foi postada ou ainda não
    # houve tentativa).
    posting_error: str | None


class StatusSchema(BaseModel):
    """O status geral do backend, devolvido em /."""

    last_headline: LastHeadlineSchema | None
    last_posting_date: UTCDatetime | None
