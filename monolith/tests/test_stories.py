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

        self.assertEqual(s.text, 'test story')
        self.assertEqual(s.author_id, 1)

        reply = self.app.post('/writeStory', data={})

        self.assertEqual(reply.status_code, 400)

    def test_stories(self):
        reply = self.app.get('/stories')
        self.assertEqual(reply.status_code, 200)

        with self.context:
            query = db.session.query(Story).filter_by(deleted=False)
            queried = query.all()

        body = json.loads(str(reply.data, 'UTF8'))
        numOfStories = len(body)
        self.assertEqual(numOfStories, query.count())

        for i in range(0, len(body)):
            self.assertEqual(body[i]['id'], queried[i].id)
            self.assertEqual(body[i]['text'], queried[i].text)

        self.app.post('/login', data={'usrn_eml': 'Admin', 'password': 'admin'})

        reply = self.app.post('/writeStory', data={'text': 'test story'})

        self.assertEqual(reply.status_code, 200)

        reply = self.app.get('/stories')
        self.assertEqual(reply.status_code, 200)
        body = json.loads(str(reply.data, 'UTF8'))

        with self.context:
            query = db.session.query(Story).filter_by(deleted=False)
            queried = query.all()

        self.assertEqual(numOfStories+1, query.count())

        for i in range(0, numOfStories+1):
            self.assertEqual(body[i]['id'], queried[i].id)
            self.assertEqual(body[i]['text'], queried[i].text)
            if body[i]['text'] == 'test story':
                toBeDeleted = str(body[i]['id'])

        reply = self.app.delete('/stories/' + toBeDeleted)
        self.assertEqual(reply.status_code, 200)

        reply = self.app.delete('/stories/' + toBeDeleted)
        self.assertEqual(reply.status_code, 400)

        reply = self.app.delete('/stories/' + toBeDeleted)
        self.assertEqual(reply.status_code, 400)

        with self.context:
            deletedStory = db.session.query(Story).get(toBeDeleted)

        self.assertEqual(deletedStory.deleted, True)

        reply = self.app.get('/logout')
        self.assertEqual(reply.status_code, 302)

        reply = self.app.post('/signup', data={'email': 'prova@prova.com',
                                          'username': 'prova',
                                          'password': 'prova123'})
        self.assertEqual(reply.status_code, 302)

        reply = self.app.post('/login', data={'usrn_eml': 'prova@prova.com',
                                          'password': 'prova123'})
        self.assertEqual(reply.status_code, 302)

        reply = self.app.post('/writeStory', data={'text': 'prova'})

        reply = self.app.get('/logout')
        self.assertEqual(reply.status_code, 302)

        self.app.post('/login', data={'usrn_eml': 'Admin', 'password': 'admin'})
        self.assertEqual(reply.status_code, 302)

        with self.context:
            notMyStory = db.session.query(Story).filter_by(author_id=2).first()

        reply = self.app.delete('/stories/' + str(notMyStory.id))
        self.assertEqual(reply.status_code, 403)

        reply = self.app.delete('/stories/999')
        self.assertEqual(reply.status_code, 404)

if __name__ == '__main__':
    unittest.main()
