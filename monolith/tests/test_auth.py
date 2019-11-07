from monolith.database import User


def test_signup(client, auth, database, templates):
    reply = client.get('/signup')
    assert reply.status_code == 200

    reply = auth.signup('prova@prova.com', 'prova', 'prova123')
    assert reply.status_code == 302

    u = database.session.query(User).filter_by(username='prova').one()
    assert [u.username, u.email] == ['prova', 'prova@prova.com']

    auth.logout()
    assert reply.status_code == 302

    reply = auth.signup('prova@prova.com', 'prova', 'prova123')
    template_capture = templates[-1]['form']['email'].errors
    assert 'This email is already used.' in template_capture

    reply = auth.signup('prova2@prova.com', 'prova', 'prova123')
    template_capture = templates[-1]['form']['email'].errors
    assert 'This username already exists.' in template_capture


def test_auth(client, auth, templates):
    reply = auth.signup('prova@prova.com', 'prova', 'prova123')
    assert reply.status_code == 302

    reply = auth.logout()
    assert reply.status_code == 302

    reply = auth.logout()
    assert reply.status_code == 203

    reply = client.get('/login')
    assert reply.status_code == 200

    reply = auth.login('prova@prova.com', 'prova123')
    assert reply.status_code == 302

    reply = auth.login('prova', 'prova123')
    assert reply.status_code == 302

    reply = auth.login('Admin', 'admin')
    assert reply.status_code == 302

    reply = auth.logout()
    assert reply.status_code == 302

    reply = auth.login('Admin', 'boh')
    template_capture = templates[-1]['form']['password'].errors
    assert 'Wrong username or password.' in template_capture

    reply = auth.login('boh', 'admin')
    template_capture = templates[-1]['form']['password'].errors
    assert 'Wrong username or password.' in template_capture
