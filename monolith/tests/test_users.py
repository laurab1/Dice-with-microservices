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
        self.config = self.app.config
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
        self.assertEqual(self.config['TEMPLATE_CONTEXT'], {'Error':'This email is already used.'})

        reply = self.app.post('/signup', data={'email': 'prova2@prova.com',
                                               'username': 'prova',
                                               'password': 'prova123'})
        self.assertEqual(self.config['TEMPLATE_CONTEXT'], {'Error':'This username already exists.'})

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
        self.assertEqual(self.config['TEMPLATE_CONTEXT'], {'Error': 'Wrong username or password.'})

        reply = self.app.post('/login', data={'usrn_eml': 'boh',
                                          'password': 'admin'})
        self.assertEqual(self.config['TEMPLATE_CONTEXT'], {'Error': 'Wrong username or password.'})

    def test_getusers(self):
        reply = self.app.post('/login', data={'usrn_eml': 'Admin',
                                              'password': 'admin'})
        reply = self.app.get('/users')
        self.assertEqual(self.config['TEMPLATE_CONTEXT'], {'users': [('Admin', 'Trial story of example admin user :)')]})
        with self.context:
            example = Story()
            example.text = 'Second story of example admin user :)'
            example.author_id = 1
            db.session.add(example)
            db.session.commit()
        
        reply = self.app.get('/users')
        self.assertEqual(self.config['TEMPLATE_CONTEXT'], {'users': [('Admin', 'Second story of example admin user :)')]})

        reply = self.app.post('/signup', data={'email': 'prova@prova.com',
                                               'username': 'prova',
                                               'password': 'prova123'})
        reply = self.app.get('/users')
        self.assertEqual(self.config['TEMPLATE_CONTEXT'], {'users': [('Admin', 'Second story of example admin user :)'),
                                                                     ('prova', None)]})
        
        with self.context:
            example = Story()
            example.text = 'First story of prova user :)'
            example.author_id = 2
            db.session.add(example)
            db.session.commit()
        
        reply = self.app.get('/users')
        self.assertEqual(self.config['TEMPLATE_CONTEXT'], {'users': [('Admin', 'Second story of example admin user :)'),
                                                                     ('prova', 'First story of prova user :)')]})
        