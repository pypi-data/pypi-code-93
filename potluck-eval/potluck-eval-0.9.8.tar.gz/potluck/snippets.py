"""
Code for defining examples that should be shown as part of instructions.

snippets.py

This module can be used in specifications files to define named examples,
which can then be compiled to HTML files using the --snippets option.
These examples will be evaluated within the context of the solution code,
and their output + return values will be formatted for display to the
students. By using snippets this way, as long as your solution file is
up-to-date, your example output will never be out-of-sync with what the
problem set is actually asking for.

Example usage:

```py
from potluck import snippets as sn

EXAMPLE = [
    {
        "key": "value",
        "key2": "value2",
    },
    {
        "key": "valueB",
        "key2": "value2B"
    }
]

sn.Variables(
    "vars", # snippet ID
    "<code>EXAMPLE</code> variable", # snippet displayed title
    (
        "A simple example of what the input data might look like, and"
        " the slightly more complex <code>DATA</code> variable provided"
        " in the starter code."
    ), # displayed snippet caption
    [ "EXAMPLE", "DATA" ] # list of variable names to display definitions of
).provide({ "EXAMPLE": EXAMPLE })
# provide overrides (or provides missing) solution module values

sn.FunctionCalls(
    "examples", # snippet ID
    "Example results", # title
    (
        "Some examples of what <code>processData</code> should return"
        " for various inputs, using the <code>EXAMPLE</code> and"
        " <code>DATA</code> variables shown above."
    ),
    # caption (note we're assuming the 'vars' snippet will be included
    # first, otherwise this caption doesn't make sense).
    [
        ("processData", (EXAMPLE, 1)),
        ("processData", (EXAMPLE, 2)),
        ("processData", (EXAMPLE, 3))",
        ("processData", (cu.SolnValue("DATA"), 3)),
    ], # list of function name, arguments tuples to evaluate
)

sn.RunModule(
    "run", # ID
    "Full output example", # title
    (
        "An example of what the output should look like when your code"
        " is run. Note that the blue text shows what inputs were"
        " provided in this example."
    ), # caption
).provide_inputs(["A", "B"]) # we're providing some inputs during the run
```

The various snippet classes like `Variable`, `Expressions`, and
`RunModule` each inherit from `potluck.specifications.TestGroup`
meaning that you can use the various modification methods from that
module (such as `provide_inputs` as shown above) to control exactly how
the code is run.
"""

import pprint
import textwrap
import re

import pygments

from . import specifications
from . import file_utils
from . import html_tools
from . import harness


#---------#
# Helpers #
#---------#

FMT_WIDTH = 80
"""
Line width we'll attempt to hit for formatting output nicely.
"""


def pprint_with_prefix(obj, prefix, indentation_level=0):
    """
    Returns a string representing the given object, as pprint.pformat
    would, except that:

    1. The first line includes the given prefix (as a string without
       repr applied to it; after indentation) and the wrapping of object
       values takes this into account.
    2. The entire representation is indented by the given indentation
       level (one space per level).
    """
    result = pprint.pformat(
        (prefix, obj),
        indent=1,
        width=FMT_WIDTH - indentation_level
    )

    # Strip off placeholder at beginning
    begins = len("({},".format(pprint.pformat(prefix)))
    rep = result[begins:-1] # one extra paren at end

    # remove extra indentation from tuple
    rep = textwrap.dedent(rep)

    # remove possible extra newline at start
    rep = rep.strip()

    # restore indent and add prefix
    return textwrap.indent(prefix + rep, ' ' * indentation_level)


#--------------#
# Registration #
#--------------#

SNIPPET_REGISTRY = {}
"""
All registered snippets, by defining module and then snippet ID.
"""


#----------------------------#
# Snippet class & subclasses #
#----------------------------#

class Snippet(specifications.TestGroup):
    """
    Common functionality for snippets. Don't instantiate this class;
    instead use one of the subclasses `Variables`, `Expressions`, or
    `RunModule`.

    Note that a `Snippet` is a `potluck.specifications.TestGroup`, from
    which it inherits provides a powerful interface for customizing
    behavior.
    """
    @staticmethod
    def base_context(task_info):
        """
        Creates a base context object for a snippet, given a task info
        object.
        """
        return {
            "task_info": task_info,
            "username": "__soln__",
            "submission_root": task_info["specification"].soln_path,
            "default_file": task_info["target"],
            "actual_file": task_info["target"]
        }

    def __init__(self, sid, title, caption, tests):
        """
        All `Snippet`s have a snippet ID, a title, a caption, and one or
        more tests. `tests` must be an iterable of unregistered
        `potluck.specifications.TestCase` objects.
        """
        # Set ourselves up as a TestGroup...
        super().__init__(sid, '_')

        # We store our sid, title & caption
        self.title = title
        self.caption = caption

        # What's the name of our spec file?
        self.spec_file = file_utils.get_spec_file_name()

        # Add our tests to ourself
        for t in tests:
            self.add(t)

        # Fetch the defining-module-specific registry
        reg = SNIPPET_REGISTRY.setdefault(
            file_utils.get_spec_module_name(),
            {}
        )

        # Prevent ID collision
        if sid in reg:
            raise ValueError(
                "Multiple snippets cannot be registered with the same"
                " ID ('{sid}')."
            )

        # Register ourself
        reg[sid] = self

        # A place to cache our compiled result
        self.cached_for = None
        self.cached_value = None

    def provide(self, vars_map):
        """
        A convenience function for providing the snippet with values not
        defined in the solution module. Under the hood, this uses
        `specifications.HasPayload.use_decorations`, so using that
        alongside this will not work (one will overwrite the other).
        """
        self.use_decorations(
            {
                k: (lambda _: v)
                for (k, v) in vars_map.items()
            },
            ignore_missing=True
        )

    # TODO: define replacements so that formatting of calls can use
    # varnames?

    def compile(self, base_context):
        """
        Runs the snippet, collects its results, and formats them as HTML.
        Returns a string containing HTML code for displaying the snippet
        (which assumes that the potluck.css stylesheet will be loaded).

        This method will always re-run the compilation process,
        regardless of whether a cached result is available, and will
        update the cached result. Use `Snippet.get_html` to recompile
        only as needed.

        Requires a base context object (see `potluck.contexts.Context`
        for the required structure).

        The returned HTML's outermost tag is a &lt;section&gt; tag with
        an id that starts with 'snippet:' and then ends with the
        snippet's ID value.
        """
        # Set up traceback-rewriting for the specifications module we
        # were defined in
        html_tools.set_tb_rewrite(
            base_context["task_info"]["specification"].__file__,
            "<task specification>"
        )
        html_tools.set_tb_rewrite(
            base_context["submission_root"],
            "<solution>"
        )

        # Create our Goal object
        goal = self.provide_goal()

        # Reset and evaluate our goal:
        goal.reset_network()
        goal.evaluate(base_context)

        # Grab the contexts that were used for each test
        if goal.test_in and len(goal.test_in["contexts"]) > 0:
            contexts = goal.test_in["contexts"]
        else:
            # This shouldn't be possible unless an empty list of
            # variables or functions was provided...
            raise ValueError(
                "A Snippet must have at least one context to compile."
                " (Did you pass an empty list to Variables or"
                " FunctionCalls?)"
            )

        # Include title & caption, and render each context to produce our
        # result
        result = (
            '<section class="snippet" id="snippet:{sid}">'
            '<div class="snippet_title">{title}</div>\n'
            '{caption}\n<pre>{snippet}</pre>'
            '</section>'
        ).format(
            sid=self.base_name,
            title=self.title,
            caption=self.caption,
            snippet=''.join(
                self.render_context(ctx.create(base_context))
                for ctx in contexts
            )
        )

        self.cached_for = base_context["task_info"]["id"]
        self.cached_value = result

        return result

    def get_html(self, task_info):
        """
        Returns the snippet value, either cached or newly-compiled
        depending on the presence of an appropriate cached value.
        """
        if self.cached_for == task_info["id"]:
            return self.cached_value
        else:
            return self.compile(Snippet.base_context(task_info))


class Variables(Snippet):
    """
    A snippet which shows the definition of one or more variables. Use
    this to display examples of input data, especially when you want to
    use shorter expressions in examples of running code. If you want to
    use variables that aren't defined in the solution module, use the
    `Snippet.provide` method (but note that that method is incompatible
    with using `specifications.HasPayload.use_decorations`).
    """
    def __init__(self, sid, title, caption, varnames):
        """
        A snippet ID, a title, and a caption are required, as is a list
        of strings indicating the names of variables to show definitions
        of. Use `Snippet.provide` to supply values for variables not in
        the solution module.
        """
        cases = [
            specifications.TestValue(
                varname,
                register=False
            )
            for varname in varnames
        ]
        super().__init__(sid, title, caption, cases)

    def render_context(self, context):
        """
        Renders a context created for goal evaluation as HTML markup for
        the definition of a variable, including Jupyter-notebook-style
        prompts.
        """
        varname = context["variable"]
        value = context["value"]

        # format value's repr using pprint, but leaving room for varname
        # = at beginning of first line
        rep = pprint_with_prefix(value, varname + ' = ')

        # Use pygments to generate HTML markup for our assignment
        markup = pygments.highlight(
            rep,
            pygments.lexers.PythonLexer(),
            pygments.formatters.HtmlFormatter()
        )
        # Note: markup will start a div and a pre we want to get rid of
        start = '<div class="highlight"><pre>'
        end = '</pre></div>\n'
        if markup.startswith(start):
            markup = markup[len(start):]
        if markup.endswith(end):
            markup = markup[:-len(end)] + '\n'
        return 'In [ ]: <code class="highlight">{}</code>'.format(markup)


class RunModule(Snippet):
    """
    A snippet which shows the output produced by running a module.
    Functions like `potluck.specifications.HasPayload.provide_inputs`
    can be used to control exactly what happens.

    The module to import is specified by the currently active file
    context (see `potluck.contexts.FileContext`).
    """
    def __init__(self, sid, title, caption):
        """
        A snippet ID, title, and caption are required.
        """
        cases = [
            specifications.TestImport(register=False)\
                .capture_output(capture_errors=True) # noqa E502
        ]
        super().__init__(sid, title, caption, cases)

    def render_context(self, context):
        """
        Renders a context created for goal evaluation as HTML markup for
        running a module. Includes a Jupyter-style prompt with %run magic
        syntax to show which file was run.
        """
        filename = context["filename"]
        captured = context.get("output", '')

        # Wrap faked inputs with spans so we can color them blue
        captured = re.sub(
            harness.FAKE_INPUT_PATTERN,
            r'<span class="input">\1</span>',
            captured
        )

        return (
            'In [ ]: <code class="magic">%run {filename}</code>\n'
            '<span class="printed">{captured}</span>'
        ).format(filename=filename, captured=captured)


class FunctionCalls(Snippet):
    """
    A snippet which shows the results (printed output and return values)
    of calling one or more functions. To control what happens in detail,
    use specialization methods from `potluck.specifications.HasPayload`
    and `potluck.specifications.HasContext`.
    """
    def __init__(self, sid, title, caption, calls):
        """
        A snippet ID, title, and caption are required, along with a list
        of function calls. Each entry in the list must be a tuple
        containing a function name followed by a tuple of arguments,
        and optionally, a dictionary of keyword arguments.
        """
        cases = [
            specifications.TestCase(
                fname,
                args,
                kwargs or {},
                register=False
            ).capture_output(capture_errors=True)
            for fname, args, kwargs in (
                map(lambda case: (case + (None,))[:3], calls)
            )
        ]
        super().__init__(sid, title, caption, cases)

    def render_context(self, context):
        """
        Renders a context created for goal evaluation as HTML markup for
        calling a function. Includes a Jupyter-style prompt for input as
        well as the return value.
        """
        fname = context["function"]
        value = context["value"]
        args = context["args"]
        kwargs = context["kwargs"]
        captured = context.get("output", '')

        # Figure out representations of each argument
        argreps = []
        for arg in args:
            argreps.append(pprint_with_prefix(arg, '', 1))

        for kw in kwargs:
            argreps.append(pprint_with_prefix(kwargs[kw], kw + "=", 1))

        # Figure out full function call representation
        oneline = "{}({})".format(
            fname,
            ', '.join(rep.strip() for rep in argreps)
        )
        if '\n' not in oneline and len(oneline) <= FMT_WIDTH:
            callrep = oneline
        else:
            callrep = "{}(\n{}\n)".format(fname, ',\n'.join(argreps))

        # Wrap faked inputs with spans so we can color them blue
        captured = re.sub(
            harness.FAKE_INPUT_PATTERN,
            r'<span class="input">\1</span>',
            captured
        )

        result = 'In [ ]: <code class="highlight">{}</code>\n'.format(
            callrep
        )

        if captured:
            result += '<span class="printed">{}</span>\n'.format(captured)

        result += 'Out [ ]: <code class="highlight">{}</code>\n'.format(
            pprint_with_prefix(value, "Out [ ]:")[8:]
        )

        return result

# TODO: A real Expressions class, with preservation of state!?


#--------#
# Lookup #
#--------#

def list_snippets(task_info):
    """
    Returns a list containing all snippet IDs (strings) for the given
    task (as a task info dictionary).
    """
    reg = SNIPPET_REGISTRY.get(task_info["specification"].__name__, {})
    return list(reg.keys())


def get_html(task_info, sid):
    """
    Retrieves the HTML code (a string) for the snippet with the given ID
    in the given task (as a task info dictionary). Returns None if there
    is no such snippet.
    """
    reg = SNIPPET_REGISTRY.get(task_info["specification"].__name__, {})
    if sid not in reg:
        return None
    return reg[sid].get_html(task_info)
