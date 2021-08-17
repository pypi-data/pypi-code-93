import os
from pathlib import Path
from godkjenn.vaults.fs_vault import FSVault

import pytest

from godkjenn.artifact import Artifact
from godkjenn.verification import MismatchError, verify
import godkjenn.comparators.exact


def pytest_addoption(parser):
    parser.addini("godkjenn_config", "Path to godkjenn configuration file")


INSTRUCTIONS = """{message}

If you wish to accept the received result, run:

    godkjenn {options} accept "{test_id}"
"""


def _make_instructions(message, test_id, pytest_config):
    """Calculate 'accept' instructions.

    Args:
        message: Any message to put before the instructions.
        test_id: The string id of the test.
        pytest_config: The full pytest configuration object.

    Returns: A string representing a command to run that will accept the received data.
    """
    pt_root = Path(pytest_config.rootdir.relto(os.getcwd()))
    options = "-C {}".format(pt_root)

    return INSTRUCTIONS.format(message=message, test_id=test_id, options=options)


def pytest_runtest_makereport(item, call):
    """pytest hook that runs to generate specialized reports.

    We find all Approver fixture arguments and generate a test report containing instructions on how to proceed (e.g.
    update the accepted value if desired).
    """
    import _pytest.runner

    if call.when == "call" and call.excinfo is not None:
        exc = call.excinfo.value

        # The test may have failed for reasons besides verification failure.
        if not isinstance(exc, MismatchError):
            return

        # There are potentially more than one approver, so we loop over them.
        for approver in _approver_args(item):
            instructions = _make_instructions(exc.message, approver._test_id, item.config)
            return _pytest.runner.TestReport(
                location=item.location,
                keywords=item.keywords,
                outcome="failed",
                when=call.when,
                nodeid=item.nodeid,
                longrepr=instructions,
            )


@pytest.fixture(scope="session")
def godkjenn_vault(pytestconfig):
    """Get the godkjenn configuration.

    If the pytest.ini specifies a config file, we'll try to use that. If it doesn't, we'll look for 'godkjenn.toml' in
    the root directory. If either exists, we load it (as TOML) and return the 'godkjenn' section. If there is no
    'godkjenn' section, we'll return a default configuration.
    """
    root_dir = Path(pytestconfig.rootdir) / ".godkjenn" / "vault"

    # TODO: If root_dir does not exist, should we create it? That would make this plugin zero-config.

    vault = FSVault(root_dir)
    return vault


@pytest.fixture(name="godkjenn")
def godkjenn_fixture(request, godkjenn_vault):
    "Returns an object on which you can call `verify()`."
    test_id = request.node.nodeid
    return Approver(test_id, godkjenn_vault)


class Approver:
    """Type returned from the godkjenn fixture.

    Users can call the `verify()` method to check their latest results.
    """

    def __init__(self, test_id, vault):
        self._test_id = test_id
        self._vault = vault

    def verify(
        self,
        received,
        mime_type="application/octet-stream",
        encoding=None,
        comparator=godkjenn.comparators.exact.compare,
    ):
        """Check the latest received data against the accepted version.

        If there's a mismatch, this will trigger a pytest failure (i.e. via `assert`).

        Args:
            received: The received test data to be compared with the approved.
            mime_type: The MIME type of `received`.
            comparator: Function determining if accepted and received data are the same.
        """
        verify(self._vault, comparator, self._test_id, received, mime_type, encoding)

    def verify_text(
        self,
        received,
        mime_type="text/plain",
        comparator=godkjenn.comparators.exact.compare,
    ):
        self.verify(received.encode("utf-8"), mime_type=mime_type, encoding="utf-8", comparator=comparator)


def _approver_args(item):
    "Find all Approver fixture arguments to a test item."
    for arg in item.funcargs.values():
        if isinstance(arg, Approver):
            yield arg
