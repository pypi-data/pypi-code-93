"""
Routines for checking whether specifications are correctly implemented
and working as intended.

meta.py
"""

import re

from . import file_utils


EXPECTATIONS = {}
"""
Global storage for expectations by spec module name and username.
"""

CURRENT_EXAMPLE = None
"""
Which username are expectations automatically registered for?
"""


def simplify(description):
    """
    Normalizes case and removes HTML tags from the given goal
    description, for use in expectation matching. Note that angle
    brackets which aren't used for HTML tags are assumed to already be
    escaped. Adds '^^^' at the start and '$$$' at the end so that rules
    can use those anchors (or part of them) for disambiguation.
    """
    stripped = re.sub(r"<[^>]*>", '', description)
    return '^^^' + stripped.casefold() + '$$$'


def categorized_goal_path(goal_type, category, *descriptions):
    """
    Returns a goal path list suitable for use with `Expectation` which
    starts by matching against a specific goal type grouping and then a
    category grouping, as would be present in a rubric that used the
    `potluck.rubrics.core_extras_categorized_metric`.

    Note: this isn't actually that complicated...
    """
    return [goal_type, category] + list(descriptions)


class Expectation:
    """
    An expectation establishes that a specific goal should evaluate to a
    specific result within a report. These expectations can be tested
    to make sure that a specification is working as designed.

    To specify which goal the expectation applies to, a list of strings
    is provided; each must uniquely match against an item in a report
    table at a specific level, with the next string matching against
    that row's sub-table, and so on. These matches are performed in a
    case-insensitive manner with HTML tags stripped out, against the
    primary obfuscated description entry for each goal/category. The
    specified string only has to match part of the goal description, but
    it must not match multiple goal descriptions at a given table level.
    The characters '^^^' are added to the beginning of the rubric string,
    and '$$$' to the end, to aid in disambiguation.

    Because of these matching rules, for a rubric where the standard
    metric `potluck.rubrics.core_extras_categorized_metric` is used,
    goal paths are usually straightforward to construct when default
    descriptions are in place. Some examples:

    - For a core FunctionDef Check for function 'foo':
       `[ "procedure", "core", "define foo" ]`

    - For an extra FunctionCall Check for 'bar' as a sub-rule of the
      check above:
       `[ "procedure", "extra", "define foo", "call bar" ]`

    - For a core trace test of function 'foo':
       `[ "process", "core", "the foo function must" ]`
    - (note that one could also use:)
       `[ "process", "core", "^the foo function must" ]`

    - For a core result value test of function 'foo':
       `[ "product", "core", "foo returns" ]`

    - For a core printed output test of function 'foo':
       `[ "behavior", "core", "foo prints" ]`
    """
    def __init__(self, goal_path, expected_status):
        """
        The goal_path is a list of strings specifying how to find the
        goal in a report (strings are matched against descriptions to
        find sub-tables). Finally, the expected evaluation result is
        required, which should be one of the strings used for goal
        statuses (see `potluck.rubrics.Goal`).

        Note that the precise goal_path an `Expectation` should have
        depends on the metric used and the details of how a
        `potluck.rubrics.Rubric` object formulates its overall report,
        because any top-level organizational report rows (e.g. for goal
        types or categories) need to be accounted for.

        For matching goals, the case-folded version of each goal_path
        entry is checked using 'in' against a case-folded version of each
        rubric entry at the relevant level. Exactly 1 rubric entry must
        match.  The rubric entries also have HTML tags stripped out, and
        have '^^^' added at the front and '$$$' at the end to aid in
        disambiguation.

        For example, if there are rubric entries named "Bug #1" and
        "Bug #11", an expectation for the "Bug #1" rubric entry could use
        "bug #1$" as its goal_path entry.
        """
        self.goal_path = goal_path
        self.expected_status = expected_status

    def check(self, report):
        """
        Checks whether this expectation is fulfilled in a given report.
        Returns a tuple containing:
            1. Either True or False indicating success or failure.
            2. A string description of why the check failed (or how it
               succeeded).
            3. A list of strings containing the full unmodified
               initial descriptions of each report table row on the path
               to the row that was checked. If the check failed because
               it could not find the row it was looking for, this will be
               None.
        """
        rows_here = report["table"]
        found = None
        trail = []

        # Match at each level of our goal path
        for match_key in self.goal_path:
            # Match against descriptions at this level
            matches_here = []
            for row in rows_here:
                match_against = simplify(row["description"][0])
                look_for = match_key.casefold()
                if look_for in match_against:
                    matches_here.append(row)

            # Check # of matching rows
            if len(matches_here) != 1: # zero or multiple matches
                if trail:
                    where = "In " + ' → '.join(trail)
                else:
                    where = "At the top level of the report"

                options = '\n'.join(
                    row['description'][0]
                    for row in rows_here
                )
                return (
                    False,
                    (
                        f"{where}, {len(matches_here)} goals matched"
                        f" '{match_key}'. Goals here are:\n{options}"
                    ),
                    None
                )
            else: # a single match, as required
                # Record the goal or other table row we found:
                found = matches_here[0]
                # Extend our trail
                trail.append(found["description"][0])
                # Enter next level of the table:
                rows_here = found["subtable"]

        # Strings for reporting our result
        where = "In " + ' → '.join(trail)

        # "found" should now be the matched goal's report row
        if found["status"] == self.expected_status:
            return (
                True,
                f"{where}, confirmed status '{self.expected_status}'.",
                trail
            )
        else:
            return (
                False,
                (
                    f"{where}, status '{found['status']}' did not match"
                    f" expected status '{self.expected_status}'."
                ),
                trail
            )


def check_entire_report(
    report,
    all_expectations,
    default_level=2,
    require_default="accomplished"
):
    """
    Given a report and a list of `Expectation` objects, this function
    checks each of the expectations within the provided report,
    returning a tuple containing True or False to indicate success or
    failure, as well as a multi-line string explaining which checks
    failed or that all checks succeeded.

    If require_default is provided, then all rubric rows in the report
    which don't have an explicit `Expectation` provided for them or a
    sub-row at the given default_level must match the require_default
    status. Set require_default to None (the default is 'accomplished')
    to leave non-explicitly-checked rows unchecked.
    """
    explanation = "Some checks failed:\n"
    coverage = {}
    succeeded = True
    for exp in all_expectations:
        success, expl, path = exp.check(report)
        if path is None:
            raise ValueError(
                "Unable to find expected goal:\n{}\n{}".format(
                    " → ".join(exp.goal_path),
                    expl
                )
            )
        c = coverage
        for entry in path:
            c = c.setdefault(entry, {})
        c[None] = True
        if not success:
            explanation += expl + '\n'
            succeeded = False

    default_count = 0
    if require_default is not None:
        def check_default_statuses(rows, covered, path):
            """
            Checks that the status of every row at a certain default
            level within the report hierarchy is equal to the required
            default status. Needs a list of rows at this level of the
            table, a dictionary of covered paths pertaining to this
            level of the table, and a list of strings indicating the
            path taken to get to this part of the table.

            Returns a tuple starting with True or False for success or
            failure, followed by a string describing the failure(s) or
            explaining the success.
            """
            nonlocal default_count, default_level, require_default
            passed = True
            explanation = ""
            level = len(path)
            if level == default_level: # Check each non-covered row
                for row in rows:
                    desc = row["description"][0]
                    if desc in covered and covered[desc].get(None, False):
                        continue # don't check this covered row
                    else:
                        default_count += 1
                        if row["status"] != require_default:
                            where = "In " + " → ".join(path + [desc])
                            explanation += (
                                f"{where} status '{row['status']}' did"
                                f" not match required default status"
                                f" '{require_default}'.\n"
                            )
                            passed = False
            else: # Recurse
                for row in rows:
                    desc = row["description"][0]
                    subtable = row["subtable"]
                    sub_success, sub_expl = check_default_statuses(
                        subtable,
                        covered.get(desc, {}),
                        path + [desc]
                    )
                    if not sub_success:
                        passed = False
                        explanation += sub_expl

            if passed:
                explanation = (
                    f"All non-expected statuses were"
                    f" '{require_default}'."
                )
            return passed, explanation

        default_success, default_expl = check_default_statuses(
            report["table"],
            coverage,
            path=[]
        )
        if not default_success:
            succeeded = False
            explanation += default_expl

    if succeeded:
        explanation = "All {} expectation(s){} were met.".format(
            len(all_expectations),
            (
                f" (plus {default_count} default expectation(s))"
                if default_count > 0
                else ""
            )
        )

    return (succeeded, explanation)


def example(username):
    """
    Registers a current username such that calls to expect create
    expectations for that example submission, and creates an entry in the
    expectations table for it so that even if no expectations are
    established it will still be tested using default expectations.
    """
    global CURRENT_EXAMPLE
    CURRENT_EXAMPLE = username
    mname = file_utils.get_spec_module_name()
    EXPECTATIONS\
        .setdefault(mname, {})\
        .setdefault(username, [])


def expect(status, goal_type, category, *path):
    """
    Creates an `Expectation` object and registers it under a given task
    ID and username. Arguments are:

    - status: The expected status. See `potluck.rubrics.Goal`.
    - taskid: The task ID this expectation applies to.
    - username: The username whose submission the expectation applies
        to (usually a fake user set up for testing purposes).
    - goal_type: The type of goal.
    - category: The goal category.
    - path: One or more additional strings specifying which goal we're
        targeting (see `Expectation`).
    """
    mname = file_utils.get_spec_module_name()
    EXPECTATIONS\
        .setdefault(mname, {})\
        .setdefault(CURRENT_EXAMPLE, [])\
        .append(
            Expectation(
                categorized_goal_path(goal_type, category, *path),
                status
            )
        )


def get_expectations(spec_module):
    """
    Returns all expectations for the given specification module, as a
    dictionary mapping user IDs to expectation lists.
    """
    return EXPECTATIONS.get(spec_module.__name__, {})
