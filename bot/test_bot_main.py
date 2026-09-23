#!/usr/bin/env python3

import unittest
from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock, patch

import aiohttp
import discord

import bot_main


class ThreadNameTruncationTests(unittest.TestCase):
    def test_short_title_kept_as_is(self):
        title = "Notícia normal"
        self.assertEqual(bot_main._thread_name(title), title)

    def test_title_exactly_no_limite_kept_as_is(self):
        title = "A" * bot_main.DISCORD_THREAD_NAME_MAX_LENGTH
        self.assertEqual(bot_main._thread_name(title), title)

    def test_long_title_is_truncated_to_limite(self):
        # Título real que travou a fila de produção (151 caracteres).
        title = (
            "Fenachopp 2026 volta à Expoville com estrutura inédita, 40 "
            "bandas, 30 opções de gastronomia, 20 tipos de chope, "
            "tradição e diversão para toda a família"
        )
        self.assertGreater(len(title), bot_main.DISCORD_THREAD_NAME_MAX_LENGTH)

        name = bot_main._thread_name(title)

        self.assertLessEqual(len(name), bot_main.DISCORD_THREAD_NAME_MAX_LENGTH)
        self.assertTrue(name.endswith("…"))
        self.assertTrue(title.startswith(name[:-1]))


class _AsyncContextManager:
    """Imita o objeto que aiohttp retorna de session.get()/post() (que
    funciona como context manager assíncrono, sem precisar de await antes
    do `async with`). Se `error` for passado, ele é lançado ao entrar no
    `async with`, que é onde o aiohttp lança os erros da requisição."""

    def __init__(self, value, error=None):
        self._value = value
        self._error = error

    async def __aenter__(self):
        if self._error is not None:
            raise self._error
        return self._value

    async def __aexit__(self, *_exc_info):
        return False


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    async def json(self):
        return self._payload


class _FakeSession:
    """Substitui aiohttp.ClientSession nos testes: mesma interface usada
    por fetch_and_post (get/post como context managers assíncronos). Os
    POSTs para as URLs em `failing_post_urls` falham como se o backend
    estivesse fora do ar."""

    def __init__(self, get_payloads, failing_post_urls=()):
        self._get_payloads = list(get_payloads)
        self._failing_post_urls = set(failing_post_urls)
        self.post_calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc_info):
        return False

    def get(self, _url):
        return _AsyncContextManager(_FakeResponse(self._get_payloads.pop(0)))

    def post(self, url, json):
        self.post_calls.append((url, json))
        if url in self._failing_post_urls:
            return _AsyncContextManager(
                None, error=aiohttp.ClientConnectionError("backend fora do ar")
            )
        return _AsyncContextManager(None)


def _forum_failing_first_thread():
    """Um fórum em que a criação da primeira thread falha (com o erro que o
    Discord devolve pra um nome longo demais) e a da segunda dá certo."""
    forum = AsyncMock()
    bad_response = SimpleNamespace(status=400, reason="Bad Request")
    forum.create_thread.side_effect = [
        discord.HTTPException(
            bad_response,
            {
                "code": 50035,
                "message": "Invalid Form Body",
                "errors": {"name": {"_errors": [{"message": "Must be between 1 and 100 in length."}]}},
            },
        ),
        AsyncMock(),
    ]
    return forum


class FetchAndPostResilienceTests(unittest.IsolatedAsyncioTestCase):
    HEADLINES = [
        {
            "entry_id": 778,
            "entry_title": "T" * 150,
            "entry_summary": "resumo",
            "entry_link": "https://exemplo/778",
        },
        {
            "entry_id": 779,
            "entry_title": "Notícia normal",
            "entry_summary": "resumo",
            "entry_link": "https://exemplo/779",
        },
    ]

    async def test_um_titulo_invalido_nao_trava_as_demais_noticias(self):
        session = _FakeSession([{"num_new_entries": 0}, self.HEADLINES])
        forum = _forum_failing_first_thread()

        with patch.object(bot_main.aiohttp, "ClientSession", return_value=session):
            await bot_main.fetch_and_post(forum, "http://backend")

        # As duas notícias foram tentadas, apesar da primeira falhar.
        self.assertEqual(forum.create_thread.call_count, 2)
        first_call, second_call = forum.create_thread.call_args_list
        self.assertLessEqual(
            len(first_call.kwargs["name"]), bot_main.DISCORD_THREAD_NAME_MAX_LENGTH
        )
        self.assertEqual(second_call.kwargs["name"], "Notícia normal")

        # O erro da primeira notícia foi relatado ao backend (pro status
        # dele) e só a segunda (que teve thread criada com sucesso) foi
        # marcada como lida.
        self.assertEqual(
            session.post_calls,
            [
                ("http://backend/report_posting_error", {"id": 778, "error": ANY}),
                ("http://backend/mark_headline_as_read", {"id": 779}),
            ],
        )
        self.assertIn(
            "Must be between 1 and 100 in length", session.post_calls[0][1]["error"]
        )

    async def test_falha_ao_relatar_o_erro_nao_trava_as_demais_noticias(self):
        session = _FakeSession(
            [{"num_new_entries": 0}, self.HEADLINES],
            failing_post_urls={"http://backend/report_posting_error"},
        )
        forum = _forum_failing_first_thread()

        with patch.object(bot_main.aiohttp, "ClientSession", return_value=session):
            await bot_main.fetch_and_post(forum, "http://backend")

        # Mesmo sem conseguir relatar o erro da primeira notícia, a segunda
        # foi postada e marcada como lida normalmente.
        self.assertEqual(forum.create_thread.call_count, 2)
        self.assertEqual(
            session.post_calls[-1],
            ("http://backend/mark_headline_as_read", {"id": 779}),
        )


if __name__ == "__main__":
    unittest.main()
