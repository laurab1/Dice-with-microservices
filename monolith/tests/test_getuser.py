from monolith.database import Story


def test_getuser(client, auth, database, templates):
    reply = auth.login()
    assert reply.status_code == 302

    reply = client.get('/users/2')
    assert reply.status_code == 200

    user = templates[-1]['user']
    stories = templates[-1]['stories']
    assert user == 'test1'
    assert stories == []

    example = Story()
    example.text = 'First story of test1 user :)'
    example.author_id = 2
    example.is_draft = False
    example.deleted = False
    database.session.add(example)
    database.session.commit()

    reply = client.get('/users/2')
    assert reply.status_code == 200

    user = templates[-1]['user']
    stories = templates[-1]['stories']
    assert user == 'test1'
    assert len(stories) == 1
    assert stories[0].id == example.id


def test_getuser_fail(client, auth, database):
    reply = auth.login()
    assert reply.status_code == 302

    reply = client.get('/users/utenteNonEsistente')
    assert reply.status_code == 404
