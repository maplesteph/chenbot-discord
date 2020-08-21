import discord
import sys, os
sys.path.insert(0, os.path.abspath('/...'))
import message_event_definitions as med

async def handle(message, message_event):
    if message.author.id == 92392230806884352:
        embed = discord.Embed(
            title = 'Recently deleted message',
            description = message.content,
            color = discord.Color.red()
        )

        embed.set_author(name = message.author.name)
        await message.channel.send(embed=embed)