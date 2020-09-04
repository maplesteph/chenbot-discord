import discord
import configparser
import time
from importlib import import_module
import message_event_definitions as med

CONFIG_FILE = "config.ini"

class Chen(discord.Client):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.server_rate_limit = int(config.get('discord', 'serverRateLimit'))
        self.server_cooldowns = {}
        self.server_blocks = set()
    
    async def on_ready(self):
        if (self.user.id == int(config.get('discord', 'chenTestID'))):
            print("Now dreaming...")
        else:
            print("Chen woke up!")

    async def on_message(self, message):
        if message.guild == None:
            return
        
        if message.author.bot:
            return

        #temporary emergency shutdown command
        if (message.author.id == int(self.config.get('discord', 'globalAdmin')) 
            and message.content == '!quit'):
            await self.close()
            
        if not self.on_cooldown(message.guild.id):
            await self.handle(message, med.MessageEvent.on_message)

    async def on_delete_message(self, message):
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
            print(".", end="")
            # Received a message in an unconfigured server.
            # Won't print anything here to avoid log clutter.

    def on_cooldown(self, guild_id):
        on_cooldown = False
        if guild_id in self.server_cooldowns:
            if time.time() < self.server_cooldowns[guild_id] + self.server_rate_limit:
                on_cooldown = True
        self.server_cooldowns[guild_id] = time.time()
        return on_cooldown
            

config = configparser.ConfigParser()
config.read(CONFIG_FILE)
token = config.get('discord', 'token')

bot = Chen(config)
bot.run(token)