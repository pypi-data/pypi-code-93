# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

from docutils.core import publish_string


def convert_rst_to_html(rst_string):
    """
    Convert a string given in ReStructuredText format to HTML.
     
    Parameters
    ----------
    rst_string : unicode
    
    Returns
    -------
    html : unicode
    """
    rst_string = unindent_rst(rst_string)
    rst_string = clear_rst_from_targets(rst_string)
    return publish_string(
        rst_string,
        writer_name='html',
        settings_overrides={
            'input_encoding': 'unicode',
            'output_encoding': 'unicode'
        }
    )


def clear_rst_from_targets(rst_string):
    """
    Replace targets of the form :<role>:`<target-name>` with the <target-name> itself.
    
    Parameters
    ----------
    rst_string : unicode
    
    Returns
    -------
    cleared_rst : unicode
    """
    return re.sub(r':[a-z]+:`~?([.a-zA-Z0-9]+)`', r'\1', rst_string)


def unindent_rst(rst_string, unindent=4):
    """
    Strip all whitespace from the left of all lines in the given RST string. This is important
    because the docutils RST converter won't recognize headings if they have leading indention.
    
    Parameters
    ----------
    rst_string : unicode
    unindent : int, optional
        The number of whitespaces to be removed in order to unindent the string.
    
    Returns
    -------
    rst_string : unicode
        All lines without leading indention (whitespace).
    """
    return '\n'.join(map(
        lambda x: re.sub(r'^([ ])\1{%d}' % (unindent-1), r'', x),
        rst_string.split('\n')
    ))
