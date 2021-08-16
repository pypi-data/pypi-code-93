"""
Package for defining and evaluating Python programming tasks.

potluck/__init__.py

For a high-level interface, import `potluck.compare`. To define a task
specification, import `potluck.specifications`. To define tests for a
specification, import `potluck.meta`.

Dependencies:

- `jinja2` for report rendering via HTML templates.
- `pygments` for code highlighting in reports.
- `importlib_resources` for resource loading.

Unless you want to get into the guts of things, `potluck.specifications`
is the place to get started, while `potluck.rubrics` and
`potluck.contexts` deal with more advanced concepts without getting too
far into the weeds. There are however many sub-modules that take care of
the complicated evaluation process:

- `potluck.compare`: Compares values and describes differences.
- `potluck.context_utils`: Utilities used by contexts and also elsewhere.
- `potluck.contexts`: Caching and dependencies for test results.
- `potluck.control`: High-level interface for core capabilities.
- `potluck.default_config`: Default configuration values.
- `potluck.explain`: Turns errors and test results into
  novice-readable English explanations.
- `potluck.file_utils`: Utility functions for dealing with files.
- `potluck.harness`: Tests code within specific contexts and records
  the resulting processes, values, and/or outputs.
- `potluck.html_tools`: Tools for dealing with HTML.
- `potluck.load`: Loads specifications and submitted and/or solution code.
- `potluck.logging`: Manages logging of the evaluation process.
- `potluck.mast`: AST matching, courtesy Ben Wood.
- `potluck.mast_utils`: Utilities used for AST matching.
- `potluck.meta`: Meta-testing for checking your specifications.
- `potluck.patterns`: Common patterns for AST matching.
- `potluck.phrasing`: Low-level language functions for generating
  English feedback (e.g., pluralization).
- `potluck.report`: Generates and saves task reports as HTML.
- `potluck.rubrics`: Core classes for defining rubrics.
- `potluck.specifications`: Defines + loads task specifications.
- `potluck.timeout`: Running functions w/ a time limit.

Note that overall `potluck` requires Python 3.6 or later, but the
following modules are compatible with Python 2.7:

- `potluck.report`
- `potluck.html_tools`
- `potluck.phrasing`
- `potluck.file_utils`
- `potluck.logging`

For automatically collecting and evaluating submissions using `potluck`,
a Flask WSGI server is available in the `potluck_server` module.
"""

# Import version variable
from ._version import __version__ # noqa F401
