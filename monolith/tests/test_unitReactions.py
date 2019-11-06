from monolith.database import Reaction, Story


def test_viewStory(client, auth, templates):
    auth.login()

    # Create new story
    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    story_text = ''
    for i in range(len(roll)):
        story_text = story_text + roll[i] + ' '

    reply = client.post(f'/stories/{new_id}/edit', data={'text': story_text})
    assert reply.status_code == 302

    # retrieve the trial story
    reply = client.get(f'/stories/{new_id}')
    assert reply.status_code == 200

    # retrieve non-existing story
    reply = client.get('/stories/0')
    assert reply.status_code == 404


def test_like(client, auth, database, templates):
    auth.login()

    # Invalid story
    reply = client.post('/stories/1/react', data={'like': 'Like it!'})
    assert reply.status_code == 404

    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    story_text = ''
    for i in range(len(roll)):
        story_text = story_text + roll[i] + ' '

    reply = client.post(f'/stories/{new_id}/edit', data={'text': story_text})
    assert reply.status_code == 302

    # First like
    reply = client.post('/stories/1/react', data={'like': 'Like it!'})
    assert reply.status_code == 200
    r = database.session.query(Reaction) \
                .filter_by(reactor_id=1, story_id=new_id).one()
    s = database.session.query(Story).get(new_id)
    assert r is not None
    assert r.reaction_val == 1
    assert s.likes == 1 and s.dislikes == 0

    # duplicated like
    reply = client.post('/stories/1/react', data={'like': 'Like it!'})
    assert reply.status_code == 400
    database.session.refresh(r)
    database.session.refresh(s)
    assert r is not None
    assert r.reaction_val == 1
    assert s.likes == 1 and s.dislikes == 0

    auth.logout()
    auth.login('test1', 'test1123')

    # Second like
    reply = client.post('/stories/1/react', data={'like': 'Like it!'})
    assert reply.status_code == 200
    r = database.session.query(Reaction) \
                .filter_by(reactor_id=2, story_id=new_id).one()
    s = database.session.query(Story).get(new_id)
    assert r is not None
    assert r.reaction_val == 1
    assert s.likes == 2 and s.dislikes == 0


def test_dislike(client, auth, database, templates):
    auth.login()

    # Invalid story
    reply = client.post('/stories/1/react', data={'dislike': 'Dislike it!'})
    assert reply.status_code == 404

    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    story_text = ''
    for i in range(len(roll)):
        story_text = story_text + roll[i] + ' '

    reply = client.post(f'/stories/{new_id}/edit', data={'text': story_text})
    assert reply.status_code == 302

    # First like
    reply = client.post('/stories/1/react', data={'dislike': 'Dislik it!'})
    assert reply.status_code == 200
    r = database.session.query(Reaction) \
                .filter_by(reactor_id=1, story_id=new_id).one()
    s = database.session.query(Story).get(new_id)
    assert r is not None
    assert r.reaction_val == -1
    assert s.likes == 0 and s.dislikes == 1

    # duplicated like
    reply = client.post('/stories/1/react', data={'dislike': 'Dislike it!'})
    assert reply.status_code == 400
    database.session.refresh(r)
    database.session.refresh(s)
    assert r is not None
    assert r.reaction_val == -1
    assert s.likes == 0 and s.dislikes == 1

    auth.logout()
    auth.login('test1', 'test1123')
    # Second like
    reply = client.post('/stories/1/react', data={'dislike': 'Dislike it!'})
    assert reply.status_code == 200
    r = database.session.query(Reaction) \
                .filter_by(reactor_id=2, story_id=new_id).one()
    s = database.session.query(Story).get(new_id)
    assert r is not None
    assert r.reaction_val == -1
    assert s.likes == 0 and s.dislikes == 2


def test_reaction_change(client, auth, database, templates):
    auth.login()

    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    story_text = ''
    for i in range(len(roll)):
        story_text = story_text + roll[i] + ' '

    reply = client.post(f'/stories/{new_id}/edit', data={'text': story_text})
    assert reply.status_code == 302

    # First like
    reply = client.post('/stories/1/react', data={'like': 'Like it!'})
    assert reply.status_code == 200
    r = database.session.query(Reaction) \
                .filter_by(reactor_id=1, story_id=new_id).one()
    s = database.session.query(Story).get(new_id)
    assert r is not None
    assert r.reaction_val == 1
    assert s.likes == 1 and s.dislikes == 0

    auth.logout()
    auth.login()

    # Change with dislike
    reply = client.post('/stories/1/react', data={'dislike': 'Dislike it!'})
    assert reply.status_code == 200
    r = database.session.query(Reaction) \
                .filter_by(reactor_id=1, story_id=new_id).one()
    s = database.session.query(Story).get(new_id)
    assert r is not None
    assert r.reaction_val == -1
    assert s.likes == 0 and s.dislikes == 1

    # Change with like
    reply = client.post('/stories/1/react', data={'like': 'Like it!'})
    assert reply.status_code == 200
    r = database.session.query(Reaction) \
                .filter_by(reactor_id=1, story_id=new_id).one()
    s = database.session.query(Story).get(new_id)
    assert r is not None
    assert r.reaction_val == 1
    assert s.likes == 1 and s.dislikes == 0

def test_react_to_deleted_story(client, auth, database, templates):
    auth.login()

    # add valid story
    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    story_text = ''
    for i in range(len(roll)):
        story_text = story_text + roll[i] + ' '

    reply = client.post(f'/stories/{new_id}/edit', data={'text': story_text})
    assert reply.status_code == 302

    reply = client.delete(f'/stories/{new_id}')
    assert reply.status_code == 200

    # like it
    reply = client.post(f'/stories/{new_id}/react', data={'like': 'Like it!'})
    assert reply.status_code == 410

    # dislike it
    reply = client.post(f'/stories/{new_id}/react', data={'dislike': 'Dislike it!'})
    assert reply.status_code == 410

def test_react_to_draft(client, auth, database, templates):
    auth.login()

    # add draft
    reply = client.get('/roll_dice', follow_redirects=True)
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    # like it
    reply = client.post(f'/stories/{new_id}/react', data={'like': 'Like it!'})
    assert reply.status_code == 403

    # dislike it
    reply = client.post(f'/stories/{new_id}/react', data={'dislike': 'Dislike it!'})
    assert reply.status_code == 403
