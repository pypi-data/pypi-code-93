import cv2
import numpy as np

class ColorJitter:
    def __init__(self, probability=0.2, fraction=0.5, change_hue=False, change_saturation=True, change_value=True):
        """ randomly change hue, saturation, value
        :param fractiobaohedu n: ramdom factor
        """
        self.probability = probability
        self.fraction = fraction
        self.change_hue = change_hue
        self.change_saturation = change_saturation
        self.change_value = change_value

    def __call__(self, image):
        if np.random.uniform(0, 1) > self.probability:
            return image

        img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        r = np.random.uniform(-1, 1, 3) * self.fraction + 1

        if self.change_hue:
            H = img_hsv[:, :, 0]
            img_hsv[:, :, 0] = ((H * r[0]) % 180).astype(img_hsv.dtype)

        if self.change_saturation:
            S = img_hsv[:, :, 1]
            S = np.clip(S * r[1], a_min=0, a_max=255)
            img_hsv[:, :, 1] = S.astype(img_hsv.dtype)

        if self.change_value:
            V = img_hsv[:, :, 2]
            V = np.clip(V * r[2], a_min=0, a_max=255)
            img_hsv[:, :, 2] = V.astype(img_hsv.dtype)

        image = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)
        return image
