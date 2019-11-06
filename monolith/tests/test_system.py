from monolith.database import Story


def test_two_users(auth, story_actions, templates):
    email = "prova@prova.com"
    username = "Test"
    password = "12345678"

    # signup and login
    reply = auth.signup(email=email, username=username, password=password)
    assert reply.status_code == 302

    reply = auth.login(username=username, password=password)
    assert reply.status_code == 302

    # add story (roll + edit)
    reply = story_actions.roll_dice()
    id = templates[-1]['story_id']
    dices = templates[-1]['dice']
    assert reply.status_code == 200

    reply = story_actions.add_story_text(id, dices)
    assert reply.status_code == 302

    # check that I actually created a story
    story_actions.get_all_stories()
    stories = templates[-1]['stories']
    assert stories.count() == 1
    assert stories.first().id == int(id)

    # visualize story
    reply = story_actions.get_story(id)
    assert reply.status_code == 200

    # add draft
    reply = story_actions.roll_dice()
    id = templates[-1]['story_id']
    dices = templates[-1]['dice']
    assert reply.status_code == 200

    # log out
    reply = auth.logout()
    assert reply.status_code == 302

    # log again
    reply = auth.login(username=username, password=password)
    assert reply.status_code == 302

    # try to post an invalid story
    reply = story_actions.add_story_text(id, dices, "text is wrong")
    assert reply.status_code == 200

    # check on form
    form = templates[-1]['form']
    assert form.text.errors[-1] == 'The story is not valid.'

    # check that doesn't show up in story list
    story_actions.get_all_stories()
    stories = templates[-1]['stories']
    assert stories.count() == 1

    # try to sign up with the same credentials (error!)
    reply = auth.signup(email=email, username=username, password=password)
    assert reply.status_code == 302
    assert templates[-1]['request'].path == '/stories'

    # correct signup and login
    other_email = "aa@bb.com"
    other_username = "Test2"
    other_password = "12345678"

    reply = auth.logout()
    assert reply.status_code == 302

    reply = auth.signup(email=other_email,
                        username=other_username, password=other_password)
    assert reply.status_code == 302

    reply = auth.login(username=username, password=password)
    assert reply.status_code == 302
    assert templates[-1]['request'].path == '/stories'

    # try to validate the draft of the other user (error!)
    reply = story_actions.add_story_text(id, dices)
    assert reply.status_code == 401

    # check that doesn't show up in story list
    story_actions.get_all_stories()
    stories = templates[-1]['stories']
    assert stories.count() == 1
