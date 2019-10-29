import unittest
from monolith import app as test_app


class TestApp(unittest.TestCase):

    def test_newStory(self):
        app = test_app.create_app()
        app.config['LOGIN_DISABLED'] = True
        app.login_manager.init_app(app)
        tested_app = app.test_client()

        # new story page
        reply = tested_app.get('/newStory')
        self.assertEqual(reply.status_code, 200)

    def test_roll_valid_dice_success(self):
        app = test_app.create_app()
        app.config['LOGIN_DISABLED'] = True
        app.login_manager.init_app(app)
        tested_app = app.test_client()

        # new story page
        reply = tested_app.get('/rollDice?diceset=standard')
        self.assertEqual(reply.status_code, 200)

    def test_roll_invalid_dice_fail(self):
        app = test_app.create_app()
        app.config['LOGIN_DISABLED'] = True
        app.login_manager.init_app(app)
        tested_app = app.test_client()

        # new story page
        reply = tested_app.get('/rollDice?diceset=LukeImYourFather')
        self.assertEqual(reply.status_code, 404)
