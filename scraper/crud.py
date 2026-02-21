# crud.py: operações no banco de dados, usando os modelos estabelecidos em models.py
# e os schemas de schemas.py.
#
import logging
from datetime import datetime
from time import mktime

import feedparser
from sqlalchemy.orm import Session

from .models import Headline
from .schemas import HeadlineSchema


def get_latest_headlines_from_feed(db: Session, feed_URL: str):
    """Lê o feed e atualiza o BD com as novas notícias.
    TODO: separar essa função em duas partes, uma que leia o feed e outra que
    de fato atualize o BD."""
    logging.info("Iniciando a leitura do feed.")
    feed = feedparser.parse(feed_URL)
    logging.info("O título do feed é %s.", feed.feed.title)

    for entry_number, entry in enumerate(feed.entries):
        # Converte os dados do schema para o modelo ORM
        # Converte os dados do feed para o modelo ORM
        headline = Headline(
            entry_title=entry.title,
            entry_publication_date=datetime.fromtimestamp(
                mktime(entry.published_parsed)
            ),
            entry_summary=entry.summary,
            entry_link=entry.link,
            was_already_posted=False,
        )
        db.add(headline)
        db.commit()


def get_unposted_headlines(db: Session, max_days: int = 3):
    """A partir do BD, pega apenas as notícias não lidas dos últimos `max_days` dias.
    3 dias é uma escolha bem razoável para eventos pontuais."""
    pass


def mark_headline_as_read(db: Session, headline_id: int):
    """Marca a notícia de ID `headline_ID` como lida, ou seja, não será postada novamente.
    Essa marcação é solicitada pelo bot, ou seja, se ele estiver fora, a notícia não é postada."""
    pass
