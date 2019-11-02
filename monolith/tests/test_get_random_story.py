import unittest
import json
import datetime
from flask import request, jsonify

from monolith.database import db, User, Story
from monolith.views.stories import _get_story
from monolith.app import create_app
from flask import current_app

class TestGetStory(unittest.TestCase):
    def setUp(self):
        self.app = create_app(test=True)
        self.context = self.app.app_context()
        self.test_client = self.app.test_client()

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
        reply = self.test_client.get('/stories/random_story')
        self.assertEqual(reply.status_code, 200)

        template_context = json.loads(str(self.app.config['TEMPLATE_CONTEXT'].data, 'utf8'))
        self.assertEqual(template_context['story'], '1')
        self.assertEqual(template_context['message'], '')

    
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
        reply = self.test_client.get('/stories/random_story')
        self.assertEqual(reply.status_code, 200)

        template_context = json.loads(str(self.app.config['TEMPLATE_CONTEXT'].data, 'utf8'))
        self.assertTrue(template_context['story'] == '1' or template_context['story'] == '3')
        self.assertEqual(template_context['message'], '')

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
        reply = self.test_client.get('/stories/random_story')
        self.assertEqual(reply.status_code, 200)

        template_context = json.loads(str(self.app.config['TEMPLATE_CONTEXT'].data, 'utf8'))
        self.assertTrue(template_context['story'] == '1' or template_context['story'] == '2')
        self.assertEqual(template_context['message'], 'no stories today. Here is a random one:')
    
    def test_no_stories(self):
        #story not found
        reply = self.test_client.get('/stories/random_story')
        self.assertEqual(reply.status_code, 200)

        template_context = json.loads(str(self.app.config['TEMPLATE_CONTEXT'].data, 'utf8'))
        self.assertEqual(template_context['story'], 'None')
        self.assertEqual(template_context['message'], 'no stories!')

