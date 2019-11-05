import datetime as dt
from random import randint

from flask import Blueprint, abort
from flask import jsonify, redirect, render_template, request
from flask import current_app as app
from flask_login import current_user, login_required

from monolith.classes.DiceSet import DiceSet
from monolith.database import Reaction, Story, db
from monolith.forms import StoryForm
from monolith.task import add_reaction, remove_reaction
from monolith.utility.diceutils import get_dice_sets_list
from monolith.utility.validate_story import NotValidStoryError, _check_story
from sqlalchemy import desc


stories = Blueprint('stories', __name__)


@stories.route('/newStory', methods=['GET'])
@login_required
def _newstory():
    return render_template('new_story.html', diceset=get_dice_sets_list())


@stories.route('/rollDice', methods=['GET'])
@login_required
def _rollDice():
    diceset = ('standard' if request.args.get('diceset') is None
               else request.args.get('diceset'))
    dicenum = (6 if request.args.get('dicenum') is None
               else int(request.args.get('dicenum')))

    try:
        dice = DiceSet(diceset, dicenum)
        roll = dice.throw_dice()
        story = Story()
        story.text = ''
        story.theme = diceset
        story.likes = 0
        story.dislikes = 0
        story.dice_set = roll
        story.author_id = current_user.id
        db.session.add(story)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(400)

    return redirect(f'/stories/{story.id}/edit')


@stories.route('/stories/<storyid>', methods=['DELETE'])
@login_required
def _deleteStory(storyid):
    story = Story.query.get(storyid)
    if story is None:
        abort(404) #story not found
    else:
        if story.deleted == True:
            return jsonify(error='This story was already deleted'), 400
        else:
            if story.author_id != current_user.id:
                abort(403) #unauthorized request
            story.deleted = True
            try:
                db.session.commit()
                return jsonify(message='The story was succesfully deleted')
            except:
                return jsonify(message='Your story could not be deleted'), 500

@stories.route('/stories', methods=['GET'])
def _stories(message='', marked=True, id=0, react=0):
    stories = db.session.query(Story).filter_by(deleted=False)
    #check for query parameters
    if len(request.args) != 0:
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        theme = request.args.get('theme')
        #check if the query parameters from and to
        if from_date is not None and to_date is not None:
            from_dt = None
            to_dt = None

            #check if the values are valid
            try:
                from_dt = dt.datetime.strptime(from_date, '%Y-%m-%d')
                to_dt = dt.datetime.strptime(to_date, '%Y-%m-%d')
            except ValueError:
                message = "INVALID date in query parameters: use yyyy-mm-dd"
            else: #successful try!
                #query the database with the given values
                stories = stories.group_by(Story.date).having(Story.date >= from_dt).having(Story.date <= to_dt).filter_by(deleted=False)

                if stories.count() == 0:
                    message='no stories with the given dates'
        
        elif theme is not None:
            t_delta = dt.datetime.now() - dt.timedelta(days=5)
            stories = stories.filter(Story.date >= t_delta)
            stories = stories.filter(Story.theme == theme)
        else:
            message = 'WRONG QUERY parameters: you have to specify the date range as from=yyyy-mm-dd&to=yyyy-mm-dd or a dice set theme as theme=\'diceset\'!'

    stories = stories.order_by(desc(Story.date))
    return render_template("stories.html", message=message, stories=stories,
                           like_it_url="http://127.0.0.1:5000/stories/", storyid=id, react=react)

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
                    remove_reaction.delay(storyid, q.first().reaction_val)
                db.session.delete(q.first())
                db.session.commit()
            new_reaction = Reaction()
            new_reaction.reactor_id = current_user.id
            new_reaction.story_id = storyid
            new_reaction.reaction_val = react
            # new_like.liked_id = authorid
            db.session.add(new_reaction)
            db.session.commit()
            db.session.refresh(new_reaction)
            message = 'Got it!'
            add_reaction.delay(current_user.id, storyid, react)
            # votes are registered asynchronously by celery tasks
        else:
            if react == 1:
                message = 'You\'ve already liked this story!'
            else:
                message = 'You\'ve already disliked this story!'

        return _stories(message, False, storyid, react)


@stories.route('/stories/<storyid>/edit', methods=['GET', 'POST'])
@login_required
def _story_edit(storyid):
    story = db.session.query(Story).get(storyid)
    if story is None:
        abort(404)
    if story.author_id != current_user.id:
        abort(401)
    if not story.is_draft:
        abort(403)

    if request.method == 'POST':
        print(request.form)
        form = StoryForm()
        if form.validate_on_submit():
            form.populate_obj(story)
            if not story.is_draft:
                try:
                    _check_story(story.dice_set, story.text)
                except NotValidStoryError:
                    return jsonify(error='Your story is not valid'), 400
            db.session.commit()
            return redirect(f'/stories/{storyid}')
        return jsonify(error='Your story is too long or data is missing.'), 400

    if request.method == 'GET':
        form = StoryForm()
        form.text.data = story.text
        form.is_draft.data = story.is_draft
        return render_template('edit_story.html', story_id=storyid,
                               dice=story.dice_set, form=form)

    abort(501)
