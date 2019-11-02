import os
import shutil
from flask import Flask
from flask_bootstrap import Bootstrap
from monolith.database import db, User, Story
from monolith.views import blueprints
from monolith.auth import login_manager
from celery import Celery
import datetime

def create_app(test=False):
    app = Flask(__name__)
    Bootstrap(app)
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'ANOTHER ONE'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///storytellers.db'
    app.config['CELERY_BROKER_URL'] = 'amqp://dice:dice@localhost:5672/myvhost'
    app.config['CELERY_RESULT_BACKEND'] = 'amqp://dice:dice@localhost:5672/myvhost'
    
    #initialize Celery
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)

    app.config['PERMANENT_SESSION_LIFETIME'] =  datetime.timedelta(minutes=120)
    if not test:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///storytellers.db'
    else:
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['LOGIN_DISABLED'] = True

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

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
            example.dateofbirth = datetime.datetime(2020, 10, 5)
            example.is_admin = True
            example.set_password('admin')
            db.session.add(example)
            db.session.commit()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
