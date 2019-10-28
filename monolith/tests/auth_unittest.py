from unittest import TestCase
from monolith.forms import LoginForm, UserForm 
from flask import request
from flask_login import current_user
import json 

from monolith.app import create_app
from monolith.database import db, User, Story

class AuthUnittest(TestCase):

    def test_signup(self):
        myapp = create_app(test=True)
        context = myapp.app_context()
        app = myapp.test_client()

        reply = app.get('/signup')
        self.assertEqual(reply.status_code, 200)

        reply = app.post('/signup', data={'email': 'prova@prova.com',
                                          'username': 'prova',
                                          'password': 'prova123'})

        self.assertEqual(reply.status_code, 302)

        with context:
            users = db.session.query(User).filter_by(username="prova")
            u = users.first()

        self.assertEqual([u.username, u.email], ["prova", "prova@prova.com"])


        reply = app.post('/signup', data={'email': 'prova@prova.com',
                                          'username': 'prova',
                                          'password': 'prova123'})
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body, {'Error':'This email is already used.'})

        reply = app.post('/signup', data={'email': 'prova2@prova.com',
                                          'username': 'prova',
                                          'password': 'prova123'})
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body, {'Error':'This username already exists.'})
        
    def test_auth(self):
        app = create_app(test=True).test_client()

        reply = app.post('/signup', data={'email': 'prova@prova.com',
                                          'username': 'prova',
                                          'password': 'prova123'})

        self.assertEqual(reply.status_code, 302)

        reply = app.get('/logout')
        self.assertEqual(reply.status_code, 302)

        reply = app.get('/logout')
        self.assertEqual(reply.status_code, 203)

        reply = app.get('/login')
        self.assertEqual(reply.status_code, 200)

        reply = app.post('/login', data={'usrn_eml': 'prova@prova.com',
                                          'password': 'prova123'})
        self.assertEqual(reply.status_code, 302)

        reply = app.post('/login', data={'usrn_eml': 'prova',
                                          'password': 'prova123'})
        self.assertEqual(reply.status_code, 302)

        reply = app.post('/login', data={'usrn_eml': 'Admin',
                                          'password': 'admin'})
        self.assertEqual(reply.status_code, 302)

        reply = app.get('/logout')
        self.assertEqual(reply.status_code, 302)

        reply = app.post('/login', data={'usrn_eml': 'Admin',
                                          'password': 'boh'})
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body, {'Error': 'Wrong username or password.'})

        reply = app.post('/login', data={'usrn_eml': 'boh',
                                          'password': 'admin'})
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body, {'Error': 'Wrong username or password.'})
