import numpy as np


class Normalize:
    """Normalize a image with mean and standard deviation"""

    def __init__(self, mean=(127.5, 127.5, 127.5), std=255.0):
        assert len(mean)
        self.mean = np.array(mean, np.float32)
        self.std = np.array(std, np.float32)

    def __call__(self, img):
        return (img - self.mean) / self.std
