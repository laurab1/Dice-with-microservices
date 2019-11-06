from monolith.database import Story, Reaction


def test_get_story(client, auth, database, templates):
    example = Story()
    example.text = 'Trial story of example admin user :)'
    example.likes = 42
    example.author_id = 1
    example.dice_set = ['dice1', 'dice2']

    database.session.add(example)
    database.session.commit()

    auth.login()

    # story found
    reply = client.get('/stories/1')
    template_capture = templates[-1]
    assert reply.status_code == 200
    assert template_capture['story'].id == 1
    # assert template_capture['message'] == ''

    # story not found
    reply = client.get('/stories/0')
    assert reply.status_code == 404

    # invalid input
    reply = client.get('stories/ciao')
    assert reply.status_code == 404

    #deleted story
    reply = client.delete('/stories/1')
    assert reply.status_code == 200
    reply = client.get('stories/1')
    assert reply.status_code == 410

def test_unauthorized_draft(client, auth, database, templates):
    auth.login()
    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    new_id = templates[-1]['story_id']
    auth.logout()

    auth.login('test1', 'test1123')
    reply = client.get(f'/stories/{new_id}')
    assert reply.status_code == 403

def test_story_with_unmarked_like(client, auth, database, templates):
    s = Story()
    s.text = 'Trial story of example admin user :)'
    s.likes = 42
    s.dislikes = 0
    s.author_id = 1
    s.dice_set = ['dice1', 'dice2']

    database.session.add(s)

    r = Reaction()
    r.reactor_id = 1
    r.author = s
    r.reaction_val = 1
    r.marked = False

    database.session.add(r)

    database.session.commit()

    auth.login()
    reply = client.get('/stories/1')
    template_capture = templates[-1]
    assert reply.status_code == 200
    assert template_capture['story'].likes == 43
    assert template_capture['story'].dislikes == 0

    database.session.commit()

def test_story_with_unmarked_dislike(client, auth, database, templates):
    s = Story()
    s.text = 'Trial story of example admin user :)'
    s.likes = 42
    s.dislikes = 0
    s.author_id = 1
    s.dice_set = ['dice1', 'dice2']

    database.session.add(s)

    r = Reaction()
    r.reactor_id = 1
    r.author = s
    r.reaction_val = -1
    r.marked = False

    database.session.add(r)

    database.session.commit()

    auth.login()
    reply = client.get('/stories/1')
    template_capture = templates[-1]
    assert reply.status_code == 200
    assert template_capture['story'].likes == 42
    assert template_capture['story'].dislikes == 1

    database.session.commit()
