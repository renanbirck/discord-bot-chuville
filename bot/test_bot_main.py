#!/usr/bin/env python3

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

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
    do `async with`)."""

    def __init__(self, value):
        self._value = value

    async def __aenter__(self):
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
    por fetch_and_post (get/post como context managers assíncronos)."""

    def __init__(self, get_payloads):
        self._get_payloads = list(get_payloads)
        self.post_calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc_info):
        return False

    def get(self, _url):
        return _AsyncContextManager(_FakeResponse(self._get_payloads.pop(0)))

    def post(self, _url, json):
        self.post_calls.append(json)
        return _AsyncContextManager(None)


class FetchAndPostResilienceTests(unittest.IsolatedAsyncioTestCase):
    async def test_um_titulo_invalido_nao_trava_as_demais_noticias(self):
        headlines = [
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

        session = _FakeSession([{"num_new_entries": 0}, headlines])

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

        with patch.object(bot_main.aiohttp, "ClientSession", return_value=session):
            await bot_main.fetch_and_post(forum, "http://backend")

        # As duas notícias foram tentadas, apesar da primeira falhar.
        self.assertEqual(forum.create_thread.call_count, 2)
        first_call, second_call = forum.create_thread.call_args_list
        self.assertLessEqual(
            len(first_call.kwargs["name"]), bot_main.DISCORD_THREAD_NAME_MAX_LENGTH
        )
        self.assertEqual(second_call.kwargs["name"], "Notícia normal")

        # Só a segunda notícia (que teve thread criada com sucesso) foi
        # marcada como lida.
        self.assertEqual(session.post_calls, [{"id": 779}])


if __name__ == "__main__":
    unittest.main()
