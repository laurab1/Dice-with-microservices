from unittest import TestCase
from monolith.forms import LoginForm, UserForm
from flask import request
from flask_login import current_user
import json
import unittest

from monolith.app import create_app
from monolith.database import db, User, Story

class ReactionsUnitTest(TestCase):
    def setUp(self):
        self.app = create_app(test=True)
        self.context = self.app.app_context()
        self.app = self.app.test_client()

    def tearDown(self):
        with self.context:
            db.drop_all()

    def test_viewStory(self):
        
        self.app.post('/login', data={'usrn_eml': 'Admin', 'password': 'admin'})
        
        #retrieve the trial story
        reply = self.app.get('/stories/1')
        self.assertEqual(reply.status_code, 200)
        
        #retrieve non-existing story
        reply = self.app.get('/stories/0')
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['message'], 'story not found!')

    def test_like(self):
        self.app.post('/login', data={'usrn_eml': 'Admin', 'password': 'admin'})

        # first like
        reply = self.app.post('/stories/1', data={'like' :'Like it!'})
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['message'], 'Got it!')
        
        # duplicated like
        reply = self.app.post('/stories/1', data={'like' :'Like it!'})
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['message'], 'You\'ve already liked this story!')

    def test_dislike(self):
        self.app.post('/login', data={'usrn_eml': 'Admin', 'password': 'admin'})

        # same as likes: this also tests reaction changes
        reply = self.app.post('/stories/1', data={'dislike' :'Disike it!'})
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['message'], 'Got it!')
        
        reply = self.app.post('/stories/1', data={'dislike' :'Dislike it!'})
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['message'], 'You\'ve already disliked this story!')