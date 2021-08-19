"""
Sort Class
"""


class Sort:
    # private boolean sorted;
    sorted = None
    # private boolean unsorted;
    unsorted = None

    def __init__(self, sorted: bool = None, unsorted: bool = None):
        """
        Initializer for the Sort Class
        :param sorted: sorted to set. Optional.
        :param unsorted: unsorted to set. Optional.
        """
        self.sorted = sorted
        self.unsorted = unsorted

    def is_sorted(self) -> bool:
        """
        :return: sorted
        """
        return self.sorted

    def set_sorted(self, sorted: bool):
        """
        :param sorted: the sorted to set
        """
        self.sorted = sorted

    def is_unsorted(self) -> bool:
        """
        :return: unsorted [boolean]
        """
        return self.unsorted

    def set_unsorted(self, unsorted: bool):
        """
        :param unsorted: the unsorted to set
        """
        self.unsorted = unsorted
