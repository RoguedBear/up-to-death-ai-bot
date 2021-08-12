import asyncio
import time
from typing import Tuple

import cv2.cv2 as cv2
import imutils
import mss
import numpy as np


def show_img(img: np.ndarray):
    cv2.imshow("result", img)
    cv2.waitKey()
    cv2.destroyAllWindows()


async def __best_match(image: np.ndarray, template: np.ndarray, tH: int, tW: int, scale: int) -> Tuple[
        float, Tuple[int, int], float, float]:
    resized = imutils.resize(image, width=int(image.shape[1] * scale))
    ratio = image.shape[1] / float(resized.shape[1])

    # image is smaller than template
    if resized.shape[0] < tH or resized.shape[1] < tW:
        return 0, (0, 0), 0, scale

    # apply template matching
    result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
    (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

    return maxVal, maxLoc, ratio, scale


def best_match(image: np.ndarray, template: np.ndarray, min_scale=0.2, max_scale=1) -> \
        Tuple[int, Tuple[int, int], Tuple[int, int]]:
    async def get_max(coros: list):
        return max(await asyncio.gather(*coros), key=lambda x: x[0])
    (tH, tW) = template.shape[:2]
    result = None
    scale = 0

    coroutines = []
    for scale in np.linspace(min_scale, 1, 20)[::-1]:
        coroutines.append(__best_match(image, template, tH, tW, scale))
    now = time.time()
    coro_result = asyncio.run(get_max(coroutines))
    print("Best match took: ", time.time() - now)
    print(coro_result)
    (maxVal, maxLoc, ratio, scale) = coro_result
    print(maxVal, maxLoc, ratio, scale)
    # show_img(result)
    (startX, startY) = (int(maxLoc[0] * ratio), int(maxLoc[1] * ratio))
    (endX, endY) = (int((maxLoc[0] + tW) * ratio), int((maxLoc[1] + tH) * ratio))
    return maxVal, (startX, startY), (endX, endY)


def find_rough_coords(sct: mss.mss, template: np.ndarray, threshold=0.89) -> dict:
    while True:
        # take screenshot of entire screen
        screenshot = np.array(sct.grab({"top": 0, "left": 0, "width": 1920, "height": 1080}))
        found = best_match(screenshot[:, :, :3], template, 0.7)
        if found[0] > threshold:
            print(found)
            cv2.rectangle(screenshot, *found[1:], (0, 255, 255), 2)
            print(" " * 100, end="\r")
            print("Image found!", found)
            # show_img(screenshot)
            print("Rough location found at: ", found[1])
            print("Do NOT move the window anywhere now")
            monitor = {
                "top": found[1][1],
                "left": found[1][0],
                "width": found[2][0] - found[1][0],
                "height": found[2][1] - found[1][1]
            }
            print("rough coords found: ", monitor)
            return monitor

        else:
            print("Game screen not found...", end="\r")


if __name__ == '__main__':
    # TODO: TESTING. USE SOMETHING ELSE FOR PATHS
    game_screen: np.ndarray = cv2.imread("../screens/spikes.png", cv2.IMREAD_UNCHANGED)
    test_image: np.ndarray = cv2.imread("../test/playscreen.png", cv2.IMREAD_UNCHANGED)
    # show_img(test_image)
    # show_img(game_screen)

    coords = best_match(test_image, game_screen)
    cv2.rectangle(test_image, *coords[1:], (0, 255, 255), 2)
    show_img(test_image)
    cv2.destroyAllWindows()
