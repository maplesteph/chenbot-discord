import discord
import dataset
import message_event_definitions as med

class Starboard:
    def __init__(self, config):
        self.config = config

    async def handle(self, message, message_event, client):
        if message_event == med.MessageEvent.on_raw_reaction_add:
            await self.on_raw_reaction_add(message, client)

    async def on_raw_reaction_add(self, payload, client):
        reaction = str(payload.emoji)
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reaction_object = await self.get_reaction_object(message, reaction)
        if (str(channel.id) == self.config.get('starboard', 'channelID')
            or channel.is_nsfw()):
            return
        if reaction == self.config.get('starboard', 'emoteID') and reaction_object.count >= int(self.config.get('starboard', 'threshold')):
            db = dataset.connect('sqlite:///guilds/' + self.config.get('meta', 'id') + '/starboard/server.db')
            table = db['starboard']

            result = table.find_one(message_id=message.id)

            starboard_channel = client.get_channel(int(self.config.get('starboard', 'channelID')))
            
            if result == None:
                embed = await self.generate_starboard_embed(message, reaction_object)
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

                await starboard_msg.edit(embed=await self.generate_starboard_embed(message, reaction_object))
        else:
            return

    async def generate_starboard_embed(self, message, reaction):
        embed = discord.Embed(
            description = message.content,
            color = discord.Color.teal()
        )
        embed.set_author(name=message.author.name, icon_url=str(message.author.avatar_url))
        embed.add_field(name='\u200b', value='→ [original message]({0}) in {1}'.format(message.jump_url, message.channel.mention))
        if len(message.attachments) > 0:
            embed.set_image(url=message.attachments[0].url)
        embed.set_footer(text='{0} ⭐ ({1}) • {2} UTC'.format(
            str(reaction.count),
            message.id,
            message.created_at.strftime('%Y-%m-%d at %H:%M')))

        return embed

    async def get_reaction_object(self, message, emoji):
        reactions = message.reactions
        for r in reactions:
            if str(r) == emoji:
                return r