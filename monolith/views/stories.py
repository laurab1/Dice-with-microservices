from flask import Blueprint, redirect, render_template, request
from monolith.database import db, Story, Reaction
from monolith.auth import admin_required, current_user
from flask_login import (current_user, login_user, logout_user, login_required)
from monolith.utility.diceutils import *
from monolith.forms import *
from monolith.classes.DiceSet import *

stories = Blueprint('stories', __name__)


@stories.route('/newStory', methods=['GET', 'POST'])
@login_required
def _newstory():
    form = StoryForm()
    if request.method == 'POST':
        diceset = request.form['diceset']
        # if dice set selected #
        if diceset is not None:
            diceset = DiceSet(diceset, 6)
            roll = diceset.throw_dice()
            return render_template("new_story.html", dice=roll, form=form)
        else:
            if form.validate_on_submit():
                # new story inserted #
                # TODO: write a story on the rolled dice #
                return render_template("stories.html")

    if request.method == 'GET':
        return render_template("new_story.html", diceset=get_dice_sets_lsit())


@stories.route('/stories')
def _stories(message=''):
    allstories = db.session.query(Story)
    return render_template("stories.html", message=message, stories=allstories,
                           like_it_url="http://127.0.0.1:5000/stories/")


@stories.route('/stories/<storyid>/<int:react>')
@login_required
def _like(storyid, react):
    q = Reaction.query.filter_by(reactor_id=current_user.id, story_id=storyid)
    if q.first() is None or react != q.first().reaction_val:
        if q.first() != None and react != q.first().reaction_val:
            #CHECK
            if q.first().marked:
                s = Story.query.filter_by(story_id=storyid)
                #TODO: remove the previous vote and add the new one to the queue
            db.session.delete(q.first())
            db.session.commit()
        new_reaction = Reaction()
        new_reaction.reactor_id = current_user.id
        new_reaction.story_id = storyid
        new_reaction.reaction_val = react
        #new_like.liked_id = authorid
        db.session.add(new_reaction)
        db.session.commit()
        message = 'Got it!'
        #TODO: here the like/dislike is performed, but still not counted.
        #we need to update the form by showing the performed like/dislike
        #to the user, yet counting votes asynchronously
    else:
        message = 'You\'ve already voted this story!'
    return _stories(message)

