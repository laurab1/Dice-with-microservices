from __future__ import absolute_import, unicode_literals
from celery import shared_task
from monolith.database import *

#celery task to run asynchronously
@shared_task
def add_reaction(reaction, storyid, react):
    s = Story.query.filter_by(id=storyid)
    if s.first() != None:
        if react == 1:
            s.first().likes += 1
        elif s.first() != None and react == -1:
            s.first().dislikes += 1
    reaction.marked = True
    db.session.commit()
    
#another celery task to remove an old reaction
@shared_task
def remove_reaction(storyid, react):
    s = Story.query.filter_by(id=storyid)
    if s.first() != None:
        if react == 1:
            s.first().likes -= 1 #TODO: remove the previous vote and add the new one to the queue
        elif s.first() != None and react == -1:
            s.first().dislikes -= 1
    db.session.commit()