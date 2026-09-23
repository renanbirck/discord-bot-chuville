#!/usr/bin/env python3

import os
import unittest
from datetime import datetime, timezone

# O config.py exige estas variáveis já na importação (e carregaria o .env,
# cujo DATABASE_PATH aponta para o BD de verdade). Definindo-as antes de
# importar o backend, nada nos testes chega perto de um BD real: o
# load_dotenv() não sobrescreve variáveis já definidas, e cada teste usa o
# próprio BD em memória.
os.environ["DATABASE_PATH"] = ":memory:"
os.environ["RSS_URL"] = "http://feed.invalido/rss"

from fastapi import HTTPException  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from backend import crud, database, main, models, schemas  # noqa: E402


def _memory_engine(test_case):
    """Um engine para um BD SQLite novo em memória, descartado no fim do teste."""
    engine = create_engine("sqlite://")
    test_case.addCleanup(engine.dispose)
    return engine


class StatusTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        engine = _memory_engine(self)
        models.Base.metadata.create_all(bind=engine)
        self.db = Session(engine)
        self.addCleanup(self.db.close)

    def _add_headline(self, entry_id, publication_date, **columns):
        self.db.add(
            models.Headline(
                entry_id=entry_id,
                entry_title=f"Notícia {entry_id}",
                entry_publication_date=publication_date,
                entry_summary="resumo",
                entry_link=f"https://exemplo/{entry_id}",
                **columns,
            )
        )
        self.db.commit()

    async def _status(self):
        """O JSON que o endpoint / devolve, passando pelo response_model."""
        status = await main.root(self.db)
        return schemas.StatusSchema.model_validate(status).model_dump(mode="json")

    async def test_bd_vazio(self):
        self.assertEqual(
            await self._status(), {"last_headline": None, "last_posting_date": None}
        )

    async def test_ultima_noticia_e_a_de_publicacao_mais_recente(self):
        # Numa leitura do feed, as entradas são gravadas da mais nova para a
        # mais antiga, então a mais recente fica com o menor ID.
        self._add_headline(1, datetime(2026, 9, 22, 13, 0, tzinfo=timezone.utc))
        self._add_headline(2, datetime(2026, 9, 21, 8, 30, tzinfo=timezone.utc))

        self.assertEqual(
            await self._status(),
            {
                "last_headline": {
                    "entry_id": 1,
                    "entry_title": "Notícia 1",
                    # O SQLite não guarda o fuso, mas a data sai marcada como UTC.
                    "entry_publication_date": "2026-09-22T13:00:00Z",
                    "was_already_posted": False,
                    "posting_error": None,
                },
                "last_posting_date": None,
            },
        )

    async def test_data_da_ultima_postagem_vale_para_qualquer_noticia(self):
        self._add_headline(1, datetime(2026, 9, 22, 13, 0, tzinfo=timezone.utc))
        self._add_headline(
            2,
            datetime(2026, 9, 21, 8, 30, tzinfo=timezone.utc),
            was_already_posted=True,
            posting_date=datetime(2026, 9, 21, 8, 35, 12, tzinfo=timezone.utc),
        )

        status = await self._status()

        self.assertEqual(status["last_headline"]["entry_id"], 1)
        self.assertEqual(status["last_posting_date"], "2026-09-21T08:35:12Z")

    async def test_erro_ao_postar_aparece_no_status_ate_a_postagem_dar_certo(self):
        self._add_headline(1, datetime(2026, 9, 22, 13, 0, tzinfo=timezone.utc))

        await main.report_posting_error(
            schemas.PostingErrorSchema(id=1, error="400 Bad Request"), self.db
        )

        status = await self._status()
        self.assertEqual(status["last_headline"]["posting_error"], "400 Bad Request")
        self.assertFalse(status["last_headline"]["was_already_posted"])
        self.assertIsNone(status["last_posting_date"])

        before_posting = datetime.now(timezone.utc)
        await main.mark_headline_as_read(schemas.EntrySchema(id=1), self.db)

        status = await self._status()
        self.assertIsNone(status["last_headline"]["posting_error"])
        self.assertTrue(status["last_headline"]["was_already_posted"])
        self.assertGreaterEqual(
            datetime.fromisoformat(status["last_posting_date"]), before_posting
        )

    async def test_relatar_erro_de_noticia_inexistente(self):
        with self.assertRaises(HTTPException) as raised:
            await main.report_posting_error(
                schemas.PostingErrorSchema(id=999, error="400 Bad Request"), self.db
            )

        self.assertEqual(raised.exception.status_code, 400)


class AddMissingColumnsTests(unittest.TestCase):
    def test_cria_as_colunas_novas_num_bd_antigo(self):
        engine = _memory_engine(self)
        # A tabela como as versões anteriores do backend a criavam (é o
        # esquema do BD de produção), com uma notícia já postada.
        with engine.begin() as connection:
            connection.execute(
                text(
                    'CREATE TABLE "RSS_Entries" ('
                    "entry_id INTEGER NOT NULL, entry_title VARCHAR, "
                    "entry_publication_date DATETIME, entry_summary VARCHAR, "
                    "entry_link VARCHAR, was_already_posted BOOLEAN, "
                    "PRIMARY KEY (entry_id), UNIQUE (entry_link))"
                )
            )
            connection.execute(
                text(
                    "INSERT INTO \"RSS_Entries\" VALUES (675, 'Notícia antiga', "
                    "'2026-05-15 16:43:59.000000', 'resumo', 'https://exemplo/675', 1)"
                )
            )

        # O que o lifespan do main.py faz ao subir o backend; duas vezes, como
        # em dois restarts seguidos, porque no segundo não há mais nada a criar.
        for _ in range(2):
            models.Base.metadata.create_all(bind=engine)
            database.add_missing_columns(engine)

        with Session(engine) as db:
            headline = db.query(models.Headline).one()
            self.assertEqual(headline.entry_title, "Notícia antiga")
            self.assertIsNone(headline.posting_date)
            self.assertIsNone(headline.posting_error)

            crud.mark_headline_as_read(db, 675)
            self.assertIsInstance(crud.get_last_posting_date(db), datetime)


if __name__ == "__main__":
    unittest.main()
