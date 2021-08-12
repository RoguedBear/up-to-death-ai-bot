# load test image
from cv2 import cv2


def none(x):
    pass


img = cv2.imread("ingame_manual2.png")
cv2.namedWindow('output')

# create trackbar
cv2.createTrackbar("0: White \n1: Black", "output", 0, cv2.COLOR_BGR2GRAY, none)
cv2.createTrackbar("threshold1", "output", 0, 500, none)
cv2.createTrackbar("threshold2", "output", 0, 500, none)

img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

while True:

    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

    # get current position
    grayscale = cv2.getTrackbarPos("0: White \n1: Black", "output")
    threshold1 = cv2.getTrackbarPos("threshold1", "output")
    threshold2 = cv2.getTrackbarPos("threshold2", "output")

    edges = cv2.Canny(img, threshold1=threshold1, threshold2=threshold2)

    cv2.imshow("image", edges)
