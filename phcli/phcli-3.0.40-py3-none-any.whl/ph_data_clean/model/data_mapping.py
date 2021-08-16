# -*- coding: utf-8 -*-


class ColCharactor(object):
    """
    对于每个单元格的匹配规则
    """

    def __init__(self, col_name: str, col_desc: str, candidate: list = [], type: str = 'String',
                 not_null: bool = False):
        self.col_name = col_name
        self.col_desc = col_desc
        self.candidate = candidate
        self.type = type
        self.not_null = not_null

    def to_dict(self) -> dict:
        return self.__dict__


class DataMapping(object):
    """
    对于指定源的指定公司的匹配规则
    """

    def __init__(self, source: str, company: str, cols: list):
        self.source = source
        self.company = company
        self.cols = cols

    def to_dict(self) -> dict:
        self.__dict__['cols'] = [col.to_dict() for col in self.cols]
        return self.__dict__

    def get_metadata(self) -> list:
        return [{'key': col.col_name, 'type': col.type} for col in self.cols]


