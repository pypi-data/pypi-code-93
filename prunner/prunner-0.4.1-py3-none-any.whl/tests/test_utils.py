from prunner.util.convert import split_file_component


def test_split_file_component():
    assert split_file_component("Just content") == ("Just content", None)
    assert split_file_component("Filename#Content") == ("Content", "Filename")
