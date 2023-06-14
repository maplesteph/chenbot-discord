import configparser
import message_event_definitions as med
import modules.starboard as starboard
import modules.yeller as yeller

SERVER_ID = str(160584505776799744)
CONFIG_FILE = 'guilds/' + SERVER_ID + "/server_config.ini"
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

async def handle(message, message_event, client):
    if message_event == med.MessageEvent.on_raw_reaction_add:
        await on_raw_reaction_add(message, message_event, client)

async def on_raw_reaction_add(message, message_event, client):
    sb = starboard.Starboard(config)
    await sb.handle(message, message_event, client)