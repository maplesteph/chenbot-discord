import sys, os
import discord
import configparser

import message_event_definitions as med
import modules.starboard as sb

#SERVER_ID = 182996941339099136
#CONFIG_FILE = "guilds/" + str(SERVER_ID) + "/serverconfig.ini"

config = configparser.ConfigParser()
config.read('serverconfig.ini')
SERVER_ID = config.get('meta', 'id')

async def handle(message, message_event, client):
    print(SERVER_ID)