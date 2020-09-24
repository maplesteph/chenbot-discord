import discord
import configparser
import dataset
import re
import sys, os
sys.path.insert(0, os.path.abspath('/...'))
import message_event_definitions as med
from datetime import date

SERVER_ID = 160584505776799744
CONFIG_FILE = 'guilds/' + str(SERVER_ID) + "/serverconfig.ini"
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

async def handle(message, message_event, client):
    if message_event == med.MessageEvent.on_message:
        await on_message(message, client)
    elif message_event == med.MessageEvent.on_delete_message:
        await on_message_delete(message, client)
    elif message_event == med.MessageEvent.on_raw_reaction_add:
        await on_raw_reaction_add(message, client)
    else:
        return

async def on_message(message, client):
    if yell_check(message):
        await handle_yell(message)
    elif message.content == '!wholast':
        await who_yelled(message, client)

async def on_message_delete(message, client):
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
    if (str(channel.id) == config.get('starboard', 'channelID')
        or channel.is_nsfw()):
        return

    if reaction == config.get('starboard', 'emoteID') and reaction_object.count >= 5:
        db = dataset.connect('sqlite:///guilds/' + str(SERVER_ID) + '/server.db')        
        table = db['starboard']

        result = table.find_one(message_id=message.id)
        starboard_channel = client.get_channel(int(config.get('starboard', 'channelID')))
        if result == None:
            embed = await generate_starboard_embed(message, reaction_object)

            starboard_msg = await starboard_channel.send(embed=embed)

            table.insert(dict(
                message_id = message.id,
                stars = reaction_object.count,
                starboard_msg_id = starboard_msg.id))
        else:
            result = table.find_one(message_id=message.id)
            starboard_msg = await starboard_channel.fetch_message(result['starboard_msg_id'])

            data = dict(
                starboard_msg_id = starboard_msg.id,
                stars = reaction_object.count)
            table.upsert(data, ['stardboard_msg_id'])

            await starboard_msg.edit(embed=await generate_starboard_embed(message, reaction_object))
    else:
        return

### HELPERS ###
def yell_check(message):
    # too lazy to update conditions figure it out lol
    return (message.content != ''
            and message.content.replace('\r', '').replace('\n', '') != ''
            and len(message.content) >= 5
            and len(message.content) <= 128
            and len(message.mentions) == 0
            and re.search('[A-Z]+', message.content) != None
            and re.search('[A-Z]+', message.content).group(0) != ''
            and message.content == message.content.upper())

async def handle_yell(message):
    db = dataset.connect('sqlite:///guilds/' + str(SERVER_ID) + '/server.db')
    table = db['yells']
    
    if table.find_one(message_text=message.content) == None: 
        table.insert(dict(
            channel_id = message.channel.id,
            author = message.author.id,
            message_id = message.id,
            message_text = message.content.replace('\r', '').replace('\n', ''),
            post_date = message.created_at
            ))

    result = db.query('''SELECT * FROM yells ORDER BY RANDOM() LIMIT 1''')
    row = result.next()
    msg = row['message_text']
    db.close()

    config['yells']['lastYell'] = str(row['id'])
    with open('serverconfig.ini', 'w') as configfile:
        config.write(configfile)

    await message.channel.send(msg)

async def who_yelled(message, client):
    last_yell_id = config.get('yells', 'lastYell')

    db = dataset.connect('sqlite:///guilds/' + str(SERVER_ID) + '/server.db')
    table = db['yells']
    last_yell = table.find_one(id=last_yell_id)

    if last_yell == None:
        await message.channel.send("Couldn't find the last yell!")

    author = client.get_user(last_yell['author'])
    post_date = last_yell['post_date']
    msg = message.author.fetch_message(last_yell['message_id'])

    embed = discord.Embed(
        description = "{0} taught me that on {1}!".format(author.name, post_date.strftime("%B %d %Y")),
        color = discord.Color.blurple
    )
    embed.add_field(name='\u200b', value ='→ [original message]({0}) in {1}'.format(msg.jump_url, msg.channel.mention))

    await message.channel.send(embed=embed)

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
