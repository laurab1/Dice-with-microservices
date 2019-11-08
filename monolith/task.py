import datetime as dt
from smtplib import SMTP

from flask import current_app as app

from flask_login import current_user

import monolith.utility.digests as digests
from monolith import celeryapp
from monolith.database import Reaction, Story, User, db


celery = celeryapp.celery


# Celery task to run asynchronously
@celery.task
def add_reaction(reactorid, storyid, react):
    '''
    Performs the add of a reaction to a user's story.
    '''

    # Without this two lines testing raises DetachedInstanceError
    # No explanation still found
    if app.config['TESTING']:
        current_user.id
    s = Story.query.get(storyid)
    if s is not None:
        if react == 1:
            s.likes += 1
        elif s is not None and react == -1:
            s.dislikes += 1
    r = Reaction.query.filter(Reaction.reactor_id == reactorid,
                              Reaction.story_id == storyid).one()
    r.marked = True
    db.session.commit()
    if app.config['TESTING']:
        current_user.id

# another celery task to remove an old reaction
@celery.task
def remove_reaction(storyid, react):
    '''
    Performs the removal of a reaction to a user's story.
    '''

    # Without this two lines testing raises DetachedInstanceError
    # No explanation still found
    if app.config['TESTING']:
        current_user.id
    s = Story.query.get(storyid)
    if s is not None:
        if react == 1:
            s.likes -= 1
        elif s is not None and react == -1:
            s.dislikes -= 1
    db.session.commit()
    if app.config['TESTING']:
        current_user.id


@celery.task
def send_digest():
    '''
    Periodic task that sends to users a digest of the stories that were
    submitted during the last 4 weeks from followed users.
    '''
    
    ids = User.query.all()
    now = dt.datetime.now().replace(minute=0, hour=0, second=0, microsecond=0)
    date_from = now - dt.timedelta(weeks=4)
    date_to = now
    mails = [digests.build_user_digest(u, date_from, date_to) for u in ids]
    address = app.config['SMTP_SERVER_ADDRESS']
    port = app.config['SMTP_SERVER_PORT']
    with SMTP(address, port) as smtp:
        for mail in mails:
            smtp.send_message(mail)
