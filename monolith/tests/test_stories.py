from monolith.database import Story


def test_write_new_story(client, auth, database):
    auth.login('Admin', 'admin')

    reply = client.post('/writeStory', data={'text': 'test story'})
    assert reply.status_code == 200

    story = database.session.query(Story).order_by(Story.date.desc()).first()
    assert story.text == "test story"
    assert story.author_id == 1

    reply = client.post('/writeStory', data={})
    assert reply.status_code == 400


def test_write_new_not_valid_story(client, auth, database):
    auth.login('Admin', 'admin')

    roll = client.get("/rollDice").get_json()
    
    story = ''
    for i in range(1,len(roll)):
        story = story + roll[i]+' '
    
    reply = client.post('/writeStory',data={'text':story})
    assert reply.status_code == 400