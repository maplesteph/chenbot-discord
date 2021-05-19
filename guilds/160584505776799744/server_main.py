import configparser
import message_event_definitions as med
import modules.starboard as starboard
import modules.yeller as yeller

SERVER_ID = str(160584505776799744)
CONFIG_FILE = 'guilds/' + SERVER_ID + "/serverconfig.ini"
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

async def handle(message, message_event, client):
    if message_event == med.MessageEvent.on_message:
        await on_message(message, message_event, client)
    elif message_event == med.MessageEvent.on_raw_reaction_add:
        await on_raw_reaction_add(message, message_event, client)

async def on_message(message, message_event, client):
    if message.channel.id == config.get('misc','peopleCID'):
        return
    else:
        y = yeller.Yeller(config)
        await y.handle(message, message_event, client)

async def on_raw_reaction_add(message, message_event, client):
    sb = starboard.Starboard(config)
    await sb.handle(message, message_event, client)