from monolith.database import Story, User


def test_signup(client, database):
    reply = client.get('/signup')
    assert reply.status_code == 200

    reply = client.post('/signup', data={'email': 'prova@prova.com',
                                         'username': 'prova',
                                         'password': 'prova123'})

    assert reply.status_code == 302

    user = database.session.query(User).filter_by(username='prova').one()
    assert [user.username, user.email] == ['prova', 'prova@prova.com']

    reply = client.post('/signup', data={'email': 'prova@prova.com',
                                         'username': 'prova',
                                         'password': 'prova123'})
    assert reply.get_json()['error'] == 'This email is already used.'
    database.session.rollback()

    reply = client.post('/signup', data={'email': 'prova2@prova.com',
                                         'username': 'prova',
                                         'password': 'prova123'})
    assert reply.get_json()['error'] == 'This username already exists.'
    database.session.rollback()


def test_auth(client, database, templates):
    reply = client.post('/signup', data={'email': 'prova@prova.com',
                                         'username': 'prova',
                                         'password': 'prova123'})
    assert reply.status_code == 302

    reply = client.get('/logout')
    assert reply.status_code == 302

    reply = client.get('/logout')
    assert reply.status_code == 203

    reply = client.get('/login')
    assert reply.status_code == 200

    reply = client.post('/login', data={'usrn_eml': 'prova@prova.com',
                                        'password': 'prova123'})
    assert reply.status_code == 302

    reply = client.post('/login', data={'usrn_eml': 'prova',
                                        'password': 'prova123'})
    assert reply.status_code == 302

    reply = client.post('/login', data={'usrn_eml': 'Admin',
                                        'password': 'admin'})
    assert reply.status_code == 302

    reply = client.get('/logout')
    assert reply.status_code == 302

    reply = client.post('/login', data={'usrn_eml': 'Admin',
                                        'password': 'boh'})
    template_capture = templates[-1]['form']['password'].errors
    assert 'Wrong username or password.' in template_capture

    reply = client.post('/login', data={'usrn_eml': 'boh',
                                        'password': 'admin'})
    template_capture = templates[-1]['form']['password'].errors
    assert 'Wrong username or password.' in template_capture


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
    database.session.add(example)
    database.session.commit()

    reply = client.get('/users')
    template_capture = templates[-1]['result']
    users = [(r[0], r[1]) for r in template_capture]
    assert users == [('Admin', 'First story of admin user :)'),
                     ('test1', None),
                     ('test2', None),
                     ('test3', None)]

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
