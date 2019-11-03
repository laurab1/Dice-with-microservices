from unittest import TestCase
from monolith.forms import LoginForm, UserForm
from flask import request
from flask_login import current_user
import json
import unittest

from monolith.app import create_app
from monolith.database import db, User, Story


def test_viewStory(client):
        
    client.post('/login', data={'usrn_eml': 'Admin', 'password': 'admin'})
    
    #retrieve the trial story
    reply = client.get('/stories/1')
    assert reply.status_code == 200
    
    #retrieve non-existing story
    reply = client.get('/stories/0')
    assert reply.get_json()['message'] == 'story not found!'


def test_like(client):
    client.post('/login', data={'usrn_eml': 'Admin', 'password': 'admin'})

    # first like
    reply = client.post('/stories/1', data={'like' :'Like it!'})
    assert reply.get_json()['message'] == 'Got it!'
    
    # duplicated like
    reply = client.post('/stories/1', data={'like' :'Like it!'})
    assert reply.get_json()['message'] == 'You\'ve already liked this story!'


def test_dislike(client):
    client.post('/login', data={'usrn_eml': 'Admin', 'password': 'admin'})

    # same as likes: this also tests reaction changes
    reply = client.post('/stories/1', data={'dislike' :'Disike it!'})
    assert reply.get_json()['message'] == 'Got it!'
    
    reply = client.post('/stories/1', data={'dislike' :'Dislike it!'})
    assert reply.get_json()['message'] == 'You\'ve already disliked this story!'