from monolith.database import Story, Reaction


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
    # add a draft
    auth.login()
    reply = story_actions.roll_dice()
    assert reply.status_code == 200
    new_id = templates[-1]['story_id']
    auth.logout()

    # try to edit a draft of another user
    auth.login('test1', 'test1123')
    reply = story_actions.get_story(new_id)
    assert reply.status_code == 403


def test_story_with_unmarked_like(client, auth, database, templates,
                                  story_actions):
    # example story and unmarked reaction
    s = Story()
    s.text = 'Trial story of example admin user :)'
    s.likes = 42
    s.dislikes = 0
    s.author_id = 1
    s.dice_set = ['dice1', 'dice2']
    s.is_draft = False
    s.deleted = False

    database.session.add(s)

    r = Reaction()
    r.reactor_id = 1
    r.author = s
    r.reaction_val = 1
    r.marked = False

    database.session.add(r)

    database.session.commit()

    # get the story
    auth.login()
    reply = story_actions.get_story(1)
    template_capture = templates[-1]
    assert reply.status_code == 200
    # check that the unmarked like is counted
    assert template_capture['story'].likes == 43
    assert template_capture['story'].dislikes == 0

    database.session.commit()


def test_story_with_unmarked_dislike(client, auth, database, templates,
                                     story_actions):
    # example story and unmarked reaction
    s = Story()
    s.text = 'Trial story of example admin user :)'
    s.likes = 42
    s.dislikes = 0
    s.author_id = 1
    s.dice_set = ['dice1', 'dice2']
    s.is_draft = False
    s.deleted = False

    database.session.add(s)

    r = Reaction()
    r.reactor_id = 1
    r.author = s
    r.reaction_val = -1
    r.marked = False

    database.session.add(r)

    database.session.commit()

    # get the story
    auth.login()
    reply = story_actions.get_story(1)
    template_capture = templates[-1]
    assert reply.status_code == 200
    assert template_capture['story'].likes == 42
    # check that the unmarked dislike is counted
    assert template_capture['story'].dislikes == 1

    database.session.commit()
