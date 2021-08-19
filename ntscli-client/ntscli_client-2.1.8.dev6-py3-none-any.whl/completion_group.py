import os

import click
import click_completion
import click_completion.core


def custom_startswith(string, incomplete):
    """A custom completion matching that supports case insensitive matching"""
    if os.environ.get("_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE"):
        string = string.lower()
        incomplete = incomplete.lower()
    return string.startswith(incomplete)


cmd_help = """Shell tab completion commands for nts. Available shells:\n
  %s\n
\n
Default type: auto-detection\n
""" % "\n\n  ".join(
    sorted(click_completion.core.shells.keys())
)


@click.group(help=cmd_help)
def completion():
    """
    Show tab completion scripts.
    """


@click.group(name="completion", help=cmd_help)
def completion_alpha():
    """
    Install tab completion scripts.

    These will eventually move to the nts completion command group.
    """


@completion.command()
@click.option("-i", "--case-insensitive/--no-case-insensitive", help="Case insensitive completion")
@click.argument("shell", required=False, type=click_completion.DocumentedChoice(click_completion.core.shells))
def show(shell, case_insensitive):
    """
    Show tab completion code.

    The final instructions to install this block of code will differ from shell to shell.
    Frequently all you have to do is source the output of this command from the load sequence of your shell, such as:
    source "$(nts completion show)"

    or redirect it to a file that is loaded during your shell startup.
    \b
    You may prefer to try the pre-release command to attempt an installation:

    nts alpha completion install
    """
    extra_env = {"_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE": "ON"} if case_insensitive else {}
    click.echo(click_completion.core.get_code(shell, extra_env=extra_env))


@completion.command()
@click.option("-i", "--case-insensitive/--no-case-insensitive", help="Case insensitive completion")
@click.argument("shell", required=False, type=click_completion.DocumentedChoice(click_completion.core.shells))
def install(shell, case_insensitive):
    """
    Show tab completion code.

    The final instructions to install this block of code will differ from shell to shell.
    Frequently all you have to do is source the output of this command from the load sequence of your shell, such as:
    source "$(nts completion show)"

    or redirect it to a file that is loaded during your shell startup.
    \b
    You may prefer to try the pre-release command to attempt an installation:

    nts alpha completion install --help
    """
    print("This command is currently in alpha. Instead see nts alpha completion install --help")


@completion_alpha.command(name="show")
@click.option("-i", "--case-insensitive/--no-case-insensitive", help="Case insensitive completion")
@click.argument("shell", required=False, type=click_completion.DocumentedChoice(click_completion.core.shells))
def alpha_show(shell, case_insensitive):
    """
    Show tab completion code.

    The final instructions to install this block of code will differ from shell to shell.
    Frequently all you have to do is source the output of this command from the load sequence of your shell, such as:
    source "$(nts completion show)"

    or redirect it to a file that is loaded during your shell startup.
    \b
    You may prefer to try the pre-release command to attempt an installation:

    nts alpha completion install --help
    """
    extra_env = {"_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE": "ON"} if case_insensitive else {}
    click.echo(click_completion.core.get_code(shell, extra_env=extra_env))


@completion_alpha.command(name="install")
@click.option("-i", "--case-insensitive/--no-case-insensitive", help="Case insensitive completion")
@click.argument("shell", required=False, type=click_completion.DocumentedChoice(click_completion.core.shells))
@click.argument("path", required=False)
def alpha_install(case_insensitive, shell, path):
    """
    Install the completion code.

    This requires that you start a new shell session before it is noticed.
    This installs the completion code in the default documented location for your shell to pick it up. If your shell configuration
    is not the exact default, you might have to make slight changes to pick up the completion script, or load it only on request using
    the output of the command:

    nts completion show
    """
    extra_env = {"_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE": "ON"} if case_insensitive else {}
    shell, path = click_completion.core.install(shell=shell, path=path, append=True, extra_env=extra_env)  # nosec B604
    click.echo("%s completion installed in %s" % (shell, path))
    click.echo("You will need to restart your shell to load the completion into memory.")
