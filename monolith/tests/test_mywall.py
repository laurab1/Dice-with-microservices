#tests myWall functionality
import unittest
import json 
from monolith.auth import current_user
from monolith.app import create_app 
from monolith.database import db, User, Story, Like
from flask import Blueprint, render_template, request

class TestMywall(unittest.TestCase):
    def setUp(self):
        self.app = create_app() #self.app = create_app(test=True) is wrong with tox
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
                example.text = 'Trial story of example admin user :)'
                example.likes = 42
                example.author_id = 1
                #print(example)
                assert [example.text, example.likes, example.author_id] == ['Trial story of example admin user :)', 42, 1]
                db.session.add(example)
                db.session.commit()

        q = db.session.query(Story).filter(Story.id == 1)
        story = q.first()
        #assert [story.text, story.likes, story.author_id] == ['Trial story of example admin user :)', 42, 1]
        
        #print(reply)


        #body = json.loads(str(reply.data, 'utf8'))
        #print(body)
        #assert body['text'] == 'Trial story of example admin user :)'
        #assert body['likes'] == 42
        #assert body['author_id'] == 1
        #assert reply.status_code == 200
        

#        with self.context:
#            q = db.session.query(Story).filter(Story.id == 1)
#            story = q.first()
#            if story is not None: #to add an other story, with a new execution of flask run
#                example = Story()
#        	    example.text = 'New Trial story of example admin user :)'
#                example.likes = 30
#                example.author_id = 1
#                #print(example)
#        	    db.session.add(example)
#        	    db.session.commit()
#        reply = self.app.get('/')
#        body = reply.get_json()
#        assert body['text'] == 'Trial story of example admin user :)'
#        assert body['likes'] == 42
#        assert body['author_id'] == 1
#        assert body['text'] == 'New Trial story of example admin user :)'
#        assert body['likes'] == 30
#        assert body['author_id'] == 1
#        assert reply.status_code == 200

#        with self.context:
#            q = db.session.query(Story).filter(Story.id == 1)
#            story = q.first()
#            if story is not None: #to add an other story, with a new execution of flask run
#        	    example.text = 'New Trial story of example not admin user :)'
#        	    example.likes = 15
#        	    example.author_id = 2 #if it's different from 1 it's not in the wall of the admin user
#        	    #print(example)
#        	    db.session.add(example)
#        	    db.session.commit()
#        reply = self.app.get('/')
#        body = reply.get_json()
#        assert body['text'] == 'Trial story of example admin user :)'
#        assert body['likes'] == 42
#        assert body['author_id'] == 1
#        assert body['text'] == 'New Trial story of example admin user :)'
#        assert body['likes'] == 30
#        assert body['author_id'] == 1
#        assert reply.status_code == 200