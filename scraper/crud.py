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
from .schemas import HeadlineSchema


def get_latest_headlines_from_feed(db: Session, feed_URL: str) -> int:
    """Lê o feed e atualiza o BD com as novas notícias, retornando
    o número de notícias que foram adicionadas.
    TODO: separar essa função em duas partes, uma que leia o feed e outra que
    de fato atualize o BD."""
    logging.info("Iniciando a leitura do feed.")
    feed = feedparser.parse(feed_URL)
    logging.info("O título do feed é %s.", feed.feed.title)

    new_entries = 0

    for entry_number, entry in enumerate(feed.entries):
        # Converte os dados do feed para o modelo ORM
        headline = Headline(
            entry_title=entry.title,
            entry_publication_date=datetime.fromtimestamp(
                mktime(entry.published_parsed)  # pyright:ignore[reportArgumentType]
            ),
            entry_summary=entry.summary,
            entry_link=entry.link,
            was_already_posted=False,
        )

        try:
            db.add(headline)
            db.commit()
            new_entries += 1
        except sqlalchemy.exc.IntegrityError:  # Já existe a entrada
            logging.info(  # então vamos avisar
                "A entrada %s, de %s, já existe! (Não é um erro)",
                headline.entry_title,
                headline.entry_publication_date,
            )
            db.rollback()  # e desfazer a nossa mudança

    db.commit()
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
