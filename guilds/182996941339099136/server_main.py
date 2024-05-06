import configparser
from message_event_definitions import MessageEvent
import modules.starboard as starboard

SERVER_ID = str(182996941339099136)
CONFIG_FILE = 'guilds/' + SERVER_ID + "/server_config.ini"
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

async def handle(message, message_event, client):
  match (message_event):
    # Event Unmapping
    case MessageEvent.on_raw_message_delete:
      await on_raw_message_delete(message, message_event, client)
    case MessageEvent.on_raw_message_edit:
      await on_raw_message_edit(message, message_event, client)
    case MessageEvent.on_raw_reaction_add:
      await on_raw_reaction_add(message, message_event, client)

async def on_raw_message_delete(message, message_event, client):
  return
  
async def on_raw_message_edit(message, message_event, client):
  return

async def on_raw_reaction_add(message, message_event, client):
  sb = starboard.Starboard(config)
  await sb.handle(message, message_event, client)