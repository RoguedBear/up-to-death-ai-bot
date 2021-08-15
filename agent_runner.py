import pathlib
import time

import keyboard
import mss
import numpy as np
from cv2 import cv2
from fastai.learner import load_learner

from util.detect_game_scene import find_rough_coords
from util.detect_game_start import is_spikes_visible, fine_tune
from util.get_key import key_check

# fix for fast ai
# https://stackoverflow.com/a/64200241
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath


def label_func(x): return x.parent.name

print("Loading model...")
model = load_learner("test3_15k_0.15.pkl")

sct = mss.mss()
template = cv2.imread("screens/splashscreen1.png")

print("Finding game screen...")
# monitor = {'top': 202, 'left': 6, 'width': 1221, 'height': 688}
monitor = find_rough_coords(sct, template, 0.69)

# fine tune
while 0.5 > is_spikes_visible(np.array(sct.grab(monitor))):
    pass
monitor = fine_tune(np.array(sct.grab(monitor)), monitor)

# wait to press space
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

# the loop
while True:
    # ----
    start = time.time()

    # grab screenshot
    image = np.array(sct.grab(monitor))
    # ----

    # convert to b/w
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # resize to 224x224
    image = cv2.resize(image, (224, 224))
    # run canny detection
    image = cv2.Canny(image, 167, 287)

    # show preview
    cv2.imshow("preview", image)
    cv2.waitKey(1)

    # ask AI what to do
    result, _, confidence = model.predict(image)

    print(result.upper(), "confidence: ", [round(float(i), 2) for i in confidence])

    if result == "left":
        keyboard.press("a")
        keyboard.release("d")
    elif result == "right":
        keyboard.press("d")
        keyboard.release("a")
    elif result == "nothing":
        keyboard.release("a")
        keyboard.release("d")

    # ---
    print("FPS: ", round(1/(time.time() - start), 0), end=" ")
