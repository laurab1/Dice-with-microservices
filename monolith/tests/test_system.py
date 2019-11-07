from monolith.database import Story
from monolith.tests.conftest import get_auth, get_story_actions


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

    #client2 likes the story
    reply = story_actions2.post_like_reaction(id)
    assert reply.status_code == 200

    #client2 visualizes if the story is correctly liked
    story_actions2.get_all_stories()
    stories = templates[-1]['stories']
    assert stories.count() == 1
    assert stories.first().likes == 1 and stories.first().dislikes == 0

    #client1 dislikes its own story
    reply = story_actions1.post_dislike_reaction(id)
    assert reply.status_code == 200

    #client1 visualizes if the story is correctly disliked
    reply = story_actions1.get_all_stories()
    stories = templates[-1]['stories']
    assert stories.count() == 1
    assert stories.first().likes == 1 and stories.first().dislikes == 1

    #client2 create a draft for an xmas story
    reply = story_actions2.roll_dice(dice_set="xmas")
    xmas_id = templates[-1]['story_id']
    xmas_dices = templates[-1]['dice']
    assert reply.status_code == 200

    #client2 writes a wrong story
    reply = story_actions2.add_story_text(xmas_id, dices, "text is wrong")
    assert reply.status_code == 200

    form = templates[-1]['form']
    assert form.text.errors[-1] == 'The story is not valid.'

    #client2 gives to client1 the id for the xmas story, thinking that it is viewable
    reply = story_actions1.get_story(xmas_id)
    assert reply.status_code == 403

    #client1 fixes the error, by correctly posting the story
    reply = story_actions2.add_story_text(xmas_id, xmas_dices)
    assert reply.status_code == 302

    #client1 searches by interest
    reply = story_actions1.get_all_stories(theme='xmas')
    stories = templates[-1]['stories']
    assert stories.count() == 1

    #client1 logout
    reply = auth1.logout()
    assert reply.status_code == 302

    #client2 logout
    reply = auth1.logout()
    assert reply.status_code == 302