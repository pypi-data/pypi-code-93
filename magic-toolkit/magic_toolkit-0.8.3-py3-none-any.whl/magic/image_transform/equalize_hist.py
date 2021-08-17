import cv2
import numpy as np

class EqualizeHist:
    def __init__(self, probability=0.2):
        self.probability = probability

    def rgb_equalize(self, img):
        # equalize histogram in rgb colorspace
        img_b = img[..., 0]
        img_g = img[..., 1]
        img_r = img[..., 2]

        img_b = cv2.equalizeHist(img_b)
        img_g = cv2.equalizeHist(img_g)
        img_r = cv2.equalizeHist(img_r)
        out = cv2.merge([img_b, img_g, img_r])
        return out

    def hsv_equalize(self, img):
        # convert to hsv to equalize histogram
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img_h = img_hsv[..., 0]
        img_s = img_hsv[..., 1]
        img_v = img_hsv[..., 2]

        rand = np.random.uniform(0, 1)

        if rand < 0.33:
            img_s = cv2.equalizeHist(img_s)
        elif rand < 0.66:
            img_v = cv2.equalizeHist(img_v)
        else:
            img_s = cv2.equalizeHist(img_s)
            img_v = cv2.equalizeHist(img_v)
        out = cv2.merge([img_h, img_s, img_v])
        out = cv2.cvtColor(out, cv2.COLOR_HSV2BGR)
        return out

    def __call__(self, img):
        if np.random.uniform(0, 1) > self.probability:
            return img

        if np.random.uniform(0, 1) < 0.5:
            return self.rgb_equalize(img)
        else:
            return self.hsv_equalize(img)


if __name__ == '__main__':

    img = cv2.imread("/home/liam/deepblue/liamsir/research_py/broom_classifier/data/positive/image/1609858379_77.jpg")
    equlizeHist = EqualizeHist(0.5)
    while True:
        img_e = img.copy()
        out = equlizeHist(img_e)
        cv2.imshow("img", img)
        cv2.imshow("out", out)
        cv2.waitKey(0)
