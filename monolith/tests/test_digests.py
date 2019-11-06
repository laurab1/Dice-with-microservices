import datetime as dt

import monolith.utility.digests as digests
from monolith.database import Story, User


def test_story_digest_format():
    u = User()
    u.username = 'Username'
    u.email = 'username@example.com'
    u.firstname = 'Firstname'
    u.lastname = 'Lastname'

    date = dt.datetime.now()
    s = Story()
    s.author = u
    s.text = 'Lorem ipsum dolor sit amet'
    s.date = date
    s.likes = 42
    s.dislikes = 69
    s.dice_set = ['lorem', 'ipsum', 'dolor', 'sit', 'amet']
    s.deleted = False
    s.is_draft = False

    lines = digests.story_digest(s).split('\n')
    assert lines[0] == 'author: Firstname Lastname (Username)'
    assert lines[1] == 'roll: lorem, ipsum, dolor, sit, amet'
    assert lines[2] == f'date: {date}'
    assert lines[3] == 'story: Lorem ipsum dolor sit amet'
    assert lines[4] == 'likes: 42 -- dislikes: 69'


def test_user_digest_format(client, database):
    now = dt.datetime.now()

    s1 = Story(author_id=2, text='Story 1',
               likes=42, dislikes=69, is_draft=False, deleted=False)
    s1.dice_set = ['dice', 'set']
    s1.date = now - dt.timedelta(days=1)
    database.session.add(s1)

    s2 = Story(author_id=2, text='Story 2', date=now, likes=42, dislikes=69,
               is_draft=False, deleted=False)
    s2.dice_set = ['dice', 'set']
    s2.date = now
    database.session.add(s2)

    s3 = Story(author_id=2, text='Story 3',
               likes=42, dislikes=69, is_draft=False, deleted=False)
    s3.dice_set = ['dice', 'set']
    s3.date = now - dt.timedelta(days=7)
    database.session.add(s3)

    s4 = Story(author_id=3, text='Story 4', likes=42, dislikes=69,
               is_draft=False, deleted=False)
    s4.dice_set = ['dice', 'set']
    s4.date = now
    database.session.add(s4)

    s5 = Story(author_id=2, text='Story 5', likes=42, dislikes=69,
               is_draft=True, deleted=False)
    s5.dice_set = ['dice', 'set']
    s5.date = now
    database.session.add(s5)

    s6 = Story(author_id=2, text='Story 5', likes=42, dislikes=69,
               is_draft=False, deleted=True)
    s6.dice_set = ['dice', 'set']
    s6.date = now
    database.session.add(s6)

    u = User.query.get(1)
    u.follows.append(User.query.get(2))
    database.session.commit()

    digest = digests.build_user_digest(u, now - dt.timedelta(days=2),
                                       now + dt.timedelta(days=2)) \
                    .get_content().split('----------\n')
    assert len(digest) == 2
    assert digest[0] == digests.story_digest(s2)
    assert digest[1] == digests.story_digest(s1)


def test_no_followed_digest(client, database):
    u = User.query.get(1)
    now = dt.datetime.now()

    digest = digests.build_user_digest(u, now, now)
    msg = 'Start following your favourite users to get periodic digests.\n'
    assert digest.get_content() == msg


def test_no_stories_digest(client, database):
    now = dt.datetime.now()
    u = User.query.get(1)
    u.follows.append(User.query.get(2))
    database.session.commit()

    digest = digests.build_user_digest(u, now, now)
    assert digest.get_content() == 'No stories uploaded from your following.\n'


def test_digest_task(client, database, smtp_server):
    # Here because it requires the app context to be set
    from monolith.task import send_digest

    no_stories = 'Start following your favourite users to get ' \
                 'periodic digests.'
    send_digest.apply()
    for msg in smtp_server.messages:
        assert msg.get_payload() == no_stories

    now = dt.datetime.now()
    s1 = Story(author_id=2, text='Story 1',
               likes=42, dislikes=69, is_draft=False, deleted=False)
    s1.dice_set = ['dice', 'set']
    s1.date = now - dt.timedelta(days=1)
    database.session.add(s1)

    s2 = Story(author_id=2, text='Story 2',
               likes=42, dislikes=69, is_draft=False, deleted=False)
    s2.dice_set = ['dice', 'set']
    s2.date = now - dt.timedelta(days=60)
    database.session.add(s2)

    s3 = Story(author_id=3, text='Story 3',
               likes=42, dislikes=69, is_draft=False, deleted=False)
    s3.dice_set = ['dice', 'set']
    s3.date = now - dt.timedelta(days=4)
    database.session.add(s3)

    u1 = User.query.get(1)
    u2 = User.query.get(2)
    u3 = User.query.get(3)
    u4 = User.query.get(4)
    u1.follows.append(u2)
    u2.follows.append(u3)
    u3.follows.append(u4)
    database.session.commit()

    smtp_server.reset()
    send_digest.apply()
    for msg in smtp_server.messages:
        u = User.query.filter_by(email=msg['To']).one()
        digest = digests.build_user_digest(u, now - dt.timedelta(weeks=4), now)
        payload = msg.get_payload().replace('\r\n', '\n').strip()
        digest = digest.get_payload().replace('\r\n', '\n').strip()
        assert payload == digest
