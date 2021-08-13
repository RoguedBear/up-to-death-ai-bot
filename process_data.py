"""
Processes keystrokes and images and then finally save them in an organised folder.
TODO:
    - concatenate data from multiple files from a folder
Processing rules:
    - remove all data between `del` and `space` keys                ✔
    - remove all data between `del` and the previous `space` key    ✔
    - remove contiguous (1,2,3) recurring space or delete keys      ✔
    - remove 1-1.5s prior data (or when a previous "space" is encountered, whichever comes first) when encounter `space`

What we doing now:
    - removing contigous spaces
        - use np.where,
        - convert it to 1d array
        - use diff and prepend with n[0] - 2
        - np.where(difference != 1)[0]
        - np.delete(keys, indexes[np.where(difference == 1)[0]])
    - finding pairs of del and spaces
        - custom for loop through del arrays
        - find index of spaces b/w current delete index and next delete index
            - if more than one spaces are found, exit the program
            - other wise we have pairs


"""
from typing import Tuple, List, Union

import numpy as np


def remove_contiguous_stuff(arr: np.ndarray, to_delete: str) -> np.ndarray:
    """Accepts an array and then removes repeating contiguous spaces
    # Pseudocode:
    - removing contigous spaces
        - use np.where,
        - convert it to 1d array
        - use diff and prepend with n[0] - 2
        - np.where(difference != 1)[0]
        - np.delete(keys, indexes[np.where(difference == 1)[0]])
    """
    # get indexes of spaces
    index_of_spaces = np.where(arr == to_delete)[0]

    # get differences for detecting repeating
    differences = np.diff(index_of_spaces, prepend=index_of_spaces[0] - 2)

    # now get the indexes to freakin delete
    indexes_of_spaces_to_delete = np.where(differences == 1)[0]

    # now return
    return index_of_spaces[indexes_of_spaces_to_delete]


def find_del_space_pairs(keystrokes: np.ndarray) -> Tuple[Tuple[int, int], ...]:
    """Find del-space-del pairs or something like that. im not quite sure how."""
    spaces: np.ndarray = np.where(keystrokes == " ")[0]
    delete: np.ndarray = np.where(keystrokes == "del")[0]
    pairs: List[Tuple[int, int]] = []
    # iterate and get intersection and pairs
    print(delete, spaces)
    if len(delete) == 1:
        # use the property that the difference b/w numbers is the distance b/w numbers. so finding the index of the
        # number having minimum distance, and then the index of number w/ 2nd big distance will give us the pair
        first: Tuple[int, int]
        second: Tuple[int, int]
        min_index = np.abs(spaces - delete).argmin()
        if spaces[min_index] < delete[0]:
            first = spaces[min_index], delete[0]
            second = delete[0], spaces[min_index + 1]
        elif spaces[min_index] > delete[0]:
            first = spaces[min_index - 1], delete[0]
            second = spaces[min_index], delete[0]
        else:
            print("uh oh. something's going on here, you might wanna take a look....")
            print("spaces:", spaces)
            print("delete:", delete)
            exit(1)
        return first, second

    for i in range(len(delete) - 1):
        intersection = np.intersect1d(spaces[delete[i] < spaces], spaces[spaces < delete[i + 1]])[0]
        if not isinstance(intersection, np.int64):
            print("ERROR! WARNING! ERROR! there are more than 2 spaces. ABORT!")
            print(intersection)
            exit(1)
        pairs.append((delete[i], intersection))
        pairs.append((intersection, delete[i + 1]))
    return tuple(pairs)


def remove(keystroke: np.ndarray, time: np.ndarray, image: np.ndarray, indexes: Union[np.ndarray, range]) -> Tuple[
    np.ndarray, np.ndarray, np.ndarray]:
    return np.delete(keystroke, indexes), \
           np.delete(time, indexes), \
           np.delete(image, indexes, axis=0)


if __name__ == '__main__':
    # first thing to do
    x = np.load("data/sample_data_6_keys.npz.npy", allow_pickle=True)
    img = np.load("data/sample_data_6_img-bin.npz.npy", allow_pickle=True)
    # replace None with null byte
    # keystokes = x[:, 0]
    # time = x[:, 1]
    # x[:, 0][x[:, 0] == None] = "\0"

    # TEST
    keys = x[:, 0]
    time = x[:, 1]

    print("Len of key, time, img", len(keys), len(time), len(img))
    indexes = remove_contiguous_stuff(keys, " ")
    print(indexes)
    keys, time, img = remove(keys, time, img, indexes)
    print("Len of key, time, img", len(keys), len(time), len(img))

    # Test 2
    print("-------------------------------")
    pairs = find_del_space_pairs(keys)
    for i,j in pairs:
        keys, time, img = remove(keys, time, img, range(i, j))
    print("Len of key, time, img", len(keys), len(time), len(img))
