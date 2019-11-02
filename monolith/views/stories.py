import datetime as dt
from random import randint

from flask import Blueprint, abort
from flask import current_app as app
from flask import jsonify, render_template, request

from flask_login import current_user, login_required

from monolith.classes.DiceSet import DiceSet
from monolith.database import Like, Story, db
from monolith.forms import StoryForm
from monolith.utility.diceutils import get_dice_sets_list


stories = Blueprint('stories', __name__)


@stories.route('/newStory', methods=['GET'])
@login_required
def _newstory():
    return render_template('new_story.html', diceset=get_dice_sets_list())


@stories.route('/rollDice', methods=['GET'])
@login_required
def _rollDice():
    form = StoryForm()
    diceset = ('standard' if request.args.get('diceset') is None
               else request.args.get('diceset'))
    dicenum = (6 if request.args.get('dicenum') is None
               else int(request.args.get('dicenum')))

    try:
        dice = DiceSet(diceset, dicenum)
        roll = dice.throw_dice()
    except Exception:
        abort(400)

    if app.config['TESTING']:
        return jsonify(roll)

    return render_template('new_story.html', dice=roll, form=form)


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
        except Exception:
            return jsonify({'Error': 'Your story could not be posted.'}), 400

    return (jsonify({'Error': 'Your story is too long or data is missing.'}),
            400)


@stories.route('/stories', methods=['GET'])
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

    # TODO: change like_it_url
    if app.config["TESTING"]:
        return jsonify(story=str(id), message=message)

    return render_template("stories.html", message=message, stories=story,
                           like_it_url="http://127.0.0.1:5000/stories/like/")


@stories.route('/stories/random_story', methods=['GET'])
def _get_random_recent_story(message=''):
    stories = db.session.query(Story)  # .order_by(Story.date.desc())
    recent_story = []
    id = None

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
            id = today_stories[i].id
        else:
            message = "no stories today. Here is a random one:"
            # (randint returns a fixed value when using pytest, but works fine
            # in reality)
            i = randint(1, stories.count() - 1)

            recent_story.append(stories.get(i))
            id = recent_story[0].id
    else:
        message = "no stories!"

    # TODO: change like_it_url
    # if app.config["TESTING"]:
    #     app.config["TEMPLATE_CONTEXT"] = jsonify(
    #         {'story': str(id), 'message': message})

    return render_template("stories.html", message=message,
                           stories=recent_story,
                           like_it_url="http://127.0.0.1:5000/stories/like/")


@stories.route('/stories/like/<authorid>/<storyid>')
@login_required
def _like(authorid, storyid):
    q = Like.query.filter_by(liker_id=current_user.id, story_id=storyid)
    if q.first() is not None:
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
