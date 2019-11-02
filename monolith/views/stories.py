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
