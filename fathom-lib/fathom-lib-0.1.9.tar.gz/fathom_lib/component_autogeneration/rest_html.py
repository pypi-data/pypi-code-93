""" Classes and functions for converting reST docstrings to HTML
"""

import cgi
import logging
import platform
import textwrap

from docutils import core
from docutils.frontend import OptionParser
from docutils.parsers.rst import Parser
from docutils.utils import new_document
from docutils.writers.html4css1 import HTMLTranslator, Writer

logger = logging.getLogger(__name__)


class HTMLFragmentTranslator(HTMLTranslator):
    """A subclass of HTMLTranslator which produces only fragments of HTML.
    Used in convert_string_fragment.
    """

    def __init__(self, document):
        HTMLTranslator.__init__(self, document)
        self.head_prefix = ["", "", "", "", ""]
        self.body_prefix = []
        self.body_suffix = []
        self.stylesheet = []
        self.initial_header_level = 5

    def astext(self):
        return "".join(self.body)


def _count_indent(string):
    """In a string, return the length of leading whitespace."""

    if string.lstrip() != string:
        return len(string) - len(string.lstrip())
    return 0


def _fix_indent(string):
    """Attempts to fix abornaml indentation."""

    string_list = string.splitlines()

    start_first = 0
    if len(string_list) > 1:
        # The first line has it's own whitespace adjustment.
        # The 'first' line is actually the first line that is not blank
        while start_first < len(string_list):
            if string_list[start_first] == "":
                start_first += 1
            else:
                break
        # The following lines use a different one.
        # Starts from the first non-blank line
        start_next = start_first + 1
        while start_next < len(string_list):
            if string_list[start_next] == "":
                start_next += 1
            else:
                break
        indentRest = _count_indent(string_list[start_next])
        for i, line in enumerate(string_list[start_next:]):
            string_list[i + start_next] = line[indentRest:]
    indent_first = _count_indent(string_list[start_first])
    string_list[start_first] = string_list[start_first][indent_first:]

    # Join the split string back together and create HTML
    return "\n".join(string_list)


def _html_header():
    """Checks if on windows platform (this means that ie widget should have
    been used), and print an html header that provides a nicer font setting.
    Otherwise, print a standard header.
    """
    if platform.system() is "Windows":
        return """<html>
                  <head>
                  <style type="text/css">
                  body, table
                  {
                      font-family: sans-serif;
                      font-size: 80%;
                      margin: 0px;
                      padding: 0px
                  }
                  .literal-block
                  {
                      margin-top: 0px;
                      margin-bottom: 0px;
                      margin-left: 15px
                  }
                  .desc { margin-top: 0px; margin-bottom: 0px }
                  </style>
                  </head>
                  <body>
                """
    else:
        return "<html>\n<body>\n"


def pre_formatted_html(text):
    """Render the given text inside <pre> tags."""
    lines = text.split("\n")
    # Handle the first line specially.
    firstline = lines[0].strip()
    body = textwrap.dedent("\n".join([line.rstrip() for line in lines[1:]]))
    text = "%s\n%s" % (firstline, body)
    html = (
        "<html>\n<head></head>\n<body>\n<pre>\n%s</pre>\n</body>\n</html>"
        % cgi.escape(text)
    )
    return html


def convert_string_fragment(string):
    """Converts a string of reST text into an html fragment (ie no <header>,
    <body>, etc tags).
    """

    html_fragment_writer = Writer()
    html_fragment_writer.translator_class = HTMLFragmentTranslator
    return core.publish_string(
        _fix_indent(string),
        writer=html_fragment_writer,
        # Suppress output of warnings in html
        settings_overrides={"report_level": 5},
    )
