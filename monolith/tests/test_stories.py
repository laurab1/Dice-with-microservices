from unittest import TestCase
from monolith.forms import LoginForm, UserForm
from flask import request
from flask_login import current_user
import json
import unittest

from monolith.app import create_app
from monolith.database import db, User, Story

class StoriesUnittest(TestCase):
    def setUp(self):
        self.app = create_app(test=True)
        self.context = self.app.app_context()
        self.app = self.app.test_client()

    def tearDown(self):
        with self.context:
            db.drop_all()

    def test_write_new_story(self):
        self.app.post('/login', data={'usrn_eml': 'Admin', 'password': 'admin'})

        reply = self.app.post('/writeStory', data={'text': 'test story'})

        self.assertEqual(reply.status_code, 200)

        with self.context:
            stories = db.session.query(Story).order_by(Story.date.desc())
            s = stories.first()

        self.assertEqual(s.text, "test story")
        self.assertEqual(s.author_id, 1)

        reply = self.app.post('/writeStory', data={})

        self.assertEqual(reply.status_code, 400)

    def test_see_all_stories(self):
        reply = self.app.get('/stories')
        self.assertEqual(reply.status_code, 200)

        with self.context:
            queried = db.session.query(Story)

        body = json.loads(str(reply.data, 'UTF8'))
        self.assertEqual(len(body), queried.count())

        for i in range(0, len(body)):
            self.assertEqual(reply[i].body['id'], queried[i].id)
            self.assertEqual(reply[i].body['text'], queried[i].text)
