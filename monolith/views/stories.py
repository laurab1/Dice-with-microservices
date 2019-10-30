from flask import Blueprint, redirect, render_template, request, abort, jsonify
from monolith.database import db, Story, Like
from flask_login import (current_user, login_user, logout_user, login_required)
from flask import current_app as app
from random import randrange
import datetime

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
        if form.validate_on_submit():
            # new story inserted #
            # TODO: write a story on the rolled dice #
            return render_template("stories.html")

    if request.method == 'GET':
        return render_template("new_story.html", diceset=get_dice_sets_lsit())


@stories.route('/rollDice', methods=['GET'])
@login_required
def _rollDice():
    form = StoryForm()
    diceset = 'standard' if request.args.get('diceset') is None else request.args.get('diceset')
    dicenum = 6 if request.args.get('dicenum') is None else int(request.args.get('dicenum'))

    try:
        dice = DiceSet(diceset, dicenum)
        roll = dice.throw_dice()
    except Exception as e:
        abort(400)

    if app.config['TESTING']==True:
        return jsonify(roll)
    else:
        return render_template("new_story.html", dice=roll, form=form)


@stories.route('/stories')
def _stories(message=''):
    allstories = db.session.query(Story)
    return render_template("stories.html", message=message, stories=allstories,
                           like_it_url="http://127.0.0.1:5000/stories/like/")


@stories.route('/stories/<storyid>', methods=['GET'])
def _get_story(storyid, message=''):
    story = db.session.query(Story).filter_by(id=storyid)
    id = None

    if story.first() is None:
        message = 'story not found!'
    else:
        id = story.first().id
    
    #TODO: change like_it_url
    if app.config["TESTING"] == True:
        return jsonify({'story': str(id), 'message' : message})
    else:
        return render_template("stories.html", message=message, stories=story, like_it_url="http://127.0.0.1:5000/stories/like/")

@stories.route('/stories/<storyid>', methods=['GET'])
def _get_random_recent_story(message=''):
    #recent story = story of today
    current_time = datetime.datetime.now()
    recent_stories = db.session.query(Story).filter_by(date=current_time)

    #get a random one
    i = randrange(0, recent_stories.count() - 1)

    if recent_stories.first() is None:
        message = 'no recent stories'
    random_story = recent_stories.get(i)

    #TODO: change like_it_url
    if app.config["TESTING"] == True:
        return jsonify({'story': str(random_story.id), 'message' : message})
    else:
        return render_template("stories.html", message=message, stories=random_story, like_it_url="http://127.0.0.1:5000/stories/like/")



@stories.route('/stories/like/<authorid>/<storyid>')
@login_required
def _like(authorid, storyid):
    q = Like.query.filter_by(liker_id=current_user.id, story_id=storyid)
    if q.first() != None:
        new_like = Like()
        new_like.liker_id = current_user.id
        new_like.story_id = storyid
        new_like.liked_id = authorid
        db.session.add(new_like)
        db.session.commit()
        message = ''
    else:
        message = 'You\'ve already liked this story!'
    return _stories(message)
