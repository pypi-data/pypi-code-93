import numpy as np
import cv2

class Mirror:
    """
    Initialization parameters: probability

    For example: probability = 0.5, that means the mirror operation is implemented with a probability of 0.5
    """

    def __init__(self, probability=0.2):
        self.probability = probability

    def __call__(self, image, boxes=None):
        """
        :param image:
        :param boxes: x1, y1, x2, y2
        :return:
        """
        _, width, _ = image.shape
        if np.random.uniform(0, 1) < self.probability:
            image = cv2.flip(image, 1)
            # image = image[:, ::-1]
            if boxes is not None:
                assert isinstance(boxes, np.ndarray)
                boxes[:, [0, 2]] = width - boxes[:, [2, 0]]

        if boxes is None:
            return image
        else:
            return image, boxes
