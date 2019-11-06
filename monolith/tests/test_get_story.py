from monolith.database import Story


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
