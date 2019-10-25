from monolith.classes.DiceSet import DiceSet, Die
import random as rnd
import unittest
 
class TestDie(unittest.TestCase):
 
    def test_create_dice_set_with_size(self):
        diceset = DiceSet("standard", 6);
        thrown = diceset.throw_dice();
        self.assertEqual(len(thrown), 6);


    
 
 
if __name__ == '__main__':
    unittest.main()