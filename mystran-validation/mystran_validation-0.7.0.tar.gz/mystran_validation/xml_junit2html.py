from io import StringIO
from pathlib import Path
import xml.etree.ElementTree as ET
from collections import defaultdict
from jinja2 import Environment, BaseLoader


class TestSuite:
    """TestSuite: container for all testsuite test cases. Normally, this is only one."""

    def __init__(self, xml):
        self.meta = xml.attrib
        self.testcases = defaultdict(list)
        for tc in xml.findall("./testcase"):
            tcobject = TestCase(tc)
            self.testcases[tcobject.classname].append(tcobject)
        self.testcases = dict(self.testcases)

    def __repr__(self):
        return "testsuite errors={errors} failures={failures} skipped={skipped} tests={tests} time={time} timestamp={timestamp}".format(
            **self.meta
        )


class TestCase:
    def __init__(self, xml):
        for k, v in xml.attrib.items():
            setattr(self, k, v)
        self.properties = {}
        for prop in xml.findall("./properties/property"):
            self.properties[prop.attrib["name"]] = prop.attrib["value"]
        # ---------------------------------------------------------------
        # skipped
        skipped = xml.find("./skipped")
        if skipped is not None:
            self.skipped = skipped.attrib
        else:
            self.skipped = None
        # ---------------------------------------------------------------
        # failed
        failure = xml.find("./failure")
        if failure is not None:
            self.failure = failure.attrib
        else:
            self.failure = None

    def __repr__(self):
        s = f"{self.classname}::{self.name}"
        if self.skipped:
            s += " (skipped)"
        if self.failure:
            s += " (failed)"
        return s


def parse_xml(filepath):
    """parse JUnit  XML file and return a tuple of `TestSuite` instances"""
    fpath = Path(filepath)
    assert fpath.exists()
    tree = ET.parse(filepath)
    root = tree.getroot()
    # get all testsuites
    return tuple((TestSuite(ts) for ts in root.findall("./testsuite")))


MASTER_TPL = """
MYSTRAN TESTING
===============

{% for testsuite in testsuites %}
Test Suite "{{ testsuite.meta["name"] }}"
----------------------------------

{% for ini_name, testcases in testsuite.testcases.items() %}
### {{ ini_name }}
{% for tc in testcases %}
#### {{ tc }}
{% if tc.skipped %}**SKIPPED**: {{tc.skipped['message']}} {% endif %}
{% if tc.failure %}**FAILED**: \n{{tc.failure['message']}} {% endif %}
{% endfor %}

{% endfor %}{# end of test cases #}
{% endfor %}{# end of test suites #}
"""


def xml2md(xmlfpath):
    tss = parse_xml(xmlfpath)
    rtemplate = Environment(loader=BaseLoader).from_string(MASTER_TPL)
    return rtemplate.render({"testsuites": tss})
