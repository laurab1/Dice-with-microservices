import random as rnd

from monolith.definitions import RESOURCES_DIR
from monolith.utility.diceutils import get_dice_sets_list


class Die:
    '''
    Models a 6-faces die.
    '''
    def __init__(self, filename):
        self.faces = []
        self.pip = None
        with open(filename, 'r') as f:
            for line in f.readlines():
                self.faces.append(line.replace('\n', ''))
            self.throw_die()

    def throw_die(self):
        '''
        Rolls a die and randomly returns of the faces.
        '''
        if self.faces:
            self.pip = rnd.choice(self.faces)
            return self.pip
        raise IndexError("throw_die(): empty die error.")


class DiceSet:
    '''
    Models a dice set.
    '''
    def __init__(self, setname, dicenumber):
        '''
        Initializes the dice set.

        Args:
            setname(str): the name of the directory of the chosen dice set
            dicenumber(int): the number of dice to be used
        '''
        self.dice = [Die] * dicenumber
        self.pips = [Die] * dicenumber
        self.dicenumber = dicenumber
        self.setname = setname

        # Check given parameters #
        self._dice_preconditions(setname, dicenumber)

        # Create all the dice #
        for i in range(dicenumber):
            path = '{}/diceset/{}/die{}.txt'.format(RESOURCES_DIR, setname, i)
            self.dice[i] = Die(path)

    def throw_dice(self):
        '''
        Each die is rolled (a random face is chosen)
        '''
        for i in range(self.dicenumber):
            self.pips[i] = self.dice[i].throw_die()
        return self.pips

    def _dice_preconditions(self, setname, dicenum):
        '''
        Checks the dice set preconditions and eventually raises an exception.
        '''
        if dicenum < 4 or dicenum > 6:
            raise InvalidDiceSet()

        if setname not in get_dice_sets_list():
            raise InvalidDiceSet(setname)


class InvalidDiceSet(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
