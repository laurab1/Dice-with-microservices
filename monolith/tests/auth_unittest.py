from monolith.app import create_app
from unittest import TestCase
from monolith.forms import LoginForm, UserForm 
from flask import request

class AuthUnittest(TestCase):
    def test_signup(self):
        global app 
        app = create_app(test=True)
        app_client = app.test_client()

        with app.test_request_context('/signup') as form:

            form.email = 'prova@prova.com'
            form.username = 'prova'
            form.password = 'prova123'
            reply = app_client.post('/signup', data={'email': 'prova@prova.com',
                                                     'username': 'prova',
                                                     'password': 'prova123'})

            self.assertEqual(reply.status_code, 302)
        
        with app.test_request_context('/signup'):
            form = UserForm()

            self.assertIsInstance(form, UserForm)

            form.email = 'prova@prova.com'
            form.username = 'prova2'
            form.password = 'prova123'
            reply = app_client.post('/signup')
            print(reply)
            self.assertEqual(form.email.errors[-1], 'This email is already used.')

        with app.test_request_context('/signup'):
            form = UserForm()

            self.assertIsInstance(form, UserForm)

            form.email = 'prova2@prova.com'
            form.username = 'prova'
            form.password = 'prova123'
            app_client.post('/signup')
            self.assertEqual(form.email.errors[-1], 'This username already exists.')

    '''
    def login_logout_test(self):
        
        # Act
        with app.test_request_context('/login'):
            form = MyForm()

        # Assert
        self.assertIsInstance(form, MyForm)
    
    def logout_test(self):
        # Arrange
        app = Flask(__name__)

        # Assert
        self.assertIsInstance(form, MyForm)
    '''