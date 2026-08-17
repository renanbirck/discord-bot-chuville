#!/usr/bin/env python3

import logging
from os import environ

import aiohttp
import discord
from discord.ext import tasks
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def bot_main():
    load_dotenv()

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    client = discord.Client(intents=intents)
    backend = environ["BACKEND_TARGET"]

    # Inicialização do bot
    @client.event
    async def on_ready():
        logger.info("Conseguimos lugar como %s!", client.user)
        # on_ready dispara de novo a cada reconexão; start() duplicado lançaria erro.
        if not post_new_events.is_running():
            post_new_events.start()
        logger.info(
            "Bot no ar! Irá atualizar a cada %d minutos.", int(environ["UPDATE_DELAY"])
        )

    # A rotina principal
    @tasks.loop(minutes=int(environ["UPDATE_DELAY"]))
    async def post_new_events():
        # Qualquer exceção que escapar daqui mata o tasks.loop silenciosamente,
        # então tratamos tudo (inclusive erros lendo o .env) e tentamos de novo
        # no próximo ciclo.
        try:
            # get_channel não lança exceção quando o canal não existe: retorna None.
            forum = client.get_channel(int(environ["FORUM_ID"]))
            if forum is None:
                logger.error(
                    "Não achei o canal com ID %s! Verifique o arquivo .env.",
                    environ["FORUM_ID"],
                )
                return

            await fetch_and_post(forum)
        except Exception:
            logger.exception(
                "Erro ao buscar/postar notícias; tentando de novo no próximo ciclo."
            )

    async def fetch_and_post(forum):
        logger.info("Vendo se aconteceu algo novo...")

        async with aiohttp.ClientSession(
            raise_for_status=True, timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            async with session.get(backend + "/fetch_headlines") as response:
                new_headlines_count = (await response.json())["num_new_entries"]

            if new_headlines_count == 0:  # Nada de novo! Passar adiante.
                logger.info(
                    "Nenhuma nova notícia! Vamos ver se tem alguma notícia pendente."
                )
            else:
                logger.info("%d novas notícias.", new_headlines_count)

            async with session.get(backend + "/get_unposted_headlines") as response:
                pending_headlines = await response.json()

            # Ver se ficou algo pendente (não postado)
            if (num_headlines := len(pending_headlines)) == 0:
                logger.info("Não há nenhuma notícia pendente.")
                return

            logger.info("%d notícias estão na fila.", num_headlines)
            for headline in pending_headlines:
                logger.info("Processando notícia %d.", headline["entry_id"])
                text = (
                    f"**{headline['entry_title']}**\n"
                    f"{headline['entry_summary']}\n"
                    f"Saiba mais: {headline['entry_link']}"
                )

                await forum.create_thread(name=headline["entry_title"], content=text)

                # A thread já foi criada no Discord neste ponto; se marcar como
                # lida falhar, não podemos deixar a exceção abortar o loop e
                # pular as demais notícias pendentes deste ciclo. Essa notícia
                # em particular pode ser postada de novo no próximo ciclo (o
                # backend não saberá que ela já foi postada), mas ao menos as
                # outras seguem sendo processadas normalmente.
                try:
                    async with session.post(
                        backend + "/mark_headline_as_read",
                        json={"id": headline["entry_id"]},
                    ):
                        logger.info(
                            "Entrada %d marcada como lida", headline["entry_id"]
                        )
                except aiohttp.ClientError:
                    logger.exception(
                        "Falha ao marcar a entrada %d como lida; ela pode ser "
                        "postada de novo no próximo ciclo.",
                        headline["entry_id"],
                    )

    # Agora, de fato rodar o bot
    logger.info("Iniciando a execução do bot.")
    client.run(environ["CLIENT_PUBLIC_KEY"])


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(funcName)s %(message)s",
        datefmt="%Y/%m/%d %I:%M:%S %p",
        level=logging.INFO,
    )
    bot_main()
