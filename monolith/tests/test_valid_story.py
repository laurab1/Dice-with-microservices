import unittest
from kombu.utils import json
from monolith.utility.diceutils import *
from monolith import app as test_app
from monolith.utility.validate_story import _check_story,NotValidStoryError,get_synonyms
from monolith.classes.DiceSet import *

class TestApp(unittest.TestCase):
    
    def test_correct_story(self):        
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

    def test_empty_story(self):
        diceset = 'standard'
        dicenum = 6
        dice = DiceSet(diceset, dicenum)
        roll = dice.throw_dice()

        story = ''
        self.assertRaises(NotValidStoryError,_check_story,roll,story)
    

    def test_correct_story_with_punctuation(self):

        roll = ['table','window','cat','chair']
        story = 'The cat is on the table! The chair, I think, is near the window.'
        try:
            _check_story(roll,story)
        except NotValidStoryError:
            raise NotValidStoryError("Test failed...")
    
    def test_correct_story_with_parentesys(self):

        roll = ['table','window','cat','chair']
        story = 'The cat is on the table and...the chair, I think, is near the window:)'
        try:
            _check_story(roll,story)
        except NotValidStoryError:
            raise NotValidStoryError("Test failed...")

    
    def test_correct_story_synonym(self):
        roll = ['table','window','cat','chair']
        story = 'The cat is on the board, the chair is near the window.'
        try:
            _check_story(roll,story)
        except NotValidStoryError:
            raise NotValidStoryError("Test failed...")
    
    def test_wrong_story_synonym(self):
        roll = ['table','window','cat','chair']
        story = 'The cat is on the board, the chair is near the door.'
        self.assertRaises(NotValidStoryError,_check_story,roll,story)
    
    def test_wrong_word_in_roll(self):
        roll = ['table','window','cat','chai']
        story = 'The cat is on the board, the chair is near the window.'
        try:
            _check_story(roll,story)
        except NotValidStoryError as error:
            print(str(error))
        