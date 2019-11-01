from flask import Blueprint, redirect, render_template, request, abort, jsonify
from monolith.database import db, Story, Like
from flask_login import (current_user, login_user, logout_user, login_required)
from flask import current_app as app
from sqlalchemy import desc
import random
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

@stories.route('/stories/random_story', methods=['GET'])
def _get_random_recent_story(message=''):
    stories = db.session.query(Story) #.order_by(Story.date.desc())
    recent_story = []
    id = None

    if stories.first() is not None:
        recent_stories = stories.group_by(Story.date)
        
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        today_stories = recent_stories.having(Story.date >= yesterday)
        
        #check if there are stories posted today
        if today_stories.first() is not None:
            query_size = today_stories.count()
            #we will pick randomly between at most pool_size stories from today
            pool_size = 5
            
            if pool_size > query_size:
                pool_size = query_size
            
            #returns a fixed value when using pytest, but works fine in reality
            i = random.randint(0, pool_size - 1)

            #convert the query result in list (Unfortunately, I can't apply the get() method on the query)
            today_stories = [story for story in today_stories]

            '''
            for s in recent_stories:
                print(s.id, s.date)
            print("-")
            for s in today_stories:
                print(s.id, s.date)
            print("-")
            print(i)
            print(today_stories[i].id, today_stories[i].date)
            '''

            recent_story.append(today_stories[i])
            id = today_stories[i].id
        else:
            message = "no stories today. Here is a random one:"
            #returns a fixed value when using pytest, but works fine in reality
            i = random.randint(1, stories.count() - 1)
            
            recent_story.append(stories.get(i))
            id = recent_story[0].id
    else:
        message = "no stories!"

    #TODO: change like_it_url
    if app.config["TESTING"] == True:
        app.config["TEMPLATE_CONTEXT"] = jsonify({'story': str(id), 'message' : message})
        
    return render_template("stories.html", message=message, stories=recent_story, like_it_url="http://127.0.0.1:5000/stories/like/")

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
