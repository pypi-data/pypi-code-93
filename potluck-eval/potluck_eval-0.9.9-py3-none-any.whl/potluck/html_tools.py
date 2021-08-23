# -*- coding: utf-8 -*-
"""
Tools for building HTML strings.

html_tools.py
"""

import sys
import traceback
import difflib
import os
import re

from . import phrasing
from . import file_utils


# Figure out how to escape HTML (2/3 compatibility)
if sys.version_info[0] < 3:
    # use cgi.escape instead of html.escape
    import cgi
    escape = cgi.escape
else:
    # use html.escape
    import html
    escape = html.escape


#---------#
# Globals #
#---------#

STATUS_SYMBOLS = {
    "unknown": " ", # non-breaking space
    "not applicable": "–",
    "failed": "✗",
    "partial": "~",
    "accomplished": "✓",
}
"""
The symbols used as shorthand icons for each goal accomplishment status.
"""

SHORT_REPR_LIMIT = 160
"""
Limit in terms of characters before we try advanced formatting.
"""


#-----------#
# Functions #
#-----------#

def len_as_text(html_string):
    """
    Returns an approximate length of the given string in characters
    assuming HTML tags would not be visible and HTML entities would be
    single characters.
    """
    without_tags = re.sub("<[^>]*>", "", html_string)
    without_entities = re.sub("&[#0-9A-Za-z]+;", ".", without_tags)
    return len(without_entities)


def wrapped_fragments(line, width=80, indent=''):
    """
    Wraps a single line of text into one or more lines, yielding a
    sequence of strings. Breaks on spaces/tabs only, and does not
    attempt any kind of optimization but simply breaks greedily as close
    to the given width as possible. The given indentation will be
    prepended to each line, including the first.
    """
    # Apply indentation
    line = indent + line

    if len(line) <= width:
        yield line
        return

    # Look backwards from width for a place we can break at
    breakpoint = None
    for i in range(width, len(indent), -1):
        # (note: breaking on first char doesn't make sense)
        c = line[i]
        if c in ' \t':
            breakpoint = i
            break

    # If we didn't find a breakpoint that would respect the
    # target width, find the first one we can
    if breakpoint is None:
        for i in range(width, len(line)):
            c = line[i]
            if c in ' \t':
                breakpoint = i

    if breakpoint is None:
        # Can't find any breakpoint :'(
        yield line
    else:
        first = line[:breakpoint]
        rest = line[breakpoint + 1:]
        yield first
        # Note: avoiding yield from because we want Python2 compatibility
        for item in wrapped_fragments(rest, width, indent):
            yield item


def wrap_text_with_indentation(text, width=80):
    """
    Word-wraps the given text, respecting indentation, to the given
    width. If there is a line that's more-indented than the given width,
    wrapping will happen as aggressively as possible after that. Wraps
    only at spaces. Replicates tab/space mix of indentation in the
    output.

    This function does NOT optimize for line lengths, and instead just
    breaks each line greedily as close to the given width as possible.
    """
    lines = text.splitlines()
    wrapped = []
    for line in lines:
        if len(line) <= width:
            wrapped.append(line)
        else:
            indentation = ''
            for c in line:
                if c in ' \t':
                    indentation += c
                else:
                    break

            wrapped.extend(
                wrapped_fragments(
                    line[len(indentation):],
                    width,
                    indentation
                )
            )

    return '\n'.join(wrapped)


def create_help_button(help_content):
    """
    Returns an HTML string for a button that can be clicked to display
    help. The button will have a question mark when collapsed and a dash
    when expanded, and the help will be displayed in a box on top of
    other content to the right of the help button.
    """
    return (
        '<details class="help_button">\n'
      + '<summary aria-label="More details"></summary>\n'
      + '<div class="help">{}</div>\n'
      + '</details>\n'
    ).format(help_content)


def build_list(items, ordered=False):
    """
    Builds an HTML ul tag, or an ol tag if `ordered` is set to True.
    Items must be a list of (possibly HTML) strings.
    """
    tag = "ol" if ordered else "ul"
    return (
        "<{tag}>\n{items}\n</{tag}>"
    ).format(
        tag=tag,
        items="\n".join("<li>{}</li>".format(item) for item in items)
    )


def build_html_details(title, content, classes=None):
    """
    Builds an HTML details element with the given title as its summary
    and content inside. The classes are attached to the details element
    if provided, and should be a string.
    """
    return (
        '<details{}><summary>{}</summary>{}</details>'
    ).format(
        ' class="{}"'.format(classes) if classes is not None else "",
        title,
        content
    )


def build_html_tabs(tabs):
    """
    Builds an HTML structure which uses several tab elements and a
    scrollable region to implement a multiple-tabs structure. The given
    tabs list should contain title, content pairs, where both titles and
    contents are strings that may contain HTML code.

    `resources/potluck.js` defines the Javascript code necessary for the
    tabs to work correctly.
    """
    tab_pieces = [
        (
            """
<li
 class='tab{selected}'
 tabindex="0"
 aria-label="Activate to display {title} after this list."
>
{title}
</li>
"""         .format(
                selected=" selected" if i == 0 else "",
                title=title
            ),
            """
<section
 class='tab-content{selected}'
 tabindex="0"
>
{content}
</section>
"""         .format(
                selected=" selected" if i == 0 else "",
                content=content
            )
        )
        for i, (title, content) in enumerate(tabs)
    ]
    tabs = '\n\n'.join([piece[0] for piece in tab_pieces])
    contents = '\n\n'.join([piece[1] for piece in tab_pieces])
    return """
<div class="tabs" role="presentation">
  <ul class="tabs-top">
{tabs}
  </ul>
  <div class="tabs-bot" aria-live="polite">
{contents}
  </div>
</div>
""" .format(
        tabs=tabs,
        contents=contents
    )


def fileslug(filename):
    """
    Returns a safe-for-HTML-ID version of the given filename.
    """
    return filename\
        .replace(os.path.sep, '-')\
        .replace('.py', '')\
        .replace('.', '-')


def line_id(taskid, filename, lineno):
    """
    Generates an HTML ID for a code line, given the task ID, file name,
    and line number.
    """
    return "{taskid}_{slug}_codeline_{lineno}".format(
        taskid=taskid,
        slug=fileslug(filename),
        lineno=lineno
    )


def block_id(taskid, filename):
    """
    Generates an HTML ID for a code block, given the task ID and file
    name.
    """
    return "{taskid}_code_{slug}".format(
        taskid=taskid,
        slug=fileslug(filename)
    )


def html_link_to_line(taskid, filename, lineno):
    """
    Returns an HTML anchor tag (as a string) that links to the specified
    line of code in the specified file of the specified task.

    `resources/potluck.js` includes code that will add click handlers to
    these links so that the line being jumped to gets highlighted.
    """
    lineid = line_id(taskid, filename, lineno)
    return (
        '<a class="lineref" data-lineid="{lineid}"'
        ' href="#{lineid}">{lineno}</a>'
    ).format(
        lineid=lineid,
        lineno=lineno
    )


def html_output_details(raw_output, title="Output"):
    """
    Takes raw program output and turns it into an expandable details tag
    with pre formatting.
    """
    return (
        '<details>\n'
      + '<summary>{}</summary>\n'
      + '<pre class="printed_output">{}</pre>\n'
        '</details>'
    ).format(
        title,
        raw_output
    )


def html_diff_table(
    output,
    reference,
    out_title='Actual output',
    ref_title='Expected output',
    joint_title=None,
    line_limit=300,
    trim_lines=1024
):
    """
    Uses difflib to create and return an HTML string that encodes a table
    comparing two (potentially multi-line) outputs. If joint_title is
    given, the result is wrapped into a details tag with that title and
    class diff_table.

    If line_limit is not None (the default is 300) then only that many
    lines of each output will be included, and a message about the
    limitation will be added.

    If the trim_lines value is None (the default is 1024) then the full
    value of every line will be included no matter how long it is,
    otherwise lines beyond that length will be trimmed to that length
    (with three periods added to indicate this).
    """
    if isinstance(output, str):
        output = output.split('\n')
    if isinstance(reference, str):
        reference = reference.split('\n')

    if line_limit and len(output) > line_limit or len(reference) > line_limit:
        result = "(comparing the first {})<br>\n".format(
            phrasing.obj_num(line_limit, "line")
        )
        output = output[:line_limit]
        reference = reference[:line_limit]
    else:
        result = ""

    if (
        trim_lines
    and (
            any(len(line) > trim_lines for line in output)
         or any(len(line) > trim_lines for line in reference)
        )
    ):
        result += (
            "(comparing the first {} on each line)<br>\n"
        ).format(phrasing.obj_num(trim_lines, "character"))
        output = [
            line[:trim_lines] + ('...' if len(line) > trim_lines else '')
            for line in output
        ]
        reference = [
            line[:trim_lines] + ('...' if len(line) > trim_lines else '')
            for line in reference
        ]

    result += difflib.HtmlDiff().make_table(
        output,
        reference,
        fromdesc=out_title,
        todesc=ref_title,
    )
    if joint_title is None:
        return result
    else:
        return build_html_details(joint_title, result, classes="diff_table")


def status_css_class(status):
    """
    Returns the CSS class used to indicate the given status.
    """
    return "status_" + status.replace(' ', '_')


def build_status_indicator(status):
    """
    Builds a single div that indicates the given goal accomplishment
    status.
    """
    status_class = status_css_class(status)
    status_symbol = STATUS_SYMBOLS.get(status, "!")
    return '<div class="goal_status {stc}">{sy}</div>'.format(
        stc=status_class,
        sy=status_symbol
    )


def indent(string, indent):
    """
    Indents a string using spaces. Newlines will be '\\n' afterwards.
    """
    lines = string.splitlines()
    return '\n'.join(' ' * indent + line for line in lines)


def big_repr(thing):
    """
    A function that works like repr, but with some extra formatting for
    special known cases when the results would be too large.
    """
    base = repr(thing)
    if len(base) > SHORT_REPR_LIMIT:
        if type(thing) in (tuple, list, set): # NOT isinstance
            # left and right delimeters
            ld, rd = repr(type(thing)())
            stuff = ',\n'.join(big_repr(elem) for elem in thing)
            return ld + '\n' + indent(stuff, 2) + '\n' + rd
        elif type(thing) is dict: # NOT isinstance
            stuff = ',\n'.join(
                big_repr(key) + ": " + big_repr(value)
                for key, value in thing.items()
            )
            return '{\n' + indent(stuff, 2) + '\n}'
        elif type(thing) is str and '\n' in thing:
            return "'''\\\n{thing}'''".format(thing=thing)
        # else we fall out and return base

    return base


def truncate(text, limit=50000, tag='\n...truncated...'):
    """
    Truncates the given text so that it does not exceed the given limit
    (in terms of characters; default 50K)

    If the text actually is truncated, the string '\\n...truncated...'
    will be added to the end of the result to indicate this, but an
    alternate tag may be specified; the tag characters are not counted
    against the limit, so it's possible for this function to actually
    make a string longer if it starts out longer than the limit by less
    than the length of the tag.
    """
    if len(text) > limit:
        return text[:limit] + tag
    else:
        return text


def build_display_box(text):
    """
    Creates a disabled textarea element holding the given text. This
    allows for a finite-size element to contain (potentially a lot) of
    text that the user can scroll through or even search through.
    """
    # TODO: A disabled textarea is such a hack! Instead, use an inner pre
    # inside an outer div with CSS to make it scrollable.
    return '<textarea class="display_box" disabled>{text}</textarea>'.format(
        text=text
    )


def dynamic_html_repr(thing, reasonable=200, limit=10000):
    """
    A dynamic representation of an object which is simply a pre-formatted
    string for objects whose representations are reasonably small, and
    which turns into a display box for representations which are larger,
    with text being truncated after a (very large) limit.

    The threshold for reasonably small representations as well as the
    hard limit may be customized; use None for the hard limit to disable
    truncation entirely (but don't complain about file sizes if you do).
    """
    rep = big_repr(thing)
    if len(rep) <= reasonable:
        return '<pre class="short_repr">{rep}</pre>'.format(rep=rep)
    else:
        return build_display_box(truncate(rep, limit))


def html_traceback(exc=None, title=None, linkable=None):
    """
    In an exception handler, returns an HTML string that includes the
    exception type, message, and traceback. Must be called from an except
    clause, unless an exception object with a __traceback__ value is
    provided.

    If title is given and not None, a details tag will be returned
    using that title, which can be expanded to show the traceback,
    otherwise just a pre tag is returned containing the traceback.

    If linkable is given, it must be a dictionary mapping filenames to
    task IDs, and line numbers of those files which appear in the
    traceback will be turned into links to those lines.
    """
    result = escape(string_traceback(exc))
    if linkable:
        for fn in linkable:
            taskid = linkable[fn]

            def replacer(match):
                link = html_link_to_line(taskid, fn, int(match.group(1)))
                return '{}&quot;, line {},'.format(fn, link)

            pat = r'{}&quot;, line ([0-9]+),'.format(fn)
            result = re.sub(pat, replacer, result)

    pre = '<pre class="traceback">\n{}\n</pre>'.format(result)
    if title is not None:
        return build_html_details(title, pre, "error")
    else:
        return pre


REWRITES = {
    file_utils.potluck_src_dir(): "<potluck>"
}
"""
The mapping from filenames to replacements to be used for rewriting
filenames in tracebacks.
"""


def set_tb_rewrite(filename, rewrite_as):
    """
    Sets up a rewriting rule that will be applied to string and HTML
    tracebacks. You must provide the filename that should be rewritten,
    and the string to replace it with. Set rewrite_as to None to remove a
    previously-established rewrite rule.
    """
    global REWRITES
    REWRITES[filename] = rewrite_as


def string_traceback(exc=None):
    """
    When called in an exception handler, returns a multi-line string
    including what Python would normally print: the exception type,
    message, and a traceback. You can also call it anywhere if you can
    provide an exception object which has a __traceback__ value.

    The traceback gets obfuscated by replacing full file paths that start
    with the potluck directory with just the package directory and
    filename, and by replacing full file paths that start with the spec
    directory with just the task ID and then the file path from the spec
    directory (usually starter/, soln/, or the submitted file itself).
    """
    sfd = os.path.split(file_utils.get_spec_file_name())[0]
    rewrites = {}
    rewrites.update(REWRITES)
    if sfd:
        rewrites[sfd] = "<task>"

    if exc is None:
        raw = traceback.format_exc()
    else:
        raw = ''.join(traceback.format_tb(exc.__traceback__) + [ str(exc) ])

    return rewrite_traceback_filenames(raw, rewrites)


def rewrite_traceback_filenames(raw_traceback, prefix_map=None):
    """
    Accepts a traceback as a string, and returns a modified string where
    filenames have been altered by replacing the keys of the given
    prefix_map with their values. In addition, filenames which include a
    directory that ends in "__tmp" will have all directory entries up to
    and including that one stripped from their path.

    If no prefix map is given, the value of REWRITES will be used.
    """
    prefix_map = prefix_map or REWRITES
    result = raw_traceback
    for prefix in prefix_map:
        replace = prefix_map[prefix]
        result = result.replace(
            'File "{prefix}'.format(prefix=prefix),
            'File "{replace}'.format(replace=replace)
        )

    result = re.sub(
        'File ".*__tmp' + os.path.sep,
        'File "<submission>/',
        result
    )

    return result


def function_def_code_tags(fn_name, args_pattern, announce=None):
    """
    Returns a tuple containing two strings of HTML code used to represent
    the given function definition in both short and long formats. The
    short format just lists the first acceptable definition, while the
    long format lists all of them. Note that both fn_name and
    args_pattern may be lists of strings instead of strings; see
    function_def_patterns.
    """
    if isinstance(fn_name, str):
        names = [fn_name]
    else:
        names = list(fn_name)

    # If there are specific args we can give users more info about what
    # they need to do.
    if isinstance(args_pattern, str):
        specific_names = [
            "{}({})".format(name, args_pattern) for name in names
        ]
    else:
        specific_names = names

    # Figure out what we're announcing as:
    if announce is None:
        announce = specific_names[0]

    # Make code tag and detailed code tag:
    code_tag = "<code>{}</code>".format(announce)
    details_code = phrasing.comma_list(
        ["<code>{}</code>".format(n) for n in specific_names],
        junction="or"
    )

    # Add a comment about the number of arguments required
    if isinstance(args_pattern, int):
        with_n = " with {} {}".format(
            args_pattern,
            phrasing.plural(args_pattern, "argument")
        )
        code_tag += with_n
        details_code += with_n

    return code_tag, details_code


def function_call_code_tags(fn_name, args_pattern, is_method=False):
    """
    Works like `potluck.patterns.function_call_patterns`, but generates a
    pair of HTML strings with summary and detailed descriptions of the
    function call. In that sense it's also similar to
    `function_def_code_tags`, except that it works for a function call
    instead of a function definition.

    If the args_pattern is "-any arguments-", the parentheses for the
    function call will be omitted entirely.
    """
    if isinstance(fn_name, str):
        names = [fn_name]
    else:
        names = list(fn_name)

    # If there are specific args we can give users more info about what
    # they need to do.
    if args_pattern == "-any arguments-":
        specific_names = names
    elif isinstance(args_pattern, str):
        if is_method:
            specific_names = [
                ".{}({})".format(name, args_pattern)
                for name in names
            ]
        else:
            specific_names = [
                "{}({})".format(name, args_pattern)
                for name in names
            ]
    else:
        specific_names = names

    # Make code tag and detailed code tag:
    code_tag = "<code>{}</code>".format(
        escape(specific_names[0])
    )

    details_code = phrasing.comma_list(
        [
            "<code>{}</code>".format(escape(name))
            for name in specific_names
        ],
        junction="or"
    )

    return code_tag, details_code


def args_repr_list(args, kwargs):
    """
    Creates an HTML string representation of the given positional and
    keyword arguments, as a bulleted list.
    """
    arg_items = []
    for arg in args:
        arg_items.append(dynamic_html_repr(arg))

    for kw in kwargs:
        key_repr = dynamic_html_repr(kw)
        val_repr = dynamic_html_repr(kwargs[kw])
        arg_items.append(key_repr + "=" + val_repr)

    return build_list(arg_items)
