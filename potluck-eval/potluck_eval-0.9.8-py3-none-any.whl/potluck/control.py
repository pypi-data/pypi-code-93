"""
High-level evaluation tools for launching core potluck tasks such as
rubric creation, spec validation, and submission evaluation.

control.py

Typically, one would call `load_configuration`, then `setup`, and finally
one of the `launch_*` functions.

Dependencies:

- `jinja2` for report rendering via HTML templates.
- `pygments` for code highlighting in reports.
- `importlib_resources` for resource loading.

This module relies on a configuration file to find task meta-data, task
specifications, and the submission it will evaluate. Call
`load_configuration` to load `config.py` (or another named module) from
he current directory.

See `potluck.default_config` for a configuration file template; values
not specified in a custom config file will be pulled from this file.
"""

import sys
import os
import json
import shutil

from ._version import __version__
from . import logging
from . import file_utils
from . import load
from . import rubrics
from . import render
from . import contexts
from . import meta
from . import snippets


def load_configuration(config_module_name):
    """
    Loads a configuration module, backing up missing values from the
    default configuration.
    """

    import importlib

    # Import default config
    from . import default_config

    # Import named config file if it exists
    try:
        config = importlib.import_module(config_module_name)
    except Exception:
        config = None

    # Import attributes from default which are not present in custom:
    if config:
        already = set(dir(config))
        for attr in dir(default_config):
            if (
                attr not in already
            and (not attr.startswith("__") or not attr.endswith("__"))
            ):
                setattr(config, attr, getattr(default_config, attr))
    else: # otherwise use default by itself
        config = default_config

    return config


def generate_rubric(task_info, rubric_filename):
    """
    Generates a rubric for a single task, based on the task info and a
    filename to write to.

    Writes log messages using the logging sub-module, so redirect those
    beforehand if you wish.
    """
    logging.log(
        f"Generating rubric:\n"
        f"    task: {task_info['id']}\n"
        f"    output: {rubric_filename}"
    )

    # Ensure we've got a place to put our report
    os.makedirs(os.path.dirname(rubric_filename), exist_ok=True)

    # Given a Rubric, evaluate that Rubric in blank mode to produce a
    # report for a rubric HTML file.
    logging.log("Creating blank rubric...")
    evaluation = task_info["specification"].rubric.create_blank_report(
        task_info
    )

    # Now that we've got a rubric report, write it to the report file.
    logging.log(f"Rendering rubric to '{rubric_filename}'...")
    render.render_blank_rubric(evaluation, rubric_filename)
    logging.log("...done creating rubric.")
    return True


def generate_snippets(task_info, snippets_directory):
    """
    Generates HTML code for each snippet defined by a single task, based
    on the task info and a directory where snippet files should be
    created (these are .part.html files containing HTML code fragments).

    Writes log messages using the logging sub-module, so redirect those
    beforehand if you wish.
    """
    logging.log(
        f"Generating snippets:\n"
        f"    task: {task_info['id']}\n"
        f"    output directory: {snippets_directory}"
    )

    # Ensure we've got a place to put our snippets
    os.makedirs(snippets_directory, exist_ok=True)

    logging.log("Listing snippets...")
    registered = snippets.list_snippets(task_info)

    if len(registered) == 0:
        logging.log(
            "Warning: task specification has not defined any snippets."
        )
    else:
        # We iterate through and compile each snippet
        logging.log("Compiling snippets...")
        for sid in registered:
            # Compile snippet
            logging.log("  Compiling snippet '{}'...".format(sid))
            markup = snippets.get_html(task_info, sid)

            # Identify output file
            target = os.path.join(snippets_directory, sid) + ".part.html"
            logging.log(
                "  Writing snippet '{}' into '{}'...".format(sid, target)
            )

            # Write to file
            with open(target, 'w', encoding="utf-8") as fout:
                fout.write(markup)

    logging.log("...done compiling snippets.")
    return True


def generate_instructions(
    task_info,
    output_directory,
    resources_dirname="resources",
    refresh_resources=True
):
    """
    Generates HTML code for the instructions of a single task, based
    on the task info and a file name where the result should be written.

    Writes log messages using the logging sub-module, so redirect those
    beforehand if you wish.

    Unless refresh_resources is set to False, any resources folder in
    the given output directory will be deleted. In that case (or if it
    didn't exist) resources from the specifications directory will be
    copied to the output directory.
    """
    logging.log(
        f"Generating instructions:\n"
        f"    task: {task_info['id']}\n"
        f"    output directory: {output_directory}\n"
        f"    resources directory name: {resources_dirname}\n"
        f"    refresh resources? {refresh_resources}"
    )

    # Ensure we've got a place to put our result
    os.makedirs(output_directory, exist_ok=True)

    # Grab the specification module
    spec = task_info["specification"]

    # Copy resources
    logging.log("Checking for resource files...")
    res_dst = os.path.join(output_directory, resources_dirname)
    res_src = os.path.join(spec.base_path, resources_dirname)
    if os.path.exists(res_src): # only if there is a source directory
        if os.path.exists(res_dst): # does destination already exist?
            if refresh_resources:
                logging.log(
                    f"Removing presumed-stale resources '{res_dst}'..."
                )
                shutil.rmtree(res_dst)
                copy_resources = True
            # else we'll leave destination as-is, although it might be
            # out-of-date
        else:
            copy_resources = True

        if copy_resources:
            logging.log(
                f"Copying resource files from '{res_src}' to"
                f" '{res_dst}'..."
            )
            shutil.copytree(res_src, res_dst)
            logging.log("...done copying resource files.")
        else:
            logging.log("...skipped copying resource files.")
    else:
        logging.log("...specification has no resource files.")

    # Target filename
    output_file = os.path.join(output_directory, "index.html")

    # Fetch markdown
    logging.log("Fetching markdown instructions...")
    src = os.path.join(spec.base_path, "instructions.md")
    if os.path.exists(src):
        with open(src, 'r', encoding="utf-8") as fin:
            instructions = fin.read()
        logging.log(f"Fetched instructions from '{src}'...")
    elif spec.__doc__:
        # Pull from spec docstring if there's no instructions.md file
        instructions = spec.__doc__
        logging.log(
            "Fetched instructions from spec module's docstring..."
        )
    else:
        logging.log("Couldn't find any instructions...")
        instructions = "(no instructions available)"

    # Render rubric
    logging.log("Rendering rubric...")
    rubric_table = spec.rubric.create_blank_report(task_info)

    # Collect snippets
    logging.log("Collecting snippets...")
    registered = snippets.list_snippets(task_info)
    snippet_markup = []
    for sid in registered:
        snippet_markup.append(snippets.get_html(task_info, sid))

    # Render instructions text
    logging.log(f"Rendering instructions to '{output_file}'...")
    render.render_instructions(
        task_info,
        instructions,
        rubric_table,
        snippet_markup,
        output_file
    )

    logging.log("...done rendering instructions.")
    return True


def test_specification(task_info, examples_dir):
    """
    Tests the specification for a single task, based on the task info
    and a directory where test submissions should be found.

    Writes log messages using the logging sub-module, so redirect those
    beforehand if you wish.

    Exits with exit code 1 if any specification tests fail.
    """
    logging.log(
        f"Testing specification:\n"
        f"    task: {task_info['id']}"
        f"    examples_dir: {examples_dir}"
    )

    spec = task_info["specification"]

    any_failed = False

    by_user = meta.get_expectations(spec)
    if len(by_user) == 0:
        logging.log(
            "No explicit expectations; only testing solution code."
        )
    else:
        total = sum(len(exp) for exp in by_user.values())
        logging.log(
            f"Found {total} expectation(s) for {len(by_user)} example"
            f" submission(s)."
        )
        failed = []
        for username in by_user:
            # Resolve which file we're targeting
            user_folder = os.path.join(
                examples_dir,
                username
            )
            task_folder = os.path.join(user_folder, task_info["id"])
            submission_target = os.path.join(
                task_folder,
                task_info["target"]
            )

            # Retrieve expectations list
            expectations = by_user[username]
            logging.log(f"Checking expectations for '{username}'...")
            # Evaluate our rubric against the example submission
            evaluation = spec.rubric.evaluate(
                task_info,
                username,
                submission_target
            )
            # Check the resulting report
            passed, expl = meta.check_entire_report(evaluation, expectations)
            # Log the resulting explanation
            logging.log(expl)
            status = "passed"
            if not passed:
                status = "FAILED"
                failed.append(username)
                any_failed = True
                # Render failed report for inspection
                if os.path.isdir("reports"):
                    cfdir = os.path.join("reports", "__checks__")
                    os.makedirs(cfdir, exist_ok=True)
                    fnbase = os.path.join(
                        cfdir,
                        f"{task_info['id']}-{username}"
                    )
                    render.render_report(
                        evaluation,
                        fnbase + ".json",
                        fnbase + ".html",
                    )
                    logging.log(f"Wrote report to '{fnbase}.html'")
            logging.log(f"...done checking '{username}' ({status}).")
        if len(failed) > 0:
            logging.log(f"{len(failed)}/{len(by_user)} examples failed.")
        else:
            logging.log("All examples met expectations.")

    logging.log("Checking solution code...")
    soln_file = os.path.join(
        os.path.dirname(spec.__file__),
        "soln",
        task_info["target"]
    )
    soln_evaluation = spec.rubric.evaluate(
        task_info,
        "__soln__",
        soln_file
    )
    # Check just defaults for solution report
    passed, expl = meta.check_entire_report(soln_evaluation, [])
    status = "passed"
    if not passed:
        status = "FAILED"
        any_failed = True
        # Render failed report for inspection
        if os.path.isdir("reports"):
            cfdir = os.path.join("reports", "__checks__")
            os.makedirs(cfdir, exist_ok=True)
            fnbase = os.path.join(
                cfdir,
                f"{task_info['id']}-__soln__"
            )
            render.render_report(
                soln_evaluation,
                fnbase + ".json",
                fnbase + ".html",
            )
            logging.log(f"Wrote report to '{fnbase}.html'")
    logging.log(expl)
    logging.log(f"Check of solution code {status}.")

    logging.log("...done checking expectations.")

    if any_failed:
        logging.log("Halting due to failed expectations.")
        return False
    else:
        return True


def evaluate_submission(
    task_info,
    username,
    user_folder,
    report_filename,
    report_html_filename,
    target_file=None,
    clean=False
):
    """
    Evaluates a single submission, based on a task info (specifies the
    rubric to load), a username (who submitted the task?), and a
    target file (either a filename or directory for the submission
    to be evaluated, or None to determine this automatically from the
    provided configuration). Creates/overwrites the given report file.

    Writes log messages using the logging sub-module, so redirect those
    beforehand if you wish.

    If clean is given and set to True, normally cached info will be
    re-generated instead of used as-is. Useful when e.g., solutions
    change requiring re-generating solution images.
    """
    logging.log(
        f"Evaluating submission:\n"
        f"    task: {task_info['id']}\n"
        f"    user: {username}\n"
        f"    file: {target_file}\n"
        f"    report: {report_filename}\n"
        f"    html_report: {report_html_filename}"
    )

    # Figure out the submission file for this user
    if target_file is not None: # explicit
        submission_target = target_file
        user_folder = None
        task_folder = None
        logging.log(
            f"Submission is (explicit): {submission_target}"
        )
    else: # implicit from task/user
        task_folder = os.path.join(user_folder, task_info["id"])

        submission_target = os.path.join(
            task_folder,
            task_info["target"]
        )

        logging.log(
            f"Submission is (implicit): {submission_target}"
        )

    # Fatal error if the submission file/directory doesn't exist
    if not os.path.exists(submission_target):
        logging.log(
            f"Fatal error: Submission file (or folder)"
            f" '{submission_target}' does not exist"
        )

        # Log more info on which directories don't exist
        if user_folder and not os.path.isdir(user_folder):
            logging.log(f"    No user folder {user_folder}")

        if task_folder and not os.path.isdir(task_folder):
            logging.log(f"    No task folder {task_folder}")

        exit(1) # Cannot proceed

    if clean:
        logging.log("    (ignoring cached data)")
        # TODO: Something with this!!!

    # Given a submission to evaluate and a Rubric, evaluate that Rubric
    # in the context of the submission. This produces a report with
    # 'taskid', 'username', 'evaluation', 'warnings', 'summary', 'table',
    # and 'context' keys (see rubrics.Rubric.evaluate).
    logging.log("Evaluating rubric...")
    evaluation = task_info["specification"].rubric.evaluate(
        task_info,
        username,
        submission_target
    )

    # Now that we've got a rubric report, write it to the report file.
    logging.log(
        f"Rendering report to '{report_filename}' and"
        f" '{report_html_filename}'..."
    )
    render.render_report(
        evaluation,
        report_filename,
        report_html_filename
    )
    logging.log("...done evaluating submission.")
    return True


def setup(config, specs_dir=None, templates_dir=None, resources_dir=None):
    """
    Performs common setup tasks. Requires a configuration object (see
    `load_configuration`). Supplies defaults for specifications,
    templates, and resources directories if they're not explicitly
    provided.

    This must be called before any of the launch_ functions are run.
    """
    # Set specs directory for evaluate.py
    if specs_dir is None:
        specs_dir = os.path.join(config.BASE_DIR, "specs")

    load.set_specs_dir(specs_dir)

    # Set up reports system based on templates and resources directories
    # from config
    if templates_dir is None and config.TEMPLATES_DIRECTORY is not None:
        templates_dir = os.path.join(
            file_utils.potluck_src_dir(),
            config.TEMPLATES_DIRECTORY
        )

    if resources_dir is None and config.RESOURCES_DIRECTORY is not None:
        resources_dir = os.path.join(
            file_utils.potluck_src_dir(),
            config.RESOURCES_DIRECTORY
        )

    render.setup(templates_dir, resources_dir)


def launch_job(job, args, config, taskid, log_file=None):
    """
    Common setup code for launchers. Sets up logging and loads task
    info. Runs the given job function with a task_info object followed
    by the given arguments tuple. Based on its return value (True for
    success; anything else for failure) logs a final completion or
    failure message.
    """
    # Ensure logging directory exists if we're logging to a file
    if log_file is not None:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Note: all other actions will happen with log file open
    if log_file:
        log_out = open(log_file, 'w', encoding="utf-8")
    else:
        log_out = sys.stdout

    logging.set_log_target(log_out)

    # From here on out, we want to log either a completion message or
    # an error message at the end no matter what, and we need to close
    # the log file if we're not using sys.stdout
    done = False
    try:
        logging.log(f"This is potluck version {__version__}")

        # Load task meta-data
        task_info_file = os.path.join(
            config.BASE_DIR,
            config.TASKS_FILENAME
        )
        logging.log(
            f"Loading task metadata from '{task_info_file}'..."
        )
        with open(task_info_file, 'r') as fin:
            tasks_data = json.load(fin)

        if taskid not in tasks_data["tasks"]:
            logging.log(
                f"Fatal error: Task '{taskid}' does not exist in"
                f" task info file '{task_info_file}'"
            )
            exit(1)

        task_info = tasks_data["tasks"][taskid]
        task_info["id"] = taskid

        # Load the task spec. This results in a task-specification
        # module, which should define a 'rubric' variable.
        contexts.AutoContext.reset(task_info["target"])
        spec = load.load_task_spec(task_info)
        # Attach the loaded spec back into the task info
        task_info["specification"] = spec

        if (
            not hasattr(spec, "rubric")
         or not isinstance(spec.rubric, rubrics.Rubric)
        ):
            logging.log(
                "Fatal error: task specification has no 'rubric'"
                " attribute, or 'rubric' value is not a Rubric."
            )
            exit(1)

        # Run the specified job & check return value
        if job(task_info, *args):
            done = True

    finally: # log our completion or error message
        # Write a final message to our log
        if done:
            logging.log(render.DONE_MSG)
        else:
            logging.log(render.ERROR_MSG)

        # Close our log file
        if log_file:
            log_out.close()

    # Prevent further tasks from starting
    if not done:
        exit(1)


def launch_rubric_generation(
    config,
    taskid,
    log_file=None,
    rubric_filename=None,
):
    """
    Generates a blank rubric for a task, without needing a submission.
    """

    rubrics_dir = os.path.join(
        config.BASE_DIR,
        config.RUBRICS_DIRECTORY
    )

    if rubric_filename is None:
        rubric_filename = os.path.join(
            rubrics_dir,
            f"rubric-{taskid}.html"
        )

    logging.log(f"Generating blank rubric for {taskid}...")

    # Set up and launch
    launch_job(
        generate_rubric,
        (rubric_filename,),
        config,
        taskid,
        log_file
    )


def launch_snippet_generation(
    config,
    taskid,
    log_file=None,
    snippets_directory=None,
):
    """
    Generates the snippet HTML fragment files for a task, without
    needing a submission.
    """
    logging.log("Finding snippets directory...")

    snippets_base = os.path.join(
        config.BASE_DIR,
        config.SNIPPETS_DIRECTORY
    )

    if snippets_directory is None:
        snippets_directory = os.path.join(snippets_base, taskid)

    if (
        os.path.exists(snippets_directory)
    and not os.path.isdir(snippets_directory)
    ):
        raise FileExistsError(
            (
                "Output directory '{}' already exists, and it's"
                " not a directory!"
            ).format(snippets_directory)
        )

    logging.log(f"Generating snippets for {taskid}...")
    # Set up and launch
    launch_job(
        generate_snippets,
        (snippets_directory,),
        config,
        taskid,
        log_file
    )


def launch_instruction_generation(
    config,
    taskid,
    log_file=None,
    output_directory=None,
    refresh_resources=True
):
    """
    Generates the instructions HTML file for a task, without needing a
    submission. Also copies resources from the task spec directory into
    the instructions directory for the task.

    If refresh_resources is set to False, resources from the
    specifications folder will not be copied to the instructions folder
    if a resources folder already exists there. Otherwise, any existing
    resources folder in the instructions folder will be deleted and
    resources will be re-copied from the specifications folder.
    """
    logging.log("Finding instructions directory...")

    # Default for output directory
    if output_directory is None:
        instructions_base = os.path.join(
            config.BASE_DIR,
            config.INSTRUCTIONS_DIRECTORY
        )
        output_directory = os.path.join(instructions_base, taskid)

    # Check output directory is available
    if (
        os.path.exists(output_directory)
    and not os.path.isdir(output_directory)
    ):
        raise FileExistsError(
            (
                "Output directory '{}' already exists, and it's"
                " not a directory!"
            ).format(output_directory)
        )

    logging.log(f"Generating instructions for {taskid}...")
    # Set up and launch
    launch_job(
        generate_instructions,
        (
            output_directory,
            config.INSTRUCTION_RESOURCES_DIRNAME,
            refresh_resources
        ),
        config,
        taskid,
        log_file
    )


def launch_specifications_test(
    config,
    taskid,
    log_file=None
):
    """
    Loads a specification and checks any `potluck.meta.Expectation`s
    defined there. Note that corresponding test submissions must already
    be present in the evaluation directory.

    Test results are written to the log, which by default is simply
    printed to stdout; no files are produced (unless logging is directed
    to a file).
    """
    logging.log(f"Testing specification for {taskid}...")
    # Use config to determine directory where submissions live
    examples_dir = os.path.join(
        config.BASE_DIR,
        config.EXAMPLES_DIR
    )

    # Set up and launch
    launch_job(
        test_specification,
        (examples_dir,),
        config,
        taskid,
        log_file
    )


def launch_evaluation(
    config,
    taskid,
    username,
    log_file=None,
    target_file=None,
    report_filename=None
):
    """
    Evaluates a submitted task, generating a report file.
    """
    if username is None:
        print("Error: A username is required for task evaluation.")
        exit(1)

    logging.log(f"Evaluating {taskid} for user {username}...")

    # Figure out user folder
    user_folder = os.path.join(
        config.BASE_DIR,
        config.SUBMISSIONS_DIR,
        username
    )

    # Find report directory for this user
    report_dir = os.path.join(
        config.BASE_DIR,
        config.REPORTS_DIR,
        username
    )

    # Ensure per-user report directory exists
    os.makedirs(report_dir, exist_ok=True)

    if report_filename is None:
        timestamp = file_utils.timestamp()
        report_filename = os.path.join(
            report_dir,
            f"{taskid}_{timestamp}.json"
        )
        report_html_filename = os.path.join(
            report_dir,
            f"{taskid}_{timestamp}.html"
        )
    else:
        report_html_filename = (
            os.path.splitext(report_filename)[0] + '.html'
        )

    # Set up and launch
    launch_job(
        evaluate_submission,
        (
            username,
            user_folder,
            report_filename,
            report_html_filename,
            target_file,
        ),
        config,
        taskid,
        log_file
    )
