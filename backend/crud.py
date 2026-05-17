# crud.py: operações no banco de dados, usando os modelos estabelecidos em models.py
# e os schemas de schemas.py.
#
import logging
from datetime import datetime, timedelta
from time import mktime

import feedparser
import sqlalchemy.exc
from sqlalchemy.orm import Session

from .models import Headline


def get_latest_headlines_from_feed(db: Session, feed_URL: str) -> int:
    logging.info("Iniciando a leitura do feed.")
    feed = feedparser.parse(feed_URL)
    logging.info("O título do feed é %s.", feed.feed.title)

    new_entries = 0

    for entry in feed.entries:
        headline = Headline(
            entry_title=entry.title,
            entry_publication_date=datetime.fromtimestamp(
                mktime(entry.published_parsed)
            ),
            entry_summary=entry.summary,
            entry_link=entry.link,
            was_already_posted=False,
        )

        # Verifica se já existe antes de tentar inserir
        exists = db.query(Headline).filter(
            Headline.entry_link == headline.entry_link
        ).first()

        if exists:
            logging.info(
                "A entrada %s já existe! (Não é um erro)", headline.entry_title
            )
            continue

        db.add(headline)
        new_entries += 1

    db.commit()  # Um único commit no final
    return new_entries

def get_unposted_headlines(db: Session, max_days: int = 3):
    """A partir do BD, pega apenas as notícias não lidas dos últimos `max_days` dias.
    3 dias é uma escolha bem razoável para eventos pontuais."""

    return (
        db.query(Headline)
        .filter(
            Headline.entry_publication_date
            >= datetime.now() - timedelta(days=max_days),
            Headline.was_already_posted == False,
        )
        .all()
    )


def mark_headline_as_read(db: Session, headline_id: int):
    """Marca a notícia de ID `headline_ID` como lida, ou seja, não será postada novamente.
    Essa marcação é solicitada pelo bot, ou seja, se ele estiver fora, a notícia não é postada."""

    headline_to_update = (
        db.query(Headline).filter(Headline.entry_id == headline_id).first()
    )

    if headline_to_update:
        headline_to_update.was_already_posted = True
        db.commit()
    else:
        logging.info("Não existe a notícia com ID %d!", headline_id)
        raise ValueError("A notícia com o ID especificado não existe.")
