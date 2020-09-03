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
    if message_event == med.MessageEvent.on_message:
        await on_message(message, client)
    elif message_event == med.MessageEvent.on_raw_reaction_add:
        await on_raw_reaction_add(message, client)
    else:
        return

async def on_message(message, client):
    print("WOW: " + config.sections()[0])
    #print(CONFIG_FILE)
    #print("FEJFOIE")
    if message.author.id == 92392230806884352:
        embed = discord.Embed(
            title = 'Recently deleted message',
            description = message.content,
            color = discord.Color.red()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/746210589193535569/750673146188660736/chingun.mp4")
        embed.add_field(name='\u200b', value='#{0}'.format(message.channel.mention))
        embed.set_author(name = message.author.name)
        await message.channel.send(embed=embed)

async def on_raw_reaction_add(payload, client):
    pog = client.get_channel(payload.channel_id)
    pog2 = await pog.fetch_message(payload.message_id)
    r = pog2.reactions
    for r2 in r:
        print(r2)