from .BaseTable import *
from UniversalParser._tools import *
from UniversalParser._parse import parse_string
from zipfile import ZIP_MAX_COMMENT, ZipFile
from UniversalParser._exception import *

class WordTable(BaseTable):

    def __init__(self
            , zip_file_path: str
            , read_file_path: str = 'word/document.xml'
            , encoding: str = 'utf-8'
            , mode: str = 'a' # do not use `w` mode, remember!
            , analysis_text = False
        ) -> None:

        self.modify_file_path = read_file_path
        self.encoding = encoding

        try:
            self.zip_obj = ZipFile(zip_file_path, mode=mode)
        except Exception as e:
            raise ZipParseError(f'zip-file can not be parsed.{e}')

        self.ori_xml = read_content_from_zipobj(self.zip_obj, read_file_path, encoding)
        self.manager = parse_string(
            self.ori_xml
            , analysis_text = analysis_text
        )

        super().__init__(self.manager, 'word')

    def save(self, new_word_path: str='output.docx'):
        new_xml_data = self.manager.get_xml_data()
        save_docs_with_modify_by_move(self.zip_obj, {self.modify_file_path: new_xml_data}, new_word_path)
    
    def save_from_modify(self, new_word_path: str='output.docx', patt=None, **kwargs):
        new_content = patt_template_replace(self.ori_xml, patt=patt, **kwargs)
        save_docs_with_modify_by_move(self.zip_obj, {self.modify_file_path: new_content}, new_word_path)

    def __del__(self):
        try:
            self.zip_obj.close()
        except:
            pass

def parse_table(
        zip_file_path: str
        , read_file_path: str = 'word/document.xml'
        , encoding: str = 'utf-8'
    ) -> WordTable:
    return WordTable(
        zip_file_path = zip_file_path
        , read_file_path = read_file_path
        , encoding = encoding
    )
