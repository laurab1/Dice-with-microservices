from monolith.definitions import RESOURCES_DIR


def get_dice_sets_list():
    with open(f'{RESOURCES_DIR}/diceset.txt', 'r') as f:
        set_list = f.read().splitlines()
    return set_list


def get_die_faces_list(setname, dienum):
    path = f'{RESOURCES_DIR}/diceset/{setname}/die{dienum}.txt'
    with open(path, 'r') as f:
        face_list = f.read().splitlines()
    return face_list
