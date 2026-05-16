#!/usr/bin/env python3

import logging
from os import environ

import discord
import requests
from discord.ext import tasks
from dotenv import load_dotenv


def bot_main():
    load_dotenv()

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    client = discord.Client(intents=intents)

    # Inicialização do bot
    @client.event
    async def on_ready():
        logging.info("Conseguimos lugar como %s!", client.user)
        post_new_events.start()
        logging.info(
            "Bot no ar! Irá atualizar a cada %d minutos.", int(environ["UPDATE_DELAY"])
        )

    # A rotina principal
    @tasks.loop(minutes=int(environ["UPDATE_DELAY"]))
    async def post_new_events():
        try:
            forum = client.get_channel(int(environ["FORUM_ID"]))
        except:
            logging.fatal(
                "Erro encontrando o canal onde postar! Verifique o arquivo .env."
            )
            return

        logging.info("Vendo se aconteceu algo novo...")
        new_request = requests.get(environ["BACKEND_TARGET"] + "/fetch_headlines")
        new_headlines_count = new_request.json()["num_new_entries"]
        if new_headlines_count == 0:  # Nada de novo! Passar adiante.
            logging.info(
                "Nenhuma nova notícia! Vamos ver se tem alguma notícia pendente."
            )
        else:
            logging.info("%d novas notícias.", new_headlines_count)

        pending_headlines = requests.get(
            environ["BACKEND_TARGET"] + "/get_unposted_headlines"
        ).json()

        # Ver se ficou algo pendente (não postado)
        if (num_headlines := len(pending_headlines)) == 0:
            logging.info("Não há nenhuma notícia pendente.")
        else:
            logging.info("%d notícias estão na fila.", num_headlines)
            for headline in pending_headlines:
                logging.info("Processando notícia %d.", headline["entry_id"])
                text = (
                    f"**{headline['entry_title']}**\n"
                    f"{headline['entry_summary']}\n"
                    f"Saiba mais: {headline['entry_link']}"
                )

                await forum.create_thread(name=headline["entry_title"], content=text)

                mark_as_read = requests.post(
                    environ["BACKEND_TARGET"] + "/mark_headline_as_read",
                    json={"id": headline["entry_id"]},
                )

                if mark_as_read.status_code == 200:
                    logging.info("Entrada %d marcada como lida", headline["entry_id"])

    # Agora, de fato rodar o bot
    logging.info("Iniciando a execução do bot.")
    client.run(environ["CLIENT_PUBLIC_KEY"])


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(funcName)s %(message)s",
        datefmt="%Y/%m/%d %I:%M:%S %p",
        level=logging.INFO,
    )
    bot_main()
