from flask import Flask, Blueprint
from flask import request, redirect, flash, url_for, render_template

import telegram

from monolith.database import User, db, DATABASE_NAME

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(DATABASE_NAME, convert_unicode=True)
db_telegram_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

telebot = Blueprint('telebot', __name__)

token = "1057812273:AAH0w4miBCIhL-lRV4viJ1-egoA8-rcBrs0"
telegram_bot = telegram.Bot(token)
chat_id = ""

def send_telegram_message(story):
    # TODO: check chat id on database
    telegram_bot.send_message(chat_id, str(story.text))
    pass

def on_start(update, context):
    global token, chat_id
    chat_id = update.message.chat_id
    
    telegram_bot.send_message(chat_id, "Please use /login <username> to receive stories from your follow users")
    pass


def on_login(update, context):
    global token, chat_id
    username = ' '.join(context.args)
    if username == "":
        telegram_bot.send_message(chat_id=update.effective_chat.id, text="Use the command /login <username>")
    else:
        if '@' in username:
            user = db_telegram_session.query(User).filter(User.email == username).first()
        else:
            user = db_telegram_session.query(User).filter(User.username == username).first()

    # Checking if the query returns a user
    if user is None:
        telegram_bot.send_message(chat_id=update.effective_chat.id, text="No user is registered with this username")
    else:
        telegram_bot.send_message(chat_id=update.effective_chat.id, text="Hello {0} You want to receive your follow users stories".format(user.firstname))
    pass