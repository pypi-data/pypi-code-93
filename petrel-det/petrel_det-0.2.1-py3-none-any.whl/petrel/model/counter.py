class AvgCounter:
    """
    Stores totals and counts.
    """

    def __init__(self):
        self._sum = 0
        self._count = 0

    def reset(self):
        self._sum = 0
        self._count = 0

    @property
    def avg(self):
        """
        Returns the current average.
        :return: The current average.
        """
        return self._sum/self._count

    def concat(self, other_counter):
        """
        Add values from anther counter.
        :param other_counter: Second counter whose totals are added to the current counter.
        """
        self._sum += other_counter.sum()
        self._count += other_counter.count()

    @property
    def count(self):
        """
        Returns the current count
        :return: The current count.
        """
        return self._count

    @property
    def sum(self):
        """
        Returns the current total.
        :return: The current total.
        """
        return self._sum

    def update(self, val, count):
        """
        Updates totals and counts. Assumes val is the sum of count elements
        :param val: New value to add to the total
        :param count: Count of new elements being added.
        """
        self._sum += val
        self._count += count

    def update_avg(self, avg, count):
        """
        Updates totals and counts. Assumes avg is the average of the values of count elements
        :param avg: Average of new values being added.
        :param count: Count of new elements being added.
        """
        self._sum += avg * count
        self._count += count


