from time import sleep

import mss
import numpy as np
from cv2 import cv2

from util.detect_game_scene import best_match, show_img, find_rough_coords
from util.detect_game_start import is_spikes_visible, fine_tune

sct = mss.mss()
splash_screen = cv2.imread("screens/splashscreen1.png")

# top: y; left: x
monitor = find_rough_coords(sct, splash_screen, 0.7)

# fine tune the exact screenshot coordinates


while True:
    print("Waiting for game to start....")
    screenshot = sct.grab(monitor)
    screenshot_np = np.array(screenshot)
    confidence = is_spikes_visible(screenshot_np)
    if confidence > 0.5:
        monitor = fine_tune(screenshot_np, monitor)
        break

cv2.imshow("final result", np.array(sct.grab(monitor)))

cv2.waitKey()
cv2.destroyAllWindows()
