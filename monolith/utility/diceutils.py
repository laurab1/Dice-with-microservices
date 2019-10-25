from monolith.definitions import *


def get_dice_sets_lsit():
    f = open(RESOURCES_DIR + "/diceset.txt", "r")
    set_list = f.read().splitlines()
    f.close();
    return set_list


def get_die_faces_lsit(setname, dienum):
    f = open(RESOURCES_DIR + "/diceset/" + setname + "/die" + str(dienum) + ".txt", "r")
    face_list = f.read().splitlines()
    f.close();
    return face_list
