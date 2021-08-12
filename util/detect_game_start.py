from typing import Tuple, Dict

import numpy as np
from cv2 import cv2

from util.detect_game_scene import best_match, show_img

spikes = cv2.imread("screens/spikes.png")


def is_spikes_visible(img: np.ndarray) -> float:
    """
    Usefule when you wanna know if the game has started or not
    :param img:
    :return:
    """
    found = best_match(img[:, :, :3], spikes)
    # print(found)
    cv2.rectangle(img, *found[1:], (0, 255, 0), 3)
    # cv2.imshow("result", img)
    return found[0]


def fine_tune(img: np.ndarray, monitor: dict) -> Dict:
    """
    fine tunes exactly which coordinate to take screenshots from
    :param img:
    :return:
    """
    x_cord = monitor["left"]
    y_cord = monitor["top"]
    width = monitor["width"]
    height = monitor["height"]

    for i, row in enumerate(img):
        if np.sum(img[i] == 0) > 10:
            print("first row of found.")
            y_cord += i

            # now find all columns that are black
            black_pixels_y = np.array(np.where(img[40] == 0)[0])
            # remove duplicates
            black_pixels_y_unique = np.unique(black_pixels_y)

            # now group contiguous pixels
            black_px_groups = np.split(black_pixels_y_unique, np.where(np.diff(black_pixels_y_unique) != 1)[0] + 1)
            # print(black_px_groups)
            # now get the y_cord and width [ ..------.....------.. ]
            #  like this:                       [0] ^     ^ [1]
            x_cord += black_px_groups[0][-1]
            width = black_px_groups[1][0] - x_cord

            # done.
            print("Coords found: ", (x_cord, y_cord))
            break

    # now iterate from last
    for i in range(len(img) - 1, -1, -1):
        if np.sum(img[i] == 0) > 10:
            print("last row found")
            height = i


            # now break
            break

    monitor = {
        "top": y_cord,
        "left": x_cord,
        "width": int(width),
        "height": int(height)
    }
    print("Fine tuned monitor: ", monitor)
    return monitor

def none(x):
    pass


if __name__ == '__main__':
    from util.detect_game_scene import find_rough_coords
    import mss
    import mss.tools
    import sys
    import imutils
    sct = mss.mss()
    spikes = cv2.imread("../screens/spikes2.png")
    test_image = cv2.imread("../test/playscreen.png")

    monitor = find_rough_coords(sct, cv2.imread("../screens/splashscreen1.png"), 0.7)
    found = False
    count = 0
    cv2.namedWindow('output')
    cv2.createTrackbar("threshold1", "output", 0, 500, none)
    cv2.createTrackbar("threshold2", "output", 0, 500, none)
    while True:
        image = sct.grab(monitor)
        if not found:
            confidence = is_spikes_visible(np.array(image))
        if confidence > 0.5 and not found:
            monitor = fine_tune(np.array(image), monitor.copy())
            found = True
        if not found:
            smal_preview = imutils.resize(np.array(image), width=int(image.size[0] * 0.4))
        else:
            smal_preview = image
        smal_preview = cv2.cvtColor(np.array(smal_preview), cv2.COLOR_BGR2GRAY)
        # threshold1 = cv2.getTrackbarPos("threshold1", "output")
        # threshold2 = cv2.getTrackbarPos("threshold2", "output")
        # smal_preview = cv2.Canny(smal_preview, threshold1, threshold2)
        cv2.imshow("preview", smal_preview)
        cv2.waitKey(1)
        # if found:
        #     mss.tools.to_png(image.rgb, image.size, output=f"ingame{count}.png")
        #     count += 1
    #
    # print("first image")
    # is_spikes_visible(test_image)
    # print("second image")
    # is_spikes_visible(cv2.imread("../test/orig_screen1.png"))
    # print("third image")
    # is_spikes_visible(cv2.imread("../test/orig_screen2.png"))
    # img: np.ndarray = cv2.imread("ss2.png")
    # print(img)
    # for i, row in enumerate(img):
    #     print(f"row {i:3d}: ", np.sum(img[i] == 0))
    #     if i > 50:
    #         break
    # new = fine_tune(img, {
    #             "top": 0,
    #             "left": 0,
    #             "width": 1220,
    #             "height": 688
    #         })
    # cv2.rectangle(img, (new["left"], new["top"]), (new["left"] + new["width"], new["top"] + new["height"]), (0, 255, 0), 2)
    # cv2.imshow("rig", img)
    # cv2.waitKey()
