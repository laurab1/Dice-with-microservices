import unittest
import json
import datetime
from flask import request, jsonify

from monolith.database import db, User, Story
from monolith.views.stories import _get_story
from monolith.app import create_app

class TestGetStory(unittest.TestCase):
    def setUp(self):
        self.app = create_app(test=True)
        self.context = self.app.app_context()
        self.app = self.app.test_client()

    def tearDown(self):
        with self.context:
            db.drop_all()
    
    #one recent story, two not so recent
    def test_get_random_recent_story_1(self):
        with self.context:
            example = Story()
            example.text = 'recent story'
            example.likes = 0
            example.author_id = 1
            db.session.add(example)
  
            example = Story()
            example.text = 'old story (months/years ago)'
            example.likes = 0
            example.author_id = 1
            example.date = datetime.datetime(2019, 9, 5)
            db.session.add(example)

            example = Story()
            example.text = 'not recent story (yesterday)'
            example.date = datetime.datetime.now() - datetime.timedelta(days=1)
            example.likes = 0
            example.author_id = 2
            db.session.add(example)

            db.session.commit()
        
        #story found
        reply = self.app.get('/stories/random_story')
        body = json.loads(str(reply.data, 'utf8'))
        
        self.assertEqual(body['story'], '1')
        self.assertEqual(body['message'], '')
        self.assertEqual(reply.status_code, 200)

    #two recent stories to pick from, two not so recent
    def test_get_random_recent_story_2(self):
        with self.context:
            example = Story()
            example.text = 'recent story 1'
            example.likes = 0
            example.author_id = 1
            db.session.add(example)
  
            example = Story()
            example.text = 'very not recent story (months/years ago)'
            example.likes = 0
            example.author_id = 1
            example.date = datetime.datetime(2019, 9, 5)
            db.session.add(example)

            example = Story()
            example.text = 'recent story 2'
            example.likes = 0
            example.author_id = 1
            db.session.add(example)

            example = Story()
            example.text = 'not recent story (yesterday)'
            example.date = datetime.datetime.now() - datetime.timedelta(days=1)
            example.likes = 0
            example.author_id = 2
            db.session.add(example)

            db.session.commit()
        
        #story found
        reply = self.app.get('/stories/random_story')
        body = json.loads(str(reply.data, 'utf8'))
        
        self.assertTrue(body['story'] == '1' or body['story'] == '3')
        self.assertEqual(body['message'], '')
        self.assertEqual(reply.status_code, 200)

    #no recent story, get a random one
    def test_get_random_story(self):
        with self.context:
            example = Story()
            example.text = 'very not recent story (months/years ago)'
            example.likes = 0
            example.author_id = 1
            example.date = datetime.datetime(2019, 9, 5)
            db.session.add(example)

            example = Story()
            example.text = 'not recent story (yesterday)'
            example.date = datetime.datetime.now() - datetime.timedelta(days=1)
            example.likes = 0
            example.author_id = 2
            db.session.add(example)

            db.session.commit()
        
        #story found
        reply = self.app.get('/stories/random_story')
        body = json.loads(str(reply.data, 'utf8'))
        
        self.assertTrue(body['story'] == '1' or body['story'] == '2')
        self.assertEqual(body['message'], 'no stories today. Here is a random one:')
        self.assertEqual(reply.status_code, 200)
    
    def test_no_stories(self):
        #story not found
        reply = self.app.get('/stories/random_story')
        body = json.loads(str(reply.data, 'utf8'))
        
        self.assertEqual(body['story'], 'None')
        self.assertEqual(body['message'], 'no stories!')
        self.assertEqual(reply.status_code, 200)

