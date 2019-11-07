import datetime as dt

from monolith.database import Story


# one recent story, two not so recent
def test_get_random_recent_story_1(client, database, templates):
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
    reply = client.get('/stories/random_story')
    assert reply.status_code == 200

    template_context = templates[-1]
    assert template_context['story'].id == 1
    assert template_context['message'] == ''


# two recent stories to pick from, two not so recent
def test_get_random_recent_story_2(client, database, templates):
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
    reply = client.get('/stories/random_story')
    print(reply)
    assert reply.status_code == 200

    template_context = templates[-1]
    id = template_context['story'].id
    assert id == 1 or id == 3
    assert template_context['message'] == ''


# no recent story, get a random one
def test_get_random_story(client, database, templates):
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
    reply = client.get('/stories/random_story')
    assert reply.status_code == 200

    template_context = templates[-1]
    id = template_context['story'].id
    message = template_context['message']
    assert id == 1 or id == 2
    assert message == 'no stories today. Here is a random one:'


def test_no_stories(client, templates):
    # story not found
    reply = client.get('/stories/random_story')
    assert reply.status_code == 404

    template_context = templates[-1]
    assert template_context['message'] == 'no stories!'
