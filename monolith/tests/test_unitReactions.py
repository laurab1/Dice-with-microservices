def test_viewStory(client, auth, templates):
    auth.login('Admin', 'admin')

    # retrieve the trial story
    reply = client.get('/stories/1')
    assert reply.status_code == 200

    # retrieve non-existing story
    reply = client.get('/stories/0')
    template_context = templates[-1]
    assert template_context['message'] == 'story not found!'


def test_like(client, auth, templates):
    auth.login('Admin', 'admin')

    # first like
    reply = client.post('/stories/1', data={'like': 'Like it!'})
    assert reply.status_code == 200
    template_context = templates[-1]
    assert template_context['message'] == 'Got it!'

    # duplicated like
    reply = client.post('/stories/1', data={'like': 'Like it!'})
    assert reply.status_code == 200
    template_context = templates[-1]
    assert template_context['message'] == 'You\'ve already liked this story!'


def test_dislike(client, auth, templates):
    auth.login('Admin', 'admin')

    # same as likes: this also tests reaction changes
    reply = client.post('/stories/1', data={'dislike': 'Disike it!'})
    assert reply.status_code == 200
    template_context = templates[-1]
    assert template_context['message'] == 'Got it!'

    reply = client.post('/stories/1', data={'dislike': 'Dislike it!'})
    assert reply.status_code == 200
    template_context = templates[-1]
    assert template_context['message'] == 'You\'ve already disliked this story!'
