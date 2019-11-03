from monolith.database import User, Story

def test_getuser(client, database):
    reply = client.post('/login', data={'usrn_eml': 'Admin',
                                        'password': 'admin'})
    assert reply.status_code == 302

    reply = client.get('/user/test1')
    assert reply.get_json()['user'] == 'test1'
    assert reply.get_json()['stories'] == []

    example = Story()
    example.text = 'First story of test1 user :)'
    example.author_id = 2
    database.session.add(example)
    database.session.commit()
    
    reply = client.get('/user/test1')
    assert reply.get_json()['user'] == 'test1'
    assert reply.get_json()['stories'] == [example.toJSON()]

def test_getuser_fail(client, database):
    reply = client.post('/login', data={'usrn_eml': 'Admin',
                                        'password': 'admin'})
    assert reply.status_code == 302

    reply = client.get('/user/utenteNonEsistente')
    assert reply.status_code == 404
