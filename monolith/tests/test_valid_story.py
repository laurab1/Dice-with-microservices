from monolith.classes.DiceSet import DiceSet
from monolith.utility.validate_story import NotValidStoryError, _check_story

import pytest


def test_correct_story():
    diceset = 'standard'
    dicenum = 6
    dice = DiceSet(diceset, dicenum)
    roll = dice.throw_dice()

    story = ''
    for word in roll:
        story += word + ' '

    _check_story(roll, story)


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
    _check_story(roll, story)


def test_correct_story_with_parentesys():
    roll = ['table', 'window', 'cat', 'chair']
    story = 'The cat is on the table and...the chair, I think, is near the ' \
        'window:)'
    _check_story(roll, story)


def test_correct_story_synonym():
    roll = ['table', 'window', 'cat', 'chair']
    story = 'The cat is on the board, the chair is near the window.'
    _check_story(roll, story)


def test_wrong_story_synonym():
    roll = ['table', 'window', 'cat', 'chair']
    story = 'The cat is on the board, the chair is near the door.'
    with pytest.raises(NotValidStoryError):
        _check_story(roll, story)


def test_wrong_word_in_roll():
    roll = ['table', 'window', 'cat', 'chai']
    story = 'The cat is on the board, the chair is near the window.'
    with pytest.raises(NotValidStoryError):
        _check_story(roll, story)
