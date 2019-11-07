import datetime as dt
from random import randint

from flask import Blueprint, abort, url_for
from flask import jsonify, redirect, render_template, request

from flask_login import current_user, login_required
from monolith.database import User

telebot = Blueprint('telebot', __name__)


@telebot.route('/bot/register', methods=['POST'])
def register():
    username = request.args.get('username')
    tel_id = request.args.get('tel_id')
    if username is not None and tel_id is not None:
        user = db.session.query(User).filter_by(username=username).one_or_none()
        if user is not None:
            user.tel_id = tel_id
            return 200
        else:
            abort(404)
    abort(400)
    
# Process webhook calls
@telebot.route(WEBHOOK_URL_PATH, methods=['GET', 'POST'])
def webhook():
    print(flask.request.headers)
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        print('You NOT made it!')
        flask.abort(403)