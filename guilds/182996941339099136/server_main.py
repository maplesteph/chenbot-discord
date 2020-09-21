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
    return