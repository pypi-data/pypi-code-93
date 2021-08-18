import re
from datetime import datetime
from collections import OrderedDict
import warnings
import json
import pytest
from _pytest.mark.structures import Mark


_py_ext_re = re.compile(r"\.py$")


def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return "%s:%s: %s:%s\n" % (filename, lineno, category.__name__, message)


warnings.formatwarning = warning_on_one_line


def pytest_addoption(parser):
    """
    Adds commandline option for creating the json file.
    """
    group = parser.getgroup("Json report")
    group.addoption(
        "--jsonfile",
        action="store",
        dest="jsonpath",
        default=None,
        help="name of the json file where test details are saved.",
    )


def pytest_configure(config):
    """
    Adds jsonpath to pytest config and additional markers to pytest ini.
    """
    jsonpath = config.option.jsonpath
    if jsonpath:
        config.json = JiraJsonReport(jsonpath)
        config.pluginmanager.register(config.json)
    # register an additional marker
    config.addinivalue_line("markers", "railflow(options): read custom metadata")


def pytest_unconfigure(config):
    json = getattr(config, "json", None)
    if json:
        del config.json
        config.pluginmanager.unregister(json)


def mangle_test_address(address):
    """Split and modify test address to required format"""
    path, brack, params = address.partition("[")
    names = path.split("::")
    try:
        names.remove("()")
    except ValueError:
        pass

    names[0] = names[0].replace("/", ".")
    names[0] = _py_ext_re.sub("", names[0])
    names[-1] += brack + params
    return names


def restructure(data):
    restructured_list = []
    temp_list = []
    for i in data:
        if isinstance(i, OrderedDict):
            restructured_dict = OrderedDict(
                [("railflow_test_attributes", OrderedDict(temp_list))]
            )
            restructured_dict.update(i)
            restructured_list.append(restructured_dict)
            temp_list = []
        else:
            temp_list.append(i)
    return restructured_list


class JiraJsonReport(object):
    """
    Creates Json report
    """

    def __init__(self, jsonpath):
        self.results = []
        self.jsonpath = jsonpath
        self.class_list = [
            "testrail_user",
            "testrail_project",
            "case_fields",
            "result_fields",
            "test_path",
            "case_type",
            "case_priority",
            "assign",
        ]
        self.fun_list = [
            "author",
            "description",
            "jira_id",
            "test_path",
            "case_fields",
            "result_fields",
            "id_mappings",
            "case_type",
            "case_priority",
        ]

    def append(self, result):
        self.results.append(result)

    def build_result(self, report, status, message):
        """
        Builds test results
        """
        result = OrderedDict()
        names = mangle_test_address(report.nodeid)

        result["suite_name"] = names[-2]
        result["test_name"] = names[-1]
        if report.test_doc is None:
            result["details"] = report.test_doc
        else:
            result["details"] = report.test_doc.strip()
        result["markers"] = report.test_marker
        result["result"] = status
        result["duration"] = getattr(report, "duration", 0.0)
        result["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        result["message"] = message
        result["file_name"] = report.location[0]
        self.append(result)

    def append_pass(self, report):
        status = "PASSED"
        message = None
        self.build_result(report, status, message)

    def append_failure(self, report):

        if hasattr(report, "wasxfail"):
            status = "XPASSED"
            message = "xfail-marked test passes Reason: %s " % report.wasxfail

        else:
            message = str(report.longrepr)
            # if hasattr(report.longrepr, "reprcrash"):
            # message = report.longrepr.reprcrash.message
            # elif isinstance(report.longrepr, (unicode, str)):
            # message = report.longrepr
            # else:
            # message = str(report.longrepr)

            status = "FAILED"

        self.build_result(report, status, message)

    def append_error(self, report):

        message = report.longrepr
        status = "ERROR"
        self.build_result(report, status, message)

    def append_skipped(self, report):

        if hasattr(report, "wasxfail"):
            status = "XFAILED"
            message = "expected test failure Reason: %s " % report.wasxfail

        else:
            status = "SKIPPED"
            _, _, message = report.longrepr
            if message.startswith("Skipped: "):
                message = message[9:]

        self.build_result(report, status, message)

    @pytest.mark.hookwrapper
    def pytest_runtest_makereport(self, item, call):

        outcome = yield

        report = outcome.get_result()
        report.test_doc = item.obj.__doc__
        test_marker = []
        for k, v in item.keywords.items():
            if isinstance(v, list):
                for x in v:
                    if isinstance(x, Mark) and x.name != "railflow":
                        test_marker.append(x.name)

        report.test_marker = ", ".join(test_marker)

        if report.when == "call":
            for mark in item.iter_markers(name="railflow"):
                for i in mark.kwargs:
                    if item.cls:
                        if i in self.fun_list:
                            self.results.append((i, mark.kwargs[i]))
                        elif i in self.class_list:
                            self.results.append((i, mark.kwargs[i]))
                        else:
                            warnings.warn(
                                "%s is not a valid class attribute" % i, UserWarning
                            )
                    else:
                        if i in self.fun_list:
                            self.results.append((i, mark.kwargs[i]))
                        else:
                            warnings.warn(
                                "%s is not a valid test attribute" % i, UserWarning
                            )

    def pytest_runtest_logreport(self, report):

        if report.passed:
            if report.when == "call":
                self.append_pass(report)

        elif report.failed:
            if report.when == "call":
                self.append_failure(report)

            else:
                self.append_error(report)

        elif report.skipped:
            self.append_skipped(report)

    def pytest_sessionfinish(self, session):
        if not hasattr(session.config, "slaveinput"):
            if self.results:
                fieldnames = restructure(self.results)
                if self.jsonpath:
                    filepath = self.jsonpath
                    with open(filepath, "w") as file:
                        json.dump(
                            fieldnames,
                            file,
                            sort_keys=False,
                            indent=4,
                            separators=(",", ": "),
                        )

    def pytest_terminal_summary(self, terminalreporter):
        if self.results:
            terminalreporter.write_sep(
                "-*", "Json report written to %s" % self.jsonpath
            )
        else:
            terminalreporter.write_sep("-*", "No Json report is created.")
