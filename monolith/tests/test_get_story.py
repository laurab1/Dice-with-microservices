from monolith.database import Story


def test_get_story(client, database, templates):
    example = Story()
    example.text = 'Trial story of example admin user :)'
    example.likes = 42
    example.author_id = 1

    database.session.add(example)
    database.session.commit()

    # story found
    reply = client.get('/stories/1')
    template_capture = templates[-1]
    assert template_capture['stories'].first().id == 1
    assert template_capture['message'] == ''
    assert reply.status_code == 200

    # story not found
    reply = client.get('/stories/0')
    template_capture = templates[-1]
    assert template_capture['stories'].first() is None
    assert template_capture['message'] == 'story not found!'
    assert reply.status_code == 200

    # invalid input
    reply = client.get('stories/ciao')
    template_capture = templates[-1]
    assert template_capture['stories'].first() is None
    assert template_capture['message'] == 'story not found!'
    assert reply.status_code == 200
