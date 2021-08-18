"""
Tests for PatternCreator.
"""

from bookfolder.pattern_creator import PatternCreator

# pylint: disable=missing-function-docstring
# test functions should be self-documenting


def test_input_path():
    creator = PatternCreator("some/path.png")
    assert creator.input_path == "some/path.png"


def test_default_measurement_interval():
    creator = PatternCreator("some/path.png")
    assert creator.measurement_interval == 0.25


def test_measurement_interval_initialization():
    creator = PatternCreator("some/path.png", 1.0)
    assert creator.measurement_interval == 1.0


def test_extracts_correct_number_of_sheets():
    creator = PatternCreator("tests/data/simple_pattern.png")
    assert len(creator.sheets()) == 3


def test_extracted_sheets_have_correct_number_of_folds():
    creator = PatternCreator("tests/data/simple_pattern.png")
    assert len(creator.sheets()[0].folds) == 3
    assert len(creator.sheets()[1].folds) == 5
    assert len(creator.sheets()[2].folds) == 4


def test_extracted_sheets_have_correct_folds_locations():
    creator = PatternCreator("tests/data/simple_pattern.png")
    assert creator.sheets()[0].folds == [4, 6, 7]


def test_extracted_multicolor_sheets_have_correct_number_of_folds():
    creator = PatternCreator("tests/data/color_pattern.png")
    assert len(creator.sheets()[0].folds) == 5
    assert len(creator.sheets()[1].folds) == 5
    assert len(creator.sheets()[2].folds) == 4


def test_extracted_color_sheets_have_correct_folds_locations():
    creator = PatternCreator("tests/data/color_pattern.png")
    assert creator.sheets()[0].folds == [1, 3, 4, 6, 7]


def test_extracing_empty_column():
    creator = PatternCreator("tests/data/empty_column_pattern.png")
    assert creator.sheets()[1].folds == []


def test_default_start_page():
    creator = PatternCreator("tests/data/simple_pattern.png")
    assert creator.sheets()[0].page_number == 1


def test_setting_negative_start_page():
    creator = PatternCreator("tests/data/simple_pattern.png", start_page=-1)
    assert creator.sheets()[0].page_number == -1
    assert creator.sheets()[1].page_number == 1
    assert creator.sheets()[2].page_number == 3


def test_setting_positive_start_page():
    creator = PatternCreator("tests/data/simple_pattern.png", start_page=200)
    assert creator.sheets()[0].page_number == 200
    assert creator.sheets()[1].page_number == 202
    assert creator.sheets()[2].page_number == 204
