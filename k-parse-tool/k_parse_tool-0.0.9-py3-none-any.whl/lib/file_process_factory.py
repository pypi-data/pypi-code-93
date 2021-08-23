from k_parse_tool.lib.word_file_process import WordFileProcessAbstractFactory

from k_parse_tool.lib.pdf_file_process import PdfFileProcessAbstractFactory


class FileProcessFactory:
    @staticmethod
    def get_file_content(file_path, files_process_api, file_lib_type=None):
        if file_path is None or len(file_path.strip()) == 0: return ''
        lower_file_path = file_path.lower()
        if lower_file_path.endswith('.pdf') or lower_file_path.endswith('.pdfx'):
            pdf_extract = PdfFileProcessAbstractFactory.get_pdf_file_process_object(
                PdfFileProcessAbstractFactory.pdf_lib_type.pdfplumber)
            result = pdf_extract.process_file_content(file_path, files_process_api)
            result = PdfFileProcessAbstractFactory.pdf_file_content_format(result)
            return result
        elif lower_file_path.endswith('.doc') or lower_file_path.endswith('.docx'):
            word_extract = WordFileProcessAbstractFactory.get_word_file_process_object(file_path.split('.')[-1])
            result = word_extract.process_file_content(file_path, files_process_api)
            return result
        elif lower_file_path.endswith('.xls') or lower_file_path.endswith('.xlsx'):
            pass
        else:
            return ''

    @staticmethod
    def convent_file_to_html(file_path):
        raise NotImplementedError("Must implement process_file_content")
