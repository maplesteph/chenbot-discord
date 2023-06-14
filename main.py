import sys, getopt

import discord
import configparser
import time

from importlib import import_module
import message_event_definitions as med

class Chen(discord.Client):
    def __init__(self, config, debug):
        super().__init__(intents = discord.Intents.default())
        self.config = config
        self.debug = debug
        self.server_rate_limit = int(config.get('discord', 'serverRateLimit'))
        self.server_cooldowns = {}
        self.server_blocks = set()
    
    async def on_ready(self):
        if self.debug:
            print("Now dreaming...")
        else:
            print("Chen woke up!")

    async def on_message(self, message):
        if message.guild == None:
            return
        
        if message.author.bot:
            return

        # "temporary" emergency shutdown command
        if (message.author.id == int(self.config.get('discord', 'globalAdmin')) 
            and message.content == '!quit'):
            await self.close()
            
        if not self.on_cooldown(message.guild.id):
            await self.handle(message, med.MessageEvent.on_message)

    async def on_message_delete(self, message):
        await self.handle(message, med.MessageEvent.on_delete_message)

    async def on_raw_reaction_add(self, payload):
        await self.handle(payload, med.MessageEvent.on_raw_reaction_add)

    async def handle(self, message, message_event):
        try:
            guild_id = str(message.guild.id)
        except AttributeError:
            guild_id = str(message.guild_id)

        try:
            guild_module = import_module("guilds." + guild_id + ".server_main")
            await guild_module.handle(message, message_event, self)
        except ModuleNotFoundError:
            # Received a message in an unconfigured server.
            return

    def on_cooldown(self, guild_id):
        on_cooldown = False
        if guild_id in self.server_cooldowns:
            if time.time() < self.server_cooldowns[guild_id] + self.server_rate_limit:
                on_cooldown = True
        self.server_cooldowns[guild_id] = time.time()
        return on_cooldown

def print_help():
    print("    d, debug        Run as ChenTest")
    print("    l, lumi         Run as Lumi")

def main(argv):
    CONFIG_FILE = "config.ini"
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    token = config.get('discord', 'defaultToken')
    debug = False

    short_opts = "dhl"
    long_opts = ["debug", "help", "lumi"]

    try:
        opts, args = getopt.getopt(argv[1:], short_opts, long_opts)
    except getopt.error as err:
        print(str(err))
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-d", "--debug"):
            debug = True
            token = config.get('discord', 'debugToken')
        elif opt in ("-h", "--help"):
            print_help()
            return
        elif opt in ("-l", "--lumi"):
            token = config.get('discord', 'lumiToken')            

    bot = Chen(config, debug)
    bot.run(token)

main(sys.argv)