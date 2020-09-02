import discord
import configparser
import dataset
import sys, os
sys.path.insert(0, os.path.abspath('/...'))
import message_event_definitions as med
from datetime import date

SERVER_ID = 160584505776799744
CONFIG_FILE = 'guilds/' + str(SERVER_ID) + "/serverconfig.ini"
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

async def on_message(message, client):
    if (yell_check(message)):
        await handle_yell(message)

async def on_delete_message(message, client):
    if message.author.id == int(config.get('misc', 'kevinID')):
        embed = discord.Embed(
            title = 'Recently deleted message',
            description = message.content,
            color = discord.Color.red()
        )

        embed.set_author(name=message.author.name)
        embed.set_thumbnail(url=str(message.author.avatar_url))
        await message.channel.send(embed=embed)

async def on_raw_reaction_add(payload, client):
    reaction = str(payload.emoji)
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    reaction_object = await get_reaction_object(message, reaction)
    if str(channel.id) == config.get('starboard', 'channelID'):
        return

    if reaction == config.get('starboard', 'emoteID') and reaction_object.count >= 1:
        db = dataset.connect('sqlite:///guilds/' + str(SERVER_ID) + '/server.db')        
        table = db['starboard']

        result = table.find_one(message_id=message.id)
        if result == None:
            starboard_channel = client.get_channel(int(config.get('starboard', 'channelID')))
            embed = await generate_starboard_embed(message, reaction_object)

            starboard_msg = await starboard_channel.send(embed=embed)

            table.insert(dict(
                message_id = message.id,
                stars = reaction_object.count,
                starboard_msg_id = starboard_msg.id))
        else:
            result = table.find_one(message_id=message.id)
            starboard_msg = await channel.fetch_message(result['starboard_msg_id'])

            data = dict(
                starboard_msg_id = starboard_msg.id,
                stars = reaction_object.count)
            table.update(data, ['stardboard_msg_id'])

            await starboard_msg.edit(embed=generate_starboard_embed(message, reaction_object))
    else:
        return

async def handle(message, message_event, client):
    if message_event == med.MessageEvent.on_message:
        await on_message(message, client)
    elif message_event == med.MessageEvent.on_delete_message:
        await on_delete_message(message, client)
    elif message_event == med.MessageEvent.on_raw_reaction_add:
        await on_raw_reaction_add(message, client)
    else:
        return

### HELPERS ###
def yell_check(message):
    # Conditions:   1. Message must not be blank and more then 3 characters
    #               2. Message must not ping anyone
    #               3. Message must be all caps
    # Also, self author check
    return (message.content != '' 
            and len(message.content) >= 3
            and len(message.mentions) == 0
            and message.content.replace('\r', '').replace('\n', '') != ''
            and message.content == message.content.upper())

async def handle_yell(message):
    db = dataset.connect('sqlite:///guilds/' + str(SERVER_ID) + '/server.db')
    table = db['yells']
    table.insert(dict(
        channel_id = message.channel.id,
        author = message.author.id,
        message_id = message.id,
        message_text = message.content,
        post_date = message.created_at
        ))

    result = db.query('''SELECT * FROM yells ORDER BY RANDOM() LIMIT 1''')
    row = result.next()
    msg = row['message_text']
    db.close()

    await message.channel.send(msg)

async def generate_starboard_embed(message, reaction):
    user = message.author

    embed = discord.Embed(
        description = message.content,
        color = discord.Color.teal()
    )
    embed.set_author(name=user.name, icon_url=str(user.avatar_url))
    embed.add_field(name='\u200b', value ='→ [original message]({0}) in {1}'.format(message.jump_url, message.channel.mention))
    if len(message.attachments) > 0:
        embed.set_image(url=message.attachments[0].url)
    embed.set_footer(text='{0} ⭐ ({1}) • {2} UTC'.format(
        str(reaction.count),
        message.id,
        message.created_at.strftime('%Y-%m-%d at %H:%M')))

    return embed

async def get_reaction_object(message, emoji):
    reactions = message.reactions
    for r in reactions:
        if str(r) == emoji:
            return r