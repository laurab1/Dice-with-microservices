from monolith.database import Story


def test_get_story(client, auth, database, templates, story_actions):
    example = Story()
    example.text = 'Trial story of example admin user :)'
    example.likes = 42
    example.author_id = 1
    example.dice_set = ['dice1', 'dice2']

    database.session.add(example)
    database.session.commit()

    auth.login()

    # story found
    reply = story_actions.get_story(1)
    template_capture = templates[-1]
    assert reply.status_code == 200
    assert template_capture['story'].id == 1
    # assert template_capture['message'] == ''

    # story not found
    reply = story_actions.get_story(0)
    assert reply.status_code == 404

    # invalid input
    reply = story_actions.get_story('ciao')
    assert reply.status_code == 404

    # deleted story
    reply = story_actions.delete_story(1)
    assert reply.status_code == 200
    reply = story_actions.get_story(1)
    assert reply.status_code == 410


def test_unauthorized_draft(client, auth, database, templates, story_actions):
    auth.login()
    reply = story_actions.roll_dice()
    assert reply.status_code == 200
    new_id = templates[-1]['story_id']
    auth.logout()

    auth.login('test1', 'test1123')
    reply = story_actions.get_story(new_id)
    assert reply.status_code == 403
