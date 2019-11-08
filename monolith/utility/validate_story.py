import json
import string

import requests


_URL_WORDS_API = 'https://wordsapiv1.p.rapidapi.com/words/'
_HEADERS_WORDS_API = {
    'x-rapidapi-host': 'wordsapiv1.p.rapidapi.com',
    'x-rapidapi-key': 'e1dff88001mshdad21a84475367ap10433ejsn4f5e5f807958'
}


class NotValidStoryError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class WrongWordError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def get_synonyms(word):
    '''
    Gets the synonyms of a word.
    '''

    url = f'{_URL_WORDS_API}{word}/synonyms'
    response = requests.request('GET', url, headers=_HEADERS_WORDS_API)

    if response.status_code == 200:
        return json.loads(response.text)['synonyms']
    raise WrongWordError(f'The word {word} does not exist!')


def _check_story(roll, story_text):
    '''
    Validates the story by checking if the words (or a synonym) of all the faces of the
    rolled dice are contained in the text. 

    Args:
        roll(list(str)): list of words representing the faces
        story_text(str): the text of the story
    
    Raises:
        NotValidStoryError

    '''

    n_dices = len(roll)
    roll_lower = [w.lower() for w in roll]

    trans = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    story_words = story_text.translate(trans).replace(' ' * 4, ' ') \
                            .replace(' ' * 3, ' ').replace(' ' * 2, ' ') \
                            .split()
    story_words = [w.lower() for w in story_words]

    story_len = len(story_words)
    if story_len < n_dices:
        raise NotValidStoryError('the story is not valid')

    n_dices_checked = 0
    for w in roll_lower:
        if w in story_words:
            n_dices_checked += 1
        else:  # check in the synonyms
            try:
                syn_words = get_synonyms(w)
                idx = 0

                while idx < len(story_words):
                    sw = story_words[idx]
                    if sw in syn_words:
                        n_dices_checked += 1
                        break
                    else:
                        idx += 1
            # what if in the roll there is a word that does not exist?
            except WrongWordError as e:
                print(e)

    if n_dices_checked != n_dices:
        raise NotValidStoryError('the story is not valid')
