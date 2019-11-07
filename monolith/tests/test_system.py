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
    reply = auth2.logout()
    assert reply.status_code == 302

def test_interaction_among_followers(client_factory, templates):
    email1 = "prova@prova.com"
    username1 = "Test1"
    password1 = "12345678"
    user1_id = 2

    email2 = "xx@xx.com"
    username2 = "Test2"
    password2 = "12345678"
    user2_id = 3

    #create clients
    client1 = client_factory.get()
    client2 = client_factory.get()

    assert client1 != client2

    #create auth actions utility
    auth1 = get_auth(client1)
    auth2 = get_auth(client2)

    assert auth1 != auth2

    #create story actions utility
    story_actions1 = get_story_actions(client1, templates)
    story_actions2 = get_story_actions(client2, templates)

    #create user actions utility
    user_actions1 = get_user_actions(client1, templates)
    user_actions2 = get_user_actions(client2, templates)

    # signup and login
    reply = auth1.signup(email=email1, username=username1, password=password1)
    assert reply.status_code == 302

    # signup and login
    reply = auth2.signup(email=email2, username=username2, password=password2)
    assert reply.status_code == 302

    # client1 publish 2 stories
    reply = story_actions1.roll_dice()
    id_story1 = templates[-1]['story_id']
    dices = templates[-1]['dice']
    assert reply.status_code == 200

    reply = story_actions1.add_story_text(id_story1, dices)
    assert reply.status_code == 302

    reply = story_actions1.roll_dice()
    id_story2 = templates[-1]['story_id']
    dices = templates[-1]['dice']
    assert reply.status_code == 200

    reply = story_actions1.add_story_text(id_story2, dices)
    assert reply.status_code == 302

    # client2 follows client1
    reply = user_actions2.follow_user(user1_id)
    assert reply.status_code == 200

    reply = user_actions2.get_followed()
    assert reply.status_code == 200
    assert templates
    users = templates[-1]['users']
    assert len(users) == 1
    assert users[0]['id'] == user1_id

    reply = user_actions1.get_followed()
    assert reply.status_code == 200
    assert templates
    users = templates[-1]['users']
    assert len(users) == 0

    # client1 see client2 wall
    reply = user_actions1.get_user_wall(user2_id)
    assert reply.status_code == 200
    assert len(templates[-1]['stories']) == 0

    # client2 see client1 wall
    reply = user_actions2.get_user_wall(user1_id)
    assert reply.status_code == 200
    assert len(templates[-1]['stories']) == 2
    assert templates[-1]['stories'][0].id == int(id_story2)
    assert templates[-1]['stories'][1].id == int(id_story1)

    # client1 delete a story
    reply = story_actions1.delete_story(id_story2)
    assert reply.status_code == 200

    # client2 (tries to) see client1 deleted story
    reply = story_actions2.get_story(id_story2)
    assert reply.status_code == 410

    # client2 see client1 wall
    reply = user_actions2.get_user_wall(user1_id)
    assert reply.status_code == 200
    assert len(templates[-1]['stories']) == 1
    assert templates[-1]['stories'][0].id == int(id_story1)

    # client1 unfollow client2
    reply = user_actions1.unfollow_user(user2_id)
    # ok! client1 was not following client2, nothing changed
    assert reply.status_code == 200

    # client2 publish a story
    reply = story_actions2.roll_dice()
    id = templates[-1]['story_id']
    dices = templates[-1]['dice']
    assert reply.status_code == 200

    reply = story_actions2.add_story_text(id, dices)
    assert reply.status_code == 302

    # client1 look for client2's story in the list of all stories
    reply = story_actions1.get_all_stories()
    assert reply.status_code == 200
    assert (int(id) in [s.id for s in templates[-1]['stories']]) == True

    # client1 reads client2's story
    reply = story_actions1.get_story(id)
    assert reply.status_code == 200

    # client1 follows client1
    reply = user_actions1.follow_user(user1_id)
    assert reply.status_code == 400

    reply = user_actions1.get_followed()
    assert reply.status_code == 200
    assert templates
    users = templates[-1]['users']
    # client1 is not a follower of client1
    assert (int(user1_id) in [u.id for u in templates[-1]['users']]) == False
