import datetime
import logging
import sqlite3

import feedparser

import config
import database
from models import CreateHeadline


def get_new_events():
    db = database.Database()

    logging.info("Iniciando a leitura do feed.")
    feed = feedparser.parse(config.RSS_URL)
    logging.info(f"O título do feed é {feed.feed.title}.")

    for entry_number, entry in enumerate(feed.entries):
        logging.info(
            "A entrada %s tem o título %s e foi publicada em %s. Seu conteúdo é %s. Mais informações em %s.",
            entry_number,
            entry.title,
            entry.published_parsed,
            entry.summary,
            entry.link,
        )
        try:
            # logging.info("Processando a entrada %s: %s.", entry_number, entry)
            headline = CreateHeadline.from_entry(entry)
            logging.info("A data da entrada é %s.", headline.publishing_date)

            db.put_entry(headline)

        except sqlite3.IntegrityError:
            logging.info(
                f"A entrada da data {entry.published} já existe (não há nada de errado nisso, mas convém verificar)."
            )

        # Desativei a exceção porque eu *quero* que o bot falhe
        # no caso de algo dar errado.

        # except Exception as e:
        #    logging.error(f"Ocorreu um erro ao processar a entrada: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(funcName)s %(message)s",
        datefmt="%Y/%m/%d %I:%M:%S %p",
        level=logging.INFO,
    )
    get_new_events()
