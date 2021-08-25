import numpy as np
import plotly.figure_factory as ff


class Distribution:
    def __init__(self, dist_func):
        self.dist_func = dist_func

    def generate(self):
        """
        Generate random number by some distribution
        :return: float
        """
        return self.dist_func()

    @classmethod
    def from_dist_func(cls, dist_func):
        sample = dist_func()
        assert isinstance(sample, float)

        return cls(dist_func)

    def hist(self):
        """
        plot the distribution histogram
        :return: None
        """
        data = [[float(self.generate()) for _ in range(2500)]]
        fig = ff.create_distplot(data, ['sample'])
        fig.update_layout(
            title='Sample Distribution',
            xaxis_title='Sample Data'
        )
        fig.show()
        return

    @staticmethod
    def array_to_dist(arr):
        """
        convert numpy array/list to distribution function
        :param arr: numpy array
        :return: distribution function
        """
        arr = np.array(arr, dtype=np.float)

        def dist_func():
            return np.random.choice(arr, 1, replace=False)[0]

        return dist_func

    @classmethod
    def from_array(cls, arr):
        dist_func = cls.array_to_dist(arr)
        return cls.from_dist_func(dist_func)
