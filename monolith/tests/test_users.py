from monolith.database import Story, User


def test_getusers(client, database, auth, templates):
    reply = auth.login('Admin', 'admin')
    assert reply.status_code == 302

    reply = client.get('/users')
    template_capture = templates[-1]['result']
    users = [(r[0], r[1]) for r in template_capture]
    assert users == [('Admin', None),
                     ('test1', None),
                     ('test2', None),
                     ('test3', None)]

    example = Story()
    example.text = 'First story of admin user :)'
    example.author_id = 1
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)
    database.session.commit()

    reply = client.get('/users')
    template_capture = templates[-1]['result']
    users = [(r[0], r[1]) for r in template_capture]
    assert users == [('Admin', 'First story of admin user :)'),
                     ('test1', None),
                     ('test2', None),
                     ('test3', None)]

    client.get('/logout')

    client.post('/signup', data={'email': 'prova@prova.com',
                                 'username': 'prova',
                                 'password': 'prova123'})
    reply = client.get('/users')
    template_capture = templates[-1]['result']
    users = [(r[0], r[1]) for r in template_capture]
    assert users == [('Admin', 'First story of admin user :)'),
                     ('test1', None),
                     ('test2', None),
                     ('test3', None),
                     ('prova', None)]

    example = Story()
    example.text = 'First story of prova user :)'
    example.author_id = 5
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)
    database.session.commit()

    reply = client.get('/users')
    template_capture = templates[-1]['result']
    users = [(r[0], r[1]) for r in template_capture]
    assert users == [('Admin', 'First story of admin user :)'),
                     ('test1', None),
                     ('test2', None),
                     ('test3', None),
                     ('prova', 'First story of prova user :)')]

    example = Story()
    example.text = 'Second story of admin user :)'
    example.author_id = 1
    example.is_draft = False
    example.deleted = False
    example.dice_set = ['a', 'b', 'c']
    database.session.add(example)
    database.session.commit()

    reply = client.get('/users')
    template_capture = templates[-1]['result']
    users = [(r[0], r[1]) for r in template_capture]
    assert users == [('Admin', 'Second story of admin user :)'),
                     ('test1', None),
                     ('test2', None),
                     ('test3', None),
                     ('prova', 'First story of prova user :)')]


def test_telegram_register(app, client, database):
    reply = client.post('/bot/register',
                        data={'username': 'Admin', 'chat_id': 42})
    assert reply.status_code == 200
    assert database.session.query(User).get(1).telegram_chat_id == 42

    reply = client.post('/bot/register',
                        data={'username': 'test', 'chat_id': 42})
    assert reply.status_code == 404

    reply = client.post('/bot/register', data={'username': 'test'})
    assert reply.status_code == 400
    reply = client.post('/bot/register', data={'chat_id': 42})
    assert reply.status_code == 400
