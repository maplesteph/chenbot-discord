import sys, getopt, discord

import configparser
import time
from importlib import import_module
from message_event_definitions import MessageEvent

class ModularDiscordBot(discord.Client):
  def __init__(self, config, debug):
    super().__init__(intents = discord.Intents.all())
    self.config = config
    self.debug = debug
    self.owner = int(config.get('discord', 'owner_id'))
    self.server_rate_limit = int(config.get('discord', 'server_rate_limit'))
    self.server_cooldowns = {}
    self.server_blocks = set()

  # Setup and Logging
  async def on_ready(self):
    if (self.debug):
      print("Now dreaming...")
    else:
      print("Up and working!")

  # Command/Event Mapping
  async def on_message(self, message):
    if (message.guild == None):
      if (message.author.id == self.owner):
        # global shutdown command
        if (message.content == "die"):
          await self.close()
      else:
        return
    
    if message.author.bot:
      # ignore other bots
      return
    
    #if not self.on_cooldown(message.guild.id):
    await self.handle(message, MessageEvent.on_message)

  async def on_raw_message_delete(self, message):
    await self.handle(message, MessageEvent.on_raw_message_delete)

  async def on_raw_message_edit(self, message):
    await self.handle(message, MessageEvent.on_raw_message_edit)

  async def on_raw_reaction_add(self, message):
    await self.handle(message, MessageEvent.on_raw_reaction_add)

  async def handle(self, message, message_event: MessageEvent):
    try:
      guild_id = str(message.guild.id)
    except AttributeError:
      guild_id = str(message.guild_id)

    try:
      guild_module = import_module('guilds.' + guild_id + '.server_main')
      await guild_module.handle(message, message_event, self)
    except ModuleNotFoundError:
      await message.channel.send(content="There's no configuration for this channel!")
      return

# Startup
def main(argv):
  CONFIG_FILE = 'config.ini'
  config = configparser.ConfigParser()
  config.read(CONFIG_FILE)
  token = config.get('discord', 'default_token')
    
  debug = False
  short_opts = 'dhl'
  long_opts = ['debug', 'help', 'lumi']

  try:
    opts, args = getopt.getopt(argv[1:], short_opts, long_opts)
  except getopt.error as err:
    print(str(err))
    sys.exit(1)
    
  for opt, arg in opts:
    if opt in ('-d', '--debug'):
      debug = True
      token = config.get('discord', 'debug_token')
    elif opt in ('-h', '--help'):
      #print_help()
      return
    elif opt in ('-l', '--lumi'):
      token = config.get('discord', 'lumi_token')

  bot = ModularDiscordBot(config, debug)
  bot.run(token)

def print_help():
  print("    d, debug        Run as ChenTest")
  print("    l, lumi         Run as Lumi")

main(sys.argv)
