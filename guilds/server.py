import discord
import configparser
from message_event_definitions import MessageEvent

class Server:
  def __init__(self, guild_id):
    self.guild_id = guild_id
    self.server_config_path = '/guilds/{0}/server_config.ini'.format(self.guild_id)
    self.config = configparser.ConfigParser()
    self.config.read(self.server_config_path)

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
