import os
import tempfile

from monolith.utility.diceutils import get_die_faces_list

import pytest


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    from monolith.app import create_app
    db_fd, db_path = tempfile.mkstemp()
    db_url = 'sqlite:///' + db_path
    app = create_app(test=True, database=db_url, login_disabled=True)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


def test_newStory(client):
    # new story page
    reply = client.get('/newStory')
    assert reply.status_code == 200


def test_roll_valid_dice_success(client):
    reply = client.get('/rollDice?diceset=standard')
    assert reply.status_code == 200


def test_roll_invalid_dice_fail(client):
    # new story page
    reply = client.get('/rollDice?diceset=LukeImYourFather')
    assert reply.status_code == 400

    # 3 standard dice
    reply = client.get('/rollDice?diceset=standard&dicenum=3')
    assert reply.status_code == 400

    # -1 standard dice
    reply = client.get('/rollDice?diceset=standard&dicenum=-1')
    assert reply.status_code == 400

    # 0 standard dice
    reply = client.get('/rollDice?diceset=standard&dicenum=0')
    assert reply.status_code == 400


def test_roll_dice_standard(client):
    # 6 standard dice
    reply = client.get('/rollDice?diceset=standard')
    assert len(reply.get_json()) == 6

    # 5 standard dice
    reply = client.get('/rollDice?diceset=standard&dicenum=5')
    assert len(reply.get_json()) == 5

    # 4 standard dice
    reply = client.get('/rollDice?diceset=standard&dicenum=4')
    assert len(reply.get_json()) == 4


def test_roll_dice_halloween(client):
    # dice thrown in halloween set
    reply = client.get('/rollDice?diceset=halloween')
    body = reply.get_json()
    assert len(body) == 6
    for i in range(0, 6):
        face_list = get_die_faces_list("halloween", i)
        assert body[i] in face_list


def test_roll_dice_xmas(client):
    # dice thrown in xmas set
    reply = client.get('/rollDice?diceset=xmas')
    body = reply.get_json()
    assert len(body) == 6
    for i in range(0, 6):
        face_list = get_die_faces_list("xmas", i)
        assert body[i] in face_list
