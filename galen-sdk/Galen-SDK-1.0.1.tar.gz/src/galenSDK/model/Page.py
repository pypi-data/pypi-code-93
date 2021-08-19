"""
Page Class
"""

from galenSDK.model.Pageable import Pageable
from galenSDK.model.Sort import Sort


class Page:
    # boolean first;
    first = None
    # boolean last;
    last = None
    # int totalElements;
    totalElements = None
    # int totalPages;
    totalPages = None
    # int size;
    size = None
    # int number;
    number = None
    # int numberOfElements;
    numberOfElements = None
    # Sort sort;
    sort = None
    # Pageable pageable;
    pageable = None
    # List<T> content;
    content = []

    def __init__(self, first: bool = None, last: bool = None, totalElements: int = None, totalPages: int = None,
                 size: int = None, number: int = None, numberOfElements: int = None, sort: Sort = None,
                 pageable: Pageable = None, content=[]):
        """
        Initializer for the Page Class
        :param first: first to set. Optional.
        :param last: last to set. Optional.
        :param totalElements: totalElements to set. Optional.
        :param totalPages: totalPages to set. Optional.
        :param size: size to set. Optional.
        :param number: number to set. Optional.
        :param numberOfElements: numberOfElements to set. Optional.
        :param sort: sort to set. Optional.
        :param pageable: pageable to set. Optional.
        :param content: content to set. Optional.
        """
        self.first = first
        self.last = last
        self.totalElements = totalElements
        self.totalPages = totalPages
        self.size = size
        self.number = number
        self.numberOfElements = numberOfElements
        self.sort = sort
        self.pageable = pageable
        self.content = content

    @staticmethod
    def from_json(json_dict):
        """
        takes in a dictionary and returns a Page object [Helper function for SDK]
        :return: Page
        """
        json_dict_holder = {}

        if "first" in json_dict:
            json_dict_holder["first"] = json_dict["first"]
        if "last" in json_dict:
            json_dict_holder["last"] = json_dict["last"]
        if "totalElements" in json_dict:
            json_dict_holder["totalElements"] = json_dict["totalElements"]
        if "totalPages" in json_dict:
            json_dict_holder["totalPages"] = json_dict["totalPages"]
        if "size" in json_dict:
            json_dict_holder["size"] = json_dict["size"]
        if "number" in json_dict:
            json_dict_holder["number"] = json_dict["number"]
        if "numberOfElements" in json_dict:
            json_dict_holder["numberOfElements"] = json_dict["numberOfElements"]
        if "sort" in json_dict:
            json_dict_holder["sort"] = json_dict["sort"]
        if "pageable" in json_dict:
            json_dict_holder["pageable"] = json_dict["pageable"]
        if "content" in json_dict:
            json_dict_holder["content"] = json_dict["content"]
        return Page(**json_dict_holder)

    def is_first(self) -> bool:
        """
        :return: is_first [boolean]
        """
        return self.first

    def set_first(self, first: bool):
        """
        :param first: the first to set [boolean]
        """
        self.first = first

    def is_last(self) -> bool:
        """
        :return: last
        """
        return self.last

    def set_last(self, last: bool):
        """
        :param last: the last to set
        """
        self.last = last

    def get_total_elements(self) -> int:
        """
        :return: totalElements
        """
        return self.totalElements

    def set_total_elements(self, totalElements: int):
        """
        :param totalElements: the totalElements to set
        """
        self.totalElements = totalElements

    def get_total_pages(self) -> int:
        """
        :return: totalPages
        """
        return self.totalPages

    def set_total_pages(self, totalPages: int):
        """
        :param totalPages: the totalPages to set
        """
        self.totalPages = totalPages

    def get_size(self) -> int:
        """
        :return: size
        """
        return self.size

    def set_size(self, size: int):
        """
        :param size: the size to set
        """
        self.size = size

    def get_number(self) -> int:
        """
        :return: number
        """
        return self.number

    def set_number(self, number: int):
        """
        :param number: the number to set
        """
        self.number = number

    def get_number_of_elements(self) -> int:
        """
        :return: numberOfElements
        """
        return self.numberOfElements

    def set_number_of_elements(self, numberOfElements: int):
        """
        :param numberOfElements: the numberOfElements to set
        """
        self.numberOfElements = numberOfElements

    def get_sort(self) -> Sort:
        """
        :return: sort
        """
        return self.sort

    def set_sort(self, sort: Sort):
        """
        :param sort: the sort to set
        """
        self.sort = sort

    def get_pageable(self) -> Pageable:
        """
        :return: pageable
        """
        return self.pageable

    def set_pageable(self, pageable: Pageable):
        """
        :param pageable: the pageable to set
        """
        self.pageable = pageable

    def get_content(self):  # returns a list
        """
        :return: content
        """
        return self.content

    def set_content(self, content):  # content is a list
        """
        :param content: the content to set
        """
        self.content = content
