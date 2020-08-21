import discord
import sqlite3
import sys, os
sys.path.insert(0, os.path.abspath('/...'))
import message_event_definitions as med


async def handle(message, message_event):
    if message_event == med.MessageEvent.on_delete_message:
        await on_delete_message(message)
    if message_event == med.MessageEvent.on_message:
        await on_message(message)


# EVENT HANDLERS

async def on_delete_message(message):
    if message.author.id == 155489418659102720:
        embed = discord.Embed(
            title = 'Recently deleted message',
            description = message.content,
            color = discord.Color.red()
        )

        embed.set_author(name=message.author.name)
        embed.set_thumbnail(url=str(message.author.avatar_url))
        await message.channel.send(embed=embed)

async def on_message(message):
    if (yell_check(message)):
        await handle_yell(message)

# HELPERS

def yell_check(message):
    return (message.content != '' 
            and len(message.content) >= 3
            and len(message.mentions) == 0
            and message.content.replace('\r', '').replace('\n', '') != ''
            and message.content == message.content.upper())

async def handle_yell(message):
    # init check
    db = sqlite3.connect("guilds/160584505776799744/yells.db")
    cursor = db.cursor()
    sql_create_yell_table = ''' CREATE TABLE IF NOT EXISTS yells (
                                id integer PRIMARY KEY,
                                server_id int NOT NULL,
                                author int NOT NULL,
                                message_id int NOT NULL,
                                message_text text NOT NULL,
                                post_date timestamp NOT NULL
                            ); '''
    cursor.execute(sql_create_yell_table)
    db.commit()

    # actual yell handle
    server_id = message.guild.id
    author = message.author.id
    message_id = message.id
    message_text = message.content
    post_date = message.created_at

    cursor.execute(''' INSERT INTO yells(server_id, author, message_id, message_text, post_date) 
                        VALUES(?, ?, ?, ?, ?)''', (server_id, author, message_id, message_text, post_date))
    db.commit()
    cursor.execute('''SELECT * FROM yells ORDER BY RANDOM() LIMIT 1''')
    randomly_selected_message = cursor.fetchone()
    msg = randomly_selected_message[4]

    await message.channel.send(msg)