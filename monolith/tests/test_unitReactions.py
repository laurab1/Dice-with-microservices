from monolith.database import Reaction, Story


def test_viewStory(client, auth, templates, story_actions):
    auth.login()

    # Create new story
    reply = story_actions.roll_dice()
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    reply = story_actions.add_story_text(new_id, roll)
    assert reply.status_code == 302

    # retrieve the trial story
    reply = story_actions.get_story(new_id)
    assert reply.status_code == 200

    # retrieve non-existing story
    reply = story_actions.get_story(0)
    assert reply.status_code == 404


def test_like(client, auth, database, templates, story_actions):
    auth.login()

    # Invalid story
    reply = story_actions.post_like_reaction(1)
    assert reply.status_code == 404

    reply = story_actions.roll_dice()
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    reply = story_actions.add_story_text(new_id, roll)
    assert reply.status_code == 302

    # First like
    reply = story_actions.post_like_reaction(new_id)
    assert reply.status_code == 200
    r = Reaction.query.filter_by(reactor_id=1, story_id=new_id).one()
    s = Story.query.get(new_id)
    assert r is not None
    assert r.reaction_val == 1
    assert s.likes == 1 and s.dislikes == 0

    # duplicated like
    reply = story_actions.post_like_reaction(new_id)
    assert reply.status_code == 400
    database.session.refresh(r)
    database.session.refresh(s)
    assert r is not None
    assert r.reaction_val == 1
    assert s.likes == 1 and s.dislikes == 0

    auth.logout()
    auth.login('test1', 'test1123')

    # Second like
    reply = story_actions.post_like_reaction(new_id)
    assert reply.status_code == 200
    r = Reaction.query.filter_by(reactor_id=2, story_id=new_id).one()
    s = Story.query.get(new_id)
    assert r is not None
    assert r.reaction_val == 1
    assert s.likes == 2 and s.dislikes == 0


def test_dislike(client, auth, database, templates, story_actions):
    auth.login()

    # Invalid story
    reply = story_actions.post_dislike_reaction(1)
    assert reply.status_code == 404

    reply = story_actions.roll_dice()
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']
    reply = story_actions.add_story_text(new_id, roll)
    assert reply.status_code == 302

    # First like
    reply = story_actions.post_dislike_reaction(new_id)
    assert reply.status_code == 200
    r = Reaction.query.filter_by(reactor_id=1, story_id=new_id).one()
    s = Story.query.get(new_id)
    assert r is not None
    assert r.reaction_val == -1
    assert s.likes == 0 and s.dislikes == 1

    # duplicated like
    reply = story_actions.post_dislike_reaction(new_id)
    assert reply.status_code == 400
    database.session.refresh(r)
    database.session.refresh(s)
    assert r is not None
    assert r.reaction_val == -1
    assert s.likes == 0 and s.dislikes == 1

    auth.logout()
    auth.login('test1', 'test1123')
    # Second like
    reply = story_actions.post_dislike_reaction(new_id)
    assert reply.status_code == 200
    r = Reaction.query.filter_by(reactor_id=2, story_id=new_id).one()
    s = Story.query.get(new_id)
    assert r is not None
    assert r.reaction_val == -1
    assert s.likes == 0 and s.dislikes == 2

def test_reaction_change(client, auth, database, templates, story_actions):
    auth.login()

    reply = story_actions.roll_dice()
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    reply = story_actions.add_story_text(new_id, roll)
    assert reply.status_code == 302

    # First like
    reply = story_actions.post_like_reaction(1)
    assert reply.status_code == 200
    r = Reaction.query.filter_by(reactor_id=1, story_id=new_id).one()
    s = Story.query.get(new_id)
    assert r is not None
    assert r.reaction_val == 1
    assert s.likes == 1 and s.dislikes == 0

    auth.logout()
    auth.login()

    # Change with dislike
    reply = story_actions.post_dislike_reaction(new_id)
    assert reply.status_code == 200
    r = Reaction.query.filter_by(reactor_id=1, story_id=new_id).one()
    s = Story.query.get(new_id)
    assert r is not None
    assert r.reaction_val == -1
    assert s.likes == 0 and s.dislikes == 1

    # Change with like
    reply = story_actions.post_like_reaction(new_id)
    assert reply.status_code == 200
    r = Reaction.query.filter_by(reactor_id=1, story_id=new_id).one()
    s = Story.query.get(new_id)
    assert r is not None
    assert r.reaction_val == 1
    assert s.likes == 1 and s.dislikes == 0


def test_react_to_deleted_story(client, auth, database, templates,
                                story_actions):
    auth.login()

    # add valid story
    reply = story_actions.roll_dice()
    assert reply.status_code == 200
    roll = templates[-1]['dice']
    new_id = templates[-1]['story_id']

    reply = story_actions.add_story_text(new_id, roll)
    assert reply.status_code == 302

    reply = story_actions.delete_story(new_id)
    assert reply.status_code == 200

    # like it
    reply = story_actions.post_like_reaction(new_id)
    assert reply.status_code == 410

    # dislike it
    reply = story_actions.post_dislike_reaction(new_id)
    assert reply.status_code == 410


def test_react_to_draft(client, auth, database, templates, story_actions):
    auth.login()

    # add draft
    reply = story_actions.roll_dice()
    assert reply.status_code == 200
    new_id = templates[-1]['story_id']

    # like it
    reply = story_actions.post_like_reaction(new_id)
    assert reply.status_code == 403

    # dislike it
    reply = story_actions.post_dislike_reaction(new_id)
    assert reply.status_code == 403
