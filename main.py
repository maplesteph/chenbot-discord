import discord
import auth

import time
from importlib import import_module

import message_event_definitions as med

client = discord.Client()
server_cooldowns = {}
server_blocks = set()
server_rate_limit = 3 # seconds

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    guild_id = str(message.guild.id)
    if guild_id in server_cooldowns:
        if time.time() < server_cooldowns[guild_id] + server_rate_limit:
            return
    server_cooldowns[guild_id] = time.time()

    await handle(message, med.MessageEvent.on_message)

@client.event
async def on_delete_message(message):
    await handle(message, med.MessageEvent.on_delete_message)
    
@client.event
async def on_ready():
    print("Chen woke up!")
    print("----------------")

async def handle(message, message_event):
    guild_id = str(message.guild.id)
    try:
        guild_module = import_module("guilds." + guild_id + ".server_main")
        await guild_module.handle(message, message_event)
    except ModuleNotFoundError:
        print(".", end="")
        # Received a message in an unconfigured server.
        # Won't print anything here to avoid log clutter.

client.run(auth.TOKEN)