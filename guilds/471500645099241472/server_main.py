import discord
import configparser
import dataset
import sys, os
sys.path.insert(0, os.path.abspath('/...'))
import message_event_definitions as med
import random
from datetime import datetime
from datetime import timedelta

SERVER_ID = 471500645099241472
CONFIG_FILE = 'guilds/' + str(SERVER_ID) + '/serverconfig.ini'
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

command_prefix = '.'

async def on_message(message, client):
    if message.content != '' and message.content[0] == command_prefix:
        await handle_command(message, client)

async def slots(message, client):
    params = message.content.split(' ') # where [0] is the command
    db = dataset.connect('sqlite:///guilds/' + str(SERVER_ID) + '/server.db')

    if len(params) == 1: #no parameter
        await slots_check(message, db)
        db.close()
        return
    if params[1] == '-h':
        await post_help(message, client)
        db.close()
        return

    table = db['slots']

    user = message.author
    user_row = table.find_one(id = user.id)
    if user_row == None:
        await slots_check(message, db)
        db.close()
        return

    bet = int(params[1])
    if bet > int(user_row['money']):
        await message.channel.send("Nice try, bitch")
        db.close()
        return

    odds = 50
    if len(params) > 2:
        odds = int(params[2])
        if odds > 80:
            await message.channel.send("Try harder, coward")
            db.close()
            return

    pull = random.randint(0, 100)
    threshold = 100 - odds
    if pull > threshold:
        winnings = int(bet * (100 / odds))
        money = int(user_row['money'] - bet + winnings)
        msg = "{0}: You won! ({1} > {2}) (+{3}, you have {4} Poggers)".format(user.name, pull, threshold, winnings, money)
    else:
        money = int(user_row['money'] - bet)
        msg = "{0}: Better luck next time! ({1} <= {2}) (-{3}, you have {4} Poggers)".format(user.name, pull, threshold, bet, money)
    data = dict(id = user.id, money = money)
    table.upsert(data, ['id'])
    db.close()

    await message.channel.send(msg)

async def daily(message, client):
    db = dataset.connect('sqlite:///guilds/' + str(SERVER_ID) + '/server.db')
    table = db['slots']
    await slots_check(message, db)
    
    user = message.author
    user_row = table.find_one(id = user.id)
    if (user_row['daily'] == datetime.date(datetime.now())):
        await message.channel.send("{0}: You have already claimed today's login bonus.".format(user.name))
    else:
        money = int(user_row['money']) + 500
        data = dict(id = user.id, money = money, daily = datetime.date(datetime.now()))
        table.upsert(data, ['id'])
        await message.channel.send("{0}: You've claimed your daily login bonus! (+500 Poggers)".format(user.name))
    db.close()

async def slots_check(message, db):
    user = message.author
    table = db['slots']
    user_row = table.find_one(id = user.id)
    if user_row == None:
        yesterday = datetime.date(datetime.now() - timedelta(days=1))
        table.upsert(dict(id = user.id, money = 2000, daily = yesterday), ['id'])
        await message.channel.send("{0}: Welcome to the slots! You've been given a starting balance of 2000 Poggers. For rolling help, type .roll -h".format(user.name))

async def check_money(message, client):
    db = dataset.connect('sqlite:///guilds/' + str(SERVER_ID) + '/server.db')
    table = db['slots']
    await slots_check(message, db)

    user = message.author
    user_row = table.find_one(id = user.id)
    await message.channel.send("{0}: You have {1} Poggers".format(user.name, user_row['money']))
    db.close()

async def post_help(message, client):
    user = message.author
    dm_channel = await user.create_dm()
    await dm_channel.send("you can do .roll [amount] or .roll [amount] [odds], where odds is out of 100\n"
                            "you are rewarded based on your odds, so if your odds are 30 , then you will be rewarded (100 / 30) * bet amount\n"
                            "you can claim 500 points daily with .daily (i plan to make dailies more rewarding soon)\n"
                            "i don't remember anything else off the top of my head")

async def handle_command(message, client):
    command = message.content[1:].split(' ')[0]
    if command == 'roll' or command == 'r':
        await slots(message, client)
    elif command == 'daily' or command == 'd':
        await daily(message, client)
    elif command == 'my':
        await check_money(message, client)
    else:
        return

async def handle(message, message_event, client):
    if message_event == med.MessageEvent.on_message:
        await on_message(message, client)
    else:
        return