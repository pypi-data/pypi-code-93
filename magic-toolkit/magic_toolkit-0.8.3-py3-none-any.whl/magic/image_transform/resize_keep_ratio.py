import numpy as np
import cv2

class ResizeKeepRatio:
    """resize a rectangular image to a padded square"""
    def __init__(self, height, color=(0, 0, 0)):
        self.height = height
        self.color = color

    def __call__(self, img, boxes=None):
        """
        :param img:
        :param boxes: x1, y1, x2, y2
        :return:
        """

        shape = img.shape[:2]  # shape = [height, width]
        ratio = float(self.height) / max(shape)  # ratio  = old / new
        new_shape = [round(shape[0] * ratio), round(shape[1] * ratio)]
        dw = self.height - new_shape[1]  # width padding
        dh = self.height - new_shape[0]  # height padding
        top, bottom = dh // 2, dh - (dh // 2)
        left, right = dw // 2, dw - (dw // 2)
        img = cv2.resize(img, (new_shape[1], new_shape[0]), interpolation=cv2.INTER_AREA)  # resized, no border
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=self.color)

        if boxes is not None:
            assert isinstance(boxes, np.ndarray)
            boxes[:, 0] = boxes[:, 0] * ratio + left
            boxes[:, 1] = boxes[:, 1] * ratio + top
            boxes[:, 2] = boxes[:, 2] * ratio + left
            boxes[:, 3] = boxes[:, 3] * ratio + top

            return img, boxes
        else:
            return img

class ResizeKeepRatioV2:
    """resize a rectangular image to a padded square"""
    def __init__(self, width, height, color=(0, 0, 0)):
        self.width = width
        self.height = height
        self.color = color

    def __call__(self, img):
        oh, ow = img.shape[:2]  # shape = [height, width]
        ratio = min(self.height / float(oh), self.width / float(ow))
        new_shape = [round(oh * ratio), round(ow * ratio)]
        dw = self.width - new_shape[1]  # width padding
        dh = self.height - new_shape[0]  # height padding
        top = dh // 2
        bottom = dh - top
        left = dw // 2
        right = dw - left
        img = cv2.resize(img, (new_shape[1], new_shape[0]), interpolation=cv2.INTER_AREA)  # resized, no border
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=self.color)
        return img, (ratio, top, left)
