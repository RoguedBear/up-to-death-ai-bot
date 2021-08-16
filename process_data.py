"""
Processes keystrokes and images and then finally save them in an organised folder.
TODO:
    - concatenate data from multiple files from a folder
    - Convert None to either \0 null byte ot just "null"
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
import os
from glob import glob
from typing import Tuple, List, Union

import numpy as np
from cv2.cv2 import imwrite


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

    for i in range(1, len(spaces) - 1):
        intersection = np.intersect1d(delete[spaces[i] < delete], delete[delete < spaces[i + 1]])
        if intersection.size > 0:
            intersection = intersection[0]
            if not isinstance(intersection, np.int64):
                print("ERROR! WARNING! ERROR! there are more than 2 delete in between space. ABORT!")
                print(intersection)
                exit(1)
            # pairs.append((spaces[i], intersection)) --- commented out because we're already deleting space-del
            # #Repetition #NoFilters #SaveEarth #Windy4Cybersec #WINDYAPPROVES!!!!
            pairs.append((intersection, spaces[i + 1]))
    return tuple(pairs)


def remove_1s_data(time: np.ndarray, index_of_space: np.int64) -> Tuple[int, int]:
    """
    Returns the index of data to be removed
    PSEUDOCODE:
        - store the difference from time - space
        - filter by indexes whose difference is greater than -1.5s
        - get the min value. that'll be the range to delete
    """
    time = time.astype(np.float64)
    from_time = time[index_of_space]
    difference = time - from_time
    to_index = np.where(difference > -1.5)[0][0]
    return to_index, int(index_of_space)


def remove(keystroke: np.ndarray, time: np.ndarray, image: np.ndarray, indexes: Union[np.ndarray, range, List]) -> \
Tuple[
    np.ndarray, np.ndarray, np.ndarray]:
    return np.delete(keystroke, indexes), \
           np.delete(time, indexes), \
           np.delete(image, indexes, axis=0)


def process_data(keys: np.ndarray, time: np.ndarray, images: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The main function to process data and call every function known to mankind"""

    # first filter the data to remove continuous spaces and del keys
    duplicated_space_indexes = remove_contiguous_stuff(keys, " ")
    keys, time, images = remove(keys, time, images, duplicated_space_indexes)
    if keys[keys == "del"].size > 0:
        duplicated_space_indexes = remove_contiguous_stuff(keys, "del")
        keys, time, images = remove(keys, time, images, duplicated_space_indexes)
    assert len(keys) == len(time) == len(images), f"Length is not same for key, time, img: {len(keys)}, {len(time)}, " \
                                                  f"{len(images)} "
    # delete space-del-space pairs
    if keys[keys == "del"].size > 0:
        pairs = find_del_space_pairs(keys)
        print("pairs of del:", pairs)
        to_delete = [np.array(range(i, j)) for i, j in pairs]
        keys, time, images = remove(keys, time, images, np.concatenate(to_delete).astype(np.int64))

        assert len(keys) == len(time) == len(images), f"Length is not same for key, time, img: {len(keys)}, " \
                                                      f"{len(time)}, {len(images)} "

    # remove 1.5s prior data
    game_over_indexes: List[Tuple[int, int], ...] = []
    for space_index in np.where(keys == " ")[0][1:]:  # don't consider first space
        pair = remove_1s_data(time, space_index)
        game_over_indexes.append(pair)

    to_delete = [np.array(range(x, y)) for x, y in game_over_indexes]

    keys, time, images = remove(keys, time, images, np.concatenate(to_delete).astype(np.int64))

    assert len(keys) == len(time) == len(images), f"Length is not same for key, time, img: {len(keys)}, {len(time)}, " \
                                                  f"{len(images)} "

    return keys, time, images


def generate_images(keys: np.ndarray, images: np.ndarray, game_number=0):
    """Generates images from the processed npy data"""
    for folder in ["left", "right", "nothing"]:
        if not os.path.isdir("images/" + folder):
            os.mkdir("images/" + folder)

    left_count = 0
    right_count = 0
    nothing_count = 0
    success = False
    path = ""
    for index, key in enumerate(keys):
        if key == "A":
            left_count += 1
            path = f"images/left/data_{game_number}_left_{left_count}_{index}.png"
        elif key == "D":
            right_count += 1
            path = f"images/right/data_{game_number}_right_{right_count}_{index}.png"
        elif key == None:
            nothing_count += 1
            path = f"images/nothing/data_{game_number}_nothing_{nothing_count}_{index}.png"
        else:
            continue
        success = imwrite(path, images[index])

        assert success, "Failed to write: " + path
    print("total images:", len(images))
    print("no of images output:", left_count + right_count + nothing_count)


if __name__ == '__main__':
    TEST = False
    if TEST:
        # first thing to do
        x = np.load("data/sample_data_2_keys.npz.npy", allow_pickle=True)
        img = np.load("data/sample_data_2_img-bin.npz.npy", allow_pickle=True)
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
        print("for del:", np.where(keys == "del"))

        # Test 2
        print("-------------------------------")
        indexes = remove_contiguous_stuff(keys, "del")
        keys, time, img = remove(keys, time, img, indexes)
        pairs = find_del_space_pairs(keys)
        print("pairs: ", pairs)
        for i, j in pairs:
            keys, time, img = remove(keys, time, img, range(i, j))
        print("Len of key, time, img", len(keys), len(time), len(img))

        # Test 3
        print("------------------------------")
        time = time.astype(np.float64)
        spaces = np.where(keys == " ")[0][1:]
        print("spaces: ", spaces)
        for spaces in spaces:
            index = remove_1s_data(time, spaces)
            print(index)
            print("time difference of returned:", time[index[0]] - time[index[1]])
            print("time difference of returned - 1:", time[index[0] - 1] - time[index[1]])

        print("eee")

    if not TEST:
        keys = glob("data/*keys.npz.npy")
        images = glob("data/*bin.npz.npy")
        keys.sort()
        images.sort()

        print(keys, "\n", images)
        for index, file in enumerate(zip(keys, images)):
            print("Processing: ", file[0][5:-8])
            x = np.load(file[0], allow_pickle=True)
            img = np.load(file[1], allow_pickle=True)
            keys = x[:, 0]
            time = x[:, 1]
            print("original length:", len(img), len(keys), len(time))
            print("------------------------------")
            keys, time, img = process_data(keys, time, img)
            generate_images(keys, img)
