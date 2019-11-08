import datetime as dt

from celery.schedules import crontab

from flask import Flask

from flask_bootstrap import Bootstrap

from monolith import celeryapp
from monolith.auth import login_manager
from monolith.database import DATABASE_NAME, User, db
from monolith.utility.telebot import create_bot, on_login, on_start, token

from telegram.ext import CommandHandler, Updater


def create_app(test=False, database=DATABASE_NAME,
               login_disabled=False, test_telegram=False):
    '''
    Prepares initializes the application and its utilities.
    '''
    app = Flask(__name__)
    Bootstrap(app)
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'ANOTHER ONE'
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKED'] = 'redis://localhost:6379/0'
    # Specifies the mail from where digests are sent
    app.config['SERVER_MAIL'] = 'digest@localhost'
    # The address of the SMTP server
    app.config['SMTP_SERVER_ADDRESS'] = 'localhost'
    # The port of the SMTP server
    app.config['SMTP_SERVER_PORT'] = 8025
    app.config['CELERY_TIMEZONE'] = 'Europe/Rome'
    app.config['PERMANENT_SESSION_LIFETIME'] = dt.timedelta(minutes=120)
    app.config['SQLALCHEMY_DATABASE_URI'] = database
    app.config['LOGIN_DISABLED'] = login_disabled
    app.config['CELERYBEAT_SCHEDULE'] = {
        'monthly-digest': {
            'task': 'monolith.task.send_digest',
            # Scheduled for the first day of each month
            'schedule': crontab(day_of_month='1'),
            # Scheduled every 10 seconds
            # 'schedule': 10.0,
        }
    }

    if test:
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['CELERY_ALWAYS_EAGER'] = True
        app.config['SMTP_SERVER_ADDRESS'] = 'localhost'
        app.config['SMTP_SERVER_PORT'] = 8025
        # Disables periodic task
        app.config['CELERYBEAT_SCHEDULE'] = {}
    if test_telegram:
        app.config['TELEGRAM_TESTING'] = True

    # Celery initialization
    celery = celeryapp.create_celery_app(app)
    celeryapp.celery = celery

    # Initialization of the DB and login manager
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = '/login'
    db.create_all(app=app)

    if not test or (test and test_telegram):
        # initialize Telegram
        create_bot(mock=test_telegram)
        updater = Updater(token, use_context=True)
        dp = updater.dispatcher

        # Add functions to the dispatcher.
        # When a function such as start is launched on telegram it will run the
        # corresponding function
        dp.add_handler(CommandHandler('start', on_start))
        dp.add_handler(CommandHandler('login', on_login))
        updater.start_polling()
        app.config['TELEGRAM_UPDATER'] = updater

    # Required to avoid circular dependencies
    from monolith.views import blueprints
    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    # Registration of the error handlers
    from monolith.views import errors
    app.register_error_handler(400, errors.bad_request)
    app.register_error_handler(401, errors.unauthorized)
    app.register_error_handler(403, errors.forbidden)
    app.register_error_handler(404, errors.page_not_found)
    app.register_error_handler(410, errors.gone)

    # Creation of an admin user
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
