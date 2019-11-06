from flask import Flask, Blueprint
from flask import request, redirect, flash, url_for, render_template
import telegram

from monolith.utility.telegram_tasks import reply_message

telebot = Blueprint('telebot', __name__)

token = "1057812273:AAH0w4miBCIhL-lRV4viJ1-egoA8-rcBrs0"
telegram_bot = telegram.Bot(token)
chat_id = ""

def send_telegram_message(story):
    # TODO: check chat it
    telegram_bot.send_message(chat_id, str(story.text))
    return "OK"


def on_message(update, context):
    global token, chat_id
    chat_id = update.message.chat_id
    # Maybe we want to store token and chat_id to contact this user later
    telegram_bot.send_message(chat_id, "You wrote {}".format(update['message']['text']))
    return "OK"