import cv2

from weedcv.weedcv import params


def show_images(visual, filename):
    window = "results"
    visual = cv2.resize(visual, (600, 400))
    cv2.imshow(window, visual)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
