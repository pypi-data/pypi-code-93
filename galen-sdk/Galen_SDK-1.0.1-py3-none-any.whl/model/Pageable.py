"""
Pageable Class
"""

from galenSDK.model.Sort import Sort


class Pageable:
    # private boolean paged;
    paged = None
    # private boolean unpaged;
    unpaged = None
    # private int offset;
    offset = None
    # private int pageSize;
    pageSize = None
    # private int pageNumber;
    pageNumber = None
    # public Sort sort;
    sort = None

    def __init__(self, paged: bool = None, unpaged: bool = None, offset=None, pageSize=None, pageNumber=None,
                 sort: Sort = None):
        """
        Initializer for the Pageable Class
        :param paged: paged to set. Optional.
        :param unpaged: unpaged to set. Optional.
        :param offset: offset to set. Optional.
        :param pageSize: pageSize to set. Optional.
        :param pageNumber: pageNumber to set. Optional.
        :param sort: sort to set. Optional.

        """
        self.paged = paged
        self.unpaged = unpaged
        self.offset = offset
        self.pageSize = pageSize
        self.pageNumber = pageNumber
        self.sort = sort

    def is_paged(self) -> bool:
        """
        :return: paged [boolean]
        """
        return self.paged

    def set_paged(self, paged: bool):
        """
        :param paged: the paged to set
        """
        self.paged = paged

    def is_unpaged(self) -> bool:
        """
        :return: unpaged
        """
        return self.unpaged

    def set_unpaged(self, unpaged: bool):
        """
        :param unpaged: the unpaged to set
        """
        self.unpaged = unpaged

    def get_offset(self) -> int:
        """
        :return: offset
        """
        return self.offset

    def set_offset(self, offset: int):
        """
        :param offset: the offset to set
        """
        self.offset = offset

    def get_page_size(self) -> int:
        """
        :return: pageSize
        """
        return self.pageSize

    def set_page_size(self, pageSize: int):
        """
        :param pageSize: the pageSize to set
        """
        self.pageSize = pageSize

    def get_page_number(self) -> int:
        """
        :return: pageNumber
        """
        return self.pageNumber

    def set_page_number(self, pageNumber: int):
        """
        :param pageNumber: the pageNumber to set
        """
        self.pageNumber = pageNumber

    def get_sort(self) -> Sort:
        """
        :return: sort
        """
        return self.sort

    def set_sort(self, sort: Sort):
        """
        :param sort:  the sort to set
        """
        self.sort = sort
