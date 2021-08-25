from .distribution import Distribution


class Action:
    def __init__(self, distribution):
        """
        A single arm for the multi-bandit system
        :param distribution: the distribution function of the arm.
        Should return a random number according to the distribution
        """
        # make sure the type
        assert isinstance(distribution, Distribution)

        self.distribution = distribution
        self.number = 0

    @classmethod
    def from_distribution_func(cls, dist_func):
        dist = Distribution.from_dist_func(dist_func)
        return cls(dist)

    @classmethod
    def from_array(cls, arr):
        distribution = Distribution.from_array(arr)
        return cls(distribution)

    def generate(self):
        return self.distribution.generate()

    def get_num(self):
        return self.number

    def set_num(self, number):
        self.number = number

    def hist(self):
        self.distribution.hist()
