from monolith.database import User
# from monolith.utility.mockbot import Mockbot
from ptbtest import Mockbot

import requests

import telegram


token = '1057812273:AAH0w4miBCIhL-lRV4viJ1-egoA8-rcBrs0'
telegram_bot = None


def create_bot(mock=False):
    global telegram_bot

    if mock:
        telegram_bot = Mockbot()
    else:
        telegram_bot = telegram.Bot(token)
    return telegram_bot


def send_telegram_message(story, user_id):
    # Get my user so that I can find my followers
    me = User.query.get(user_id)

    for user in me.followed:
        # Retrieving follower chat id
        if user.telegram_chat_id is not None:
            telegram_bot.send_message(user.telegram_chat_id, story.text)


def on_start(update, context):
    chat_id = update.message.chat_id
    return telegram_bot.send_message(
        chat_id, 'Please use /login <username> to receive stories from your '
                 'followed users')


def on_login(update, context):
    chat_id = update.effective_chat.id
    username = ' '.join(context.args)
    if username == '':
        return telegram_bot.send_message(
            chat_id=chat_id,
            text='Use the command /login <username>')

    try:
        reply = requests.post('http://localhost:5000/bot/register',
                              data={'username': username, 'chat_id': chat_id})
    except Exception:
        return telegram_bot.send_message(
            chat_id=chat_id,
            text='Server is currently not reachable')

    if reply.status_code == 200:
        return telegram_bot.send_message(
            chat_id=chat_id,
            text='You will now receive updates about followed users')
    else:
        return telegram_bot.send_message(
            chat_id=chat_id, text='No user is registered with this username')
