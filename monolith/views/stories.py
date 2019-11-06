import datetime as dt
from random import randint

from flask import Blueprint, abort, url_for
from flask import jsonify, redirect, render_template, request

from flask_login import current_user, login_required

from monolith.classes.DiceSet import DiceSet
from monolith.database import Reaction, Story, db
from monolith.forms import StoryForm
from monolith.task import add_reaction, remove_reaction
from monolith.utility.diceutils import get_dice_sets_list
from monolith.utility.validate_story import NotValidStoryError, _check_story
from monolith.views.users import get_followed_dict

stories = Blueprint('stories', __name__)


@stories.route('/new_story', methods=['GET'])
@login_required
def _newstory():
    '''
    Prepares the initialization of the new story.

    Returns:
        200 -> a form which enables the user to start a new story with a
                given dice set (theme and #dice)
    '''
    return render_template('new_story.html', diceset=get_dice_sets_list())


@stories.route('/roll_dice', methods=['GET'])
@login_required
def _rollDice():
    '''
    Rolls the dice and enables the user to start writing a story.

    The story is created as a draft, so that it can be edited.

    Raises:
        Exception: due to eventual failures during the commit of the
            created story into the database.

    Returns:
        302 -> the user is redirected to the page in which he/she can
                start writing the story on the faces which came out.
    '''

    diceset = request.args.get('diceset', 'standard')
    dicenum = request.args.get('dicenum', 6, type=int)

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
    except Exception as e:
        print(e)
        db.session.rollback()
        abort(400)

    return redirect(url_for('stories._story_edit', storyid=story.id))


@stories.route('/stories', methods=['GET'])
def _stories(message='', marked=True, id=0, react=0):
    '''
    Returns a list of stories depending on the query parameters.

    1) from/to query parameters: the user specifies from which time frame he/she
        wants the stories;
    2) theme query parameter: the user specifies the theme of the dice set used in the
        stories.
    
    Raises:
        1) ValueError: the date format is not valid

    Returns:
        1) 200 -> the list of the stories in the chosen time frame
        2) 200 -> the list of the stories of the last 5 days about the chosen theme
    '''
    stories = Story.query.filter_by(deleted=False, is_draft=False)
    stories = stories.order_by(Story.date.desc())
    # check for query parameters
    if len(request.args) != 0:
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        theme = request.args.get('theme')
        # check if the query parameters from and to
        if from_date is not None and to_date is not None:
            from_dt = None
            to_dt = None

            # check if the values are valid
            try:
                from_dt = dt.datetime.strptime(from_date, '%Y-%m-%d')
                to_dt = dt.datetime.strptime(to_date, '%Y-%m-%d')
            except ValueError:
                message = 'INVALID date in query parameters: use yyyy-mm-dd'
            else:  # successful try!
                # query the database with the given values
                stories = stories.group_by(Story.date) \
                    .having(Story.date >= from_dt) \
                    .having(Story.date <= to_dt)
                if stories.count() == 0:
                    message = 'no stories with the given dates'
        elif theme is not None:
            t_delta = dt.datetime.now() - dt.timedelta(days=5)
            stories = stories.filter(Story.date >= t_delta)
            stories = stories.filter(Story.theme == theme)
        else:
            message = 'WRONG QUERY parameters: you have to specify the date ' \
                      'range as from=yyyy-mm-dd&to=yyyy-mm-dd or a dice set ' \
                      'theme as theme=\'diceset\'!'

    try:
        template_dict = get_followed_dict(current_user.id)
    except Exception:
        template_dict = {}

    return render_template('stories.html', message=message, stories=stories,
                           like_it_url='http://127.0.0.1:5000/stories/',
                           storyid=id, react=react, **template_dict)


@stories.route('/stories/random_story', methods=['GET'])
def _get_random_recent_story(message=''):
    '''
    Gets a random recent story. 
    
    It is checked whether there are stories written
    in the last 24 hours: if there exists a random one of them is returned, otherwise
    a random story from the database is returned.

    Returns:
        200 -> a random story chosen with the criteria described above. 
    '''

    stories = Story.query.filter_by(deleted=False, is_draft=False)
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
            i = randint(0, stories.count() - 1)

            recent_story.append(stories.all()[i])
    else:
        message = 'no stories!'

    return render_template('stories.html', message=message,
                           stories=recent_story,
                           like_it_url='http://127.0.0.1:5000/stories/')


@stories.route('/stories/<storyid>', methods=['GET'])
@login_required
def _get_story(storyid):
    '''
    Gets the story with id <storyid>.

    Returns:
        404 -> no available story with id <storyid> has been found
        200 -> a story has been found and it is returned to the user
    '''
    q = Reaction.query.filter_by(reactor_id=current_user.id,
                                 story_id=storyid).one_or_none()
    s = Story.query.get(storyid)

    if s is None:
        abort(404, f'Story {storyid} not found')
    if s.deleted:
        abort(410, f'Story {storyid} was deleted')
    if s.author_id != current_user.id and s.is_draft:
        abort(403)  # unauthorized request

    # This check allows to count also the user's reaction even if celery
    # has not updated it yet.
    if q is not None and not q.marked:
        if q.reaction_val == 1:
            s.likes += 1
        else:
            s.dislikes += 1
    return render_template('story.html', story=s)


@stories.route('/stories/<storyid>/react', methods=['POST'])
@login_required
def _post_story_react(storyid):
    '''
    Sets a reaction to the story with id <storyid>.

    The reactions are handled as tasks from celery, allowing an asynchronous
    update of the database.

    Returns:
        200 -> the reaction has been set correctly
        400 -> a reaction to the story was already set by the user
    '''
    s = Story.query.get(storyid)

    if s is None:
        abort(404, f'Story {storyid} not found')
    if s.deleted:
        abort(410, f'Story {storyid} was deleted')
    if s.is_draft:
        abort(403)

    q = Reaction.query.filter_by(reactor_id=current_user.id,
                                 story_id=storyid).one_or_none()

    react = 1 if 'like' in request.form else -1
    removed = False
    if q is None or react != q.reaction_val:
        if q is not None and react != q.reaction_val:
            # remove the old reaction if the new one has different value
            if q.marked:
                print(current_user.id)
                remove_reaction.delay(storyid, q.reaction_val)
                removed = True
            db.session.delete(q)
            db.session.commit()
        new_reaction = Reaction()
        new_reaction.reactor_id = current_user.id
        new_reaction.story_id = storyid
        new_reaction.reaction_val = react
        db.session.add(new_reaction)
        db.session.commit()
        db.session.refresh(new_reaction)
        # votes are registered asynchronously by celery tasks
        add_reaction.delay(current_user.id, storyid, react)
        message = 'Reaction registerd' if not removed else 'Reaction updated'
        return jsonify(message=message)

    if react == 1:
        return jsonify(error='You\'ve already liked this story!'), 400
    return jsonify(error='You\'ve already disliked this story!'), 400


@stories.route('/stories/<storyid>', methods=['DELETE'])
@login_required
def _deleteStory(storyid):
    '''
    Deletes a story.

    The deletion is implemented with a flag into the Story object which determines
    whether or not the story has been deleted by the user. This has been done in order
    to maintain coherency of the statistics of the user.

    Raises:
        Exception: the commit of the story with the modified flag has failed
    
    Returns:
        500 -> the exception above has been raised
        404 -> the story with id <storyid> was not found
        403 -> the user is not the owner of the story
        200 -> the deletion was succesful
    '''
    story = Story.query.get(storyid)
    if story is None:
        abort(404, f'Story {storyid} not found')  # story not found

    if story.deleted:
        return jsonify(error='This story was already deleted'), 400

    if story.author_id != current_user.id:
        abort(403)  # unauthorized request

    story.deleted = True
    try:
        db.session.commit()
        return jsonify(message='The story was succesfully deleted')
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(message='Your story could not be deleted'), 500


@stories.route('/stories/<storyid>/edit', methods=['GET', 'POST'])
@login_required
def _story_edit(storyid):
    '''
    GET
    ---
    Opens the draft with id <storyid> in edit mode.
    
    Returns:
        404 -> the story was not found
        401 -> the user is not the author of the story
        403 -> the story has been posted and it is not a draft anymore
        410 -> the story was deleted
        200 -> provides the story in edit mode


    POST
    ----
    Posts the draft with id <storyid> as a completed story.

    If the operation is succesful, the story is not editable anymore.

    Raises:
        NotValidStoryError -> some of the words (or synonyms) representing the faces
            of the rolled dice were missing in the story, so it has been rejected
    
    Returns:
        404 -> the story was not found
        401 -> the user is not the author of the story
        403 -> the story has been posted and it is not a draft anymore
        410 -> the story was deleted
        200 -> the story has been submitted correctly
    '''
    story = db.session.query(Story).get(storyid)
    if story is None:
        abort(404, f'Story {storyid} not found')
    if story.author_id != current_user.id:
        abort(401, f'You must be the author of story {storyid} to edit')
    if not story.is_draft:
        abort(403, f'Story {storyid} cannot be edited')
    if story.deleted:
        abort(410, f'Story {storyid} was deleted')

    form = StoryForm()
    if form.validate_on_submit():
        form.populate_obj(story)
        if not story.is_draft:
            try:
                _check_story(story.dice_set, story.text)
                db.session.commit()
                return redirect(url_for('stories._get_story', storyid=storyid))
            except NotValidStoryError:
                db.session.rollback()
                form.text.errors.append('The story is not valid.')
        else:
            db.session.commit()
            return redirect(url_for('stories._get_story', storyid=storyid))

    if request.method == 'GET':
        form.text.data = story.text
        form.is_draft.data = story.is_draft

    return render_template('edit_story.html', story_id=storyid,
                           dice=story.dice_set, form=form)
