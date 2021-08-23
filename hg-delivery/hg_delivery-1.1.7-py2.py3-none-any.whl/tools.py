
# ------------------------------------------------------------------------------
import os
import re

from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles

styles = list(get_all_styles())


class DiffWrapper(object):
    """
    """
    def __init__(self, raw_diff):
        """
        """
        self.raw_diff = raw_diff

        self.lst_files = []
        self.dict_files = []
        self.lst_basename_files = []

        if self.raw_diff:
            # we init content ...
            self.lst_files = self.__get_lst_files()
            self.lst_basename_files = [
                os.path.basename(f_name) for f_name in self.lst_files
            ]
            self.dict_files = self.__get_files_to_diff()

    def __get_lst_files(self):
        """
        """
        # add some non capturing group for revision argument ...
        # (just for remind !)
        groups = re.findall(u"diff(?: -r [a-z0-9]+){1,2} (?P<file_name>.+)$",
                            self.raw_diff, re.MULTILINE)
        return groups

    def __get_files_to_diff(self):
        """
        """
        groups = self.__get_lst_files()
        diffs_content = [
            highlight(bloc, DiffLexer(),
                      HtmlFormatter(cssclass=u'source', style=u'colorful'))
            for bloc in re.split(u"\n*diff -r [a-z0-9]{8,20} [^\n]+\n",
                                 self.raw_diff) if bloc.strip()
        ]
        return dict(zip(groups, diffs_content))

    def __json__(self, request):
        """
        """
        return {
            u'id': self.raw_diff,
            u'lst_files': self.lst_files,
            u'lst_basename_files': self.lst_basename_files,
            u'dict_files': self.dict_files
        }
