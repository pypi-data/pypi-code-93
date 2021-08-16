import pytest

from w.services.technical.csv_service import CsvService
from w.tests.mixins.testcase_mixin import TestCaseMixin


class TestCsvService(TestCaseMixin):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.filename = cls.get_datasets_dir("csv/simple.csv")
        cls.mapping = {"colA": "columnA", "colB": "columnB", "colC": "columnC"}

    """
    is_csv
    """

    def test_is_csv_with_no_csv_file_return_false(self):
        """ Ensure method return False on no csv file """
        files = ["toto.txt", "csv.txt", "csv.csv.gz"]
        for file in files:
            assert CsvService.is_csv(file) is False

    def test_is_csv_with_success_return_true(self):
        """ Ensure method return True on csv file """
        files = ["toto.csv", "csv.csv"]
        for file in files:
            assert CsvService.is_csv(file) is True

    """
    load
    """

    def test_load_with_invalid_csv_raise_runtime_error(self):
        """ Ensure method raise runtime error if file is not csv """
        filename = self.get_datasets_dir("excel/Excel2007File.xlsx")
        match = "Excel2007File.xlsx is not a csv file"
        with pytest.raises(RuntimeError, match=match):
            CsvService.load(filename, self.mapping)

    def test_load_with_invalid_header_raise_runtime_error(self):
        """ Ensure method raise runtime error if header is false """
        mapping = self.mapping.copy()
        mapping["colWrongA"] = mapping.pop("colA")
        match = (
            "incorrect or missing header, expected 'colB;colC;colWrongA'"
            " got 'colA;colB;colC'"
        )
        with pytest.raises(RuntimeError, match=match):
            CsvService.load(self.filename, mapping)

    def test_load_with_success_return_list(self):
        """ Ensure method succeed """
        self.assert_equals_resultset(CsvService.load(self.filename, self.mapping))

    """
    dump
    """

    def test_dump_with_success_return_none(self):
        """ Ensure method succeed """
        self.clean_sandbox()
        filename = self.get_sandbox_dir("test_dump.csv")
        mapping = {"colA": "columnA", "colB": "columnB", "colC": "columnC"}
        rows = [
            {
                "colA": "row 1 data, columnA",
                "colB": "row 1 data; columnB",
                "colC": "row 1 data\tcolumnC éàç",
            },
            {
                "colA": "row 2 data, columnA",
                "colB": "row 2 data, columnB",
                "colC": "row 2 data, columnC",
            },
        ]
        CsvService.dump(filename, mapping, rows)
        self.assert_file_exists(filename)
        reverse_mapping = {v: k for k, v in mapping.items()}
        self.assert_equals_resultset(CsvService.load(filename, reverse_mapping))
