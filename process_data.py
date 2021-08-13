"""
Processes keystrokes and images and then finally save them in an organised folder.
TODO:
    - concatenate data from multiple files from a folder
Processing rules:
    - remove all data between `del` and `space` keys
    - remove all data between `del` and the previous `space` key
    - remove contiguous (1,2,3) recurring space or delete keys      ✔
    - remove 1-1.5s prior data when encounter `space`

What we doing now:
    - removing contigous spaces
        - use np.where,
        - convert it to 1d array
        - use diff and prepend with n[0] - 2
        - np.where(difference != 1)[0]
        - np.delete(keys, indexes[np.where(difference == 1)[0]])

"""
from typing import Tuple

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

    # now delete
    return index_of_spaces[indexes_of_spaces_to_delete]


def remove(keystroke: np.ndarray, time: np.ndarray, image: np.ndarray, indexes: np.ndarray) -> Tuple[
    np.ndarray, np.ndarray, np.ndarray]:
    return np.delete(keystroke, indexes), \
           np.delete(time, indexes),\
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
