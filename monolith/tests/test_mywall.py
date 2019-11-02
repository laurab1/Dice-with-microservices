#tests myWall functionality
import unittest
import json
from monolith.auth import current_user
from monolith.app import create_app
from monolith.database import db, User, Story, Like
from flask import Blueprint, render_template, request

class TestMywall(unittest.TestCase):
    def setUp(self):
        self.app = create_app(test=True) 
        self.context = self.app.app_context()
        self.app = self.app.test_client()

    def tearDown(self):
        with self.context:
            db.drop_all() #it's necessary to drop and create again all the db

    def test_check_mywall(self):
        reply = self.app.get('/')
        self.assertEqual(reply.status_code, 200)

        reply = self.app.get('/1') #also with other numbers and characters
        self.assertEqual(reply.status_code, 404)
        with self.context:
            q = db.session.query(Story).filter(Story.id == 1)
            story = q.first()
            if story is None: #to add stories for the first time
                example = Story()
                example.text = 'Trial story of example admin user :)' #gets story_id=1 as user_id or as the first?
                example.likes = 42
                example.author_id = 1
                #print(example) #to see it run pytest -s from console
                assert [example.text, example.likes, example.author_id] == ['Trial story of example admin user :)', 42, 1]
                db.session.add(example)

                example = Story()
                example.text = 'New Trial story of example admin user :)' #gets story_id=2 
                example.likes = 30
                example.author_id = 1
                db.session.add(example)

                db.session.commit()

            story = q.first()
            assert [story.text, story.likes, story.author_id] == ['Trial story of example admin user :)', 42, 1]
            #print(story.text)
            
            q = db.session.query(Story).filter(Story.id == 2) #Story.author_id==1 and Story.id==2 fails
            story = q.first()
            assert [story.text, story.likes, story.author_id] == ['New Trial story of example admin user :)', 30, 1]
            #print(story.text)

            example.text = 'New Trial story of example not admin user :)' #gets story_id=2 as user_id
            example.likes = 15
            example.author_id = 3 #if it's different from 1 it's not in the wall of the admin user
            db.session.add(example)

            q = db.session.query(Story).filter(Story.author_id == 3)
            story = q.first()
            assert [story.text, story.likes, story.author_id] == ['New Trial story of example not admin user :)', 15, 3]
            #print(q.first().text)