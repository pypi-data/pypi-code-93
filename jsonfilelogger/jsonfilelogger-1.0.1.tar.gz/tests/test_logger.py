import os
import pytest
import glob

from jsonfilelogger.logger import LogWriter, LogReader


def test_writer_and_reader():
    writer = LogWriter(threshold=2)
    writer.reset()
    writer.log({"test": 1, "this": "logger", "with": True, "all": 1.337, "kinds": ["of", "values"]})
    writer.log({"test": 2, "this": "logger", "with": True, "all": 7.331, "kinds": [1, 3, 3, 7]})
    assert os.path.exists("./log.json")
    reader = LogReader()
    data = reader.retrieve()
    assert len(data) == 2
    assert data == [{"test": 1, "this": "logger", "with": True, "all": 1.337, "kinds": ["of", "values"]},
                    {"test": 2, "this": "logger", "with": True, "all": 7.331, "kinds": [1, 3, 3, 7]}]
    writer.log({"test": 3, "this": "logger", "with": True, "all": 1337.1337, "kinds": [None]})
    data = reader.retrieve()
    assert len(data) == 2
    writer.flush()
    data = reader.retrieve()
    assert len(data) == 3
    assert data == [{"test": 1, "this": "logger", "with": True, "all": 1.337, "kinds": ["of", "values"]},
                    {"test": 2, "this": "logger", "with": True, "all": 7.331, "kinds": [1, 3, 3, 7]},
                    {"test": 3, "this": "logger", "with": True, "all": 1337.1337, "kinds": [None]}]
    reader.reset()
    data = reader.retrieve()
    assert len(data) == 0
    reader.remove()
    with pytest.raises(Exception):
        reader.assert_file_exists()


def test_writer_and_reader_with_datetime():
    writer = LogWriter.with_datetime(threshold=2)
    writer.reset()
    writer.log({"test": 1, "this": "logger", "with": True, "all": 1.337, "kinds": ["of", "values"]})
    writer.log({"test": 2, "this": "logger", "with": True, "all": 7.331, "kinds": [1, 3, 3, 7]})

    logs_files = sorted(glob.glob("./[0-9]*.json"))
    assert len(logs_files) > 0
    reader = LogReader(folder="./", filename=logs_files[-1])
    data = reader.retrieve()
    assert len(data) == 2
    assert data == [{"test": 1, "this": "logger", "with": True, "all": 1.337, "kinds": ["of", "values"]},
                    {"test": 2, "this": "logger", "with": True, "all": 7.331, "kinds": [1, 3, 3, 7]}]
    writer.log({"test": 3, "this": "logger", "with": True, "all": 1337.1337, "kinds": [None]})
    data = reader.retrieve()
    assert len(data) == 2
    writer.flush()
    data = reader.retrieve()
    assert len(data) == 3
    assert data == [{"test": 1, "this": "logger", "with": True, "all": 1.337, "kinds": ["of", "values"]},
                    {"test": 2, "this": "logger", "with": True, "all": 7.331, "kinds": [1, 3, 3, 7]},
                    {"test": 3, "this": "logger", "with": True, "all": 1337.1337, "kinds": [None]}]
    reader.reset()
    data = reader.retrieve()
    assert len(data) == 0
    reader.remove()
    with pytest.raises(Exception):
        reader.assert_file_exists()


@pytest.fixture(autouse=True)
def run_around_tests():
    yield
    if os.path.exists("./log.json"):
        os.remove("./log.json")
    logs_files = sorted(glob.glob("./[0-9]*.json"))
    if len(logs_files) > 0:
        [os.remove(logfile) for logfile in logs_files]
