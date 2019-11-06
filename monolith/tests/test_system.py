def test_single_user(auth, story_actions, templates):
    email="prova@prova.com"
    username="Test"
    password="12345678"

    #signup and login
    auth.signup(email=email, username=username, password=password)
    auth.login(username=username, password=password)

    #add stories
    story_actions.add_valid_story()
    story_actions.add_valid_story()

    #visualize story
    story_actions.get_story(1)
    story_actions.get_story(2)
    auth.logout()