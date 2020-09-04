import discord
import sys, os
import configparser
sys.path.insert(0, os.path.abspath('/...'))
import message_event_definitions as med

SERVER_ID = 182996941339099136
CONFIG_FILE = "guilds/" + str(SERVER_ID) + "/serverconfig.ini"

config = configparser.ConfigParser()
config.read(CONFIG_FILE)


async def handle(message, message_event, client):
    if message_event == med.MessageEvent.on_message:
        await on_message(message, client)
    else:
        return

async def on_message(message, client):
    await message.channel.send("Received!")