import argparse
import textwrap
from typing import List

from convo import telemetry
from convo.cli import SubParsersAction
import convo.cli.utils
from convo.shared.constants import TELEMETRY_DOCUMENTS_URL
import convo.shared.utils.cli


def sub_parser_addition(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser],
) -> None:
    """Add all telemetry tracking parsers.

    Args:
        subparsers: subparser we are going to attach to
        parents: Parent parsers, needed to ensure tree structure in argparse
    """

    telemetry_analyser = subparsers.add_parser(
        "telemetry",
        parents=parents,
        help="Configuration of Convo Open Source telemetry reporting.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    telemetry_sub_parsers = telemetry_analyser.add_subparsers()
    telemetry_disallow_parser = telemetry_sub_parsers.add_parser(
        "disable",
        parents=parents,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Disable Convo Open Source Telemetry reporting.",
    )
    telemetry_disallow_parser.set_defaults(func=deactivate_telemetry)

    telemetry_allow_parser = telemetry_sub_parsers.add_parser(
        "enable",
        parents=parents,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Enable Convo Open Source Telemetry reporting.",
    )
    telemetry_allow_parser.set_defaults(func=allow_telemetry)
    telemetry_analyser.set_defaults(func=notify_about_telemetry)


def notify_about_telemetry(_: argparse.Namespace) -> None:
    """Inform user about telemetry tracking."""
    is_allowed = telemetry.is_telemetry_enable()
    if is_allowed:
        convo.shared.utils.cli.printing_success(
            "Telemetry reporting is currently enabled for this installation."
        )
    else:
        convo.shared.utils.cli.printing_success(
            "Telemetry reporting is currently disabled for this installation."
        )

    print(
        textwrap.dedent(
            """
            Convo uses telemetry to report anonymous usage information. This information
            is essential to help improve Convo Open Source for all users."""
        )
    )

    if not is_allowed:
        print("\nYou can enable telemetry reporting using")
        convo.shared.utils.cli.printing_information("\n\tconvo telemetry enable")
    else:
        print("\nYou can disable telemetry reporting using:")
        convo.shared.utils.cli.printing_information("\n\tconvo telemetry disable")

    convo.shared.utils.cli.printing_success(
        "\nYou can find more information about telemetry reporting at "
        "" + TELEMETRY_DOCUMENTS_URL
    )


def deactivate_telemetry(_: argparse.Namespace) -> None:
    """Disable telemetry tracking."""
    telemetry.traverse_telemetry_disabled()
    telemetry.toggle_telemetry_report(is_enabled=False)
    convo.shared.utils.cli.printing_success("Disabled telemetry reporting.")


def allow_telemetry(_: argparse.Namespace) -> None:
    """Enable telemetry tracking."""
    telemetry.toggle_telemetry_report(is_enabled=True)
    convo.shared.utils.cli.printing_success("Enabled telemetry reporting.")
