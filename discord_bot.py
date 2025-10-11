#!/usr/bin/env python 
# 
# Módulo principal do bot do Discord 
import discord_tokens, discord, logging, database, config 
from discord.ext import tasks 
FORUM_ID=1278119278024851507  # eventos-joinville no ChuVille
UPDATE_DELAY=60 # De quantos em quantos minutos verificar?

def main():

    intents = discord.Intents.default() 
    intents.message_content = True 
    intents.members = True 

    client = discord.Client(intents=intents)

    @client.event 
    async def on_ready():
        logging.info(f"Conseguimos logar como {client.user}!")
        post_new_events.start()
        logging.info(f"Bot no ar! Irá atualizar a cada {config.UPDATE_DELAY} minutos")

    @tasks.loop(minutes=config.UPDATE_DELAY)
    async def post_new_events():
        db = database.Database()

        logging.info(f"Hora de ver se aconteceu algum evento novo!")
        forum_channel = client.get_channel(config.FORUM_ID)
        if isinstance(forum_channel, discord.ForumChannel):
            latest_headline = db.get_latest_headline()
            if not latest_headline["was_already_posted"]:
                text = (f'**{latest_headline["post_title"]}**\n'
                        f'{latest_headline["post_summary"]}\n'
                        f'Saiba mais: {latest_headline["post_link"]}')

                new_thread = await forum_channel.create_thread(name=latest_headline["post_title"], content=text)
                db.mark_headline_as_read()
            else:
                logging.info(f"A entrada id = {latest_headline["post_id"]} já foi postada anteriormente.")

        else:
            logging.critical(f"O ID informado {config.FORUM_ID} não é de um fórum!")
            return 

    client.run(discord_tokens.CLIENT_PUBLIC_KEY)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(funcName)s %(message)s',
                        datefmt='%Y/%m/%d %I:%M:%S %p',
                        level=logging.INFO)
    main()
