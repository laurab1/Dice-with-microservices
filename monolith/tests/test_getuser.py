from monolith.database import User, Story

def test_getuser(client, database):
    # TODO: implementa un test in cui effettui il login,
    #       chiami la get_user su uno degli utenti di test (si chiamano 
    #       test1, test2 e test3), dopodiché aggiungi una storia a uno di loro
    #       e controlli che anche il risultato della get_user cambi.

    reply = client.get('/login')
    assert reply.status_code == 200

    reply = client.get('/users')
    assert reply.get_json()['users'] == [['Admin', None], # ottengo TypeError: 'NoneType' object is not subscriptable ?
                                         ['test1', None],
                                         ['test2', None],
                                         ['test3', None]]    

    example = Story()
    example.text = 'First story of admin user :)'
    example.author_id = 1
    database.session.add(example)
    database.session.commit()
    
    reply = client.get('/user/Admin')
    assert reply.get_json()['user'] == ['Admin']
    assert reply.get_json()['stories'] == ['First story of admin user :)']
        
    reply = client.get('/user/test1')
    assert reply.get_json()['user'] == ['test1']
    assert reply.get_json()['stories'] == []

    pass

def test_getuser_fail(client, database):
    # TODO: implementa un test in cui effettui il login,
    #       chiami la get_user su un utente non esistente e
    #       controlli lo status code
    reply = client.get('/login')
    assert reply.status_code == 200

    reply = client.get('/user/utenteNonEsistente')
    assert reply.status_code == 404
