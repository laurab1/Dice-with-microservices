import unittest
import json
from flask import request, jsonify

from monolith.database import db, User, Story
from monolith.views.stories import _get_story
from monolith.app import create_app

def test_get_story(client):
    #story found
    reply = client.get('/stories/1')
    body = reply.get_json()

    assert body['story'] == '1'
    assert body['message'] == ''
    assert reply.status_code == 200
    #OLD ASSERTION self.assertEqual(data, '<html>\n  <body>\n    <h1>Story List</h1>\n    <h5></h5>\n    <ul>\n      \n      <li>\n      \"Trial story of example admin user :)\"    Likes: 42 (2019-10-27 21:09:18.895015)\n      \n      </li>\n      \n    </ul>\n  </body>\n</html>')

    #story not found
    reply = client.get('/stories/0')
    body = reply.get_json()

    assert body['story'] == 'None'
    assert body['message'] == 'story not found!'
    assert reply.status_code == 200
    #OLD ASSERTION self.assertEqual(data, '<html>\n  <body>\n    <h1>Story List</h1>\n    <h5>story not found!</h5>\n    <ul>\n      \n    </ul>\n  </body>\n</html>')

    #invalid input
    reply = client.get('stories/ciao')
    body = reply.get_json()

    assert body['story'] == 'None'
    assert body['message'] == 'story not found!'
    assert reply.status_code == 200
    #OLD ASSERTION self.assertEqual(data, '<html>\n  <body>\n    <h1>Story List</h1>\n    <h5>story not found!</h5>\n    <ul>\n      \n    </ul>\n  </body>\n</html>')
