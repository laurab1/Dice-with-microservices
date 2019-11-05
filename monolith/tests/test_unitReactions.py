def test_viewStory(client, auth, templates):
    auth.login('Admin', 'admin')

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


def test_like(client, auth, templates):
    auth.login('Admin', 'admin')

    # first like
    reply = client.post('/stories/1/react', data={'like': 'Like it!'})
    assert reply.status_code == 200
    # template_context = templates[-1]
    # assert template_context['message'] == 'Got it!'

    # duplicated like
    reply = client.post('/stories/1/react', data={'like': 'Like it!'})
    assert reply.status_code == 400
    # template_context = templates[-1]
    # assert template_context['message'] == 'You\'ve already liked this story!'


def test_dislike(client, auth, templates):
    auth.login('Admin', 'admin')

    # same as likes: this also tests reaction changes
    reply = client.post('/stories/1/react', data={'dislike': 'Disike it!'})
    assert reply.status_code == 200
    # template_context = templates[-1]
    # assert template_context['message'] == 'Got it!'

    reply = client.post('/stories/1/react', data={'dislike': 'Dislike it!'})
    assert reply.status_code == 400
    # template_context = templates[-1]
    # assert template_context['message'] == 'You\'ve already disliked this story!'
