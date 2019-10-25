from monolith.definitions import *


def get_dice_sets_lsit():
    f = open(RESOURCES_DIR + "/diceset.txt", "r")
    set_list = f.read().splitlines()
    f.close();
    return set_list
