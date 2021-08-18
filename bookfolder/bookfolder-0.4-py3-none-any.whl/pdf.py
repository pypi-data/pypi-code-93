"""
Module for writing the pattern into a PDF file.
"""

import math

from fpdf import FPDF


class PDFWriter():
    """
    A tool that writes bookfolding Sheet data into a file.
    """

    font = "Times"
    font_size = 10

    line_height = font_size * 1.0
    n_columns = 14

    header_height = 0
    footer_height = 0
    rows_per_page = 26

    def __init__(self, sheets):
        """
        Create a `PDFWriter`.

        :sheets: a list of Sheet objects depicting pages in the bookfolding
                 pattern.
        """
        self.sheets = sheets
        self.pdf = FPDF()
        self.pdf.set_font(self.font, size=self.font_size)
        self.column_width = self.pdf.epw / self.n_columns

    def create_document(self, table_header):
        """
        Write all `Sheet`s into a bookfolding pattern document.

        The resulting document can have multiple pages if the pattern is long.
        """
        for pageful_of_sheets in self._sheet_pages():
            self._add_table_page(table_header)
            for sheet in pageful_of_sheets:
                self._add_rows_for_sheet(sheet)

    def save(self, output_path):
        """
        Write the constructed PDF into a file.

        :output_path: the file in which the PDF file is saved.
        """
        self.pdf.output(output_path)

    def _sheet_pages(self):
        """
        Iterate over lists of sheets, each with one pageful of folds.

        :yields: lists of sheets from self.sheets, one pageful at a time
        """
        start_index = 0
        while True:

            sheets = []
            rows_required = 0

            for sheet in self.sheets[start_index:]:
                new_rows_required = math.ceil(
                    len(sheet.folds) / (self.n_columns - 1))
                if rows_required + new_rows_required > self.rows_per_page - 1:
                    break
                sheets.append(sheet)
                rows_required += new_rows_required

            start_index += len(sheets)

            if not sheets:
                return
            yield sheets

    def _add_table_page(self, table_header):
        """
        Add a new page to the document and add a table header to that page.

        :table_header: List of header fields.
        """
        self.pdf.add_page()
        self._add_header(table_header)
        self._add_new_row()

    def _add_header(self, table_header):
        """
        Write a header to the current page
        """
        if len(table_header) < self.n_columns:

            for i in range(len(table_header) - 1):
                self._add_cell(table_header[i], border=1)

            last_column_width = (
                    (self.n_columns - len(table_header) + 1)
                    * self.column_width
                    )
            self._add_cell(table_header[-1], width=last_column_width)

        elif len(table_header) == self.n_columns:
            for cell in table_header:
                self._add_cell(cell, border=1)

        else:
            raise ValueError("Header {} has too many fields: the page only "
                             "fits {} fields"
                             "".format(table_header, self.n_columns))

    def _add_rows_for_sheet(self, sheet):
        """
        Add one or more data rows representing a single `Sheet`.
        """
        rows_required = self._rows_required(sheet)

        for current_row_index, fold_indices \
                in enumerate(self._iterate_fold_rows(sheet)):
            self._add_page_number_cell(sheet,
                                       current_row_index,
                                       rows_required)
            fold_points_for_row = [
                sheet.fold_locations_in_cm()[i] for i in fold_indices
                ]

            for fold_point in fold_points_for_row:
                self._add_cell(fold_point)
            self._add_n_empty_cells(
                self.n_columns - len(fold_points_for_row) - 1)
            self._add_new_row()

    def _rows_required(self, sheet):
        """
        Return the number of rows that are needed to represent the `sheet`
        """
        n_datum_per_row = self.n_columns - 1
        return math.ceil(len(sheet.folds) / n_datum_per_row)

    def _iterate_fold_rows(self, sheet):
        """
        Iterate over rows of fold indices.

        Each row is returned as a list of indices for the folds in `sheet` that
        are to be written on that row.

        Each row has room for `self.n_columns` cells, one of which is reserved
        for the page number.
        """
        n_datum_per_row = self.n_columns - 1
        for i in range(0, len(sheet.folds), n_datum_per_row):
            yield range(
                    i,
                    min(i + n_datum_per_row, len(sheet.folds))
                    )

    def _add_page_number_cell(self, sheet, current_row_index, total_rows):
        """
        Add a page number cell for `current_row_index`th row of folds in
        `sheet`.

        The first row for each sheet contains the page number, while the other
        page number cells are empty. All page number cells have left and right
        borders, but only the topmost page number cell has top border and the
        bottom cell has bottom border.

        :sheet: `Sheet` for which the cell is added
        :current_row_index: The index of the row for which the page number cell
                            is to be added
        :total_rows: Total number of rows required for this page
        """
        if total_rows == 1:
            borders = "TBLR"
            text = sheet.page_number
        elif current_row_index == 0:
            borders = "TLR"
            text = sheet.page_number
        elif current_row_index == total_rows - 1:
            borders = "BLR"
            text = ""
        else:
            borders = "LR"
            text = ""
        self._add_cell(text, border=borders)

    def _add_cell(self, content, border=1, width=None):
        """
        Add a table cell to the PDF.

        :content: Contents of the cell
        :border: Which borders to draw. 1 for all borders, 0 for none, or a
                 string containing a set of characters from L, R, T and B for
                 left, right, top and bottom borders respectively. Defaults to
                 1.
        :width: Width of the cell. Defaults to self.column_width.
        """
        if width is None:
            width = self.column_width

        self.pdf.multi_cell(
            width,
            self.line_height,
            str(content),
            border=border,
            ln=3,
            max_line_height=self.pdf.font_size
            )

    def _add_n_empty_cells(self, n_cells):
        """
        Add `n_cells` empty cells.
        """
        for _ in range(n_cells):
            self._add_cell("")

    def _add_new_row(self):
        """
        Add new row to the table
        """
        self.pdf.ln(self.line_height)
