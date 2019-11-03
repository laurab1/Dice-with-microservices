from monolith.database import User


def test_signup(client, database, templates):
    reply = client.get('/signup')
    assert reply.status_code == 200

    reply = client.post('/signup', data={'email': 'prova@prova.com',
                                         'username': 'prova',
                                         'password': 'prova123'})

    assert reply.status_code == 302

    users = database.session.query(User).filter_by(username="prova")
    u = users.first()

    assert [u.username, u.email] == ["prova", "prova@prova.com"]

    reply = client.post('/signup', data={'email': 'prova@prova.com',
                                         'username': 'prova',
                                         'password': 'prova123'})
    template_capture = templates[-1]['form']['email'].errors
    assert 'This email is already used.' in template_capture

    reply = client.post('/signup', data={'email': 'prova2@prova.com',
                                         'username': 'prova',
                                         'password': 'prova123'})
    template_capture = templates[-1]['form']['email'].errors
    assert 'This username already exists.' in template_capture


def test_auth(client, templates):
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
