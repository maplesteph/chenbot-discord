import discord
import dataset
import re
import message_event_definitions as med

class Yeller:
    def __init__(self, config):
        self.config = config

    async def handle(self, message, message_event, client):
        if message_event == med.MessageEvent.on_message:
            if self.yell_check(message):
                await self.handle_yell(message)
            elif message.content == '!wholast':
                await self.who_yelled(message, client)

    def yell_check(self, message):
        # too lazy to update conditions figure it out lol
        return (message.content != ''
            and message.content.replace('\r', '').replace('\n', '') != ''
            and len(message.content) >= 8
            and len(message.content) <= 128
            and len(message.mentions) == 0
            and re.search('[A-Z]+', message.content) != None
            and re.search('[A-Z]+', message.content).group(0) != ''
            and ':' not in message.content
            and message.content == message.content.upper())

    async def handle_yell(self, message):
        db = dataset.connect('sqlite:///guilds/' + self.config.get('meta', 'id') + '/server.db')
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

        self.config['yells']['lastYell'] = str(row['id'])
        with open('serverconfig.ini', 'w') as configfile:
            self.config.write(configfile)

        await message.channel.send(msg)

    async def who_yelled(self, message, client):
        last_yell_id = self.config.get('yells', 'lastYell')

        db = dataset.connect('sqlite:///guilds/' + self.config.get('meta', 'id') + '/server.db')
        table = db['yells']
        last_yell = table.find_one(id=last_yell_id)

        if last_yell == None:
            await message.channel.send("Couldn't find the last yell!")

        author = client.get_user(last_yell['author'])
        post_date = last_yell['post_date']

        embed = discord.Embed(
            description = "{0} taught me that on {1}!".format(author.name, post_date.strftime("%B %d %Y")),
            color = discord.Color.blurple()
        )

        await message.channel.send(embed=embed)