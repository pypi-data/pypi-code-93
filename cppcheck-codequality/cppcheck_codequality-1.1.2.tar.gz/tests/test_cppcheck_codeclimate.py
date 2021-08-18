import pytest
import json
import logging

# PYTEST PLUGINS
# - pytest-console-scripts
# - pytest-cov

import cppcheck_codequality as uut

pytest_plugins = "console-scripts"

CPPCHECK_XML_ERRORS_START = r"""<?xml version="1.0" encoding="UTF-8"?><results version="2"><cppcheck version="1.90"/><errors>"""
CPPCHECK_XML_ERRORS_END = r"""</errors></results>"""


@pytest.mark.script_launch_mode("subprocess")
def test_cli_opts(script_runner):
    ret = script_runner.run("cppcheck-codequality", "-h")
    assert ret.success

    ret = script_runner.run("cppcheck-codequality", "-i")
    assert not ret.success

    ret = script_runner.run(
        "cppcheck-codequality", "--input-file", "./tests/cppcheck_simple.xml"
    )
    assert ret.success

    ret = script_runner.run(
        "cppcheck-codequality", "-i", "./tests/cppcheck_simple.xml", "-o"
    )
    assert not ret.success

    ret = script_runner.run(
        "cppcheck-codequality",
        "-i",
        "./tests/cppcheck_simple.xml",
        "-o",
        "cppcheck.json",
    )
    assert ret.success

    ret = script_runner.run("cppcheck-codequality", "--version")
    assert ret.success


def test_convert_no_messages(caplog):
    xml_in = CPPCHECK_XML_ERRORS_START + CPPCHECK_XML_ERRORS_END
    assert uut.__convert(xml_in) == "[]"

    print("Captured log:\n", caplog.text, flush=True)
    assert "WARNING" in caplog.text
    assert "Nothing to do" in caplog.text

    assert "ERROR" not in caplog.text


def test_convert_severity_warning(caplog):
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += r'<error id="uninitMemberVar" severity="warning" msg="Ur c0de suks" verbose="i can right go0d3r c0d3 thAn u" cwe="123456789"> <location file="tests/cpp_src/bad_code_1.cpp" line="50" column="5"/></error>'
    xml_in += CPPCHECK_XML_ERRORS_END

    json_out = json.loads(uut.__convert(xml_in))
    # print(json_out)

    assert len(json_out) == 1
    out = json_out[0]
    assert out["type"] == "issue"
    assert out["check_name"] == "uninitMemberVar"
    assert "CWE" in out["description"]
    assert out["categories"][0] == "Bug Risk"
    assert out["severity"] == "major"
    assert out["location"]["path"] == "tests/cpp_src/bad_code_1.cpp"
    assert out["location"]["positions"]["begin"]["line"] == 50
    assert out["location"]["positions"]["begin"]["column"] == 5
    assert out["fingerprint"] == "bbe03d1b9aab1db4f03edb21778e8a5b"

    print("Captured log:\n", caplog.text, flush=True)
    assert "WARNING" not in caplog.text
    assert "ERROR" not in caplog.text


def test_convert_severity_error(caplog):
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += r'<error id="uninitMemberVar" severity="error" msg="message" verbose="verbose message" cwe="123456789"> <location file="tests/cpp_src/bad_code_1.cpp" line="50" column="3"/></error>'
    xml_in += CPPCHECK_XML_ERRORS_END

    json_out = json.loads(uut.__convert(xml_in))
    assert len(json_out) == 1
    out = json_out[0]
    assert out["categories"][0] == "Bug Risk"
    assert out["severity"] == "critical"

    print("Captured log:\n", caplog.text, flush=True)
    assert "WARNING" not in caplog.text
    assert "ERROR" not in caplog.text


def test_convert_no_cwe(caplog):
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += r'<error id="uninitMemberVar" severity="error" msg="message" verbose="verbose message"> <location file="tests/cpp_src/bad_code_1.cpp" line="50" column="3"/></error>'
    xml_in += CPPCHECK_XML_ERRORS_END

    json_out = json.loads(uut.__convert(xml_in))
    assert len(json_out) == 1
    out = json_out[0]
    assert out["categories"][0] == "Bug Risk"
    assert out["severity"] == "critical"

    print("Captured log:\n", caplog.text, flush=True)
    assert "WARNING" not in caplog.text
    assert "ERROR" not in caplog.text


def test_convert_multiple_errors(caplog):
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += r'<error id="uninitMemberVar" severity="information" msg="message" verbose="verbose message"> <location file="tests/cpp_src/bad_code_1.cpp" line="60" column="456"/></error>'
    xml_in += r'<error id="uninitMemberVar" severity="warning" msg="message" verbose="verbose message"> <location file="tests/cpp_src/bad_code_1.cpp" line="68" column="9"/></error>'
    xml_in += CPPCHECK_XML_ERRORS_END

    json_out = json.loads(uut.__convert(xml_in))
    assert len(json_out) == 2
    assert json_out[0]["severity"] == "info"
    assert json_out[1]["severity"] == "major"

    print("Captured log:\n", caplog.text, flush=True)
    assert "WARNING" not in caplog.text
    assert "ERROR" not in caplog.text


def test_convert_location_file0(caplog):
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += r'<error id="cppCheckType" severity="error" msg="message" verbose="message"> <location file0="tests/cpp_src/Foo.cpp" file="tests/cpp_src/Foo.h" line="3"/></error>'
    xml_in += CPPCHECK_XML_ERRORS_END

    json_out = json.loads(uut.__convert(xml_in))
    assert json_out[0]["location"]["path"] == "tests/cpp_src/Foo.h"
    assert "tests/cpp_src/Foo.cpp" in json_out[0]["description"]

    print("Captured log:\n", caplog.text, flush=True)
    assert "WARNING" not in caplog.text
    assert "ERROR" not in caplog.text


def test_convert_multiple_locations(caplog):
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += (
        r'<error id="cppCheckType" severity="error" msg="message" verbose="message">'
    )
    xml_in += r'<location file="tests/cpp_src/Foo.h" line="1"/>'
    xml_in += r'<location file="tests/cpp_src/Foo.h" line="2"/>'
    xml_in += r'<location file="tests/cpp_src/Foo.h" line="3" column="3" />'
    xml_in += r" </error>"
    xml_in += CPPCHECK_XML_ERRORS_END

    json_out = json.loads(uut.__convert(xml_in))

    assert json_out[0]["location"]["path"] == "tests/cpp_src/Foo.h"
    assert json_out[0]["location"]["positions"]["begin"]["line"] == 1

    for i in range(0, 1):
        assert json_out[0]["other_locations"][i]["path"] == "tests/cpp_src/Foo.h"
        assert json_out[0]["other_locations"][i]["positions"]["begin"]["line"] == i + 2

    print("Captured log:\n", caplog.text, flush=True)
    assert "WARNING" not in caplog.text
    assert "ERROR" not in caplog.text


def test_convert_no_loc_column(caplog):
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += r'<error id="uninitMemberVar" severity="error" msg="message" verbose="verbose message"> <location file="tests/cpp_src/bad_code_1.cpp" line="3"/></error>'
    xml_in += CPPCHECK_XML_ERRORS_END

    json_out = json.loads(uut.__convert(xml_in))
    assert len(json_out) == 1
    out = json_out[0]
    assert out["location"]["positions"]["begin"]["line"] == 3
    assert out["location"]["positions"]["begin"]["column"] == 0

    print("Captured log:\n", caplog.text, flush=True)
    assert "WARNING" not in caplog.text
    assert "ERROR" not in caplog.text


def test_source_line_extractor_good(caplog):
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += r'<error id="id" severity="error" msg="msg" verbose="message">'
    xml_in += r'<location file="tests/cpp_src/four_lines.c" line="1" column="0" />'
    xml_in += r"</error>"
    xml_in += r'<error id="id" severity="error" msg="msg" verbose="message">'
    xml_in += r'<location file="tests/cpp_src/four_lines.c" line="2" column="0" />'
    xml_in += r"</error>"
    xml_in += r'<error id="id" severity="error" msg="msg" verbose="message">'
    xml_in += r'<location file="tests/cpp_src/four_lines.c" line="3" column="0" />'
    xml_in += r"</error>"
    xml_in += r'<error id="id" severity="error" msg="msg" verbose="message">'
    xml_in += r'<location file="tests/cpp_src/four_lines.c" line="4" column="0" />'
    xml_in += r"</error>"
    xml_in += CPPCHECK_XML_ERRORS_END

    with caplog.at_level(logging.WARNING):
        json_out = json.loads(uut.__convert(xml_in))

    print("Captured log:\n", caplog.text, flush=True)
    assert "WARNING" not in caplog.text
    assert "ERROR" not in caplog.text


def test_source_line_extractor_longer_than_file(caplog):
    """If code has included other source, then the line number CppCheck generates
    will be larger than the actual number of lines in the original source file.

    We just need to raise a warning and move on...
    """
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += r'<error id="id" severity="error" msg="msg" verbose="message">'
    xml_in += r'<location file="tests/cpp_src/four_lines.c" line="5" column="0" />'
    xml_in += r"</error>"
    xml_in += CPPCHECK_XML_ERRORS_END

    with caplog.at_level(logging.WARNING):
        json_out = json.loads(uut.__convert(xml_in))

    print("Captured log:\n", caplog.text, flush=True)
    assert "WARNING" in caplog.text
    assert "ERROR" not in caplog.text


def test_source_line_extractor_file0(caplog):
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += r'<error id="id" severity="error" msg="msg" verbose="message">'
    xml_in += r'<location file0="tests/cpp_src/four_lines.c" file="tests/cpp_src/Foo.h" line="15" column="0" />'
    xml_in += r'<location file0="tests/cpp_src/four_lines.c" file="tests/cpp_src/Foo.h" line="17" column="0" />'
    xml_in += r"</error>"
    xml_in += CPPCHECK_XML_ERRORS_END

    caplog.set_level(logging.DEBUG)
    json_out = json.loads(uut.__convert(xml_in))

    print("Captured log:\n", caplog.text, flush=True)
    assert "WARNING" not in caplog.text
    assert "ERROR" not in caplog.text


def test_convert_file(caplog):

    assert uut.convert_file("tests/cppcheck_simple.xml", "cppcheck.json")

    is_file_actually_json = False
    try:
        with open("cppcheck.json") as fin:
            json.load(fin)
        is_file_actually_json = True
    except ValueError:
        is_file_actually_json = False

    assert is_file_actually_json

    print("Captured log:\n", caplog.text, flush=True)
    assert "WARNING" not in caplog.text
    assert "ERROR" not in caplog.text
