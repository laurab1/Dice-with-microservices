import datetime
import os
import tempfile

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message

from flask import template_rendered

from monolith.app import create_app
from monolith.database import User, db

import pytest


@pytest.fixture
def app():
    """Builds and configures a new app instance for each test, using the test
    flag and a temporary fresh database. Automatically manages the temporary
    files. Can be overridden locally to pass different flags to the
    app instance, see test_unitStories for reference.
    """
    db_fd, db_path = tempfile.mkstemp()
    db_url = 'sqlite:///' + db_path
    app = create_app(test=True, database=db_url)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Builds a new test client instance."""
    return app.test_client()


def _init_database(db):
    example1 = User()
    example1.username = 'test1'
    example1.firstname = 'First1'
    example1.lastname = 'Last1'
    example1.email = 'test1@example.com'
    example1.dateofbirth = datetime.datetime(2020, 10, 5)
    example1.is_admin = False
    example1.set_password('test1123')
    db.session.add(example1)

    example2 = User()
    example2.username = 'test2'
    example2.firstname = 'First2'
    example2.lastname = 'Last2'
    example2.email = 'test2@example.com'
    example2.dateofbirth = datetime.datetime(2020, 10, 5)
    example2.is_admin = False
    example2.set_password('test2123')
    db.session.add(example2)

    example3 = User()
    example3.username = 'test3'
    example3.firstname = 'First3'
    example3.lastname = 'Last3'
    example3.email = 'test3@example.com'
    example3.dateofbirth = datetime.datetime(2020, 10, 5)
    example3.is_admin = False
    example3.set_password('test3123')
    db.session.add(example3)

    db.session.commit()


@pytest.fixture
def database(app):
    """Provides a reference to the temporary database in the app context. Use
    this instance instead of importing db from monolith.db.
    """
    with app.app_context():
        db.create_all()

        _init_database(db)
        yield db

        db.drop_all()
        db.session.commit()


class AuthActions:
    """Class for login/logout management."""

    def __init__(self, app, client):
        self._app = app
        self._client = client

    def signup(self, email, username, password, firstname=None,
               lastname=None, dateofbirth=None):
        signup_data = {'email': email,
                       'username': username,
                       'password': password}
        if firstname is not None:
            signup_data.update({'firstname': firstname})
        if lastname is not None:
            signup_data.update({'lastname': lastname})
        if dateofbirth is not None:
            signup_data.update({'dateofbirth': dateofbirth})
        return self._client.post('/signup', data=signup_data)

    def login(self, username='Admin', password='admin'):
        """Sends a login request. By default logs in as admin."""
        return self._client.post('/login', data={
            'usrn_eml': username, 'password': password})

    def logout(self):
        """Sends a logout request."""
        return self._client.get('/logout')


@pytest.fixture
def auth(app, client):
    """Provides login/logout capabilities."""
    return AuthActions(app, client)


@pytest.fixture
def templates(app):
    """Provides an array of captured templates. The last element in the array
    is the template context of the last client call. This fixture can be used
    to avoid inserting testing code and duplication inside the views
    implementation."""
    recorded = []

    def record(sender, template, context, **kwargs):
        recorded.append(context)

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class TestSMTPHandler(Message):
    """Class for intercepted SMTP messages."""

    def __init__(self, message_class=None):
        super().__init__(message_class)
        self._messages = []

    def handle_message(self, message):
        """When receives a new message, it appends the message to the queue."""
        self._messages.append(message)

    @property
    def messages(self):
        """Returns the queue of received messages."""
        return self._messages

    def reset(self):
        """Deletes all the messages from the queue of received messages."""
        self._messages = []


@pytest.fixture
def smtp_server():
    """Provides an asynchronous SMTP server to test mail
    delivering functionalities. Returns a controller that stores the received
    messages.
    """
    handler = TestSMTPHandler()
    controller = Controller(handler)
    controller.start()
    yield handler
    controller.stop()
