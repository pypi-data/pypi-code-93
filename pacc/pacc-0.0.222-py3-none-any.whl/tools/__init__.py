from .regular import findAllWithRe, findAllNumsWithRe
from .sleep import sleep
from .email import EMail
from .dir import createDir
from .xml import prettyXML, getXML
from .math import average
from .url import getURLsFromString

__all__ = [
    "findAllWithRe",
    'findAllNumsWithRe',
    "sleep",
    'EMail',
    'createDir',
    'prettyXML',
    'getXML',
    'average',
    'getURLsFromString'
]
