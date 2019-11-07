import datetime as dt

from monolith.database import Story

import pytest


@pytest.fixture
def init_database(database):
    example = Story()
    example.text = 'lorem ipsum dolor sit amet'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2018, month=12, day=1)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'bird drink coffee baloon'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2019, month=1, day=1)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'lorem Coffee dolor sit amet'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2019, month=3, day=12)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    example = Story()
    example.text = 'bird cofFee baloon amet'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2017, month=10, day=1)
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)

    database.session.commit()


def test_all_stories(client, templates, init_database):
    reply = client.get('/stories')
    assert reply.status_code == 200

    stories = templates[-1]['stories']
    message = templates[-1]['message']
    assert stories.count() == 4
    assert message == ''


def test_query_story(client, templates, init_database):
    # valid query params, no matches
    reply = client.get('/stories?q=foo')
    assert reply.status_code == 200

    stories = templates[-1]['stories']
    assert not stories.all()

    # valid query params, single word
    reply = client.get('/stories?q=dolor')
    assert reply.status_code == 200
    stories = templates[-1]['stories'].all()
    assert len(stories) == 2
    for s in stories:
        assert 'dolor' in s.text

    # valid query params, multiple word
    reply = client.get('/stories?q=lorem dolor')
    assert reply.status_code == 200
    stories = templates[-1]['stories'].all()
    assert len(stories) == 2
    for s in stories:
        assert 'lorem' in s.text or 'dolor' in s.text

    # valid query params, case insensitive
    reply = client.get('/stories?q=CoFFeE')
    assert reply.status_code == 200
    stories = templates[-1]['stories'].all()
    assert len(stories) == 3
    for s in stories:
        assert 'coffee' in s.text.lower()
