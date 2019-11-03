from monolith.database import Story


def test_write_new_story(client, auth, database):
    auth.login('Admin', 'admin')

    reply = client.post('/writeStory', data={'text': 'test story'})
    assert reply.status_code == 302

    story = database.session.query(Story).order_by(Story.date.desc()).first()
    assert story.text == 'test story'
    assert story.author_id == 1

    reply = client.post('/writeStory', data={})
    assert reply.status_code == 400
