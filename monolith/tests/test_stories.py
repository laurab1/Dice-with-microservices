from monolith.database import Story


def test_write_new_story(client, auth, database, templates):
    auth.login('Admin', 'admin')

    client.get('/rollDice')
    roll = templates[-1]['dice']

    story_text = ''
    for i in range(len(roll)):
        story_text = story_text + roll[i] + ' '

    reply = client.post('/writeStory', data={'text': story_text})
    assert reply.status_code == 302

    story = database.session.query(Story).order_by(Story.date.desc()).first()
    assert story.text == story_text
    assert story.author_id == 1

    reply = client.post('/writeStory', data={})
    assert reply.status_code == 400


def test_write_new_not_valid_story(client, auth, database, templates):
    auth.login('Admin', 'admin')

    client.get('/rollDice')
    roll = templates[-1]['dice']

    story = ''
    for i in range(1, len(roll)):
        story = story + roll[i] + ' '

    reply = client.post('/writeStory', data={'text': story})
    assert reply.status_code == 400
