import os
import tempfile

import monolith.utility.telebot as telebot
from monolith.app import create_app
from telegram.ext import CallbackContext

import pytest

import telegram

class MockContext:
    def init(self):
        self.args = [...]
        self.use_context 

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    db_url = 'sqlite:///' + db_path
    app = create_app(test=True, database=db_url, test_telegram=True)

    yield app

    app.config['TELEGRAM_UPDATER'].stop()

    os.close(db_fd)
    os.unlink(db_path)


# TODO: TEST on_login
# TODO: TEST user endpoint
def test_mock_bot(app, auth):
    user = telegram.User(id=1, first_name="test", is_bot=False)
    chat = telegram.Chat(45, "group")
    message = telegram.Message(404, user, None, chat, text="/start henlo")
    update = telegram.Update(1, message=message)
    result = telebot.on_start(update, None)
    assert result.text == 'Please use /login <username> to receive stories from your followed users'

    context = MockContext()
    # Testing login without parameters
    context.args = ""
    message = telegram.Message(405, user, None, chat, text="/login")
    update = telegram.Update(1, message=message)
    result = telebot.on_login(update, context)
    assert result.text == 'Use the command /login <username>'

    reply = auth.login('Admin', 'admin')
    # Testing login with a non existing user
    context.args = "test"
    message = telegram.Message(406, user, None, chat, text="/login test")
    update = telegram.Update(1, message=message)
    result = telebot.on_login(update, context)
    # assert result.text == 'No user is registered with this username'

    # Testing login with a existing user
    context.args =  "Admin"
    message = telegram.Message(407, user, None, chat, text="/login")
    update = telegram.Update(1, message=message)
    result = telebot.on_login(update, context)
    assert result.text == 'You will now receive updates about followed users'


