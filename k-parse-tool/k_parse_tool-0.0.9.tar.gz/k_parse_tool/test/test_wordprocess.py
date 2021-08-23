
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch

from k_parse_tool.lib.word_file_process import PyDocXFileProcess, PyDocFileProcess


class PdfProcessTestCase(unittest.TestCase):

    def test_extract_table_metadata(self):
        self.env = patch.dict('os.environ', {'SCRAPY_PROJECT': 'development'})
        path = f'C:\\Users\\kland\\Downloads\\4665921.doc'
        res = PyDocFileProcess.convert_file_to_html(path)
        print(res)
        files_process_api = u'http://192.168.1.115:8000/convertToHtml'
        html_source = PyDocFileProcess.get_word_content_by_api(path, files_process_api)
        print(html_source)

if __name__ == '__main__':
    unittest.main()