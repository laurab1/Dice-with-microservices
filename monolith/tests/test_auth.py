from unittest import TestCase
from monolith.forms import LoginForm, UserForm
from flask import request
from flask_login import current_user
import json

from monolith.app import create_app
from monolith.database import db, User, Story

class AuthUnittest(TestCase):
    def setUp(self):
        self.app = create_app(test=True)
        self.context = self.app.app_context()
        self.app = self.app.test_client()

    def tearDown(self):
        with self.context:
            db.drop_all()

    def test_signup(self):
        reply = self.app.get('/signup')
        self.assertEqual(reply.status_code, 200)

        reply = self.app.post('/signup', data={'email': 'prova@prova.com',
                                          'username': 'prova',
                                          'password': 'prova123'})

        self.assertEqual(reply.status_code, 302)

        with self.context:
            users = db.session.query(User).filter_by(username="prova")
            u = users.first()

        self.assertEqual([u.username, u.email], ["prova", "prova@prova.com"])


        reply = self.app.post('/signup', data={'email': 'prova@prova.com',
                                          'username': 'prova',
                                          'password': 'prova123'})
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body, {'Error':'This email is already used.'})

        reply = self.app.post('/signup', data={'email': 'prova2@prova.com',
                                          'username': 'prova',
                                          'password': 'prova123'})
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body, {'Error':'This username already exists.'})

    def test_auth(self):
        reply = self.app.post('/signup', data={'email': 'prova@prova.com',
                                          'username': 'prova',
                                          'password': 'prova123'})

        self.assertEqual(reply.status_code, 302)

        reply = self.app.get('/logout')
        self.assertEqual(reply.status_code, 302)

        reply = self.app.get('/logout')
        self.assertEqual(reply.status_code, 203)

        reply = self.app.get('/login')
        self.assertEqual(reply.status_code, 200)

        reply = self.app.post('/login', data={'usrn_eml': 'prova@prova.com',
                                          'password': 'prova123'})
        self.assertEqual(reply.status_code, 302)

        reply = self.app.post('/login', data={'usrn_eml': 'prova',
                                          'password': 'prova123'})
        self.assertEqual(reply.status_code, 302)

        reply = self.app.post('/login', data={'usrn_eml': 'Admin',
                                          'password': 'admin'})
        self.assertEqual(reply.status_code, 302)

        reply = self.app.get('/logout')
        self.assertEqual(reply.status_code, 302)

        reply = self.app.post('/login', data={'usrn_eml': 'Admin',
                                          'password': 'boh'})
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body, {'Error': 'Wrong username or password.'})

        reply = self.app.post('/login', data={'usrn_eml': 'boh',
                                          'password': 'admin'})
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body, {'Error': 'Wrong username or password.'})
