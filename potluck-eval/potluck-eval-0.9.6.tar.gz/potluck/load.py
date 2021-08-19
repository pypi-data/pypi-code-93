"""
Functions for loading submitted & solution code.

load.py
"""

import importlib
import os
import sys
import types
import tempfile
import shutil

from . import mast
from . import logging


def set_specs_dir(directory):
    """
    Sets the specifications directory.
    """
    global SPECS_DIR
    SPECS_DIR = directory


def load_task_spec(task_info):
    """
    Loads a task specification module for the specified task. Returns the
    imported module. Augments the module with the following values:

    - taskid: The task ID for the task
    - base_path: the path to the spec file
    - soln_path: the path to the solution files directory
    - starter_path: the path to the starter files directory
    - starter_src: the source code for the main starter file
        (or an empty string if there is no starter file or if the
        task requires more than one file)
    - helper_files: a list of strings naming files which are in the
        starter directory and the solution directory but which aren't
        the main task file (or directory) itself. These are just the
        file names, not the full paths.
    """
    # Set up sys.path and import specifically:
    # Note: Relevant directories will need __init__.py files!
    logging.log(f"Loading specification for '{task_info['id']}'")
    spec_target = os.path.join(SPECS_DIR, task_info["id"], "spec.py")
    logging.log(f"    loading from: {spec_target}")
    sys.path.insert(0, SPECS_DIR)
    try:
        spec = importlib.import_module(task_info["id"] + '.spec')
    except Exception:
        logging.log("Fatal error: Unable to load task specification.")
        logging.log_current_exception()
        raise
    sys.path.pop(0)

    # Augment imported module
    here = os.path.dirname(spec.__file__)
    spec.taskid = task_info["id"]
    spec.base_path = here
    spec.soln_path = os.path.join(here, 'soln')
    spec.starter_path = os.path.join(here, 'starter')
    starter_file = os.path.join(spec.starter_path, task_info["target"])
    if os.path.isfile(starter_file):
        with open(starter_file, encoding="utf-8") as fin:
            spec.starter_src = fin.read()
    else:
        spec.starter_src = ""

    soln_files = os.listdir(spec.soln_path)
    if os.path.exists(spec.starter_path):
        starter_files = os.listdir(spec.starter_path)
    else:
        starter_files = []
    spec.helper_files = list(
        (set(soln_files) & set(starter_files))
      - set([task_info["target"]])
    )

    logging.log("...done loading specification")

    return spec


def import_soln(taskspec):
    '''
    Uses importlib to import the solution module for the given task. If
    the module has already been imported, reloads it.

    Returns the imported module object.

    Fails if this task doesn't have a Python source file.
    '''
    # Here we temporarily both change cwd *and* push it onto our sys.path.
    original_directory = os.getcwd()
    os.chdir(taskspec.soln_path)
    sys.path.insert(0, os.getcwd())
    try:
        module_name = taskspec.src.replace('.py', '')
        if module_name in sys.modules:
            return importlib.reload(sys.modules[module_name])
        else:
            return importlib.import_module(module_name)
    finally:
        # Reset cwd and sys.path:
        os.chdir(original_directory)
        sys.path = sys.path[1:]


def link_mapping(spec):
    """
    Extracts the standard symlink mapping for sandbox files from the
    given specification, based on its helper_files and starter_path
    properties. The result is suitable as a sandbox_links argument to
    `create_module_in_sandbox`.
    """
    return {
        os.path.abspath(os.path.join(spec.starter_path, helper)): helper
        for helper in spec.helper_files
    }


def create_module_in_sandbox(
    node,
    filename,
    sandbox_links=None,
    sandbox_files=None,
    on_disk=None
):
    """
    Given an AST node and a filename, creates a temporary sandbox
    directory, runs the code in the sandbox to create a module object,
    and returns the module object that was created. If extra files are
    needed in the sandbox, a dictionary mapping absolute paths to
    paths-in-sandbox can be supplied and those files will be symlinked
    in (see `link_mapping`). Alternatively, an equivalently-structured
    sandbox_files directory may be supplied to copying files rather than
    creating links, which is typically less efficient, but desirable if
    those files will be modified.

    If on_disk is provided, it should be a full path to the file that the
    code was parsed from, and will be used to provide a __file__
    variable while the code runs.
    """
    with tempfile.TemporaryDirectory(suffix="__tmp") as tmpdir:
        # Create symlinks
        if sandbox_links is not None:
            for filepath in sandbox_links:
                to = os.path.join(tmpdir, sandbox_links[filepath])
                os.symlink(filepath, to)

        # Copy files
        if sandbox_files is not None:
            for filepath in sandbox_files:
                to = os.path.join(tmpdir, sandbox_files[filepath])
                shutil.copy(filepath, to)

        # Create the module
        result = create_module_from_code(
            node,
            filename,
            on_disk=on_disk,
            sandbox=tmpdir
        )

    return result


def create_module_from_code(node, filename, on_disk=None, sandbox=None):
    """
    Given an AST node and a filename, creates a module object and
    registers it in sys.modules. The module name is the filename without
    any extension (.py or otherwise) and the module docstring is
    extracted from the given AST node if possible (i.e., when the first
    statement in the module body is a string constant).

    If on_disk is provided, it should be a full path to the file that the
    code was parsed from, and will be used to provide a __file__
    variable while the code runs.

    If a sandbox is provided, it should be a string indicating the path
    to a directory which should be set as current while we execute the
    code.
    """
    module_name = os.path.splitext(filename)[0]

    # Compile the AST node into executable code
    bytecode = compile(
        node,
        module_name + ".py", # necessary to get __name__ correct
        "exec"
    )

    # Grab module docstring if it exists
    try:
        module_docstring = node.body[0].value.value
    except Exception:
        module_docstring = ""

    # Create a new module and insert it into sys.modules (must
    # happen before execution of the module code!)
    module = types.ModuleType(module_name, module_docstring)
    sys.modules[module_name] = module
    module.__dict__["__name__"] = module_name + ".py"
    module.__dict__["__file__"] = on_disk

    if sandbox is None:
        # Execute the code in the module's dictionary, which fleshes
        # out the module
        exec(bytecode, module.__dict__, module.__dict__)
    else:
        # If we've been given a sandbox directory, use it
        prev_dir = os.getcwd()
        os.chdir(sandbox)
        sys.path.insert(0, sandbox)
        try:
            # Execute the code in the module's dictionary, which fleshes
            # out the module
            exec(bytecode, module.__dict__, module.__dict__)
        finally:
            sys.path = sys.path[1:]
            os.chdir(prev_dir)

    # Return our completed module
    return module


def fix_parse(codestring, filename, exn=None):
    '''
    Inherited from net.py in Codder.

    Tries to comment out lines with syntax errors to recover remaining
    code. Returns a tuple containing the (possibly edited) code string
    that was parsed, the AST object resulting from the parse, and a list
    of errors (Exception objects) encountered along the way. If it
    encounters an unrecoverable exception, it will return None in place
    of the AST object.

    This function is recursive, and if given an exception to work with,
    it starts by commenting out relevant lines of the file before
    attempting to parse it again.
    '''
    try:
        # if parsing fails for any reason we'll reattempt based on the
        # error...
        if exn:
            # if we encountered an exception, comment out that line and
            # any previous lines that end with ':' or which are empty or
            # comments...
            eindex = exn.lineno - 1
            lines = codestring.split('\n')
            lines[eindex] = '## SYNTAX ERROR ## ' + lines[eindex]

            # Grab lines above too, back to the nearest line which doesn't
            # end in ':', not counting comments or blank lines. This
            # helps ensure that if our syntax error is the only statement
            # in a loop or conditional, that loop/conditional dies with
            # it.
            for i in range(eindex - 1, 0, -1):
                predline = lines[i].strip()
                if (
                  predline.endswith(':')
               or predline.startswith('#')
               or len(predline) == 0
                ):
                    lines[i] = '## SYNTAX ERROR BUDDY ## ' + lines[i]
                else:
                    break
                pass
            pass

            # Rebuild our code string with the new comments in place
            codestring = '\n'.join(lines)
        pass

        # Whether or not we just commented out some code, we'll try to
        # parse what we've got. An error here will throw us into one of
        # the except clauses below, or bubble out if it's not one we're
        # expecting.
        tree = mast.parse(codestring, filename=filename)

        # Parsing at this level didn't encounter any errors, so our error
        # list will be empty. Whoever called us is responsible for adding
        # the error they encountered if they passed us an error to watch
        # out for.
        return (codestring, tree, [])

    except (mast.MastParseError, SyntaxError, IndentationError) as e:
        # These are expected parsing errors that we're prepared to
        # address by commenting out code

        # If it's a MastParseError, process the trigger instead...
        if isinstance(e, mast.MastParseError):
            e = e.trigger

        if not isinstance(e, (SyntaxError, IndentationError)):
            # A MastParseError not triggered by a syntax/indentation error
            logging.log("'{}' is not a valid Python file".format(filename))
            return (codestring, None, [e])

        if exn and e.lineno == exn.lineno:
            # if it persists on the same line of code despite introducing
            # a comment, we give up
            raise e
        else:
            # Recurse to try to fix this new error
            try:
                c, a, es = fix_parse(
                    codestring,
                    filename,
                    exn=e
                )
            except (SyntaxError, IndentationError) as e:
                # give up if we couldn't fix it
                return (codestring, None, [exn] if exn else [e])
            else:
                # If there isn't an exception, we can return the code
                # along with this error plus any other errors
                return (c, a, [e] + es)

    except TypeError as e:
        # Happens e.g., when the file is not a python file
        logging.log("'{}' is not a valid Python file".format(filename))
        return (codestring, None, [e])

    except Exception:
        logging.log(
            "Encountered unexpected exception when parsing '{}'"
            .format(filename)
        )
        logging.log_current_exception()

    # Let any other unexpected errors bubble out
