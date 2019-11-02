import random as rnd
from monolith.definitions import RESOURCES_DIR
from monolith.utility.diceutils import get_dice_sets_lsit


class Die:

    def __init__(self, filename):
        self.faces = []
        self.pip = None
        f = open(filename, "r")
        lines = f.readlines()
        for line in lines:
            self.faces.append(line.replace("\n", ""))
        self.throw_die()
        f.close()

    def throw_die(self):
        if self.faces:  # pythonic for list is not empty
            self.pip = rnd.choice(self.faces)
            return self.pip
        else:
            raise IndexError("throw_die(): empty die error.")


class DiceSet:

    def __init__(self, setname, dicenumber):
        self.dice = [Die]*dicenumber
        self.pips = [Die]*dicenumber
        self.dicenumber = dicenumber
        self.setname = setname

        # Check if given set exist #
        if setname not in get_dice_sets_lsit():
            raise InvalidDiceSet(setname)

        # Create all the dice #
        for i in range(0,dicenumber):
            self.dice[i] = Die(RESOURCES_DIR+"/diceset/"+setname+"/die"+str(i)+".txt")

    def throw_dice(self):
        for i in range(0,self.dicenumber):
            self.pips[i] = self.dice[i].throw_die()
        return self.pips

import unittest
 
class TestDie(unittest.TestCase):
 
    def test_die_init(self):
        die = Die("tests/die0.txt")
        check = ['bike', 'moonandstars', 'bag', 'bird', 'crying', 'angry']
        self.assertEqual(die.faces, check)

    def test_die_pip(self):
        rnd.seed(574891)
        die = Die("tests/die0.txt")
        res = die.throw_die()
        self.assertEqual(res, 'bag')

    
 
 
if __name__ == '__main__':
    unittest.main()
    self.dice = [Die] * dicenumber
    self.pips = [Die] * dicenumber
    self.dicenumber = dicenumber
    self.setname = setname
    
    # Check given parameters #
    self._dice_preconditions(setname, dicenumber);
    
    # Create all the dice #
    for i in range(0, dicenumber):
        self.dice[i] = Die(RESOURCES_DIR + "/diceset/" + setname + "/die" + str(i) + ".txt")

    def throw_dice(self):
        for i in range(0, self.dicenumber):
            self.pips[i] = self.dice[i].throw_die()
        return self.pips

    def _dice_preconditions(self, setname, dicenum):
        if dicenum < 4 or dicenum > 6:
            raise InvalidDiceSet()

        if setname not in get_dice_sets_lsit():
            raise InvalidDiceSet(setname)


class InvalidDiceSet(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

