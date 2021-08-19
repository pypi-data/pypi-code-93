"""
PageInfo Class
"""

from builtins import int

from galenSDK.enumeration.SortOrder import SortOrder


class PageInfo:
    # private int currentPage;
    currentPage = None
    # private int itemsPerPage;
    itemsPerPage = None
    # private String sortBy;
    sortBy = None
    # private SortOrder sortOrder = SortOrder.ASC;
    sortOrder = SortOrder.ASC
    # private int totalItems;
    totalItems = None

    def get_current_page(self) -> int:
        """
        :return: currentPage
        """
        return self.currentPage

    def set_current_page(self, currentPage: int):
        """
        :param currentPage: the currentPage to set
        :return:
        """
        self.currentPage = currentPage

    def get_items_per_page(self) -> int:
        """
        :return: itemsPerPage
        """
        return self.itemsPerPage

    def set_items_per_page(self, itemsPerPage: int):
        """
        :param itemsPerPage: the itemsPerPage to set
        """
        self.itemsPerPage = itemsPerPage

    def get_sort_by(self) -> str:
        """
        :return: sortBy
        """
        return self.sortBy

    def set_sort_by(self, sortBy: str):
        """
        :param sortBy: the sortBy to set
        """
        self.sortBy = sortBy

    def get_sort_order(self) -> SortOrder:
        """
        :return: sortOrder
        """
        return self.sortOrder

    def set_sort_order(self, sortOrder: SortOrder):
        """
        :param sortOrder: the sortOrder to set
        """
        self.sortOrder = sortOrder

    def get_total_items(self) -> int:
        """
        :return: totalItems
        """
        return self.totalItems

    def set_total_items(self, totalItems: int):
        """
        :param totalItems: the totalItems to set
        """
        self.totalItems = totalItems
