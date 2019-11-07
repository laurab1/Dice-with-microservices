from monolith.database import Story
from monolith.tests.conftest import get_auth, get_story_actions, get_user_actions


def test_users_interactions_with_stories_and_reactions(client_factory, templates):
    #user1
    email1 = "prova@prova.com"
    username1 = "Test1"
    password1 = "12345678"

    #user2
    email2 = "xx@xx.com"
    username2 = "Test2"
    password2 = "12345678"

    #create clients
    client1 = client_factory.get()
    client2 = client_factory.get()

    assert client1 != client2

    #create auth actions utility
    auth1 = get_auth(client1)
    auth2 = get_auth(client2)

    assert auth1 != auth2

    #create auth actions utility
    story_actions1 = get_story_actions(client1, templates)
    story_actions2 = get_story_actions(client2, templates)

    # signup and login
    reply = auth1.signup(email=email1, username=username1, password=password1)
    assert reply.status_code == 302

    # signup and login
    reply = auth2.signup(email=email2, username=username2, password=password2)
    assert reply.status_code == 302

    # client1 add draft
    reply = story_actions1.roll_dice()
    id = templates[-1]['story_id']
    dices = templates[-1]['dice']
    assert reply.status_code == 200

    #client2 tries to finish it (error!)
    reply = story_actions2.add_story_text(id, dices)
    assert reply.status_code == 401

    #client1 finally finishes the story
    reply = story_actions1.add_story_text(id, dices)
    assert reply.status_code == 302

    #client2 visualizes it
    story_actions2.get_all_stories()
    stories = templates[-1]['stories']
    assert stories.count() == 1
