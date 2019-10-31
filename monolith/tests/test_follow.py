from unittest import TestCase
from flask import request
from flask_login import (current_user, login_user)
import json

from monolith.app import create_app
from monolith.database import db, User


class TestFollowers(TestCase):

    def setUp(self):
        self.app = create_app(test=True)
        self.context = self.app.app_context()
        self.app = self.app.test_client()

        with self.context:
            u = User(username='test1', email='test1@example.com')
            u.set_password('test1123')
            db.session.add(u)
            u = User(username='test2', email='test2@example.com')
            u.set_password('test2123')
            db.session.add(u)
            u = User(username='test3', email='test3@example.com')
            u.set_password('test3123')
            db.session.add(u)
            db.session.commit()

    def tearDown(self):
        with self.context:
            db.drop_all()

    def test_follow_post(self):
        with self.context:
            u = db.session.query(User).filter_by(username='test1').one()

        reply = self.app.post(
            '/login', data={'usrn_eml': 'test1@example.com', 'password': 'test1123'})
        self.assertEqual(reply.status_code, 302)

        reply = self.app.post('/users/1/follow')
        self.assertEqual(reply.status_code, 200)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['message'], 'User followed')

        reply = self.app.post('/users/3/follow')
        self.assertEqual(reply.status_code, 200)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['message'], 'User followed')

        with self.context:
            u = db.session.query(User).filter_by(username='test1').one()
            self.assertEqual(len(u.follows), 2)

        reply = self.app.post('/users/3/follow')
        self.assertEqual(reply.status_code, 200)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['message'], 'User followed')

        with self.context:
            u = db.session.query(User).filter_by(username='test1').one()
            self.assertEqual(len(u.follows), 2)

        reply = self.app.post('/users/5/follow')
        self.assertEqual(reply.status_code, 404)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['error'], 'User with id 5 does not exists')

        reply = self.app.post('/users/2/follow')
        self.assertEqual(reply.status_code, 400)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['error'], 'Cannot follow or unfollow yourself')

    def test_follow_delete(self):
        with self.context:
            u = db.session.query(User).filter_by(username='test1').one()

        reply = self.app.post(
            '/login', data={'usrn_eml': 'test1@example.com', 'password': 'test1123'})
        self.assertEqual(reply.status_code, 302)

        reply = self.app.post('/users/1/follow')
        self.assertEqual(reply.status_code, 200)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['message'], 'User followed')

        reply = self.app.post('/users/3/follow')
        self.assertEqual(reply.status_code, 200)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['message'], 'User followed')

        with self.context:
            u = db.session.query(User).filter_by(username='test1').one()
            self.assertEqual(len(u.follows), 2)

        reply = self.app.delete('/users/3/follow')
        self.assertEqual(reply.status_code, 200)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['message'], 'User unfollowed')

        with self.context:
            u = db.session.query(User).filter_by(username='test1').one()
            self.assertEqual(len(u.follows), 1)
            self.assertEqual(u.follows[0].username, 'Admin')

        reply = self.app.delete('/users/3/follow')
        self.assertEqual(reply.status_code, 200)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['message'], 'User unfollowed')

        reply = self.app.delete('/users/5/follow')
        self.assertEqual(reply.status_code, 404)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['error'], 'User with id 5 does not exists')

        reply = self.app.post('/users/2/follow')
        self.assertEqual(reply.status_code, 400)
        body = json.loads(str(reply.data, 'utf8'))
        self.assertEqual(body['error'], 'Cannot follow or unfollow yourself')

