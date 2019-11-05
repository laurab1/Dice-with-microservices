from monolith.database import Story
import datetime as dt

def test_get_by_interest(client, database, templates):
    client.post('/login', data={'usrn_eml': 'Admin', 'password': 'admin'})

    example1 = Story()
    example1.theme = 'halloween'
    example1.text = 'Halloween story of test1 user :)'
    example1.author_id = 2
    database.session.add(example1)
    database.session.commit()

    example2 = Story()
    example2.theme = 'xmas'
    example2.text = 'Xmas story of test2 user :)'
    example2.author_id = 3
    database.session.add(example2)
    database.session.commit()

    example3 = Story()
    example3.theme = 'xmas'
    example3.theme = 'Old xmas story of test3 user :)'
    example3.date = dt.datetime.now() - dt.timedelta(days=6)
    example3.author_id = 4
    database.session.add(example3)
    database.session.commit()

    reply = client.get('/stories?theme=xmas')
    assert reply.status_code == 200
    assert templates[-1]['stories'].all() == [example2]
