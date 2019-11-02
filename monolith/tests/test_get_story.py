from monolith.database import Story


def test_get_story(client, database):
    example = Story()
    example.text = 'Trial story of example admin user :)'
    example.likes = 42
    example.author_id = 1

    database.session.add(example)
    database.session.commit()

    # story found
    reply = client.get('/stories/1')
    body = reply.get_json()
    assert body['story'] == '1'
    assert body['message'] == ''
    assert reply.status_code == 200

    # story not found
    reply = client.get('/stories/0')
    body = reply.get_json()

    assert body['story'] == 'None'
    assert body['message'] == 'story not found!'
    assert reply.status_code == 200

    # invalid input
    reply = client.get('stories/ciao')
    body = reply.get_json()

    assert body['story'] == 'None'
    assert body['message'] == 'story not found!'
    assert reply.status_code == 200
