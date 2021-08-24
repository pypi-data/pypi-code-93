import argparse
import collections
import importlib
import json
import re
import sys
from argparse import Namespace
from doctest import DocTestFinder
from os import mkdir, path
from textwrap import dedent
from typing import TYPE_CHECKING, AnyStr, List, Optional

from jinja2 import Template
from jinja2.filters import FILTERS, environmentfilter

from ruleau.context_manager import mock_context

if TYPE_CHECKING:
    from ruleau.rule import Rule
    from ruleau.types import Function

PARAM_REGEX_PATTERN = ":(?P<name>[\*\s\w]+): (?P<description>.*?)\Z"  # noqa: W605


@environmentfilter
def json_print(_, value):
    """Pretty print json filter for jinja2"""
    value = value if isinstance(value, dict) or value is None else json.loads(value)
    return json.dumps(
        value,
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    )


@environmentfilter
def filter_runif_dependencies(_, dependencies):
    return [dep for dep in dependencies if dep["run_if"]]


@environmentfilter
def filter_non_runif_dependencies(_, dependencies):
    return [dep for dep in dependencies if not dep["run_if"]]


#  Add the json_print filter to jinja2 filters
FILTERS["json_print"] = json_print
FILTERS["filter_runif"] = filter_runif_dependencies
FILTERS["filter_non_runif"] = filter_non_runif_dependencies


def trim(docstring):
    """trim function implementation from PEP-257
    https://www.python.org/dev/peps/pep-0257/#id18

    :param docstring: Docstring for a function
    """
    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:  # pragma: no cover
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)

    if "\n" in docstring:
        trimmed.append("")
    # Return a single string:
    return "\n".join(trimmed)


def remove_suffix(source, suffix):
    """Removes suffix from a source string.
    :param source: String to remove suffix from
    :param suffix: Suffix to remove from the given string
    :return: a string with suffix removed
    """
    if source.endswith(suffix):
        return source[: -len(suffix)]
    else:
        return source


def description(docstring: AnyStr) -> AnyStr:
    """Takes a rule docstring, and returns just the lines
    representing a description

    :param docstring: Docstring for a function
    """
    result = trim(docstring or "")
    lines = result.split("\n")
    end_of_description_idx = next(
        (
            idx
            for idx, line in enumerate(lines)
            if any(
                [
                    # Line is empty i.e. new line after description
                    line == "" or line.isspace(),
                    # Line is the start of a doc string parameter
                    re.match(PARAM_REGEX_PATTERN, line),
                    # Line is the start of a doc test
                    line.startswith(">>>"),
                ]
            )
        ),
        # If no end to the description then it ends with the string
        len(lines),
    )

    description_ = "\n".join(lines[:end_of_description_idx])
    # Remove final new line character if present
    return remove_suffix(description_, "\n")


def parameters(docstring: AnyStr):
    """Parse list of parameters out of the docstring

    :param docstring: The docstring of the rule
    :returns: [{"name": ..., "description": ...}, ...]
    """
    param_regex = re.compile(PARAM_REGEX_PATTERN)

    params = []
    if docstring:
        lines = docstring.split("\n")
        for line in lines:
            match = param_regex.findall(line.strip())
            if match:
                param_name, param_description = match[0]
                params.append({"name": param_name, "value": param_description})

    return params


def comments(source: AnyStr) -> AnyStr:
    """Returns single line comments from provided source

    :param source: clean source (output of clean_source)
    :returns: returns single line comments from source code
    """
    output_lines = [
        line for line in source.splitlines() if line.strip().startswith("#")
    ]
    return "\n".join(output_lines)


def get_doctest_rule_args(func: "Function", source: str, globs=None):
    """Given a rule function and the source, extract the arguments used when
    calling the rule in the given source.

    :param func: The rule function
    :param source: The source that calls the function
    :param globs: Globals for the rule execution
    """

    context = None
    payload = None

    #  Mock for rule function
    def mock_func(*args, **_):
        nonlocal context
        nonlocal payload
        #  We dont return early as the arguments for the final call of the
        # function should be used
        context, payload = args

    # Execute the function with the mocked rule
    mocks = {func.__name__: mock_func, "mock_context": mock_context}
    globs = globs or {}
    globs = {**globs, **mocks}
    exec(source, globs)

    # Return the context and payload used in the final call of the rule function
    return context, payload


def get_index_of_closing_bracket(source):
    """Returns index of closing bracket
    :param: source starting with opening bracket
    :returns: returns the index of the closing bracket that matches the opening
    bracket
    """
    # Create a deque to use it as a stack.
    queue = collections.deque()

    for i in range(len(source)):
        # Pop a starting bracket
        # for every closing bracket
        if source[i] == ")":
            queue.popleft()

        # Push all starting brackets
        elif source[i] == "(":
            queue.append(source[i])

        # If deque becomes empty
        if not queue:
            return i

    return None


def remove_prefix(source, prefix):
    """Removes prefix from a string source.
    :param source: String to remove prefix from
    :param prefix: Prefix to remove from the given string
    :return: a string with prefix removed
    """
    if source.startswith(prefix):
        return source[len(prefix) :]  # noqa: E203
    else:
        return source


def source_is_example(source, function_name):

    # Remove function name
    source = source.strip()
    if not source.startswith(function_name):
        return False
    source = remove_prefix(source, function_name)
    source = source.strip()

    # Check after function name we find (
    if not source.startswith("("):
        return False

    # Find closing bracket of example
    closing_bracket_index = get_index_of_closing_bracket(source)
    if closing_bracket_index is None:
        return False

    #  If more happens after the call to the function
    if not source[closing_bracket_index:].strip() == ")":
        return False

    return True


def doctests(func: "Function") -> List[dict]:
    """Extract the doctest from a rule
    :param func: Function wrapped in a Rule instance
    :return: List of doctest examples
    """

    doctests = []
    finder = DocTestFinder(verbose=False, recurse=False)
    #  For each test
    for tests in finder.find(func):
        # Collect the source code up to the first result is expected
        source = ""
        for example in tests.examples:
            source = source + example.source

            # Once a result is expected run the source and extract the provided
            # values.
            if example.want.strip() != "":
                if source_is_example(example.source, func.__name__):
                    context, payload = get_doctest_rule_args(func, source, tests.globs)
                    doctests.append(
                        {
                            "test": source,
                            "result": example.want,
                            "context": json.dumps(context.parse()) if context else None,
                            "payload": json.dumps(payload),
                        }
                    )
                source = ""

    return doctests


def order_rules(rules: List["Rule"]) -> List["Rule"]:
    """Order rules so top level rules appear first"""
    is_root = {rule: True for rule in rules}

    # If any rule is dependent on a rule then it is not the root
    for rule in rules:
        for dependent in rules:
            if dependent != rule and dependent in rule.dependencies:
                is_root[dependent] = False

    roots = [rule for rule, is_root_rule in is_root.items() if is_root_rule]
    others = [rule for rule, is_root_rule in is_root.items() if not is_root_rule]
    return roots + others


def get_start_of_docstring(source_lines: List[AnyStr]) -> Optional[int]:
    """Get the index of line on which the doc string starts.

    :param source_lines: A list of the lines of the source of the function
    without the header or decorators
    """
    # Loop to find the start of the doc string
    for idx, line in enumerate(source_lines):

        # Skip any empty lines
        if line == "" or line.isspace():  # pragma: no cover
            # This is covered in the tests but no picked up by coverage
            continue

        # Find the start of the doc string
        if line.strip().startswith('"""'):
            return idx

        # If we find any non empty line that is not starting with """ then
        # there is no doc string for this function
        else:
            return None


def get_end_of_docstring(source_lines: List[AnyStr], start_idx=0) -> int:
    """Get the index of line on which the doc string ends.

    :param source_lines: A list of the lines of the source of the function
    without the header or decorators
    :param start_idx: The line on which the docstring starts

    :raise: Exception if no end of docstring found
    """
    for line_number, line in enumerate(source_lines[start_idx:]):  # pragma: no cover
        # A docstring cannot be started and not ended

        count = line.count('"""')  # Number of occurances of """ on line

        # If we are on the starting line (same as doc_string_start_idx) we
        # need to find 2 """ for the doc string to be closed.
        if (line_number == 0 and count == 2) or (line_number != 0 and count >= 1):
            return start_idx + line_number

    raise ValueError("No end of docstring found")


def clean_source(source: AnyStr) -> AnyStr:
    """Clean the source code.

    Remove all the lines until we have passed the decorators, function header
    and docstring.

    :param source: The source code to clean.
    """
    # Remove common indent
    source = dedent(source)

    # Get lines from source
    lines = source.split("\n")

    # Get line function header starts on. All function sources must have a header
    header_index = next(
        idx for idx, line in enumerate(lines) if line.startswith("def")
    )  # pragma: no cover

    # Remove anything above header from lines (decorators) and header it self
    lines = lines[header_index + 1 :]  # noqa: E203

    # Remove the docstring
    doc_string_start_idx = get_start_of_docstring(lines)

    # If we found a doc string
    if doc_string_start_idx is not None:
        doc_string_end_idx = get_end_of_docstring(lines, doc_string_start_idx)
        # Remove the doc string lines
        lines = lines[doc_string_end_idx + 1 :]  # noqa: E203

    clean_source_ = dedent("\n".join(lines))
    return clean_source_


def generate_documentation(rules: List["Rule"]) -> AnyStr:
    """Returns a HTML string, documenting the passed in rule and its dependents

    :param rules: List of rules to generate document of
    """
    with open(
        path.join(path.dirname(path.realpath(__file__)), "html", "documentation.html")
    ) as f:
        doc_template = Template(f.read())

    rules = order_rules(rules)
    enriched_rules = [rule.parse() for rule in rules]

    colors = {
        "light": "75FF96",
        "primary": "12C170",
        "dark": "17764A",
    }
    return doc_template.render(rules=enriched_rules, colors=colors)


def get_dependencies(rule: "Rule", rule_list: Optional[List] = None):
    """Recursively adds the rule dependencies to a list
    :param rule: The Rule to add dependencies for.
    :param: rule_list: An optional list of dependencies that
     are already known to exist.
    :return: rule_list: A list of Rule dependencies.
    """
    if rule_list is None:
        rule_list = []
    if rule not in rule_list:
        rule_list.append(rule)
    for dependency in rule.dependencies:
        get_dependencies(dependency, rule_list)
    return rule_list


def render_doc_for_module(module_file, top_level_rule) -> AnyStr:
    """Render the documentation from a rule module
    :param module_file:
    :param top_level_rule: The top level rule that is dependent on all other rules.
    :return:
    """
    spec = importlib.util.spec_from_file_location(module_file, module_file)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)

    # Pick rules to document
    rules = get_dependencies(getattr(config, top_level_rule))
    return generate_documentation(rules)


def generate_and_save_to_file(input_files, output_dir):
    """Generate the documentation and save to a file in provided output dir
    :param input_files: Rule modules and top level function names provided by
     user via CLI
    :param output_dir: Output directory of generated HTML file
    """

    generated_docs = []

    if len(input_files) == 0:
        raise Exception("No file(s) supplied to generate documentation for.")

    if not path.exists(output_dir):
        mkdir(output_dir)

    for target_file in input_files:
        if target_file.split("::") == [target_file]:
            raise ValueError(
                "Please provide a name of top level function. "
                f"Required format is {target_file}::function_name."
            )
        top_level_rule = target_file.split("::")[1]
        target_file = target_file.split("::")[0]
        if not path.exists(target_file):
            raise ValueError(f"{target_file} does not exist")

        documentation = render_doc_for_module(target_file, top_level_rule)

        output_filename = path.join(
            output_dir, "{}.html".format(path.basename(target_file).split(".")[0])
        )

        with open(output_filename, "w") as f:
            f.write(documentation)
        generated_docs.append(output_filename)

    print(
        f"{len(generated_docs)} doc{'s' if len(generated_docs) > 1 else ''} generated."
    )
    print("\n".join(generated_docs))


def get_arguments(args) -> Namespace:
    """Parses arguments for the ruleau-docs command
    :param args:
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default="./",
        help="Directory for generated documents",
    )
    parser.add_argument("files", nargs="*")
    return parser.parse_args(args)


def main() -> int:  # pragma: no cover
    """Console script for deft document generation.
    USAGE:
    ```bash
    $ ruleau-docs [--output-dir=<argument>] filename ...
    ```
    """
    args = get_arguments(sys.argv[1:])
    generate_and_save_to_file(args.files, args.output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
