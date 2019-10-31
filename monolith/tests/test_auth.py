from unittest import TestCase
from monolith.forms import LoginForm, UserForm
from flask import request
from flask_login import current_user
import json

from monolith.app import create_app
from monolith.database import db, User, Story

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
    assert reply.get_json() == {'Error':'This email is already used.'}
    database.session.rollback()

    reply = client.post('/signup', data={'email': 'prova2@prova.com',
                                         'username': 'prova',
                                         'password': 'prova123'})
    assert reply.get_json() == {'Error':'This username already exists.'}
    database.session.rollback()

def test_auth(client, database):
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
    assert reply.get_json() == {'Error': 'Wrong username or password.'}

    reply = client.post('/login', data={'usrn_eml': 'boh',
                                        'password': 'admin'})
    assert reply.get_json() == {'Error': 'Wrong username or password.'}
