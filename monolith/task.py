from monolith import celeryapp
from monolith.database import Reaction, Story, db


celery = celeryapp.celery


# celery task to run asynchronously
@celery.task
def add_reaction(reactorid, storyid, react):
    s = Story.query.filter_by(id=storyid)
    if s.first() is not None:
        if react == 1:
            s.first().likes += 1
        elif s.first() is not None and react == -1:
            s.first().dislikes += 1
    r = Reaction.query.filter(Reaction.reactor_id == reactorid,
                              Reaction.story_id == storyid).one()
    r.marked = True
    db.session.commit()

# another celery task to remove an old reaction
@celery.task
def remove_reaction(storyid, react):
    s = Story.query.get(storyid)
    if s is not None:
        if react == 1:
            # TODO: remove the previous vote and add the new one to the queue
            s.likes -= 1
        elif s is not None and react == -1:
            s.dislikes -= 1
    db.session.commit()
