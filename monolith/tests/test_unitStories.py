import unittest

from kombu.utils import json

from monolith import app as test_app


class TestApp(unittest.TestCase):

    def test_newStory(self):
        app = test_app.create_app(test=True)
        tested_app = app.test_client()

        # new story page
        reply = tested_app.get('/newStory')
        self.assertEqual(reply.status_code, 200)

    def test_roll_valid_dice_success(self):
        app = test_app.create_app(test=True)
        tested_app = app.test_client()

        # new story page
        reply = tested_app.get('/rollDice?diceset=standard')
        self.assertEqual(reply.status_code, 200)

    def test_roll_invalid_dice_fail(self):
        app = test_app.create_app(test=True)
        tested_app = app.test_client()

        # new story page
        reply = tested_app.get('/rollDice?diceset=LukeImYourFather')
        self.assertEqual(reply.status_code, 400)

        # 3 standard dice
        reply = tested_app.get('/rollDice?diceset=standard&dicenum=3')
        self.assertEqual(reply.status_code, 400)

        # -1 standard dice
        reply = tested_app.get('/rollDice?diceset=standard&dicenum=-1')
        self.assertEqual(reply.status_code, 400)

        # 0 standard dice
        reply = tested_app.get('/rollDice?diceset=standard&dicenum=0')
        self.assertEqual(reply.status_code, 400)

    def test_roll_dice_standard(self):
        app = test_app.create_app(test=True)
        tested_app = app.test_client()

        # 6 standard dice
        reply = tested_app.get('/rollDice?diceset=standard')
        body = json.loads(str(reply.data, 'UTF8'))
        self.assertEqual(len(body), 6)

        # 5 standard dice
        reply = tested_app.get('/rollDice?diceset=standard&dicenum=5')
        body = json.loads(str(reply.data, 'UTF8'))
        self.assertEqual(len(body), 5)

        # 4 standard dice
        reply = tested_app.get('/rollDice?diceset=standard&dicenum=4')
        body = json.loads(str(reply.data, 'UTF8'))
        self.assertEqual(len(body), 4)




