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

from ._version import __version__
from . import logging
from . import file_utils
from . import load
from . import rubrics
from . import report
from . import contexts
from . import meta


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

    # Load the task spec. This results in a task-specification module,
    # which must have a 'rubric' property that holds a Rubric object.
    contexts.AutoContext.reset(task_info["target"])
    spec = load.load_task_spec(task_info)
    # Attach the loaded spec back into the task info
    task_info["specification"] = spec
    if (
        not hasattr(spec, "rubric")
     or not isinstance(spec.rubric, rubrics.Rubric)
    ):
        logging.log(
            "Fatal error: task specification has no 'rubric' attribute,"
            "or 'rubric' value is not a Rubric."
        )
        sys.exit(1)

    # Given a Rubric, evaluate that Rubric in blank mode to produce a
    # report for a rubric HTML file.
    logging.log("Creating blank rubric...")
    evaluation = spec.rubric.create_blank_report(task_info)

    # Now that we've got a rubric report, write it to the report file.
    logging.log(f"Rendering rubric to '{rubric_filename}'...")
    report.render_blank_rubric(evaluation, rubric_filename)
    logging.log("...done creating rubric.")


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

    # Load the task spec. This results in a task-specification module,
    # which hopefully establishes expectations that accumulate in
    # `potluck.meta.EXPECTATIONS`.
    contexts.AutoContext.reset(task_info["target"])
    spec = load.load_task_spec(task_info)
    # Attach the loaded spec back into the task info
    task_info["specification"] = spec
    if (
        not hasattr(spec, "rubric")
     or not isinstance(spec.rubric, rubrics.Rubric)
    ):
        logging.log(
            "Fatal error: task specification has no 'rubric' attribute,"
            "or 'rubric' value is not a Rubric."
        )
        sys.exit(1)

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
                    report.render_report(
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
            report.render_report(
                soln_evaluation,
                fnbase + ".json",
                fnbase + ".html",
            )
            logging.log(f"Wrote report to '{fnbase}.html'")
    logging.log(expl)
    logging.log(f"Check of solution code {status}.")

    logging.log("...done checking expectations.")

    if any_failed:
        logging.log("Exiting due to failed expectations.")
        sys.exit(1)


def evaluate_submission(
    task_info,
    username,
    submission_target,
    report_filename,
    report_html_filename,
    clean=False
):
    """
    Evaluates a single submission, based on a task info (specifies the
    rubric to load), a username (who submitted the task?), and a
    submission target (either a filename or directory for the submission
    to be evaluated). Creates/overwrites the given report file.

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
        f"    file: {submission_target}\n"
        f"    report: {report_filename}\n"
        f"    html_report: {report_html_filename}"
    )

    if clean:
        logging.log("    (ignoring cached data)")
        # TODO: Something with this!!!

    # Load the task spec. This results in a task-specification module,
    # which must have a 'rubric' property that holds a Rubric object.
    contexts.AutoContext.reset(task_info["target"])
    # TODO: will this really match what a naive user supplies for an
    # explicit FileContext?
    spec = load.load_task_spec(task_info)
    # Attach the loaded spec back into the task info
    task_info["specification"] = spec
    if (
        not hasattr(spec, "rubric")
     or not isinstance(spec.rubric, rubrics.Rubric)
    ):
        logging.log(
            "Fatal error: task specification has no 'rubric' attribute,"
            "or 'rubric' value is not a Rubric."
        )
        sys.exit(1)

    # Given a submission to evaluate and a Rubric, evaluate that Rubric
    # in the context of the submission. This produces a report with
    # 'taskid', 'username', 'evaluation', 'warnings', 'summary', 'table',
    # and 'context' keys (see rubrics.Rubric.evaluate).
    logging.log("Evaluating rubric...")
    evaluation = spec.rubric.evaluate(
        task_info,
        username,
        submission_target
    )

    # Now that we've got a rubric report, write it to the report file.
    logging.log(
        f"Rendering report to '{report_filename}' and"
        f" '{report_html_filename}'..."
    )
    report.render_report(
        evaluation,
        report_filename,
        report_html_filename
    )
    logging.log("...done evaluating submission.")


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

    report.setup(templates_dir, resources_dir)


def launch_rubric_generation(
    config,
    taskid,
    log_file=None,
    rubric_filename=None,
):
    """
    Generates a blank rubric for a task, without needing a submission.
    """
    # Ensure logging directory exists if we're logging to a file
    if log_file is not None:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Note: all other actions will happen with log file open
    with open(log_file, 'w') if log_file else sys.stdout as lout:
        logging.set_log_target(lout)

        # From here on out, we want to log either a completion message or
        # an error message at the end no matter what
        done = False
        try:
            logging.log(f"This is potluck version {__version__}")
            logging.log(f"Generating blank rubric for {taskid}...")

            # Load task meta-data
            task_info_file = os.path.join(
                config.BASE_DIR,
                config.TASKS_FILENAME
            )
            with open(task_info_file, 'r') as fin:
                tasks_data = json.load(fin)

            if taskid not in tasks_data["tasks"]:
                logging.log(
                    f"Fatal error: Task '{taskid}' does not exist in"
                    f" task info file '{task_info_file}'"
                )
                sys.exit(1)

            task_info = tasks_data["tasks"][taskid]
            task_info["id"] = taskid

            rubrics_dir = os.path.join(
                config.BASE_DIR,
                config.RUBRICS_DIRECTORY
            )

            if rubric_filename is None:
                rubric_filename = os.path.join(
                    rubrics_dir,
                    f"rubric-{taskid}.html"
                )

            generate_rubric(task_info, rubric_filename)
            logging.log("...rubric generation complete.")
            done = True
            # Now we're done

        finally: # log our completion or error message
            if done:
                logging.log(report.DONE_MSG)
            else:
                logging.log(report.ERROR_MSG)


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
    # Ensure logging directory exists if we're logging to a file
    if log_file is not None:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Note: all other actions will happen with log file open
    with (open(log_file, 'w') if log_file else sys.stdout) as lout:
        logging.set_log_target(lout)

        # From here on out, we want to log either a completion message or
        # an error message at the end no matter what
        done = False
        try:
            logging.log(f"This is potluck version {__version__}")
            logging.log(f"Testing specification for {taskid}...")

            # Load task meta-data
            task_info_file = os.path.join(
                config.BASE_DIR,
                config.TASKS_FILENAME
            )
            with open(task_info_file, 'r') as fin:
                tasks_data = json.load(fin)

            if taskid not in tasks_data["tasks"]:
                logging.log(
                    f"Fatal error: Task '{taskid}' does not exist in"
                    f" task info file '{task_info_file}'"
                )
                sys.exit(1)

            task_info = tasks_data["tasks"][taskid]
            task_info["id"] = taskid

            # Use config to determine directory where submissions live
            examples_dir = os.path.join(
                config.BASE_DIR,
                config.EXAMPLES_DIR
            )

            test_specification(task_info, examples_dir)
            logging.log("...specification test complete.")
            done = True
            # Now we're done

        finally: # log our completion or error message
            if done:
                logging.log(report.DONE_MSG)
            else:
                logging.log(report.ERROR_MSG)


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
        print("Error: A username is required unless --rubric is used.")
        exit(1)

    # Ensure logging directory exists if we're logging to a file
    if log_file is not None:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Note: all other actions will happen with log file open
    with open(log_file, 'w') if log_file else sys.stdout as lout:
        logging.set_log_target(lout)

        # No matter what happens from here on out, we want to log an
        # error message if things don't go well
        done = False
        try:
            logging.log(f"This is potluck version {__version__}")
            logging.log(f"Evaluating {taskid} for user {username}...")

            # Load task meta-data
            task_info_file = os.path.join(
                config.BASE_DIR,
                config.TASKS_FILENAME
            )
            with open(task_info_file, 'r') as fin:
                tasks_data = json.load(fin)

            if taskid not in tasks_data["tasks"]:
                logging.log(
                    f"Fatal error: Task '{taskid}' does not exist in"
                    f" task info file '{task_info_file}'"
                )
                sys.exit(1)

            task_info = tasks_data["tasks"][taskid]
            task_info["id"] = taskid

            # Figure out the submission file for this user
            if target_file is not None: # explicit
                submission_target = target_file
                user_folder = None
                task_folder = None
                logging.log(
                    f"Submission is (explicit): {submission_target}"
                )
            else: # implicit from task/user
                user_folder = os.path.join(
                    config.BASE_DIR,
                    config.SUBMISSIONS_DIR,
                    username
                )

                task_folder = os.path.join(user_folder, taskid)

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

                sys.exit(1) # Cannot proceed

            # Evaluate the task for this user, generating a report file
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

            evaluate_submission(
                task_info,
                username,
                submission_target,
                report_filename,
                report_html_filename
            )
            logging.log("...evaluation complete.")
            done = True
            # Now we're done
        finally:
            if done:
                logging.log(report.DONE_MSG)
            else:
                logging.log(report.ERROR_MSG)
