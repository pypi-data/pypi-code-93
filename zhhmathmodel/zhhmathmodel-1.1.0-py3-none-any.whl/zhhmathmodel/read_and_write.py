import xlrd
import xlwt


def read_file(file_name: str):
    """
    :param file_name:
    :return: excel file
    """
    return xlrd.open_workbook(file_name)


def read_sheet(file, sheet_index: int):
    """
    :param file:
    :param sheet_index:
    :return: sheet
    """
    return file.sheet_by_index(sheet_index)


def read_col(sheet, col_index: int, start_index: int, end_index: int) -> list:
    """
    :param sheet:
    :param col_index: start from 0 to n
    :param start_index:
    :param end_index:
    :return: the result list
    """
    return sheet.col_values(col_index)[start_index: end_index]


def read_row(sheet, row_index: int, start_index: int, end_index: int) -> list:
    """
    read one row from the target sheet
    :param sheet:
    :param row_index:
    :param start_index:
    :param end_index:
    :return: the result list
    """
    return sheet.row_values(row_index)[start_index: end_index]


def write_excel(file_name: str,
                sheet_name: str,
                data_list: list,
                col_index: int,
                start_index: int
                ):
    """
    write the data into an excel file
    :param file_name: path
    :param sheet_name:
    :param data_list: the target List[]
    :param col_index:
    :param start_index:
    :return:
    """
    work_book = xlwt.Workbook()
    sheet = work_book.add_sheet(sheetname=sheet_name, cell_overwrite_ok=True)
    for i in range(0, len(data_list)):
        sheet.write(i + start_index, col_index, data_list[i])
    work_book.save(file_name)
