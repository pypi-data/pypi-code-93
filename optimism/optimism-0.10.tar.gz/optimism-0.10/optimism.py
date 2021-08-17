# -*- coding: utf-8 -*-
"""
A very simple testing library intended for use by students in an intro
course. Includes capabilities for mocking input and setting up
expectations for the results and/or printed output of arbitrary
expressions.

optimism.py

## Example usage

```py
import optimism as opt

# Simple example function
def f(x, y):
    "Example function"
    return x + y + 1

# Simple test for that function
opt.testCase(f(1, 2)) # line 9
opt.expectResult(4)


# Function that prints multiple lines of output
def display(message):
    print("The message is:")
    print('-' + message + '-')

# One test case with two separate expectations
opt.captureOutput()
opt.testCase(display('hello')) # line 20
opt.expectOutputContains('The message')
opt.expectOutputContains('-hello-')


# A function that uses input
def askName():
    return input("What is your name? ")

opt.provideInput('''
Name
''')
opt.testCase(askName()) # line 32
opt.expectResult('Name')
# Note: output capturing remains active for subsequent tests
# Note: inputs don't show up in captured output
opt.expectOutputContains('What is your name?')
```

If we were to run this example file, we should see the following output
(other output that one would normally expect from the test function
calls is suppressed due to `captureOutput`).

```txt
✓ example.py:10
✓ example.py:21
✓ example.py:22
✓ example.py:33
✓ example.py:35
```

If an expectation is not met, the output would look different. For
example, if our first expectation had been 3 instead of 4, we'd see:

```txt
✗ example.py:10
  Result 4 was different from the expected value 3.
```

## Core functionality

The main functions you'll need are:

- `trace` works like `print`, but shows some extra information, and you
  can use it as part of a larger expression. Use this for figuring out
  what's going wrong when your expectations aren't met.
- `testCase` establishes a test case, and subsequent expectations are
  attached to the most recent test case.
- `expectResult`, `expectOutputContains`, and/or `expectCustom` to
  establish expectations for the result and/or output of the most recent
  test case.
- `captureOutput` sets up output capturing, which is needed if
  `expectOutputContains` will be used. The captured output will saved
  and reset every time a new test case is established, but if printing
  happens between test cases, `resetOutput` may be necessary before the
  next test case. `showOutput` can be used to show the output that's
  being captured instead of suppressing it.
- `provideInput` sets up inputs ahead of time, so that interactive code
  can be tested without pausing for real user input. `restoreInput` can be
  used to resume normal interactive input.
- `runFile` can be used to test a file that's supposed to be run as a
  script, instead of testing individual expressions. Simply call
  `testCase` with `runFile()` as the argument. Testing machinery will be
  disabled during the run.
- `detailLevel` can be called to control the level of detail printed in
  the output.
- `showSummary` can be used to summarize the number of expectations
  which passed or failed.
- `colors` can be used to enable or disable color codes for printed text.
  Disable this if you're getting garbled output.

Note: currently, if test causes an error, you just get the error, and
the testing machinery doesn't do anything about that.
TODO: Some way to do something about that?

TODO: Workaround for tracing in interactive console?
TODO: Prevent crash if expr_src is unavailable when tracing...
"""

# TODO: Cache compiled ASTs!

__version__ = "0.10"

import sys
import inspect
import ast
import copy
import io
import types
import builtins


#---------#
# Globals #
#---------#

CURRENT_CASE = None
"""
The currently-active test case. See `testCase`.
"""

ALL_EXPECTATIONS = []
"""
All expectations that have been established. Each is a dictionary (see
`check_expectation`).
"""

COMPLETED_PER_LINE = {}
"""
A dictionary mapping function names to dictionaries mapping (filename,
line-number) pairs to counts. Each count represents the number of
functions of that name which have finished execution on the given line
of the given file already. This allows us to figure out which expression
belongs to which invocation if `get_my_context` is called multiple times
from the same line of code.
"""


OUTPUT_CAPTURE = None
"""
The current destination for captured output, or None if we're not
capturing output.
"""

ORIGINAL_INPUT_FN = builtins.input
"""
The original input function.
"""

ORIGINAL_STDIN = None
"""
The original `sys.stdin` value, so that it can be restored by
`restoreInput` after `provideInput` has been called.
"""

DETAIL_LEVEL = 0
"""
The current detail level, which controls how verbose our messages are.
See `detailLevel`.
"""

SUMMARY_INFO = {
    "met": [],
    "unmet": []
}
"""
Complied list of expectations that passed or failed. Used by
`showSummary`.
"""

COLORS = True
"""
Whether to print ANSI color control sequences to color the output or not.
"""


#--------#
# Errors #
#--------#

class TestError(Exception):
    """
    An error with the testing mechanisms, as opposed to an error with
    the actual code being tested.
    """
    pass


#----------------#
# Output capture #
#----------------#


class CapturingStream(io.StringIO):
    """
    An output capture object which is an `io.StringIO` underneath, but
    which has an option to also write incoming text to normal
    `sys.stdout`. Call the install function to begin capture.
    """
    def __init__(self, *args, **kwargs):
        """
        Passes arguments through to `io.StringIO`'s constructor.
        """
        self.original_stdout = None
        self.tee = False
        super().__init__(*args, **kwargs)

    def echo(self, doit=True):
        """
        Turn on echoing to stdout along with capture, or turn it off if
        False is given.
        """
        self.tee = doit

    def install(self):
        """
        Replaces `sys.stdout` to begin capturing output. Remembers the
        old `sys.stdout` value so that `uninstall` can work.
        """
        self.original_stdout = sys.stdout
        sys.stdout = self

    def uninstall(self):
        """
        Returns `sys.stdout` to what it was before `install` was called,
        or does nothing if `install` was never called.
        """
        if self.original_stdout is not None:
            sys.stdout = self.original_stdout

    def reset(self):
        """
        Resets the captured output.
        """
        self.seek(0)
        self.truncate(0)

    def writelines(self, lines):
        """
        Override writelines to work through write.
        """
        for line in lines:
            self.write(line)

    def write(self, stuff):
        """
        Accepts a string and writes to our capture buffer (and to
        original stdout if `echo` has been called). Returns the number
        of characters written.
        """
        if self.tee and self.original_stdout is not None:
            self.original_stdout.write(stuff)
        super().write(stuff)


def _echoing_input(prompt):
    """
    A stand-in for the built-in input which echoes the received input to
    stdout, under the assumption that stdin will NOT be echoed to the
    output stream because the output stream is not the console any more.
    """
    result = ORIGINAL_INPUT_FN(prompt)
    sys.stdout.write(result + '\n')
    return result


def captureOutput():
    """
    Sets up a string IO object to capture stdout. Calls to `testCase`
    will read this captured output and reset the buffer. Does nothing if
    output capturing is already in place.
    """
    global OUTPUT_CAPTURE, ORIGINAL_INPUT_FN
    if OUTPUT_CAPTURE is None or sys.stdout != OUTPUT_CAPTURE:
        ORIGINAL_INPUT_FN = builtins.input
        builtins.input = _echoing_input
        OUTPUT_CAPTURE = CapturingStream()
        OUTPUT_CAPTURE.install()


def showOutput():
    """
    If `captureOutput` has been called, modifies the capture so that
    output is also written to the original `sys.stout`. Does nothing if
    `captureOutput` is not active.
    """
    if OUTPUT_CAPTURE:
        OUTPUT_CAPTURE.echo()


def supressOutput():
    """
    If `captureOutput` has been called, modifies the capture so that
    output is NOT written to the original `sys.stout`. Does nothing if
    `captureOutput` is not active. This is the default behavior, so you
    will only need this function if you want to undo a call to
    `showOutput`.
    """
    if OUTPUT_CAPTURE:
        OUTPUT_CAPTURE.echo(False)


def resetOutput():
    """
    Resets the captured output buffer. Does nothing if `captureOutput`
    has not be called.
    """
    if OUTPUT_CAPTURE:
        OUTPUT_CAPTURE.reset()


def restoreOutput():
    """
    Reverses the effect of `captureOutput`, restoring normal output.
    Does nothing if `captureOutput` has not been called.
    """
    if OUTPUT_CAPTURE:
        OUTPUT_CAPTURE.uninstall()
        builtins.input = ORIGINAL_INPUT_FN


def getCurrentOutput():
    """
    Returns the string value of the current output capture buffer.

    Returns None if output capturing hasn't been set up by
    `captureOutput`.
    """
    if OUTPUT_CAPTURE:
        return OUTPUT_CAPTURE.getvalue()
    else:
        return None


#-----------------#
# Input provision #
#-----------------#

def provideInput(inputs, autoNewlines=True):
    """
    Replaces normal inputs with inputs from the given multi-line string.
    Normal interactive input can be resumed using `restoreInput`.

    A newline will automatically be appended to the given input string if
    it doesn't already end in one, as newlines are necessary for inputs
    to actually be sent through when the `input` function is called.

    By the same logic, to make triple-quoted input strings easier to
    define, if the inputs begin with a newline, a single newline will be
    removed from the beginning. To provide a blank input as the first
    input, simply provide two newlines at the beginning of the string.

    You can set autoNewlines to False to disable this newline-munging
    behaivor.
    """
    global ORIGINAL_STDIN
    if autoNewlines and inputs.startswith('\n'):
        inputs = inputs[1:]
    if autoNewlines and not inputs.endswith('\n'):
        inputs += '\n'
    ORIGINAL_STDIN = sys.stdin
    sys.stdin = io.StringIO(inputs)


def restoreInput():
    """
    Returns to normal interactive input, undoing the effects of
    `provideInput`. Does nothing if `provideInput` has not been called.
    """
    if ORIGINAL_STDIN:
        sys.stdin = ORIGINAL_STDIN


#--------------------#
# Whole-file testing #
#--------------------#

class FunctionCallStubber(ast.NodeTransformer):
    """
    An `ast.NodeTransformer` which stubs out function calls to certain
    functions (according to their names as accessed directly or via an
    attribute).
    """
    def __init__(self, targets, *args, **kwargs):
        """
        A list of strings is required, and specifies which function
        calls to replace. Other arguments are passed through to the
        `ast.NodeTransformer` constructor.
        """
        self.targets = targets
        super().__init__(*args, **kwargs)

    def visit_Call(self, node):
        """
        We only transform call nodes. Any call whose function is a Name
        or Attribute, and where the name used or attribute looked up
        matches one of our targets gets replaced by a new stub which is a
        constant None. Other function calls are passed through unchanged.
        """
        stub = ast.Constant()
        stub.value = None
        ast.copy_location(stub, node)
        if isinstance(node.func, ast.Name):
            if node.func.id in self.targets:
                return stub
            else:
                return node
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in self.targets:
                return stub
            else:
                return node
        else:
            return node


PROBLEMATIC = [
    "captureOutput",
    "testCase",
    "expectResult",
    "expectOutputContains",
    "expectCustom",
    "runFile",
    "provideInput"
]
"""
A list of function names which would be problematic to run if we're
re-running an entire file that might have expectations in it.
"""


def runFile():
    """
    Runs the entire file that calls this function, but without running
    any of the functions in the `PROBLEMATIC` list or evaluating any
    arguments given to them (calls to those functions are replaced by a
    constant value None in the source code).

    Note that if these functions are assigned to variables with different
    names or otherwise called indirectly, the stubbing process won't
    work, which could be undesirable. There is a backup procedure which
    replaces problematic functions with functions that just return None
    to try to catch even these kinds of cases.

    Also, calls to ANY function by one of the problematic names will be
    transformed, including calls to attributes of any object where the
    attribute is one of these names.
    """
    # Grab filename of the calling code from the stack
    filename = get_my_location()["file"]

    # Read the calling code's file
    try:
        with open(filename, 'r') as fin:
            src = fin.read()
    except Exception:
        print(
            (
                f"Error: runFile could not read the calling file"
                f" '{filename}'. Nothing to run."
            ),
            file=sys.stderr
        )
        return

    # Parse the calling code, and stub out problematic calls
    node = ast.parse(src, filename=filename, mode='exec')
    FunctionCallStubber(PROBLEMATIC).visit(node)

    # Compile the results and run them
    code = compile(node, filename, 'exec')

    # Temporarily pin away problematic functions just in case an indirect
    # call slips by...
    gl = globals()
    saved = {}
    for fn in PROBLEMATIC:
        saved[fn] = gl[fn]
        gl[fn] = lambda *args, **kwargs: None

    # Run the code
    # our environment is fresh, but we do set __name__ to main
    # builtins will be added automatically
    env = {"__name__": "__main__"}
    try:
        exec(code, env)
    finally:
        # Make sure we undo our pins
        for fn in PROBLEMATIC:
            gl[fn] = saved[fn]


#----------#
# testCase #
#----------#

def testCase(expr):
    """
    Establishes a test case. The expression provided will be picked out
    of the source code of the module calling `testCase`, and used to
    report on test case failures (see `get_my_context`). Calls to
    `expectResult` and other expect functions will be checked in the
    context of the most recently established test case.

    The test case established will have "result", "output", and "context"
    slots holding the test result value, any captured output (or None if
    output capturing wasn't enabled), and the test context (see
    `get_my_context`).

    Note that we use as deep a copy of the result as we can...

    For `testCase` to work properly, the following rules must be
    followed:

    1. When multiple calls to `testCase` appear on a single line of the
        source code (something you should probably avoid anyway), none of
        the calls should execute more times than another when that line
        is executed (it's difficult to violate this, but examples include
        the use of `testCase` multiple times on line line within
        generator or if/else expressions)
    2. None of the following components of the expression passed to
        `testCase` should have side effects when evaluated:
        - Attribute accesses
        - Subscripts (including expressions inside brackets)
        - Variable lookups
        (Note that those things don't normally have side effects!)
    3. No modification of the items involved in a test case should take
       place between that case and its associated expectation(s).
    """
    global CURRENT_CASE
    CURRENT_CASE = {
        "result": deepish_copy(expr), # (it's actually a value in this form...)
        "output": getCurrentOutput(),
        "context": get_my_context(testCase)
    }
    # Reset output capture
    resetOutput()


#--------------#
# Expectations #
#--------------#

def indent(msg, level=2):
    """
    Indents every line of the given message (a string).
    """
    indent = ' ' * level
    return indent + ('\n' + indent).join(msg.splitlines())


def ellipsis(string, maxlen=40):
    """
    Returns the provided string as-is, or if it's longer than the given
    maximum length, returns the string, truncated, with '...' at the
    end, which will, including the ellipsis, be exactly the given
    maximum length. The maximum length must be 4 or more.
    """
    if len(string) > maxlen:
        return string[:maxlen - 3] + "..."
    else:
        return string


def print_message(msg, color=None):
    """
    Prints a test result message to sys.stderr, but also flushes stdout
    and stderr both beforehand and afterwards to improve message
    ordering.

    If a color is given, it should be an ANSI terminal color code string
    (just the digits, for example '34' for blue or '1;31' for bright red).
    """
    sys.stdout.flush()
    sys.stderr.flush()

    # Make the whole message blue
    if color:
        print(f"\x1b[{color}m", end="", file=sys.stderr)
        suffix = "\x1b[0m"
    else:
        suffix = ""

    print(msg + suffix, file=sys.stderr)

    sys.stdout.flush()
    sys.stderr.flush()


def create_success_message(
    tag,
    context,
    details,
    include_expr_details=True
):
    """
    Returns an expectation success message (a string) for the given test
    context, with the given details to be printed if the detail level is
    1 or higher. Unless `include_expr_details` is set to False, details
    of the test expression will also be included (but only when the detail
    level is at least 1). The tag should be a filename:lineno string
    indicating where the expectation originated.
    """
    # Tags for us and our test
    SUMMARY_INFO["met"].append(tag)
    ctag = f"{context['file']}:{context['line']}"

    # Detail level 1 gives more output for successes
    if DETAIL_LEVEL < 1:
        result = f"✓ {tag}"
    else:
        result = f"✓ expectation from {tag} met for test at {ctag}"
        detail_msg = indent(details, 2)
        if not detail_msg.startswith('\n'):
            detail_msg = '\n' + detail_msg

        # Expression details unless suppressed
        if include_expr_details:
            expr_base, expr_extra = expr_details(context)
            detail_msg += '\n' + indent(expr_base, 2)
            detail_msg += '\n' + indent(expr_extra, 2)

        result += detail_msg

    return result


def create_failure_message(
    tag,
    context,
    details,
    extra_details,
    include_expr_details=True
):
    """
    Returns an expectation failure message (a string) for the given test
    context, with the given details to be printed if the detail level is
    0 or higher, and the given extra details to also be printed if the
    detail level is 1 or higher. Unless `include_expr_details` is set to
    false, details of the expression tested will be included
    automatically. The tag should be a filename:lineno string indicating
    where the expectation originated.
    """
    # Tags for us and our test
    SUMMARY_INFO["unmet"].append(tag)
    ctag = f"{context['file']}:{context['line']}"

    # Detail level controls initial message
    if DETAIL_LEVEL < 1:
        result = f"✗ {tag}"
    else:
        result = f"✗ expectation from {tag} NOT met for test at {ctag}"

    # Assemble our details message
    detail_msg = ''

    # Detail level controls printing of detail messages
    if DETAIL_LEVEL >= 0:
        detail_msg += '\n' + indent(details, 2)
    if DETAIL_LEVEL >= 1 and extra_details:
        detail_msg += '\n' + indent(extra_details, 2)

    # Expression details unless suppressed
    if include_expr_details:
        expr_base, expr_extra = expr_details(context)
        if DETAIL_LEVEL >= 0:
            detail_msg += '\n' + indent(expr_base, 2)
        if DETAIL_LEVEL >= 1:
            detail_msg += '\n' + indent(expr_extra, 2)

    return result + detail_msg


def expr_details(context):
    """
    Returns a pair of strings containing base and extra details for an
    expectation.
    """
    # Expression that was evaluated
    expr = context.get("expr_src", "???")
    short_expr = ellipsis(expr)
    # Results
    msg = ""
    extra_msg = ""

    # Base message
    msg += f"In expression {short_expr}, values were:"
    vdict = context.get("values", {})
    if context.get("relevant"):
        show = sorted(
            context["relevant"],
            key=lambda fragment: (expr.index(fragment), len(fragment))
        )
    else:
        show = sorted(
            vdict.keys(),
            key=lambda fragment: (expr.index(fragment), len(fragment))
        )

    longs = []
    for key in show:
        if key in vdict:
            val = repr(vdict[key])
        else:
            val = "???"

        entry = f"  {key} = {val}"
        fits = ellipsis(entry)
        msg += '\n' + fits
        if fits != entry:
            longs.append(entry)

    # Extra message
    if short_expr != expr:
        if extra_msg != "" and not extra_msg.endswith('\n'):
            extra_msg += '\n'
        extra_msg += f"Full expression:\n  {expr}"
    extra_values = sorted(
        [
            key
            for key in vdict.keys()
            if key not in context.get("relevant", [])
        ],
        key=lambda fragment: (expr.index(fragment), len(fragment))
    )
    if context.get("relevant") and extra_values:
        if extra_msg != "" and not extra_msg.endswith('\n'):
            extra_msg += '\n'
        extra_msg += "Extra values:"
        for ev in extra_values:
            if ev in vdict:
                val = repr(vdict[ev])
            else:
                val = "???"

            entry = f"  {ev} = {val}"
            fits = ellipsis(entry)
            extra_msg += '\n' + fits
            if fits != entry:
                longs.append(entry)

    if longs:
        if extra_msg != "" and not extra_msg.endswith('\n'):
            extra_msg += '\n'
        extra_msg += "Full values:"
        for entry in longs:
            extra_msg += '\n' + entry

    return msg, extra_msg


def check_expectation(exp, set_success=True):
    """
    Checks an expectation dictionary, which must have the following keys:

    - tag A string indicating the file name and line number where this
        expectation was established
    - case The test case info (see `testCase`).
    - type The type of expectation: "result", "output", or "custom".
    - value The expected value (or output fragment, or the checker function,
        depending on the expectation type).

    This function will add a "met" key to the expectation dictionary it
    checks, unless the `set_success` argument is set to False. It will
    also print a success or failure message, and add that message as the
    "message" key (again unless `set_success` is False). It will return
    True on success and False on failure.
    """
    case = exp["case"]
    context = case["context"]
    result = case["result"]
    if exp["type"] == "result":
        expected = exp["value"]
        short_result = ellipsis(repr(result))
        short_expected = ellipsis(repr(expected))
        full_result = repr(result)
        full_expected = repr(expected)
        if result == expected:
            msg = create_success_message(
                exp["tag"],
                context,
                (
                    f"Result {short_result} was equivalent to the"
                    f" expected value {short_expected}."
                )
            )
            print_message(msg, color="34" if COLORS else None)
            if set_success:
                exp["met"] = True
                exp["message"] = msg
            return True
        else:
            # Construct base report
            base_msg = (
                f"Result {short_result} was different from the"
                f" expected value {short_expected}."
            )

            # Construct extra-detailed message
            extra_msg = ""
            if short_result != full_result:
                extra_msg += f"Full result:\n  {full_result}"
            if short_expected != full_expected:
                if extra_msg != "":
                    extra_msg += '\n'
                extra_msg += f"Full expectation:\n  {full_expected}"

            msg = create_failure_message(
                exp["tag"],
                context,
                base_msg,
                extra_msg
            )
            print_message(msg, color='1;31' if COLORS else None)
            if set_success:
                exp["met"] = False
                exp["message"] = msg
            return False
    elif exp["type"] == "output":
        case = exp["case"]
        context = case["context"]
        output = case["output"]
        fragment = exp["value"]
        if output is None:
            msg = create_failure_message(
                exp["tag"],
                context,
                "No output has been captured.",
                (
                    "You must call captureOutput before testCase if you"
                    " want to use expectOutputContains."
                ),
                False
            )
            print_message(msg, color='1;31' if COLORS else None)
            if set_success:
                exp["met"] = False
                exp["message"] = msg
            return False
        short_output = ellipsis(output)
        short_fragment = ellipsis(fragment)
        full_output = output
        full_fragment = fragment
        if fragment in output:
            msg = create_success_message(
                exp["tag"],
                context,
                (
                    f'Fragment "{short_fragment}" was found in the'
                    f' recorded output """{short_output}""".'
                )
            )
            print_message(msg, color='34' if COLORS else None)
            if set_success:
                exp["met"] = True
                exp["message"] = msg
            return True
        else:
            # Construct base report
            msg = (
                f'Fragment "{short_fragment}" was NOT present in the'
                f' recorded output """{short_output}""".'
            )
            if fragment.casefold() in output.casefold():
                msg += "\n  Note: fragment would match if case were ignored."

            # Construct extra-detailed message
            extra_msg = ""
            if full_output != short_output:
                extra_msg += f"\nFull output:\n  {full_output}"
            if full_fragment != short_fragment:
                extra_msg += f"\nFull fragment:\n  {full_fragment}"

            if extra_msg.startswith('\n'):
                extra_msg = extra_msg[1:]

            msg = create_failure_message(exp["tag"], context, msg, extra_msg)
            print_message(msg, color='1;31' if COLORS else None)
            if set_success:
                exp["met"] = False
                exp["message"] = msg
            return False
    else: # we assume it's a custom expectation
        case = exp["case"]
        tester = exp["value"]
        context = case["context"]
        result = case["result"]
        output = case["output"]
        if output is None:
            test_result = tester(result)
            output_clause = ''
        else:
            test_result = tester(result, output)
            output_clause = f' and output """{ellipsis(output)}"""'

        rep = repr(result)
        short_result = ellipsis(rep)
        test_name = tester.__name__

        if test_result is True:
            msg = create_success_message(
                exp["tag"],
                context,
                (
                    f'Tester "{test_name}" succeeded for result'
                    f' {short_result}{output_clause}.'
                )
            )
            print_message(msg, color='34' if COLORS else None)
            if set_success:
                exp["met"] = True
                exp["message"] = msg
            return True
        else:
            # Construct base report
            msg = (
                f'Tester "{test_name}" failed for result'
                f' {short_result}{output_clause}.'
            )

            # Construct extra-detailed message
            extra_msg = f"Test result:\n  {repr(test_result)}"
            if rep != short_result:
                extra_msg += f"\nFull result:\n  {rep}"
            if output != ellipsis(output):
                extra_msg += f"\nFull output:\n  {output}"

            msg = create_failure_message(exp["tag"], context, msg, extra_msg)
            print_message(msg, color='1;31' if COLORS else None)
            if set_success:
                exp["met"] = False
                exp["message"] = msg
            return False


def expectResult(expected):
    """
    Expects that the most recently established `testCase`'s result
    should be exactly equivalent to the given value. Prints messages to
    `sys.stderr` about success or failure, conditional on the current
    detail level (see `detailLevel`).

    Returns True if the expectation is met and False otherwise.
    """
    if CURRENT_CASE is None:
        context = get_my_location()
        msg = create_failure_message(
            context,
            "No test case has been established!",
            "You must call testCase before calling expectResult.",
            False
        )
        print_message(msg, color='1;31' if COLORS else None)
        return False
    else:
        myloc = get_my_location()
        exp = {
            "tag": f"{myloc['file']}:{myloc['line']}",
            "case": CURRENT_CASE,
            "type": "result",
            "value": expected
        }
        ALL_EXPECTATIONS.append(exp)
        return check_expectation(exp)


def expectOutputContains(fragment):
    """
    Expects that the most recently established `testCase`'s captured
    output should contain the given fragment as a sub-string.
    Prints messages to `sys.stderr` about success or failure,
    conditional on the current detail level (see `detailLevel`).

    Returns True if the expectation is met and False otherwise.
    """
    if CURRENT_CASE is None:
        context = get_my_location()
        msg = create_failure_message(
            context,
            "No test case has been established!",
            "You must call testCase before calling expectOutputContains.",
            False
        )
        print_message(msg, color='1;31' if COLORS else None)
        return False
    else:
        myloc = get_my_location()
        exp = {
            "tag": f"{myloc['file']}:{myloc['line']}",
            "case": CURRENT_CASE,
            "type": "output",
            "value": fragment
        }
        ALL_EXPECTATIONS.append(exp)
        return check_expectation(exp)


def expectCustom(tester):
    """
    Establishes a custom expectation: the provided function will be run
    on the result of the most recent `testCase`, and the expectation
    will be considered met if the function returns True, or failed if it
    returns any other value.

    If output was captured for the relevant `testCase`, the tester
    function will be given two arguments: the result value and the
    captured output.

    If the tester fails by returning a value other than True, that value
    will be printed as part of a detailed failure message if the detail
    level is at least 1.
    """
    if CURRENT_CASE is None:
        context = get_my_location()
        msg = create_failure_message(
            context,
            "No test case has been established!",
            "You must call testCase before calling expectCustom.",
            False
        )
        print_message(msg, color='1;31' if COLORS else None)
        return False
    else:
        myloc = get_my_location()
        exp = {
            "tag": f"{myloc['file']}:{myloc['line']}",
            "case": CURRENT_CASE,
            "type": "custom",
            "value": tester
        }
        ALL_EXPECTATIONS.append(exp)
        return check_expectation(exp)


#-------------------#
# Verbosity control #
#-------------------#

def detailLevel(level):
    """
    Sets the level of detail for printed messages.
    The detail levels are:

    * -1: Super-minimal output, with no details beyond success/failure.
    * 0: Succinct messages indicating success/failure, with minimal
        details when failure occurs.
    * 1: More verbose success/failure messages, with details about
        successes and more details about failures.
    """
    global DETAIL_LEVEL
    DETAIL_LEVEL = level


#---------------#
# Summarization #
#---------------#

def showSummary():
    """
    Shows a summary of the number of expectations that have been met or
    not. Prints output to sys.stderr.
    """
    # Flush stdout & stderr to improve ordering
    sys.stdout.flush()
    sys.stderr.flush()

    met = SUMMARY_INFO["met"]
    unmet = SUMMARY_INFO["unmet"]
    print('---', file=sys.stderr)

    if len(unmet) == 0:
        if len(met) == 0:
            print("No expectations were established.", file=sys.stderr)
        else:
            print(
                f"All {len(met)} expectation(s) were met.",
                file=sys.stderr
            )
    else:
        if len(met) == 0:
            print(
                f"None of the {len(unmet)} expectation(s) were met!",
                file=sys.stderr
            )
        else:
            print(
                (
                    f"{len(unmet)} of the {len(met) + len(unmet)}"
                    f" expectation(s) were NOT met:"
                ),
                file=sys.stderr
            )
        if COLORS: # bright red
            print("\x1b[1;31m", end="", file=sys.stderr)
        for tag in unmet:
            print(f"  ✗ {tag}", file=sys.stderr)
        if COLORS: # reset
            print("\x1b[0m", end="", file=sys.stderr)
    print('---', file=sys.stderr)

    # Flush stdout & stderr to improve ordering
    sys.stdout.flush()
    sys.stderr.flush()


#---------------#
# Color control #
#---------------#

def colors(enable=False):
    """
    Enables or disables colors in printed output. If your output does not
    support ANSI color codes, the color output will show up as garbage
    and you can disable this.
    """
    global COLORS
    COLORS = enable


#---------#
# Tracing #
#---------#

def trace(expr):
    """
    Given an expression (actually, of course, just a value), returns the
    value it was given. But also prints a trace message indicating what
    the expression was, what value it had, and the line number of that
    line of code.

    The file name and overlength results are printed only when the
    `detailLevel` is set to 1 or higher.
    """
    # Flush stdout & stderr to improve ordering
    sys.stdout.flush()
    sys.stderr.flush()

    ctx = get_my_context(trace)
    rep = repr(expr)
    short = ellipsis(repr(expr))
    tag = "{line}".format(**ctx)
    if DETAIL_LEVEL >= 1:
        tag = "{file}:{line}".format(**ctx)
    print(
        f"{tag} {ctx['expr_src']} ⇒ {short}",
        file=sys.stderr
    )
    if DETAIL_LEVEL >= 1 and short != rep:
        print("  Full result is:\n    " + rep, file=sys.stderr)

    # Flush stdout & stderr to improve ordering
    sys.stdout.flush()
    sys.stderr.flush()

    return expr


#------------------------------#
# Reverse evaluation machinery #
#------------------------------#

def get_src_index(src, lineno, col_offset):
    """
    Turns a line number and column offset into an absolute index into
    the given source string, assuming length-1 newlines.
    """
    lines = src.splitlines()
    above = lines[:lineno - 1]
    return sum(len(line) for line in above) + len(above) + col_offset


def test_gsr():
    """Tests for get_src_index."""
    s = 'a\nb\nc'
    assert get_src_index(s, 1, 0) == 0
    assert get_src_index(s, 2, 0) == 2
    assert get_src_index(s, 3, 0) == 4
    assert s[get_src_index(s, 1, 0)] == 'a'
    assert s[get_src_index(s, 2, 0)] == 'b'
    assert s[get_src_index(s, 3, 0)] == 'c'


def find_identifier_end(code, start_index):
    """
    Given a code string and an index in that string which is the start
    of an identifier, returns the index of the end of that identifier.
    """
    at = start_index + 1
    while at < len(code):
        ch = code[at]
        if not ch.isalpha() and not ch.isdigit() and ch != '_':
            break
        at += 1
    return at - 1


def test_find_identifier_end():
    """Tests for find_identifier_end."""
    assert find_identifier_end("abc.xyz", 0) == 2
    assert find_identifier_end("abc.xyz", 1) == 2
    assert find_identifier_end("abc.xyz", 2) == 2
    assert find_identifier_end("abc.xyz", 4) == 6
    assert find_identifier_end("abc.xyz", 5) == 6
    assert find_identifier_end("abc.xyz", 6) == 6
    assert find_identifier_end("abc_xyz123", 0) == 9
    assert find_identifier_end("abc xyz123", 0) == 2
    assert find_identifier_end("abc xyz123", 4) == 9
    assert find_identifier_end("x", 0) == 0
    assert find_identifier_end("  x", 2) == 2
    assert find_identifier_end("  xyz1", 2) == 5
    s = "def abc(def):\n  print(xyz)\n"
    assert find_identifier_end(s, 0) == 2
    assert find_identifier_end(s, 4) == 6
    assert find_identifier_end(s, 8) == 10
    assert find_identifier_end(s, 16) == 20
    assert find_identifier_end(s, 22) == 24


def unquoted_enumerate(src, start_index):
    """
    A generator that yields index, character pairs from the given code
    string, skipping quotation marks and the strings that they delimit,
    including triple-quotes and respecting backslash-escapes within
    strings.
    """
    quote = None
    at = start_index

    while at < len(src):
        char = src[at]

        # skip escaped characters in quoted strings
        if quote and char == '\\':
            # (thank goodness I don't have to worry about r-strings)
            at += 2
            continue

        # handle quoted strings
        elif char == '"' or char == "'":
            if quote == char:
                quote = None # single end quote
                at += 1
                continue
            elif src[at:at + 3] in ('"""', "'''"):
                tq = src[at:at + 3]
                at += 3 # going to skip these no matter what
                if tq == quote or tq[0] == quote:
                    # Ending triple-quote, or matching triple-quote at
                    # end of single-quoted string = ending quote +
                    # empty string
                    quote = None
                    continue
                else:
                    if quote:
                        # triple quote of other kind inside single or
                        # triple quoted string
                        continue
                    else:
                        quote = tq
                        continue
            elif quote is None:
                # opening single quote
                quote = char
                at += 1
                continue
            else:
                # single quote inside other quotes
                at += 1
                continue

        # Non-quote characters in quoted strings
        elif quote:
            at += 1
            continue

        else:
            yield (at, char)
            at += 1
            continue


def test_unquoted_enumerate():
    """Tests for unquoted_enumerate."""
    uqe = unquoted_enumerate
    assert list(uqe("abc'123'", 0)) == list(zip(range(3), "abc"))
    assert list(uqe("'abc'123", 0)) == list(zip(range(5, 8), "123"))
    assert list(uqe("'abc'123''", 0)) == list(zip(range(5, 8), "123"))
    assert list(uqe("'abc'123''", 1)) == [(1, 'a'), (2, 'b'), (3, 'c')]
    mls = "'''\na\nb\nc'''\ndef"
    assert list(uqe(mls, 0)) == list(zip(range(12, 16), "\ndef"))
    tqs = '"""\'\'\'ab\'\'\'\'""" cd'
    assert list(uqe(tqs, 0)) == [(15, ' '), (16, 'c'), (17, 'd')]
    rqs = "a'b'''c\"\"\"'''\"d\"''''\"\"\"e'''\"\"\"f\"\"\"'''"
    print(f"X: '{rqs[23]}'", file=sys.stderr)
    assert list(uqe(rqs, 0)) == [(0, 'a'), (6, 'c'), (23, 'e')]
    assert list(uqe(rqs, 6)) == [(6, 'c'), (23, 'e')]
    bss = "a'\\'b\\''c"
    assert list(uqe(bss, 0)) == [(0, 'a'), (8, 'c')]
    mqs = "'\"a'b\""
    assert list(uqe(mqs, 0)) == [(4, 'b')]


def find_nth_attribute_period(code, start_index, n):
    """
    Given a string of Python code and a start index within that string,
    finds the nth period character (counting from first = zero) after
    that start point, but only considers periods which are used for
    attribute access, i.e., periods outside of quoted strings and which
    are not part of ellipses. Returns the index within the string of the
    period that it found. A period at the start index (if there is one)
    will be counted. Returns None if there are not enough periods in the
    code. If the start index is inside a quoted string, things will get
    weird, and the results will probably be wrong.
    """
    for (at, char) in unquoted_enumerate(code, start_index):
        if char == '.':
            if code[at - 1:at] == '.' or code[at + 1:at + 2] == '.':
                # part of an ellipsis, so ignore it
                continue
            else:
                n -= 1
                if n < 0:
                    break

    # Did we hit the end of the string before counting below 0?
    if n < 0:
        return at
    else:
        return None


def test_find_nth_attribute_period():
    """Tests for find_nth_attribute_period."""
    assert find_nth_attribute_period("a.b", 0, 0) == 1
    assert find_nth_attribute_period("a.b", 0, 1) is None
    assert find_nth_attribute_period("a.b", 0, 100) is None
    assert find_nth_attribute_period("a.b.c", 0, 1) == 3
    assert find_nth_attribute_period("a.b.cde.f", 0, 1) == 3
    assert find_nth_attribute_period("a.b.cde.f", 0, 2) == 7
    s = "a.b, c.d, 'e.f', g.h"
    assert find_nth_attribute_period(s, 0, 0) == 1
    assert find_nth_attribute_period(s, 0, 1) == 6
    assert find_nth_attribute_period(s, 0, 2) == 18
    assert find_nth_attribute_period(s, 0, 3) is None
    assert find_nth_attribute_period(s, 0, 3) is None
    assert find_nth_attribute_period(s, 1, 0) == 1
    assert find_nth_attribute_period(s, 2, 0) == 6
    assert find_nth_attribute_period(s, 6, 0) == 6
    assert find_nth_attribute_period(s, 7, 0) == 18
    assert find_nth_attribute_period(s, 15, 0) == 18


def find_closing_item(code, start_index, openclose='()'):
    """
    Given a string of Python code, a starting index where there's an
    open paren, bracket, etc., and a 2-character string containing the
    opening and closing delimiters of interest (parentheses by default),
    returns the index of the matching closing delimiter, or None if the
    opening delimiter is unclosed. Note that the given code must not
    contain syntax errors, or the behavior will be undefined.

    Does NOT work with quotations marks (single or double).
    """
    level = 1
    open_delim = openclose[0]
    close_delim = openclose[1]
    for at, char in unquoted_enumerate(code, start_index + 1):
        # Non-quoted open delimiters
        if char == open_delim:
            level += 1

        # Non-quoted close delimiters
        elif char == close_delim:
            level -= 1
            if level < 1:
                break

        # Everything else: ignore it

    if level == 0:
        return at
    else:
        return None


def test_find_closing_item():
    """Tests for find_closing_item."""
    assert find_closing_item('()', 0, '()') == 1
    assert find_closing_item('()', 0) == 1
    assert find_closing_item('(())', 0, '()') == 3
    assert find_closing_item('(())', 1, '()') == 2
    assert find_closing_item('((word))', 0, '()') == 7
    assert find_closing_item('((word))', 1, '()') == 6
    assert find_closing_item('(("(("))', 0, '()') == 7
    assert find_closing_item('(("(("))', 1, '()') == 6
    assert find_closing_item('(("))"))', 0, '()') == 7
    assert find_closing_item('(("))"))', 1, '()') == 6
    assert find_closing_item('(()())', 0, '()') == 5
    assert find_closing_item('(()())', 1, '()') == 2
    assert find_closing_item('(()())', 3, '()') == 4
    assert find_closing_item('(""")(\n""")', 0, '()') == 10
    assert find_closing_item("\"abc(\" + ('''def''')", 9, '()') == 19
    assert find_closing_item("\"abc(\" + ('''def''')", 0, '()') is None
    assert find_closing_item("\"abc(\" + ('''def''')", 4, '()') is None
    assert find_closing_item("(()", 0, '()') is None
    assert find_closing_item("(()", 1, '()') == 2
    assert find_closing_item("()(", 0, '()') == 1
    assert find_closing_item("()(", 2, '()') is None
    assert find_closing_item("[]", 0, '[]') == 1
    assert find_closing_item("[]", 0) is None
    assert find_closing_item("{}", 0, '{}') == 1
    assert find_closing_item("aabb", 0, 'ab') == 3


def get_expr_src(src, call_node):
    """
    Gets the string containing the source code for the expression passed
    to a function call, given the string source of the file that defines
    the function and the AST node for the function call.
    """
    # Find the child node for the first (and only) argument
    arg_expr = call_node.args[0]

    # If get_source_segment is available, use that
    if hasattr(ast, "get_source_segment"):
        return ast.get_source_segment(src, arg_expr)
    else:
        # We're going to have to do this ourself: find the start of the
        # expression and state-machine to find a matching paren
        start = get_src_index(src, call_node.lineno, call_node.col_offset)
        open_paren = src.index('(', start)
        end = find_closing_item(src, open_paren, '()')
        # Note: can't be None because that would have been a SyntaxError
        return src[open_paren + 1:end]


def get_ref_src(src, node):
    """
    Gets the string containing the source code for a variable reference,
    attribute, or subscript.
    """
    # Use get_source_segment if it's available
    if hasattr(ast, "get_source_segment"):
        return ast.get_source_segment(src, node)
    else:
        # We're going to have to do this ourself: find the start of the
        # expression and state-machine to find its end
        start = get_src_index(src, node.lineno, node.col_offset)

        # Figure out the end point
        if isinstance(node, ast.Attribute):
            # Find sub-attributes so we can count syntactic periods to
            # figure out where the name part begins to get the span
            inner_period_count = 0
            for node in ast.walk(node):
                if isinstance(node, ast.Attribute):
                    inner_period_count += 1
            inner_period_count -= 1 # for the node itself
            dot = find_nth_attribute_period(src, start, inner_period_count)
            end = find_identifier_end(src, dot + 1)

        elif isinstance(node, ast.Name):
            # It's just an identifier so we can find the end
            end = find_identifier_end(src, start)

        elif isinstance(node, ast.Subscript):
            # Find start of sub-expression so we can find opening brace
            # and then match it to find the end
            inner = node.slice
            if isinstance(inner, ast.Slice):
                pass
            elif hasattr(ast, "Index") and isinstance(inner, ast.Index):
                # 3.7 Index has a "value"
                inner = inner.value
            elif hasattr(ast, "ExtSlice") and isinstance(inner, ast.ExtSlice):
                # 3.7 ExtSlice has "dims"
                inner = inner.dims[0]
            else:
                raise TypeError(
                    f"Unexpected subscript slice type {type(inner)} for"
                    f" node:\n{ast.dump(node)}"
                )
            sub_start = get_src_index(src, inner.lineno, inner.col_offset)
            end = find_closing_item(src, sub_start - 1, "[]")

        return src[start:end + 1]


def deepish_copy(obj, memo=None):
    """
    Returns the deepest possible copy of the given object, using
    copy.deepcopy wherever possible and making shallower copies
    elsewhere. Basically a middle-ground between copy.deepcopy and
    copy.copy.
    """
    if memo is None:
        memo = {}
    if id(obj) in memo:
        return memo[id(obj)]

    try:
        result = copy.deepcopy(obj) # not sure about memo dict compatibility
        memo[id(obj)] = result
        return result

    except Exception:
        if isinstance(obj, list):
            result = []
            memo[id(obj)] = result
            result.extend(deepish_copy(item, memo) for item in obj)
            return result
        elif isinstance(obj, tuple):
            # Note: no way to pre-populate the memo, but also no way to
            # construct an infinitely-recursive tuple without having
            # some mutable structure at some layer...
            result = (deepish_copy(item, memo) for item in obj)
            memo[id(obj)] = result
            return result
        elif isinstance(obj, dict):
            result = {}
            memo[id(obj)] = result
            result.update(
                {
                    deepish_copy(key, memo): deepish_copy(value, memo)
                    for key, value in obj.items()
                }
            )
            return result
        elif isinstance(obj, set):
            result = set()
            memo[id(obj)] = result
            result |= set(deepish_copy(item, memo) for item in obj)
            return result
        else:
            # Can't go deeper I guess
            try:
                result = copy.copy(obj)
                memo[id(obj)] = result
                return result
            except Exception:
                # Can't even copy (e.g., a module)
                result = obj
                memo[id(obj)] = result
                return result


def get_external_calling_frame():
    """
    Uses the inspect module to get a reference to the stack frame which
    called into the `optimism` module. Returns None if it can't find an
    appropriate call frame in the current stack.

    Remember to del the result after you're done with it, so that
    garbage doesn't pile up.
    """
    myname = __name__
    cf = inspect.currentframe()
    while (
        hasattr(cf, "f_back")
    and cf.f_globals.get("__name__") == myname
    ):
        cf = cf.f_back

    return cf


def get_module(stack_frame):
    """
    Given a stack frame, returns a reference to the module where the
    code from that frame was defined.

    Returns None if it can't figure that out.
    """
    other_name = stack_frame.f_globals.get("__name__", None)
    return sys.modules.get(other_name)


def get_filename(stack_frame):
    """
    Given a stack frame, returns the filename of the file in which the
    code which created that stack frame was defined. Returns None if
    that information isn't available.
    """
    return stack_frame.f_globals.get("__file__", None)


def get_code_line(stack_frame):
    """
    Given a stack frame, returns
    """
    return stack_frame.f_lineno


def evaluate_in_context(node, stack_frame):
    """
    Given an AST node which is an expression, returns the value of that
    expression as evaluated in the context of the given stack frame.

    Shallow copies of the stack frame's locals and globals are made in
    an attempt to prevent the code being evaluated from having any
    impact on the stack frame's values, but of course there's still some
    possibility of side effects...
    """
    expr = ast.Expression(node)
    code = compile(
        expr,
        stack_frame.f_globals.get("__file__", "__unknown__"),
        'eval'
    )
    return eval(
        code,
        copy.copy(stack_frame.f_globals),
        copy.copy(stack_frame.f_locals)
    )


def walk_ast_in_order(node):
    """
    Yields all of the descendants of the given node (or list of nodes)
    in execution order. Note that this has its limits, for example, if
    we run it on the code:

    ```py
    x = [A for y in C if D]
    ```

    It will yield the nodes for C, then y, then D, then A, and finally
    x, but in actual execution the nodes for D and A may be executed
    multiple times before x is assigned.
    """
    if node is None:
        pass # empty iterator
    elif isinstance(node, (list, tuple)):
        for child in node:
            yield from walk_ast_in_order(child)
    else: # must be an ast.something
        # Note: the node itself will be yielded LAST
        if isinstance(node, (ast.Module, ast.Interactive, ast.Expression)):
            yield from walk_ast_in_order(node.body)
        elif (
            hasattr(ast, "FunctionType")
        and isinstance(node, ast.FunctionType)
        ):
            yield from walk_ast_in_order(node.argtypes)
            yield from walk_ast_in_order(node.returns)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield from walk_ast_in_order(node.args)
            yield from walk_ast_in_order(node.returns)
            yield from walk_ast_in_order(reversed(node.decorator_list))
            yield from walk_ast_in_order(node.body)
        elif isinstance(node, ast.ClassDef):
            yield from walk_ast_in_order(node.bases)
            yield from walk_ast_in_order(node.keywords)
            yield from walk_ast_in_order(reversed(node.decorator_list))
            yield from walk_ast_in_order(node.body)
        elif isinstance(node, ast.Return):
            yield from walk_ast_in_order(node.value)
        elif isinstance(node, ast.Delete):
            yield from walk_ast_in_order(node.targets)
        elif isinstance(node, ast.Assign):
            yield from walk_ast_in_order(node.value)
            yield from walk_ast_in_order(node.targets)
        elif isinstance(node, ast.AugAssign):
            yield from walk_ast_in_order(node.value)
            yield from walk_ast_in_order(node.target)
        elif isinstance(node, ast.AnnAssign):
            yield from walk_ast_in_order(node.value)
            yield from walk_ast_in_order(node.annotation)
            yield from walk_ast_in_order(node.target)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            yield from walk_ast_in_order(node.iter)
            yield from walk_ast_in_order(node.target)
            yield from walk_ast_in_order(node.body)
            yield from walk_ast_in_order(node.orelse)
        elif isinstance(node, (ast.While, ast.If, ast.IfExp)):
            yield from walk_ast_in_order(node.test)
            yield from walk_ast_in_order(node.body)
            yield from walk_ast_in_order(node.orelse)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            yield from walk_ast_in_order(node.items)
            yield from walk_ast_in_order(node.items)
        elif isinstance(node, ast.Raise):
            yield from walk_ast_in_order(node.cause)
            yield from walk_ast_in_order(node.exc)
        elif isinstance(node, ast.Try):
            yield from walk_ast_in_order(node.body)
            yield from walk_ast_in_order(node.handlers)
            yield from walk_ast_in_order(node.orelse)
            yield from walk_ast_in_order(node.finalbody)
        elif isinstance(node, ast.Assert):
            yield from walk_ast_in_order(node.test)
            yield from walk_ast_in_order(node.msg)
        elif isinstance(node, ast.Expr):
            yield from walk_ast_in_order(node.value)
        # Import, ImportFrom, Global, Nonlocal, Pass, Break, and
        # Continue each have no executable content, so we'll yield them
        # but not any children

        elif isinstance(node, ast.BoolOp):
            yield from walk_ast_in_order(node.values)
        elif hasattr(ast, "NamedExpr") and isinstance(node, ast.NamedExpr):
            yield from walk_ast_in_order(node.value)
            yield from walk_ast_in_order(node.target)
        # TODO: HERE
        #elif isinstance(node, ast.BinOp):
        #    yield from walk_ast_in_order(node.left)
        #    yield from walk_ast_in_order(node.right)
        elif isinstance(node, ast.UnaryOp):
            yield from walk_ast_in_order(node.operand)
        elif isinstance(node, ast.Lambda):
            yield from walk_ast_in_order(node.args)
            yield from walk_ast_in_order(node.body)
        elif isinstance(node, ast.Dict):
            for i in range(len(node.keys)):
                yield from walk_ast_in_order(node.keys[i])
                yield from walk_ast_in_order(node.values[i])
        elif isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            yield from walk_ast_in_order(node.elts)
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
            yield from walk_ast_in_order(node.generators)
            yield from walk_ast_in_order(node.elt)
        elif isinstance(node, ast.DictComp):
            yield from walk_ast_in_order(node.generators)
            yield from walk_ast_in_order(node.key)
            yield from walk_ast_in_order(node.value)
        elif isinstance(node, (ast.Await, ast.Yield, ast.YieldFrom)):
            yield from walk_ast_in_order(node.value)
        elif isinstance(node, ast.Compare):
            yield from walk_ast_in_order(node.left)
            yield from walk_ast_in_order(node.comparators)
        elif isinstance(node, ast.Call):
            yield from walk_ast_in_order(node.func)
            yield from walk_ast_in_order(node.args)
            yield from walk_ast_in_order(node.keywords)
        elif isinstance(node, ast.FormattedValue):
            yield from walk_ast_in_order(node.value)
            yield from walk_ast_in_order(node.format_spec)
        elif isinstance(node, ast.JoinedStr):
            yield from walk_ast_in_order(node.values)
        elif isinstance(node, (ast.Attribute, ast.Starred)):
            yield from walk_ast_in_order(node.value)
        elif isinstance(node, ast.Subscript):
            yield from walk_ast_in_order(node.value)
            yield from walk_ast_in_order(node.slice)
        elif isinstance(node, ast.Slice):
            yield from walk_ast_in_order(node.lower)
            yield from walk_ast_in_order(node.upper)
            yield from walk_ast_in_order(node.step)
        # Constant and Name nodes don't have executable contents

        elif isinstance(node, ast.comprehension):
            yield from walk_ast_in_order(node.iter)
            yield from walk_ast_in_order(node.ifs)
            yield from walk_ast_in_order(node.target)
        elif isinstance(node, ast.ExceptHandler):
            yield from walk_ast_in_order(node.type)
            yield from walk_ast_in_order(node.body)
        elif isinstance(node, ast.arguments):
            yield from walk_ast_in_order(node.defaults)
            yield from walk_ast_in_order(node.kw_defaults)
            if hasattr(node, "posonlyargs"):
                yield from walk_ast_in_order(node.posonlyargs)
            yield from walk_ast_in_order(node.args)
            yield from walk_ast_in_order(node.vararg)
            yield from walk_ast_in_order(node.kwonlyargs)
            yield from walk_ast_in_order(node.kwarg)
        elif isinstance(node, ast.arg):
            yield from walk_ast_in_order(node.annotation)
        elif isinstance(node, ast.keyword):
            yield from walk_ast_in_order(node.value)
        elif isinstance(node, ast.withitem):
            yield from walk_ast_in_order(node.context_expr)
            yield from walk_ast_in_order(node.optional_vars)
        # alias and typeignore have no executable members
        # TODO: HERE
        elif isinstance(node, ast.BinOp):
            yield from walk_ast_in_order(node.left)
            yield from walk_ast_in_order(node.right)

        # Finally, yield this node itself
        yield node


def find_call_nodes_on_line(node, frame, function, lineno):
    """
    Given an AST node, a stack frame, a function object, and a line
    number, looks for all function calls which occur on the given line
    number and which are calls to the given function (as evaluated in
    the given stack frame).

    Note that calls to functions defined as part of the given AST cannot
    be found in this manner, because the objects being called are newly
    created and one could not possibly pass a reference to one of them
    into this function. For that reason, if the function argument is a
    string, any function call whose call part matches the given string
    will be matched. Normally only Name nodes can match this way, but if
    ast.unparse is available, the string will also attempt to match
    (exactly) against the unparsed call expression.

    Only calls that start on the given line number will match.

    The return value will be a list of ast.Call nodes, and they will be
    ordered in the same order that those nodes would be executed when
    the line of code is executed.
    """
    result = []
    for child in walk_ast_in_order(node):
        # only consider call nodes on the target line
        if (
            hasattr(child, "lineno")
        and child.lineno == lineno
        and isinstance(child, ast.Call)
        ):
            call_expr = child.func
            if isinstance(function, str):
                if (
                    (
                        isinstance(call_expr, ast.Name)
                    and call_expr.id == function
                    )
                 or (
                        isinstance(call_expr, ast.Attribute)
                    and call_expr.attr == function
                    )
                 or (
                        hasattr(ast, "unparse")
                    and ast.unparse(call_expr) == function
                    )
                ):
                    result.append(child)
            else:
                callee = evaluate_in_context(call_expr, frame)
                if callee is function:
                    result.append(child)

    return result


def assign_parents(root):
    """
    Given an AST node, assigns "parent" attributes to each sub-node
    indicating their parent AST node. Assigns None as the value of the
    parent attribute of the root node.
    """
    for node in ast.walk(root):
        for child in ast.iter_child_nodes(node):
            child.parent = node

    root.parent = None


def is_inside_call_func(node):
    """
    Given an AST node which has a parent attribute, traverses parents to
    see if this node is part of the func attribute of a Call node.
    """
    if not hasattr(node, "parent") or node.parent is None:
        return False
    if isinstance(node.parent, ast.Call) and node.parent.func is node:
        return True
    else:
        return is_inside_call_func(node.parent)


def get_my_location():
    """
    Fetches the filename and line number of the external module which
    calls into this module. Returns a dictionary with "file" and "line"
    keys.
    """
    frame = get_external_calling_frame()
    try:
        filename = get_filename(frame)
        lineno = get_code_line(frame)
    finally:
        del frame

    return { "file": filename, "line": lineno }


def get_my_context(function_or_name):
    """
    Returns a dictionary indicating the context of a function call,
    assuming that this function is called from within a function with the
    given name (or from within the given function). The result has the
    following keys:

    - file: The filename of the calling module
    - line: The line number on which the call to the function occurred
    - src: The source code string of the calling module
    - expr: An AST node storing the expression passed to the function
    - expr_src: The source code string of the expression passed to
        the function
    - values: A dictionary mapping source code fragments to their
        values, for each variable reference in the test expression. These
        are deepish copies of the values encountered.
    - relevant: A list of source code fragments which appear in the
        values dictionary which are judged to be most-relevant to the
        result of the test.

    Currently, the relevant list just lists any fragments which aren't
    found in the func slot of Call nodes, under the assumption that we
    don't care as much about the values of the functions we're calling.

    Prints a warning and returns a dictionary with just "filename" and
    "lineno" entries if the other context info is unavailable.
    """
    if isinstance(function_or_name, types.FunctionType):
        function_name = function_or_name.__name__
    else:
        function_name = function_or_name

    frame = get_external_calling_frame()
    try:
        filename = get_filename(frame)
        lineno = get_code_line(frame)
        try:
            with open(filename, 'r') as fin:
                src = fin.read()
        except Exception:
            print(
                "Warning: Unable to retrieve calling line's source.",
                file=sys.stderr
            )
            print(
                "Call is on line {} of module {} from file '{}'".format(
                    lineno,
                    frame.f_globals.get("__name__"),
                    filename
                ),
                file=sys.stderr
            )
            return {
                "file": filename,
                "line": lineno
            }

        src_node = ast.parse(src, filename=filename, mode='exec')
        candidates = find_call_nodes_on_line(
            src_node,
            frame,
            function_or_name,
            lineno
        )

        # What if there are zero candidates?
        if len(candidates) == 0:
            print(
                f"Warning: unable to find call node for {function_name}"
                f" on line {lineno} of file {filename}.",
                file=sys.stderr
            )
            return {
                "file": filename,
                "line": lineno
            }

        # Figure out how many calls to get_my_context have happened
        # referencing this line before, so that we know which call on
        # this line we might be
        prev_this_line = COMPLETED_PER_LINE\
            .setdefault(function_name, {})\
            .setdefault((filename, lineno), 0)
        match = candidates[prev_this_line % len(candidates)]

        # Record this call so the next one will grab the subsequent
        # candidate
        COMPLETED_PER_LINE[function_name][(filename, lineno)] += 1

        arg_expr = match.args[0]

        # Add .parent attributes
        assign_parents(arg_expr)

        # Source code for the expression
        expr_src = get_expr_src(src, match)

        # Prepare our result dictionary
        result = {
            "file": filename,
            "line": lineno,
            "src": src,
            "expr": arg_expr,
            "expr_src": expr_src,
            "values": {},
            "relevant": set()
        }

        # Walk expression to find values for each variable
        for node in ast.walk(arg_expr):
            # If it's potentially a reference to a variable...
            if isinstance(
                node,
                (ast.Attribute, ast.Subscript, ast.Name)
            ):
                key = get_ref_src(src, node)
                if key not in result["values"]:
                    # Don't re-evaluate multiply-reference expressions
                    # Note: we assume they won't take on multiple
                    # values; if they did, even our first evaluation
                    # would probably be inaccurate.
                    val = deepish_copy(evaluate_in_context(node, frame))
                    result["values"][key] = val
                    if not is_inside_call_func(node):
                        result["relevant"].add(key)

        return result

    finally:
        del frame


#-------------------------#
# Expectation re-checking #
#-------------------------#

def recheck_expectation(expectation, new_context):
    """
    Attempts to re-check a previously-established expectation (pulled
    from the `ALL_EXPECTATIONS` list). However, as part of that process,
    it tries to re-evaluate the test expression using the given new
    context values in addition to any captured values when an item isn't
    available in the new context. Note that only variable values, not
    sub-expression values, can be set in the new context or used from the
    previous context.

    This function will print out a success or failure message similar to
    the original message, and will return a new expectation dictionary
    including "met" and "message" keys based on the new evaluation.
    """
    sys.stderr.flush()
    case = expectation["case"]
    # Get new output + result value(s) note: we always capture output
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    old_input = builtins.input
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    builtins.input = _echoing_input
    try:
        sys.stderr.flush()
        to_eval = compile(
            ast.Expression(case["context"]["expr"]),
            case["context"]["file"],
            "eval"
        )
        env = {}
        old_vals = case["context"]["values"]
        env.update(old_vals)
        for key in env:
            if key in new_context:
                env[key] = new_context[key]
        # Note: we don't include any keys from the new context that won't
        # be used...
        sys.stderr.flush()
        new_result = eval(to_eval, env, env)
        new_output = sys.stdout.getvalue()
        # clean up addition from eval
        if "__builtins__" not in old_vals:
            del env["__builtins__"]
    except Exception:
        print("Error during re-evaluation of test case:", file=sys.stderr)
        sys.stderr.flush()
        raise
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        builtins.input = old_input

    new_context = deepish_copy(case["context"])
    new_context["values"] = env
    new_case = {
        "context": new_context,
        "result": new_result,
        "output": new_output if case["output"] is not None else None
    }
    new_expectation = {}
    new_expectation.update(expectation)
    new_expectation["case"] = new_case

    # Result will be placed in the "met" key of the new expectation
    _ = check_expectation(new_expectation, set_success=True)

    return new_expectation
