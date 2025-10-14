#!/usr/bin/env python
#
# Módulo principal do bot do Discord
import discord_tokens  # type: ignore
import discord
import logging
import database
import config
import rss
from discord.ext import tasks


def main():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logging.info("Conseguimos logar como %s!", client.user)
        post_new_events.start()
        logging.info("Bot no ar! Irá atualizar a cada %d minutos", config.UPDATE_DELAY)

    @tasks.loop(minutes=config.UPDATE_DELAY)
    async def post_new_events():
        rss.get_new_events()

        db = database.Database()

        logging.info("Hora de ver se aconteceu algum evento novo!")
        forum_channel = client.get_channel(config.FORUM_ID)
        if isinstance(forum_channel, discord.ForumChannel):
            latest_headline = db.get_latest_headline()
            text = (
                f"**{latest_headline['post_title']}**\n"
                f"{latest_headline['post_summary']}\n"
                f"Saiba mais: {latest_headline['post_link']}"
            )

            await forum_channel.create_thread(
                name=latest_headline["post_title"], content=text
            )
            db.mark_headline_as_read(latest_headline["post_id"])

        else:
            logging.critical("O ID informado %d não é de um fórum!", config.FORUM_ID)
            return

    client.run(discord_tokens.CLIENT_PUBLIC_KEY)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(funcName)s %(message)s",
        datefmt="%Y/%m/%d %I:%M:%S %p",
        level=logging.INFO,
    )
    main()
