from monolith.database import User, Story

def test_getuser(client, database, templates):
    reply = client.post('/login', data={'usrn_eml': 'Admin',
                                        'password': 'admin'})
    assert reply.status_code == 302

    reply = client.get('/user/test1')
    assert reply.status_code == 200

    user = templates[-1]['user'] 
    stories = templates[-1]['stories']
    assert user == 'test1'
    assert stories == []

    example = Story()
    example.text = 'First story of test1 user :)'
    example.author_id = 2
    database.session.add(example)
    database.session.commit()
    
    reply = client.get('/user/test1')
    assert reply.status_code == 200

    user = templates[-1]['user'] 
    stories = templates[-1]['stories']
    assert user == 'test1'
    assert len(stories) == 1
    assert stories[0].id == example.id

def test_getuser_fail(client, database):
    reply = client.post('/login', data={'usrn_eml': 'Admin',
                                        'password': 'admin'})
    assert reply.status_code == 302

    reply = client.get('/user/utenteNonEsistente')
    assert reply.status_code == 404
