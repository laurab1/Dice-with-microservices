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

@stories.route('/newStory', methods=['GET'])
@login_required
def _newstory():
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

@stories.route('/writeStory', methods=['POST'])
@login_required
def _writeStory():
    form = StoryForm()
    if form.validate_on_submit():
        new_story = Story()
        form.populate_obj(new_story)
        new_story.author_id = current_user.id
        db.session.add(new_story)

        try:
            db.session.commit()
            return _stories()
        except Exception as e:
            return jsonify({'Error':'Your story could not be posted.'}), 400

    return jsonify({'Error':'Your story is too long or data is missing.'}), 400

@stories.route('/stories', methods=['GET'])
def _stories(message=''):
    allstories = db.session.query(Story)
    return render_template("stories.html", message=message, stories=allstories,
                           like_it_url="http://127.0.0.1:5000/stories/")

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
            #we will pick randomly between at most *pool_size* stories from today
            pool_size = 5
            
            if pool_size > query_size:
                pool_size = query_size
            
            #I want to pick between the last *pool_size* elements
            #(randint returns a fixed value when using pytest, but works fine in reality)
            i = random.randint(query_size - pool_size, query_size - 1)

            #convert the query result in list (Unfortunately, I can't apply the get() method on the query)
            today_stories = [story for story in today_stories]
            
            recent_story.append(today_stories[i])
            id = today_stories[i].id
        else:
            message = "no stories today. Here is a random one:"
            #(randint returns a fixed value when using pytest, but works fine in reality)
            i = random.randint(1, stories.count() - 1)
            
            recent_story.append(stories.get(i))
            id = recent_story[0].id
    else:
        message = "no stories!"

    if app.config["TESTING"] == True:
        app.config["TEMPLATE_CONTEXT"] = jsonify({'story': str(id), 'message' : message})
        
    return render_template("stories.html", message=message, stories=recent_story, like_it_url="http://127.0.0.1:5000/stories/")

@stories.route('/stories/<storyid>', methods=['GET','POST'])
@login_required
def _get_story(storyid):
    q = Reaction.query.filter_by(reactor_id=current_user.id, story_id=storyid)
    if request.method == 'GET':
        thisstory = db.session.query(Story).filter_by(id=storyid)
        if q.first().marked != True:
            if q.first().reaction_val == 1:
                return render_template("story.html", stories=thisstory, marked=False, val=1)
            else:
                return render_template("story.html", stories=thisstory, marked=False, val=-1)
        else:
            return render_template("story.html", stories=thisstory)
    if request.method == 'POST':
        react = 0
        if "like" in request.form:
            react = 1
        else:
            react = -1
        if q.first() is None or react != q.first().reaction_val:
            if q.first() != None and react != q.first().reaction_val:
                #remvoe the old reaction if the new one has different value
                if q.first().marked:
                    remove_reaction(storyid, q.first().reaction_val)
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
            add_reaction(new_reaction, storyid, react)
            #votes are registered asynchronously by celery tasks
        else:
            if react == 1:
                message = 'You\'ve already liked this story!'
            else:
                message = 'You\'ve already disliked this story!'
        return _stories(message, False, storyid, react)
