from monolith.database import User, Story

def test_getuser(client, database):
    # TODO: implementa un test in cui effettui il login,
    #       chiami la get_user su uno degli utenti di test (si chiamano 
    #       test1, test2 e test3), dopodiché aggiungi una storia a uno di loro
    #       e controlli che anche il risultato della get_user cambi.
    pass

def test_getuser_fail(client, database):
    # TODO: implementa un test in cui effettui il login,
    #       chiami la get_user su un utente non esistente e
    #       controlli lo status code
