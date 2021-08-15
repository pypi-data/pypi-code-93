"""
    pygments.lexers.amdgpu
    ~~~~~~~~~~~~~~~~~~~~~~

    Lexers for the AMDGPU ISA assembly.

    :copyright: Copyright 2006-2021 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import RegexLexer
from pygments.lexer import words
from pygments.token import Comment
from pygments.token import Keyword
from pygments.token import Name
from pygments.token import Number
from pygments.token import Text
from pygments.token import Whitespace

__all__ = ['AMDGPULexer']


class AMDGPULexer(RegexLexer):
    """
    For AMD GPU assembly.

    .. versionadded:: 2.8
    """
    name = 'AMDGPU'
    aliases = ['amdgpu']
    filenames = ['*.isa']

    flags = re.IGNORECASE

    tokens = {
        'root': [
            (r'\s+', Whitespace),
            (r'[\r\n]+', Text),
            (r'(([a-z_0-9])*:([a-z_0-9])*)', Name.Attribute),
            (r'(\[|\]|\(|\)|,|\:|\&)', Text),
            (r'([;#]|//).*?\n', Comment.Single),
            (r'((s_)?(ds|buffer|flat|image)_[a-z0-9_]+)', Keyword.Reserved),
            (r'(_lo|_hi)', Name.Variable),
            (r'(vmcnt|lgkmcnt|expcnt)', Name.Attribute),
            (words((
                'op', 'vaddr', 'vdata', 'soffset', 'srsrc', 'format',
                'offset', 'offen', 'idxen', 'glc', 'dlc', 'slc', 'tfe', 'lds',
                'lit', 'unorm'), suffix=r'\b'), Name.Attribute),
            (r'(label_[a-z0-9]+)', Keyword),
            (r'(_L[0-9]*)', Name.Variable),
            (r'(s|v)_[a-z0-9_]+', Keyword),
            (r'(v[0-9.]+|vcc|exec|v)', Name.Variable),
            (r's[0-9.]+|s', Name.Variable),
            (r'[0-9]+\.[^0-9]+', Number.Float),
            (r'(0[xX][a-z0-9]+)|([0-9]+)', Number.Integer)
        ]
    }
