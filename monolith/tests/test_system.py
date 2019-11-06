from monolith.database import Story

def test_single_user(auth, story_actions, templates):
    email="prova@prova.com"
    username="Test"
    password="12345678"

    #signup and login
    reply = auth.signup(email=email, username=username, password=password)
    assert reply.status_code == 302

    reply = auth.login(username=username, password=password)
    assert reply.status_code == 302

    #add stories
    reply = story_actions.roll_dice()
    id = templates[-1]['story_id']
    dices = templates[-1]['dice']
    assert reply.status_code == 200

    reply = story_actions.add_story_text(id, dices)
    assert reply.status_code == 302

    #visualize story
    reply = story_actions.get_story(id)
    assert reply.status_code == 200
    
    #add draft
    reply = story_actions.roll_dice()
    id = templates[-1]['story_id']
    dices = templates[-1]['dice']
    assert reply.status_code == 200

    #log out
    reply = auth.logout()
    assert reply.status_code == 302

    #log again
    reply = auth.login(username=username, password=password)
    assert reply.status_code == 302

    #invalid story
    reply = story_actions.add_story_text(id, dices, "text is wrong")
    assert reply.status_code == 200

    form = templates[-1]['form']
    assert form.text.errors[-1] == 'The story is not valid.'




