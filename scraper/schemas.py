# Arquivo onde são definidos os 'schemas' a serem usados pela API.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HeadlineSchema(BaseModel):
    id: Optional[int] = None  # é primary key no BD, logo, é gerado automaticamente
    title: str
    date: datetime
    summary: str
    link: str
    was_already_posted: bool


class EntrySchema(BaseModel):
    id: int
