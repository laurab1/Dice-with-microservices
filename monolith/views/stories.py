import datetime as dt
from random import randint

from flask import Blueprint, abort
from flask import jsonify, redirect, render_template, request

from flask_login import current_user, login_required

from monolith.classes.DiceSet import DiceSet
from monolith.database import Reaction, Story, db
from monolith.forms import StoryForm
from monolith.task import add_reaction, remove_reaction
from monolith.utility.diceutils import get_dice_sets_list
from monolith.utility.validate_story import NotValidStoryError, _check_story


stories = Blueprint('stories', __name__)
current_roll = None


@stories.route('/newStory', methods=['GET'])
@login_required
def _newstory():
    return render_template('new_story.html', diceset=get_dice_sets_list())


@stories.route('/rollDice', methods=['GET'])
@login_required
def _rollDice():
    global current_roll

    form = StoryForm()
    diceset = ('standard' if request.args.get('diceset') is None
               else request.args.get('diceset'))
    dicenum = (6 if request.args.get('dicenum') is None
               else int(request.args.get('dicenum')))

    try:
        dice = DiceSet(diceset, dicenum)
        roll = dice.throw_dice()
        current_roll = roll
    except Exception:
        abort(400)

    return render_template('new_story.html', dice=roll, form=form)


@stories.route('/writeStory', methods=['POST'])
@login_required
def _writeStory():
    global current_roll

    form = StoryForm()
    if form.validate_on_submit():
        new_story = Story()
        form.populate_obj(new_story)
        new_story.author_id = current_user.id
        new_story.likes = 0
        new_story.dislikes = 0

        # Saving the current roll in the database with '?' separator
        new_story.dice_set = '?'.join(map(str, current_roll))

        try:
            _check_story(current_roll, new_story.text)
        except NotValidStoryError:
            return jsonify(error='Your story is not valid'), 400

        db.session.add(new_story)

        try:
            db.session.commit()
            return redirect('/stories')
        except Exception:
            return jsonify(error='Your story could not be posted.'), 400
    return jsonify(error='Your story is too long or data is missing.'), 400


@stories.route('/stories', methods=['GET'])
def _stories(message='', marked=True, id=0, react=0):
    allstories = db.session.query(Story)
    return render_template('stories.html', message=message, stories=allstories,
                           like_it_url='http://127.0.0.1:5000/stories/',
                           storyid=id, react=react)


@stories.route('/stories/random_story', methods=['GET'])
def _get_random_recent_story(message=''):
    stories = db.session.query(Story)  # .order_by(Story.date.desc())
    recent_story = []

    if stories.first() is not None:
        recent_stories = stories.group_by(Story.date)

        yesterday = dt.datetime.now() - dt.timedelta(days=1)
        today_stories = recent_stories.having(Story.date >= yesterday)

        # check if there are stories posted today
        if today_stories.first() is not None:
            query_size = today_stories.count()
            # we will pick randomly between at most *pool_size* stories
            # from today
            pool_size = 5

            if pool_size > query_size:
                pool_size = query_size

            # I want to pick between the last *pool_size* elements
            # (randint returns a fixed value when using pytest, but works fine
            # in reality)
            i = randint(query_size - pool_size, query_size - 1)

            # convert the query result in list (Unfortunately, I can't apply
            # the get() method on the query)
            today_stories = [story for story in today_stories]

            recent_story.append(today_stories[i])
        else:
            message = 'no stories today. Here is a random one:'
            # (randint returns a fixed value when using pytest, but works fine
            # in reality)
            i = randint(1, stories.count() - 1)

            recent_story.append(stories.get(i))
    else:
        message = 'no stories!'

    return render_template('stories.html', message=message,
                           stories=recent_story,
                           like_it_url='http://127.0.0.1:5000/stories/')


@stories.route('/stories/<storyid>', methods=['GET', 'POST'])
@login_required
def _get_story(storyid):
    q = Reaction.query.filter_by(reactor_id=current_user.id, story_id=storyid)
    message = ''

    if request.method == 'GET':
        thisstory = db.session.query(Story).filter_by(id=storyid)

        if thisstory.first() is None:
            message = 'story not found!'
            return _stories(message)

        if q.first() is not None and not q.first().marked:
            if q.first().reaction_val == 1:
                return render_template('story.html', stories=thisstory,
                                       marked=False, val=1)
            else:
                return render_template('story.html', stories=thisstory,
                                       marked=False, val=-1)
        else:
            return render_template('story.html', stories=thisstory)

    if request.method == 'POST':
        react = 0
        if 'like' in request.form:
            react = 1
        else:
            react = -1
        if q.first() is None or react != q.first().reaction_val:
            if q.first() is not None and react != q.first().reaction_val:
                # remvoe the old reaction if the new one has different value
                if q.first().marked:
                    remove_reaction(storyid, q.first().reaction_val)
                db.session.delete(q.first())
                db.session.commit()
            new_reaction = Reaction()
            new_reaction.reactor_id = current_user.id
            new_reaction.story_id = storyid
            new_reaction.reaction_val = react
            # new_like.liked_id = authorid
            db.session.add(new_reaction)
            db.session.commit()
            message = 'Got it!'
            add_reaction(new_reaction, storyid, react)
            # votes are registered asynchronously by celery tasks
        else:
            if react == 1:
                message = 'You\'ve already liked this story!'
            else:
                message = 'You\'ve already disliked this story!'

        return _stories(message, False, storyid, react)
