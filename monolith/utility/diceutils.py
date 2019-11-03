from monolith.definitions import RESOURCES_DIR


def get_dice_sets_list():
    with open(RESOURCES_DIR + '/diceset.txt', 'r') as f:
        set_list = f.read().splitlines()
    return set_list


def get_die_faces_list(setname, dienum):
    path = '{}/diceset/{}/die{}.txt'.format(RESOURCES_DIR, setname, dienum)
    with open(path, 'r') as f:
        face_list = f.read().splitlines()
    return face_list
