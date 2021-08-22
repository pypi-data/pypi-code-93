#!/usr/bin/env python3

"Pynote main script"

from pathlib import Path, PurePath
import subprocess
import click


# Add shorhand for help page
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def get_workspace_path(workspace):
    """
    Get the workspace folder location
    """

    # Set the workspace if no name is assigned
    if workspace is None:
        workspace = "notes/"
    # Set home directory variable
    home = str(Path.home())
    # Define the workspace inside user's HOME
    workspace = Path(home, workspace)

    return workspace

def initialize_notes(workspace):
    """
    Creates a new folder to store your notes
    """

    # Initialize notes folder
    try:
        workspace = get_workspace_path(workspace)
        # Check if the folder already exists
        if not Path.exists(workspace):
            # Create notes folder
            subprocess.run(["mkdir", workspace], check=True)
            click.echo(f"{workspace.name} workspace has been initialized")
        else:
            click.echo(f"{workspace.name} workspace already exists")
    # Exit because the folder exists
    except:
        click.echo(f"{workspace.name} workspace already exists")

def get_notes_index(workspace):
    """
    Returns a pager with a numbered list of all notes
    """

    workspace = get_workspace_path(workspace)
    # Get all the notes' paths
    notes = Path(workspace).iterdir()
    # Index notes
    index = dict(enumerate(notes, start=1))
    # Rename them to their base name
    index = {key: index[key].name for key in index}

    return index


def pretty_print(workspace, dictionary):
    """
    Print dictionary in a similar way to ls command
    """

    # Print the folder containing the index
    click.echo(f"Your notes at {workspace}")
    # Show the index for each note
    for key in dictionary:
        click.echo(f"{key}\t{dictionary[key]}")

def edit_note(workspace, index, number):
    """
    Opens a note with Nvim
    """

    try:
        note = index[int(number)]
        path = PurePath(workspace, note)
        subprocess.run(["nvim", path], check=True)
        click.echo(f"Done editing {note}")
    # Exit because the notes name is lacking
    except (NameError, TypeError) as e:
        click.echo("Don't know which note to edit")

def create_note(workspace, note):
    """
    Opens a new note with Nvim
    """

    path = PurePath(workspace, note)
    try:
        subprocess.run(["nvim", path], check=True)
        click.echo(f"Created {note}")
    # Exit because the note already exists
    except FileExistsError:
        click.echo("That note already exists")

def remove_note(workspace, index, number):
    """
    Removes an existing note
    """

    note = index[int(number)]
    path = PurePath(workspace, note)
    try:
        subprocess.run(["rm", path], check=True)
        click.echo(f"'{note}' has been removed")
    # Exit because the notes name is lacking
    except (NameError, TypeError) as e:
        click.echo("Don't know which note to delete")

# Set CLI parameters
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("action")
@click.option("-n", "--note", help="Note to manipulate")
@click.option("-w", "--workspace", help="Workspace for your notes")

def pynote(action, note=None, workspace=None):
    """
    Notes at the command line with Python

    Actions available are: init, view, add, edit and delete.
    """

    # Get workspace location
    wkspace = get_workspace_path(workspace)

    # Initialize notes folder
    if action == "init":
        initialize_notes(wkspace)

    index = get_notes_index(wkspace)

    # See existing notes
    if action == "view":
        pretty_print(wkspace, index)

   # Add a new note
    if action == "add":
        create_note(wkspace, note)

   # Edit an existing note
    if action == "edit":
        edit_note(wkspace, index, note)

    # Remove a note
    if action == "delete":
        remove_note(wkspace, index, note)

#if __name__ == "__main__":
#    pynote()
