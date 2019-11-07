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

def send_telegram_message(story, user_id):
    # Get my user so that I can find my followers
    me = db.session.query(User).filter(User.id == user_id).first()

    for user in me.follows:
        # Retrieving follower chat id
        if user.telegram_chat_id is not None:
            telegram_bot.send_message(user.telegram_chat_id, story.text)
    pass

def on_start(update, context):
    chat_id = update.message.chat_id
    telegram_bot.send_message(chat_id, "Please use /login <username> to receive stories from your follow users")
    pass


def on_login(update, context):
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
        # Store chat id on the db
        try:
            user.telegram_chat_id = update.message.chat_id
            db_telegram_session.commit()
            telegram_bot.send_message(chat_id=update.effective_chat.id, text="Hello {0}. You will receive your follow users stories".format(user.firstname))
        except Exception:
            db_telegram_session.rollback()
            telegram_bot.send_message(chat_id=update.effective_chat.id, text="An error has occured while saving your chat id".format(user.firstname))
    pass