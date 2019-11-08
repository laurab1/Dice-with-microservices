import datetime as dt

from monolith.database import Story


def test_get_by_interest(client, auth, database, templates, story_actions):
    auth.login()

    example1 = Story()
    example1.theme = 'halloween'
    example1.text = 'Halloween story of test1 user :)'
    example1.author_id = 2
    example1.is_draft = False
    example1.deleted = False
    example1.dice_set = ['a', 'b', 'c']
    database.session.add(example1)
    database.session.commit()

    example2 = Story()
    example2.theme = 'xmas'
    example2.text = 'Xmas story of test2 user :)'
    example2.author_id = 3
    example2.is_draft = False
    example2.deleted = False
    example2.dice_set = ['a', 'b', 'c']
    database.session.add(example2)
    database.session.commit()

    example3 = Story()
    example3.theme = 'xmas'
    example3.theme = 'Old xmas story of test3 user :)'
    example3.date = dt.datetime.now() - dt.timedelta(days=6)
    example3.author_id = 4
    example3.is_draft = False
    example3.deleted = False
    example3.dice_set = ['a', 'b', 'c']
    database.session.add(example3)
    database.session.commit()

    reply = story_actions.get_all_stories(theme='xmas')
    assert reply.status_code == 200
    assert templates[-1]['stories'].all() == [example2]
