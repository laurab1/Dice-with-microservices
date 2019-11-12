import datetime as dt
from monolith.database import Story, Reaction
import pytest


def test_get_story(client, auth, database, templates, story_actions):
    example = Story()
    example.text = 'Trial story of example admin user :)'
    example.likes = 42
    example.author_id = 1
    example.dice_set = ['dice1', 'dice2']

    database.session.add(example)
    database.session.commit()

    auth.login()

    # story found
    reply = story_actions.get_story(1)
    template_capture = templates[-1]
    assert reply.status_code == 200
    assert template_capture['story'].id == 1
    # assert template_capture['message'] == ''

    # story not found
    reply = story_actions.get_story(0)
    assert reply.status_code == 404

    # invalid input
    reply = story_actions.get_story('ciao')
    assert reply.status_code == 404

    # deleted story
    reply = story_actions.delete_story(1)
    assert reply.status_code == 200
    reply = story_actions.get_story(1)
    assert reply.status_code == 410


def test_unauthorized_draft(client, auth, database, templates, story_actions):
    # add a draft
    auth.login()
    reply = story_actions.roll_dice()
    assert reply.status_code == 200
    new_id = templates[-1]['story_id']
    auth.logout()

    # try to edit a draft of another user
    auth.login('test1', 'test1123')
    reply = story_actions.get_story(new_id)
    assert reply.status_code == 403


def test_story_with_unmarked_like(client, auth, database, templates,
                                  story_actions):
    # example story and unmarked reaction
    s = Story()
    s.text = 'Trial story of example admin user :)'
    s.likes = 42
    s.dislikes = 0
    s.author_id = 1
    s.dice_set = ['dice1', 'dice2']
    s.is_draft = False
    s.deleted = False

    database.session.add(s)

    r = Reaction()
    r.reactor_id = 1
    r.author = s
    r.reaction_val = 1
    r.marked = False

    database.session.add(r)

    database.session.commit()

    # get the story
    auth.login()
    reply = story_actions.get_story(1)
    template_capture = templates[-1]
    assert reply.status_code == 200
    # check that the unmarked like is counted
    assert template_capture['story'].likes == 43
    assert template_capture['story'].dislikes == 0

    database.session.commit()


def test_story_with_unmarked_dislike(client, auth, database, templates,
                                     story_actions):
    # example story and unmarked reaction
    s = Story()
    s.text = 'Trial story of example admin user :)'
    s.likes = 42
    s.dislikes = 0
    s.author_id = 1
    s.dice_set = ['dice1', 'dice2']
    s.is_draft = False
    s.deleted = False

    database.session.add(s)

    r = Reaction()
    r.reactor_id = 1
    r.author = s
    r.reaction_val = -1
    r.marked = False

    database.session.add(r)

    database.session.commit()

    # get the story
    auth.login()
    reply = story_actions.get_story(1)
    template_capture = templates[-1]
    assert reply.status_code == 200
    assert template_capture['story'].likes == 42
    # check that the unmarked dislike is counted
    assert template_capture['story'].dislikes == 1

    database.session.commit()

# one recent story, two not so recent
def test_get_random_recent_story_1(client, database, templates, story_actions):
    example = Story()
    example.text = 'recent story'
    example.likes = 0
    example.author_id = 1
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'old story (months/years ago)'
    example.likes = 0
    example.author_id = 1
    example.date = dt.datetime(2019, 9, 5)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'not recent story (yesterday)'
    example.date = dt.datetime.now() - dt.timedelta(days=1)
    example.likes = 0
    example.author_id = 2
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    database.session.commit()

    # story found
    reply = story_actions.get_random_recent_story()
    assert reply.status_code == 200

    template_context = templates[-1]
    assert template_context['story'].id == 1
    assert template_context['message'] == ''


# two recent stories to pick from, two not so recent
def test_get_random_recent_story_2(client, database, templates, story_actions):
    example = Story()
    example.text = 'recent story 1'
    example.likes = 0
    example.author_id = 1
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'very not recent story (months/years ago)'
    example.likes = 0
    example.author_id = 1
    example.date = dt.datetime(2019, 9, 5)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'recent story 2'
    example.likes = 0
    example.author_id = 1
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'not recent story (yesterday)'
    example.date = dt.datetime.now() - dt.timedelta(days=1)
    example.likes = 0
    example.author_id = 2
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    database.session.commit()

    # story found
    reply = story_actions.get_random_recent_story()
    assert reply.status_code == 200

    template_context = templates[-1]
    id = template_context['story'].id
    assert id == 1 or id == 3
    assert template_context['message'] == ''


# no recent story, get a random one
def test_get_random_story(client, database, templates, story_actions):
    example = Story()
    example.text = 'very not recent story (months/years ago)'
    example.likes = 0
    example.author_id = 1
    example.date = dt.datetime(2019, 9, 5)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'not recent story (yesterday)'
    example.date = dt.datetime.now() - dt.timedelta(days=1)
    example.likes = 0
    example.author_id = 2
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'drafted story'
    example.date = dt.datetime.now() - dt.timedelta(days=1)
    example.likes = 0
    example.author_id = 1
    example.is_draft = True
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'deleted story'
    example.date = dt.datetime.now() - dt.timedelta(days=1)
    example.likes = 0
    example.author_id = 1
    example.is_draft = False
    example.deleted = True
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    database.session.commit()

    # story found
    reply = story_actions.get_random_recent_story()
    assert reply.status_code == 200

    template_context = templates[-1]
    id = template_context['story'].id
    message = template_context['message']
    assert id == 1 or id == 2
    assert message == 'no stories today. Here is a random one:'


def test_no_stories(client, templates, story_actions):
    # story not found
    reply = story_actions.get_random_recent_story()
    assert reply.status_code == 404

    template_context = templates[-1]
    assert template_context['message'] == 'no stories!'


def test_get_by_interest(client, auth, database, templates, story_actions):
    auth.login()

    example1 = Story()
    example1.theme = 'halloween'
    example1.text = 'Halloween story of test1 user :)'
    example1.author_id = 2
    example1.is_draft = False
    example1.deleted = False
    example1.dice_set = ['a', 'b', 'c']
    database.session.add(example1)
    database.session.commit()

    example2 = Story()
    example2.theme = 'xmas'
    example2.text = 'Xmas story of test2 user :)'
    example2.author_id = 3
    example2.is_draft = False
    example2.deleted = False
    example2.dice_set = ['a', 'b', 'c']
    database.session.add(example2)
    database.session.commit()

    example3 = Story()
    example3.theme = 'xmas'
    example3.theme = 'Old xmas story of test3 user :)'
    example3.date = dt.datetime.now() - dt.timedelta(days=6)
    example3.author_id = 4
    example3.is_draft = False
    example3.deleted = False
    example3.dice_set = ['a', 'b', 'c']
    database.session.add(example3)
    database.session.commit()

    reply = story_actions.get_all_stories(theme='xmas')
    assert reply.status_code == 200
    assert templates[-1]['stories'].all() == [example2]

@pytest.fixture
def init_database(database):
    example = Story()
    example.text = 'test'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2018, month=12, day=1)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'test'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2019, month=1, day=1)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'test'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2019, month=3, day=12)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'test'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2017, month=10, day=1)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'test'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2018, month=12, day=7)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    database.session.commit()


def test_all_stories(client, templates, init_database, story_actions):
    reply = story_actions.get_all_stories()
    assert reply.status_code == 200

    stories = templates[-1]['stories']
    message = templates[-1]['message']
    assert stories.count() == 5
    assert message == ''

def test_no_stories(client, templates):
    reply = client.get('/stories')
    assert reply.status_code == 200

    stories = templates[-1]['stories']
    message = templates[-1]['message']
    assert stories.count() == 0
    assert message == 'no stories'


def test_ranged_stories(client, templates, init_database, story_actions):
    # invalid query params
    reply = client.get('/stories?test=ciao')
    
    # valid query params, invalid values (1)
    reply = story_actions.get_all_stories(date_range=('2018-12-1', '2019-x-1'))
    assert reply.status_code == 200

    message = templates[-1]['message']
    assert message == 'INVALID date in query parameters: use yyyy-mm-dd'

    # valid query params, invalid values (2)
    reply = story_actions.get_all_stories(date_range=('x-12-1', '2019-10-1'))
    assert reply.status_code == 200

    message = templates[-1]['message']
    assert message == 'INVALID date in query parameters: use yyyy-mm-dd'

    # valid query params, invalid values (3)
    reply = client.get('/stories?from=x-12-1&to=2019-10-x')
    assert reply.status_code == 200

    message = templates[-1]['message']
    assert message == 'INVALID date in query parameters: use yyyy-mm-dd'

    # found something in exact range
    reply = story_actions.get_all_stories(date_range=('2018-12-1', '2019-1-1'))
    assert reply.status_code == 200

    message = templates[-1]['message']
    stories = templates[-1]['stories']
    assert message == ''
    assert stories.count() == 3
    for story in stories:
        assert story.id == 1 or story.id == 2 or story.id == 5

    # found something in "not exact" range
    reply = story_actions.get_all_stories(date_range=('2017-5-1', '2018-1-1'))
    assert reply.status_code == 200

    message = templates[-1]['message']
    stories = templates[-1]['stories']
    assert message == ''
    assert stories.count() == 1
    assert stories[0].id == 4

    # from date == to_date
    reply = story_actions.get_all_stories(date_range=('2019-1-1', '2019-1-1'))
    assert reply.status_code == 200

    message = templates[-1]['message']
    stories = templates[-1]['stories']
    assert message == ''
    assert stories.count() == 1
    assert stories[0].id == 2

    # from date < to_date
    reply = story_actions.get_all_stories(date_range=('2019-1-1', '2018-1-1'))
    assert reply.status_code == 200

    message = templates[-1]['message']
    stories = templates[-1]['stories']
    assert message == 'Wrong date parameters (from-date greater than ' \
                      'to-date or viceversa)!'
    assert stories == []
    # nothing found
    reply = story_actions.get_all_stories(date_range=('2015-12-1', '2017-1-1'))
    assert reply.status_code == 200

    message = templates[-1]['message']
    stories = templates[-1]['stories']
    assert message == 'no stories with the given dates'
    assert stories.count() == 0

def test_viewStory(client, auth, templates, story_actions):
    auth.login()

    # Create new story
    reply = story_actions.roll_dice()
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    reply = story_actions.add_story_text(new_id, roll)
    assert reply.status_code == 302

    # retrieve the trial story
    reply = story_actions.get_story(new_id)
    assert reply.status_code == 200

    # retrieve non-existing story
    reply = story_actions.get_story(0)
    assert reply.status_code == 404


def test_like(client, auth, database, templates, story_actions):
    auth.login()

    # Invalid story
    reply = story_actions.post_like_reaction(1)
    assert reply.status_code == 404

    reply = story_actions.roll_dice()
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    reply = story_actions.add_story_text(new_id, roll)
    assert reply.status_code == 302

    # First like
    reply = story_actions.post_like_reaction(new_id)
    assert reply.status_code == 200
    r = Reaction.query.filter_by(reactor_id=1, story_id=new_id).one()
    s = Story.query.get(new_id)
    assert r is not None
    assert r.reaction_val == 1
    assert s.likes == 1 and s.dislikes == 0

    # duplicated like
    reply = story_actions.post_like_reaction(new_id)
    assert reply.status_code == 400
    database.session.refresh(r)
    database.session.refresh(s)
    assert r is not None
    assert r.reaction_val == 1
    assert s.likes == 1 and s.dislikes == 0

    auth.logout()
    auth.login('test1', 'test1123')

    # Second like
    reply = story_actions.post_like_reaction(new_id)
    assert reply.status_code == 200
    r = Reaction.query.filter_by(reactor_id=2, story_id=new_id).one()
    s = Story.query.get(new_id)
    assert r is not None
    assert r.reaction_val == 1
    assert s.likes == 2 and s.dislikes == 0


def test_dislike(client, auth, database, templates, story_actions):
    auth.login()

    # Invalid story
    reply = story_actions.post_dislike_reaction(1)
    assert reply.status_code == 404

    reply = story_actions.roll_dice()
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']
    reply = story_actions.add_story_text(new_id, roll)
    assert reply.status_code == 302

    # First like
    reply = story_actions.post_dislike_reaction(new_id)
    assert reply.status_code == 200
    r = Reaction.query.filter_by(reactor_id=1, story_id=new_id).one()
    s = Story.query.get(new_id)
    assert r is not None
    assert r.reaction_val == -1
    assert s.likes == 0 and s.dislikes == 1

    # duplicated like
    reply = story_actions.post_dislike_reaction(new_id)
    assert reply.status_code == 400
    database.session.refresh(r)
    database.session.refresh(s)
    assert r is not None
    assert r.reaction_val == -1
    assert s.likes == 0 and s.dislikes == 1

    auth.logout()
    auth.login('test1', 'test1123')
    # Second like
    reply = story_actions.post_dislike_reaction(new_id)
    assert reply.status_code == 200
    r = Reaction.query.filter_by(reactor_id=2, story_id=new_id).one()
    s = Story.query.get(new_id)
    assert r is not None
    assert r.reaction_val == -1
    assert s.likes == 0 and s.dislikes == 2

def test_reaction_change(client, auth, database, templates, story_actions):
    auth.login()

    reply = story_actions.roll_dice()
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    reply = story_actions.add_story_text(new_id, roll)
    assert reply.status_code == 302

    # First like
    reply = story_actions.post_like_reaction(1)
    assert reply.status_code == 200
    r = Reaction.query.filter_by(reactor_id=1, story_id=new_id).one()
    s = Story.query.get(new_id)
    assert r is not None
    assert r.reaction_val == 1
    assert s.likes == 1 and s.dislikes == 0

    auth.logout()
    auth.login()

    # Change with dislike
    reply = story_actions.post_dislike_reaction(new_id)
    assert reply.status_code == 200
    r = Reaction.query.filter_by(reactor_id=1, story_id=new_id).one()
    s = Story.query.get(new_id)
    assert r is not None
    assert r.reaction_val == -1
    assert s.likes == 0 and s.dislikes == 1

    # Change with like
    reply = story_actions.post_like_reaction(new_id)
    assert reply.status_code == 200
    r = Reaction.query.filter_by(reactor_id=1, story_id=new_id).one()
    s = Story.query.get(new_id)
    assert r is not None
    assert r.reaction_val == 1
    assert s.likes == 1 and s.dislikes == 0


def test_react_to_deleted_story(client, auth, database, templates,
                                story_actions):
    auth.login()

    # add valid story
    reply = story_actions.roll_dice()
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    reply = story_actions.add_story_text(new_id, roll)
    assert reply.status_code == 302

    reply = story_actions.delete_story(new_id)
    assert reply.status_code == 200

    # like it
    reply = story_actions.post_like_reaction(new_id)
    assert reply.status_code == 410

    # dislike it
    reply = story_actions.post_dislike_reaction(new_id)
    assert reply.status_code == 410


def test_react_to_draft(client, auth, database, templates, story_actions):
    auth.login()

    # add draft
    reply = story_actions.roll_dice()
    assert reply.status_code == 200
    new_id = templates[-1]['story_id']

    # like it
    reply = story_actions.post_like_reaction(new_id)
    assert reply.status_code == 403

    # dislike it
    reply = story_actions.post_dislike_reaction(new_id)
    assert reply.status_code == 403
