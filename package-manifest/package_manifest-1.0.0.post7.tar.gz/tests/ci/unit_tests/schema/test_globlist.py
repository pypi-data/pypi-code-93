#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of package-manifest.
#
#  You should have received a copy of the MIT License along with package-manifest.
#  If not, see <https://opensource.org/licenses/MIT>.
#

import pydantic
import pytest
import ruamel.yaml

from package_manifest._schema import GlobList


class MockObject(pydantic.BaseModel):
    glob_list: GlobList


def test_multiline_clean():
    data = {
        "glob_list": ["one", "two"],
    }

    under_test = MockObject.parse_obj(data)

    assert under_test.glob_list[0] == "one"
    assert under_test.glob_list[1] == "two"
    assert str(under_test) == "glob_list=['one', 'two']"


def test_single_line_clean():
    data = {
        "glob_list": ["one"],
    }

    under_test = MockObject.parse_obj(data)

    assert under_test.glob_list[0] == "one"
    assert str(under_test) == "glob_list=['one']"


def test_bad_value():
    data = {
        "glob_list": 3,
    }

    with pytest.raises(pydantic.ValidationError):
        MockObject.parse_obj(data)


@pytest.fixture()
def parse_yaml():
    def _apply(content: str) -> dict:
        yaml = ruamel.yaml.YAML(typ="safe")
        data = yaml.load(content)
        return data

    return _apply


class TestYamlParsing:
    def test_simple_clean(self, parse_yaml):
        content = """---
glob_list: [one, two]
"""
        data = parse_yaml(content)

        under_test = MockObject.parse_obj(data)

        assert len(under_test.glob_list) == 2
        assert under_test.glob_list[0] == "one"
        assert under_test.glob_list[1] == "two"

    def test_single_line_clean(self, parse_yaml):
        content = """---
glob_list:
  - one
"""
        data = parse_yaml(content)

        under_test = MockObject.parse_obj(data)

        assert len(under_test.glob_list) == 1
        assert under_test.glob_list[0] == "one"

    def test_multiline_clean(self, parse_yaml):
        content = """---
glob_list:
  - one
  - two
"""
        data = parse_yaml(content)

        under_test = MockObject.parse_obj(data)

        assert len(under_test.glob_list) == 2
        assert under_test.glob_list[0] == "one"
        assert under_test.glob_list[1] == "two"
