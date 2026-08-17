# crud.py: operações no banco de dados, usando os modelos estabelecidos em models.py
# e os schemas de schemas.py.
#
import logging
from calendar import timegm
from datetime import datetime, timedelta, timezone

import feedparser
from sqlalchemy.orm import Session

from .models import Headline


class FeedUnavailableError(Exception):
    """O feed não pôde ser baixado ou o XML retornado é inválido."""


def _publication_date(entry) -> datetime:
    """Extrai a data de publicação da entrada, em UTC.

    O feedparser entrega um struct_time em UTC, então a conversão precisa ser
    com timegm (mktime interpretaria como hora local, deslocando pelo fuso).
    Nem todo feed informa a data em todas as entradas; nesse caso usamos
    "agora", para a notícia ainda contar como recente e ser postada.
    """
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed is None:
        logging.warning(
            "A entrada %s não tem data de publicação; usando a data atual.",
            entry.get("link"),
        )
        return datetime.now(timezone.utc)

    return datetime.fromtimestamp(timegm(parsed), tz=timezone.utc)


def get_latest_headlines_from_feed(db: Session, feed_URL: str) -> int:
    logging.info("Iniciando a leitura do feed.")
    feed = feedparser.parse(feed_URL)

    # O feedparser não lança exceção quando a URL está fora do ar ou o XML é
    # inválido: ele apenas liga o sinalizador "bozo". Se além disso não veio
    # nenhuma entrada, não há nada aproveitável.
    if feed.bozo and not feed.entries:
        raise FeedUnavailableError(
            f"Não foi possível ler o feed: {feed.bozo_exception}"
        )

    logging.info("O título do feed é %s.", feed.feed.get("title", "(sem título)"))

    new_entries = 0

    for entry in feed.entries:
        headline = Headline(
            entry_title=entry.title,
            entry_publication_date=_publication_date(entry),
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
            >= datetime.now(timezone.utc) - timedelta(days=max_days),
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
