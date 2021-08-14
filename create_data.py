import os
import time

import mss
import numpy as np
from cv2 import cv2

from util import array_cleaner
from util.detect_game_scene import find_rough_coords
from util.detect_game_start import fine_tune, is_spikes_visible
from util.get_key import key_check


def save(keystrokes: list, images: list):
    def generate_file_name(pattern: str, number: int) -> str:
        return f"{pattern}_{number}"

    file_name = "data/sample_data"
    count = 0
    valid_name = False
    while valid_name is False:
        if os.path.isfile(generate_file_name(file_name, count)+ "_key.txt"):
            count += 1
        else:
            valid_name = True
            file_name = generate_file_name(file_name, count)

    np.save(file_name + "_img-bin.npz", images)
    np.save(file_name + "_keys.npz", keystrokes)
    print("saved. ", file_name)


sct = mss.mss()
template = cv2.imread("screens/splashscreen1.png")

print("Finding game screen...")
# monitor = {'top': 202, 'left': 6, 'width': 1221, 'height': 688}
monitor = find_rough_coords(sct, template, 0.69)

# fine tune
while 0.5 > is_spikes_visible(np.array(sct.grab(monitor))):
    pass
monitor = fine_tune(np.array(sct.grab(monitor)), monitor)
# the loop
count = 0
load = "-\\|/"
while True:
    print("Waiting for you to press ' ' space key... ", load[count], end="\r")
    count += 1
    if count == len(load):
        count = 0
    if key_check() == ' ':
        print()
        break
    time.sleep(0.01)

print("Starting data collection...")
keystrokes = []
images = []
last_key_pressed = time.time()
last_run_index = 0
while True:
    # -------
    start = time.time()

    # grab screenshot
    image = np.array(sct.grab(monitor))

    # log keystroke
    pressed_key = key_check()
    # ------

    # fail-safe
    if start - last_key_pressed >= 6:
        print("WARNING: No input detected for the last 6 seconds!! you have choice now...")
        array_cleaner.remove_from_last_till(last_key_pressed, keystrokes, images)
        print("Waiting for input.... (' '/h)")
        continue_loop = True
        while continue_loop:
            keystroke = key_check()
            if keystroke == "H":
                print("exiting...")
                break
            elif keystroke == " ":
                print("continuing loop...")
                continue_loop = False
                last_key_pressed = start
                last_run_index = len(keystrokes)
        else:
            continue
        break

    # grace exit
    if pressed_key == "H":
        break

    # delete last run
    if pressed_key == "del":
        # dont worry, space is kept.
        keystrokes[:] = keystrokes[:last_run_index + 1]
        images[:] = images[:last_run_index + 1]
        print("discarded last run")
    # -------

    # convert to b/w
    cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, image)
    # run canny detection
    image = cv2.Canny(image, 157, 287)
    # resize to 224x224
    image = cv2.resize(image, (224, 224))

    # show preview
    cv2.imshow("preview", image)
    cv2.waitKey(1)

    if pressed_key:
        last_key_pressed = start
    # mark last run for deletion
    if pressed_key == " ":
        last_run_index = len(keystrokes)

    # add these to arrays
    images.append(image)
    keystrokes.append((pressed_key, start))

    # -------
    print("\rFPS: ", round(1 / (time.time() - start), 0), end=" ")

# start with a space, end with a space
keystrokes.append((" ", start))
images.append(image)
cv2.destroyAllWindows()
save(keystrokes, images)
