import discord
import dataset
from message_event_definitions import MessageEvent

class Starboard:
  """
  Required Config Tags:
    [starboard]
    channel_id
    emoji_id
    emoji_count_threshold
  """
  def __init__(self, config):
    self.config = config

  async def handle(self, message, message_event, client):
    match (message_event):
      # Event Unmapping
      case MessageEvent.on_message:
        await self.on_message(message, client)
      case MessageEvent.on_raw_reaction_add:
        await self.on_raw_reaction_add(message, client)

  async def on_message(self, message, client):
    

  async def on_raw_reaction_add(self, react_event, client):
    react_emoji_id = str(react_event.emoji)
    channel_obj = client.get_channel(react_event.channel_id)
    message_obj = await channel_obj.fetch_message(react_event.message_id)
    react_obj = await self.get_message_react_by_id(message_obj, react_emoji_id)

    # behavior checks
    #if (str(channel_obj.id) == self.config.get('starboard', 'channel_id')):
    #  return

    # threshold check
    if (react_emoji_id == self.config.get('starboard', 'emoji_id')
        and react_obj.count >= int(self.config.get('starboard', 'emoji_count_threshold'))
        ):
      # setup
      db = dataset.connect('sqlite:///guilds/{0}/server.db'.format(react_event.guild_id))
      table = db['starboard']
      data = table.find_one(message_id=react_event.message_id)
      starboard_channel = client.get_channel(int(self.config.get('starboard', 'channel_id')))

      # pre-existing data check
      if data == None:
        embed = await self.generate_starboard_embed(message_obj, react_obj)
        starboard_message = await starboard_channel.send(embed=embed)
        table.insert(dict(
          message_id = react_event.message_id,
          stars = react_obj.count,
          starboard_message_id = starboard_message.id))
      else:
        existing_data = table.find_one(message_id=react_event.message_id)
        embed = await self.generate_starboard_embed(message_obj, react_obj)
        starboard_message = await starboard_channel.fetch_message(existing_data['starboard_message_id'])
        new_message = await starboard_message.edit(embed=embed)
        table.upsert(dict(
            message_id = message_obj.id,
            stars = react_obj.count,
            starboard_message_id = starboard_message.id),
          ['mesage_id'])
      return
    
  async def force_add(self, react_event, client):
    """Mostly the same as an on_raw_reaction_add check, but lets the user manually add a message to starboard"""
    react_emoji_id = str(react_event.emoji)
    channel_obj = client.get_channel(react_event.channel_id)
    message_obj = await channel_obj.fetch_message(react_event.message_id)
    react_obj = await self.get_message_react_by_id(message_obj, react_emoji_id)

    # behavior checks
    if (str(channel_obj.id) == self.config.get('starboard', 'channel_id')):
      return
    
    # skip straight to setup
    db = dataset.connect('sqlite:///guilds/{0}/server.db'.format(react_event.guild_id))
    table = db['starboard']
    data = table.find_one(message_id=react_event.message_id)
    starboard_channel = client.get_channel(int(self.config.get('starboard', 'channel_id')))

    # pre-existing data check
    if data == None:
      embed = await self.generate_starboard_embed(message_obj, react_obj)
      starboard_message = await starboard_channel.send(embed=embed)
      table.insert(dict(
        message_id = react_event.message_id,
        stars = react_obj.count,
        starboard_message_id = starboard_message.id))
    else:
      existing_data = table.find_one(message_id=react_event.message_id)
      embed = await self.generate_starboard_embed(message_obj, react_obj)
      starboard_message = await starboard_channel.fetch_message(existing_data['starboard_message_id'])
      new_message = await starboard_message.edit(embed=embed)
      table.upsert(dict(
          message_id = message_obj.id,
          stars = react_obj.count,
          starboard_message_id = starboard_message.id),
        ['mesage_id'])
    return

  async def generate_starboard_embed(self, message, react):
    # initialize embed
    embed = discord.Embed(
        description = message.content,
        color = int(hex(message.channel.id)[0:8], 16)
        )
    
    # set author and icon
    embed.set_author(name=message.author.display_name,
                     icon_url=str(message.author.avatar.url),
                     url='https://discordapp.com/users/{0}'.format(message.author.id))
    
    # metadata setup
    fields = []
    fields.append('➡️ [original message]({0}) in {1}'.format(message.jump_url, message.channel.mention))

    ## image embed
    if len(message.attachments) > 0:
      embed.set_image(url=message.attachments[0].url)
      for file in message.attachments:
        fields.append('📎 [{0}]({1})'.format(file.filename, file.url))

    embed.add_field(name='\u200b',
                value='\n'.join(fields),
                inline=False)
    
    #footer
    embed.set_footer(text='{0} ⭐ ({1}) • {2} UTC'.format(
      str(react.count),
      message.id,
      message.created_at.strftime('%Y-%m-%d at %H:%M')))
    
    return embed

  async def get_message_react_by_id(self, message, emoji_id):
    for r in message.reactions:
      if (str(r) == emoji_id):
         return r