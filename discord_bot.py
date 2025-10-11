#!/usr/bin/env python 
# 
# Módulo principal do bot do Discord 

import discord_tokens, discord, logging

intents = discord.Intents.default() 
intents.message_content = True 

client = discord.Client(intents=intents)

@client.event 
async def on_ready():
    logging.info(f'Conseguimos logar como {client.user}!')

client.run(discord_tokens.CLIENT_PUBLIC_KEY)
