import datetime as dt

from celery import Celery

from flask import Flask

from flask_bootstrap import Bootstrap

from monolith import celeryapp
from monolith.auth import login_manager
from monolith.database import User, db
from monolith.utility.telebot import token, on_message

from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import telegram

def create_app(test=False, database='sqlite:///storytellers.db',
               login_disabled=False):
    app = Flask(__name__)
    Bootstrap(app)
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'ANOTHER ONE'
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKED'] = 'redis://localhost:6379/0'

    app.config['PERMANENT_SESSION_LIFETIME'] = dt.timedelta(minutes=120)
    app.config['SQLALCHEMY_DATABASE_URI'] = database
    app.config['LOGIN_DISABLED'] = login_disabled
    if test:
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['CELERY_ALWAYS_EAGER'] = True

    # initialize Celery
    celery = celeryapp.create_celery_app(app)
    celeryapp.celery = celery

    # initialize Telegram
    updater = Updater(token, use_context = True)
    
    dp = updater.dispatcher
    # function to be executed as soon as 
    dp.add_handler(CommandHandler('start', on_message))
    updater.start_polling()

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

    # Required to avoid circular dependencies
    from monolith.views import blueprints
    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    # create a first admin user
    with app.app_context():
        q = db.session.query(User).filter(User.email == 'example@example.com')
        user = q.first()
        if user is None:
            example = User()
            example.username = 'Admin'
            example.firstname = 'Admin'
            example.lastname = 'Admin'
            example.email = 'example@example.com'
            example.dateofbirth = dt.datetime(2020, 10, 5)
            example.is_admin = True
            example.set_password('admin')
            db.session.add(example)
            db.session.commit()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
