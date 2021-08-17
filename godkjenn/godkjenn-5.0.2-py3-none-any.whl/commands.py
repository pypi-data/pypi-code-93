import json
import logging
import sys

import rich.markup
from rich.console import Console
from rich.table import Table

import godkjenn
from godkjenn.diff_selector import DiffSelector
from godkjenn.vaults.fs_vault import FSVault
from godkjenn.verification import MismatchError, verify

log = logging.getLogger(__name__)


def diff(vault: FSVault, test_id, differs: DiffSelector):
    """Run differ for a single test.

    Args:
        vault: The FSVault to use.
        test_id: The ID of the test to diff.
        differ: DiffSelect to find correct differ for test artifacts.

    Raises:
        KeyError: The vault does not contain both accepted and received data for the test.
    """
    try:
        received = vault.received(test_id)
        accepted = vault.accepted(test_id)
    except KeyError:
        raise KeyError("Do not have both received and accepted data. No diff possible.")

    differ = differs[received.mime_type]
    differ(received, accepted)


def status(vault, as_json=False, stream=sys.stdout, include_up_to_date=False):
    """Print status of godkjenn vault"""

    def artifacts():
        for test_id in vault.ids():
            try:
                accepted = vault.accepted(test_id)
            except KeyError:
                accepted = None

            try:
                received = vault.received(test_id)
            except KeyError:
                received = None

            if accepted is None:
                if received is None:
                    assert False, "Test ID with no information: {}".format(test_id)
                else:
                    message = "initialized"
            else:
                if received is None:
                    if not include_up_to_date:
                        continue
                    message = "up-to-date"
                elif accepted == received:
                    # TODO: What about using a specialized comparator?
                    message = "status-quo"
                else:
                    message = "mismatch"

            yield test_id, message

    status = dict(artifacts())

    if as_json:
        json.dump(status, fp=stream, indent=4)
        return

    if not status:
        return

    table = Table()
    table.add_column("Test ID")
    table.add_column("Status")
    for test_id, message in status.items():
        table.add_row(rich.markup.escape(test_id), rich.markup.escape(message))
    console = Console(file=stream)
    console.print(table)


def review(vault: FSVault, differs: DiffSelector):
    """Run an external diff tool over mismatches.

    Args:
        vault: The vault to review.
        mime_type_command_templates: A mapping from MIME-types to command templates.
        default_command_template: The command template to use if there is no MIME-type
            specific template for a test.
    """
    for artifact_id in vault.ids():
        try:
            accepted = vault.accepted(artifact_id)
            received = vault.received(artifact_id)
        except KeyError:
            continue

        diff_command = differs[received.mime_type]

        try:
            diff_command(received, accepted)
        except Exception as exc:
            log.error("Error running diff command: %s", str(exc))
            continue

        # This compares the *new* state of the two artifacts. If they match, then the received data will be removed as a
        # result.
        try:
            verify(
                vault,
                godkjenn.comparators.exact.compare,
                artifact_id,
                received.path.read_bytes(),
                received.mime_type,
                received.encoding,
            )
        except MismatchError:
            pass
