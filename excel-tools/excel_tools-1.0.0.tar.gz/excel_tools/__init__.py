# -*- coding: utf-8 -*-
from ._xls import XlsReader
from ._xlsx import XlsxReader

import os
from typing import Optional, Union


def read_xl(name: str, path: Optional[str] = '', ignore_lines: Optional[int] = 0,
            sheet: Union[int, str, None] = 0) -> Union[XlsReader, XlsxReader]:
    """
    根据文件名,返回相应的读取类

    Returns:
        xlReader类
    """
    if os.path.splitext(name)[1] == '.xls':
        return XlsReader(name=name, path=path, ignore_lines=ignore_lines, sheet=sheet)
    elif os.path.splitext(name)[1] == '.xlsx':
        return XlsxReader(name=name, path=path, ignore_lines=ignore_lines, sheet=sheet)
    else:
        raise ValueError(f"无法读取'{name}', 路径='{path}'")
