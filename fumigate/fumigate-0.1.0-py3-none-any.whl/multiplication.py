import numpy as np


class Multiplication:
    """
    Instantiate a multiplication operation.
    Numbers will be multiplied by the given multiplier.

    :param multiplier: The multiplier.
    :type multiplier: float
    """

    def __init__(self, multiplier):
        self.multiplier = multiplier

    def multiply(self, number):
        """
        Multiply a given number by the multiplier.

        :param number: The number to multiply.
        :type number: float

        :return: The result of the multiplication.
        :rtype: float
        """

        return np.dot(number, self.multiplier)
