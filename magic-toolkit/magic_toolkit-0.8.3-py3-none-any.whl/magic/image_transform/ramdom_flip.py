import numpy as np
import cv2

class RandomFlip:
    """
    Initialization parameters: probability

    For example: probability = 0.5, that means the flip operation is implemented with a probability of 0.5
    """

    def __init__(self, probability=0.2, horizontal=False, vertical=False):
        self.probability = probability
        self.horizontal = horizontal
        self.vertical = vertical

    def __call__(self, image, boxes=None):
        """
        :param image:
        :param boxes: x1, y1, x2, y2
        :return:
        """
        height, width, _ = image.shape
        if self.horizontal and np.random.uniform(0, 1) < self.probability:
            # image = image[:, ::-1]
            image = cv2.flip(image, 1)
            if boxes is not None:
                assert isinstance(boxes, np.ndarray)
                boxes[:, [0, 2]] = width - boxes[:, [2, 0]]

        if self.vertical and np.random.uniform(0, 1) < self.probability:
            # image = image[::-1]
            image = cv2.flip(image, 0)
            if boxes is not None:
                assert isinstance(boxes, np.ndarray)
                boxes[:, [1, 3]] = height - boxes[:, [3, 1]]

        if boxes is None:
            return image
        else:
            return image, boxes
