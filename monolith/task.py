from flask import current_app as app

from flask_login import current_user

from monolith import celeryapp
from monolith.database import Reaction, Story, db


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
