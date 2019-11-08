import os
import tempfile

import monolith.utility.telebot as telebot
from monolith.app import create_app

import pytest

import telegram


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    db_url = 'sqlite:///' + db_path
    app = create_app(test=True, database=db_url, test_telegram=True)

    yield app

    app.config['TELEGRAM_UPDATER'].stop()

    os.close(db_fd)
    os.unlink(db_path)


# TODO: TEST on_start
# TODO: TEST on_login
# TODO: TEST user endpoint
def test_mock_bot(app):
    user = telegram.User(id=1, first_name="test", is_bot=False)
    chat = telegram.Chat(45, "group")
    message = telegram.Message(404, user, None, chat, text="/start henlo")
    update = telegram.Update(1, message=message)
    result = telebot.on_start(update, None)
    assert result.text == 'Please use /login <username> to receive stories from your followed users'
