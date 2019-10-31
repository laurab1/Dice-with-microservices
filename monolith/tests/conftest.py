import datetime
import os
import tempfile

import pytest

from monolith.app import create_app
from monolith.database import db, User


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    from monolith.app import create_app
    db_fd, db_path = tempfile.mkstemp()
    db_url = 'sqlite:///' + db_path
    app = create_app(test=True, database=db_url)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
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
    with app.app_context():
        db.create_all()

        _init_database(db)
        yield db

        db.drop_all()
        db.session.commit()


class AuthActions:

    def __init__(self, app, client):
        self._app = app
        self._client = client

    def disable(self):
        self._app.config['LOGIN_DISABLED'] = True

    def enable(self):
        self._app.config['LOGIN_DISABLED'] = False

    def login(self, username='Admin', password='admin'):
        return self._client.post('/login',
                                 data={'usrn_eml': username, 'password': password})

    def logout(self):
        return self._client.get('/logout')


@pytest.fixture
def auth(app, client):
    return AuthActions(app, client)
