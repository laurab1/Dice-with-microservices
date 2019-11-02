from flask import Blueprint, redirect, render_template, request, abort, jsonify
from monolith.database import db, Story, Like
from flask import current_app as app
from monolith.utility.diceutils import *
from monolith.forms import *
from monolith.classes.DiceSet import *
import string
import requests
import json


_URL_WORDS_API = 'https://wordsapiv1.p.rapidapi.com/words/'
_HEADERS_WORDS_API =  headers = {
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
 
    url = _URL_WORDS_API+word+"/synonyms"
    response = requests.request("GET", url, headers=_HEADERS_WORDS_API)

    if response.status_code == 200:
        return json.loads(response.text)["synonyms"]
    else:
        raise WrongWordError("The word {} does not exist!".format(word))

def _check_story(roll, story_text):
    
    n_dices = len(roll)
    roll_lower = [w.lower() for w in roll]

    story_words = story_text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation))).replace(' '*4, ' ').replace(' '*3, ' ').replace(' '*2, ' ').split()
    story_words = [w.lower() for w in story_words]
        
    story_len = len(story_words)
    if story_len < n_dices:
        raise NotValidStoryError("the story is not valid")
    
    n_dices_checked = 0
    
    for w in roll_lower:
        if w in story_words:
            n_dices_checked += 1
        
        else: #check in the synonyms
            try:
                syn_words = get_synonyms(w)
                found = False
                idx = 0
            
                while idx < len(story_words) and not found:
                    sw = story_words[idx]
                    if sw in syn_words:
                        n_dices_checked +=1
                        found = True
                    else:
                        idx += 1
            
            except WrongWordError as e: #what if in the roll there is a word that does not exist?
                print(e)

    if n_dices_checked != n_dices:
        raise NotValidStoryError("the story is not valid")
