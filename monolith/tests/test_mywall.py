#tests myWall functionality
from monolith.database import db, User, Reaction, Story

def test_check_mywall(client, database):
    reply = client.get('/')
    assert reply.status_code == 200
    assert reply.get_json()['login'] == 'needed'

    client.post('/login', data={'usrn_eml': 'Admin',
                                'password': 'admin'})

    reply = client.get('/')
    assert reply.status_code == 200
    assert reply.get_json()['stories'] == []

    example = Story()
    example.text = 'Trial story of example admin user :)' #gets story_id=1 as user_id or as the first?
    example.likes = 42
    example.author_id = 1
    database.session.add(example)
    database.session.commit()

    reply = client.get('/')
    assert reply.status_code == 200
    assert reply.get_json()['stories'] == [example.toJSON()]

    example2 = Story()
    example2.text = 'New story of example admin user :)' #gets story_id=1 as user_id or as the first?
    example2.likes = 42
    example2.author_id = 1
    database.session.add(example2)
    database.session.commit()

    reply = client.get('/')
    assert reply.status_code == 200
    assert reply.get_json()['stories'] == [example.toJSON(), example2.toJSON()]


def test_statistics(client, database):
    pass