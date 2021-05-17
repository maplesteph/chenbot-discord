import configparser

import message_event_definitions as med
import modules.starboard as starboard
import modules.yeller as yeller

SERVER_ID = str(160584505776799744)
CONFIG_FILE = 'guilds/' + SERVER_ID + "/serverconfig.ini"
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

async def handle(message, message_event, client):
    if message.channel.id == config.get('misc','peopleCID'):
        return
    
    sb = starboard.Starboard(config)
    sb.handle(message, message_event, client)

    y = yeller.Yeller(config)
    y.handle(message, message_event, client)