# get contours (presumably just one around the nonzero pixels)
import cv2


def crop_contours(mask):
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 2:
        contours = contours[0]
    else:
        contours[1]

    cntr = contours[0]
    x, y, w, h = cv2.boundingRect(cntr)
    return x, y, w, h
