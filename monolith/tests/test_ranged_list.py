import pytest
import datetime as dt
from monolith.database import Story, db

@pytest.fixture
def init_database(database):
    example = Story()
    example.text = 'test'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2018, month=12, day=1)
    database.session.add(example)

    example = Story()
    example.text = 'test'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2019, month=1, day=1)
    database.session.add(example)

    example = Story()
    example.text = 'test'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2019, month=3, day=12)
    database.session.add(example)

    example = Story()
    example.text = 'test'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2017, month=10, day=1)
    database.session.add(example)

    example = Story()
    example.text = 'test'
    example.likes = 42
    example.author_id = 1
    example.date = dt.datetime(year=2018, month=12, day=7)
    database.session.add(example)
    
    database.session.commit()

def test_all_stories(client, templates, init_database):
    reply = client.get('/stories')
    assert reply.status_code == 200

    stories = templates[-1]['stories']
    message = templates[-1]['message']
    assert stories.count() == 5
    assert message == ''

def test_ranged_stories(client, templates, init_database):
    #invalid query params
    reply = client.get('/stories?test=ciao')
    assert reply.status_code == 200

    message = templates[-1]['message']
    assert message == 'WRONG QUERY parameters: you have to specify the date range as from=yyyy-mm-dd&to=yyyy-mm-dd!'

    #valid query params, invalid values

    #found something in exact range
    reply = client.get('/stories?from=2018-12-1&to=2019-1-1')
    assert reply.status_code == 200

    stories = templates[-1]['stories']
    for story in stories:
        assert story.id == 1 or story.id == 2 or story.id == 5