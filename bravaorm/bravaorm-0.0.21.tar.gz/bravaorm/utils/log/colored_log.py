#!/usr/bin/env python

from copy import copy
from logging import Formatter

MAPPING = {
    'DEBUG'   : 35, # roxo
    'INFO'    : 36, # ciano
    'WARNING' : 33, # amarelo
    'ERROR'   : 31, # vermelho
    'CRITICAL': 41, # branco fundo vermelho
}

PREFIX = '\033['
SUFFIX = '\033[0m'

class ColoredFormatter(Formatter):

    def __init__(self, patern):
        Formatter.__init__(self, patern, '%Y-%m-%d %H:%M:%S')

    def format(self, record):
        colored_record = copy(record)
        levelname = colored_record.levelname
        seq = MAPPING.get(levelname, 37) # default white
        colored_levelname = ('{0}{1}m{2}{3}') \
            .format(PREFIX, seq, levelname, SUFFIX)
        colored_record.levelname = colored_levelname
        return Formatter.format(self, colored_record)
