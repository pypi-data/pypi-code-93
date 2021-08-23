# -*- coding: utf-8 -*-
def get_column_letter(col_idx):
    """Convert a column number into a column letter (3 -> 'C')

    Right shift the column col_idx by 26 to find column letters in reverse
    order.  These numbers are 1-based, and can be converted to ASCII
    ordinals by adding 64.

    """
    # these indicies corrospond to A -> ZZZ and include all allowed
    # columns
    if not 1 <= col_idx <= 18278:
        raise ValueError("Invalid column index {0}".format(col_idx))
    letters = []
    while col_idx > 0:
        col_idx, remainder = divmod(col_idx, 26)
        # check for exact division and borrow if needed
        if remainder == 0:
            remainder = 26
            col_idx -= 1
        letters.append(chr(remainder+64))
    return ''.join(reversed(letters))


def xls_float_correct(num):
    """ 用于处理xlrd在转换数字时,会把int转换为float"""
    s = str(num)
    s_split = s.split('.')
    if len(s_split) == 1:  # s = '1'
        return int(num)
    elif len(s_split) == 2:  # s = '1.0'
        if int(s_split[1]) == 0:
            return int(s_split[0])
        else:
            return float(num)
    else:
        raise ValueError('传入值错误 num={}'.format(num))


class Cell(object):
    ctype_text = {
        0: 'empty',
        1: 'text',
        2: 'number',
        3: 'xldate',
        4: 'bool',
        5: 'error',
        6: 'blank',
    }

    def __init__(self, worksheet, row: int = None, column: int = None, value=None, ctype=None):
        """
        针对xls构建的单元格类

        Args:
            row: 行数
            column: 列数
            value: 单元格内的值
            ctype: 单元格属性
        """
        self.sheet = worksheet
        self.row = row
        self.column = column
        self.data_type = ctype
        self._value = None
        if value is not None:
            self.value = value

    @property
    def coordinate(self):
        """This cell's coordinate (ex. 'A5')"""
        col = get_column_letter(self.column)
        return f"{col}{self.row}"

    def _bind_value(self, value):
        if self.data_type == 0:
            value = None
        elif self.data_type == 1:
            value = str(value)
        elif self.data_type == 2:
            pass
        elif self.data_type == 3:
            value = xls_float_correct(value)
        elif self.data_type == 4:
            value = bool(value)
        elif self.data_type == 5:
            pass

        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._bind_value(value)

    @property
    def col_idx(self):
        """The numerical index of the column"""
        return self.column

    @property
    def column_letter(self):
        return get_column_letter(self.column)

    def __repr__(self):
        return "<Cell {0!r}.{1}>".format(self.sheet.name, self.coordinate)