import unittest
import json
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
    
    def test_get_story(self):
        #story found
        reply = self.app.get('/stories/1')
        body = json.loads(str(reply.data, 'utf8'))
        
        self.assertEqual(body['story'], '1')
        self.assertEqual(body['message'], '')
        self.assertEqual(reply.status_code, 200)
        #OLD ASSERTION self.assertEqual(data, '<html>\n  <body>\n    <h1>Story List</h1>\n    <h5></h5>\n    <ul>\n      \n      <li>\n      \"Trial story of example admin user :)\"    Likes: 42 (2019-10-27 21:09:18.895015)\n      \n      </li>\n      \n    </ul>\n  </body>\n</html>')

        #story not found
        reply = self.app.get('/stories/0')
        body = json.loads(str(reply.data, 'utf8'))
        
        self.assertEqual(body['story'], 'None')
        self.assertEqual(body['message'], 'story not found!')
        self.assertEqual(reply.status_code, 200)
        #OLD ASSERTION self.assertEqual(data, '<html>\n  <body>\n    <h1>Story List</h1>\n    <h5>story not found!</h5>\n    <ul>\n      \n    </ul>\n  </body>\n</html>')

        #invalid input
        reply = self.app.get('stories/ciao')
        body = json.loads(str(reply.data, 'utf8'))
        
        self.assertEqual(body['story'], 'None')
        self.assertEqual(body['message'], 'story not found!')
        self.assertEqual(reply.status_code, 200)
        #OLD ASSERTION self.assertEqual(data, '<html>\n  <body>\n    <h1>Story List</h1>\n    <h5>story not found!</h5>\n    <ul>\n      \n    </ul>\n  </body>\n</html>')