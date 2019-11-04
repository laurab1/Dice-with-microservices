import pytest

from monolith.utility.diceutils import *
from monolith import app as test_app
from monolith.utility.validate_story import _check_story,NotValidStoryError,get_synonyms
from monolith.classes.DiceSet import DiceSet

def test_correct_story():
    diceset = 'standard'
    dicenum = 6
    dice = DiceSet(diceset, dicenum)
    roll = dice.throw_dice()

    story = ''
    for word in roll:
        story += word + ' '

    try:
        _check_story(roll,story)
    except NotValidStoryError:
        raise NotValidStoryError('Test failed...')

def test_empty_story():
    diceset = 'standard'
    dicenum = 6
    dice = DiceSet(diceset, dicenum)
    roll = dice.throw_dice()

    story = ''
    with pytest.raises(NotValidStoryError):
        _check_story(roll, story)


def test_correct_story_with_punctuation():
    roll = ['table', 'window', 'cat', 'chair']
    story = 'The cat is on the table! The chair, I think, is near the window.'
    try:
        _check_story(roll, story)
    except NotValidStoryError:
        raise NotValidStoryError("Test failed...")


def test_correct_story_with_parentesys():
    roll = ['table', 'window', 'cat', 'chair']
    story = 'The cat is on the table and...the chair, I think, is near the window:)'
    try:
        _check_story(roll,story)
    except NotValidStoryError:
        raise NotValidStoryError("Test failed...")


def test_correct_story_synonym():
    roll = ['table', 'window', 'cat', 'chair']
    story = 'The cat is on the board, the chair is near the window.'
    try:
        _check_story(roll,story)
    except NotValidStoryError:
        raise NotValidStoryError("Test failed...")


def test_wrong_story_synonym():
    roll = ['table', 'window', 'cat', 'chair']
    story = 'The cat is on the board, the chair is near the door.'
    with pytest.raises(NotValidStoryError):
        _check_story(roll, story)


def test_wrong_word_in_roll():
    roll = ['table', 'window', 'cat', 'chai']
    story = 'The cat is on the board, the chair is near the window.'
    try:
        _check_story(roll, story)
    except NotValidStoryError as error:
        print(str(error))
