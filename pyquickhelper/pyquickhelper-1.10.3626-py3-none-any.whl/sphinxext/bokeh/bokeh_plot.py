"""
@file
@brief Modified version of `bokeh_plot.py <https://github.com/bokeh/bokeh/blob/master/bokeh/sphinxext/bokeh_plot.py>`_,
`LICENSE <https://github.com/bokeh/bokeh/blob/master/LICENSE.txt>`_.

Include :epkg:`bokeh` plots in Sphinx HTML documentation.
For other output types, the placeholder text ``[graph]`` will
be generated.
The ``bokeh-plot`` directive can be used by either supplying,
**a path to a source file** as the argument to the directive::

    .. bokeh-plot:: path/to/plot.py

.. note::
    .py scripts are not scanned automatically! In order to include
    certain directories into .py scanning process use following directive
    in sphinx conf.py file: bokeh_plot_pyfile_include_dirs = ["dir1","dir2"]

**Inline code** as the content of the directive::

 .. bokeh-plot::

     from bokeh.plotting import figure, output_file, show

     output_file("example.html")

     x = [1, 2, 3, 4, 5]
     y = [6, 7, 6, 4, 5]

     p = figure(title="example", plot_width=300, plot_height=300)
     p.line(x, y, line_width=2)
     p.circle(x, y, size=10, fill_color="white")

     show(p)

This directive also works in conjunction with Sphinx autodoc, when
used in docstrings.

The ``bokeh-plot`` directive accepts the following options:

source-position (enum('above', 'below', 'none')):
    Where to locate the the block of formatted source
    code (if anywhere).

linenos (bool):
    Whether to display line numbers along with the source.

Examples
--------

The inline example code above produces the following output:

.. bokeh-plot::

    from bokeh.plotting import figure, output_file, show

    output_file("example.html")

    x = [1, 2, 3, 4, 5]
    y = [6, 7, 6, 4, 5]

    p = figure(title="example", plot_width=300, plot_height=300)
    p.line(x, y, line_width=2)
    p.circle(x, y, size=10, fill_color="white")

    show(p)
"""

# -----------------------------------------------------------------------------
# Boilerplate
# -----------------------------------------------------------------------------
# use the wrapped sphinx logger
from sphinx.util import logging  # isort:skip
log = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# Standard library imports
from os import getenv
from os.path import basename, dirname, join
from uuid import uuid4

# External imports
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives import choice, flag
from sphinx.errors import SphinxError
from sphinx.util import copyfile, ensuredir, status_iterator
from sphinx.util.nodes import set_source_info

# Bokeh imports
from bokeh.document import Document
from bokeh.embed import autoload_static
from bokeh.model import Model

# Bokeh imports
from bokeh.sphinxext.example_handler import ExampleHandler
from bokeh.sphinxext.util import get_sphinx_resources

# -----------------------------------------------------------------------------
# Globals and constants
# -----------------------------------------------------------------------------

__all__ = (
    'BokehPlotDirective',
    'setup',
)

# -----------------------------------------------------------------------------
# General API
# -----------------------------------------------------------------------------


class BokehPlotDirective(Directive):

    has_content = True
    optional_arguments = 2

    option_spec = {
        'source-position': lambda x: choice(x, ('below', 'above', 'none')),
        'linenos': lambda x: True if flag(x) is None else False,
    }

    def run(self):

        env = self.state.document.settings.env

        # filename *or* python code content, but not both
        if self.arguments and self.content:
            raise SphinxError(
                "bokeh-plot:: directive can't have both args and content")

        # need docname not to look like a path
        docname = env.docname.replace("/", "-")

        if self.content:
            log.debug("[bokeh-plot] handling inline example in %r", env.docname)
            path = env.bokeh_plot_auxdir  # code runner just needs any real path
            source = '\n'.join(self.content)
        else:
            try:
                log.debug("[bokeh-plot] handling external example in %r: %s",
                          env.docname, self.arguments[0])
                path = self.arguments[0]
                if not path.startswith("/"):
                    path = join(env.app.srcdir, path)
                source = open(path).read()
            except Exception as e:
                raise SphinxError(f"{env.docname}: {e!r}")

        js_name = "bokeh-plot-%s-external-%s.js" % (uuid4().hex, docname)

        try:
            (script, js, js_path, source) = _process_script(
                source, path, env, js_name)
        except Exception as e:
            raise RuntimeError(
                "Sphinx bokeh-plot exception: \n\n%s\n\n Failed on:\n\n %s" % (e, source))
        env.bokeh_plot_files[js_name] = (
            script, js, js_path, source, dirname(env.docname))

        # use the source file name to construct a friendly target_id
        target_id = "%s.%s" % (env.docname, basename(js_path))
        target = nodes.target('', '', ids=[target_id])
        result = [target]

        linenos = self.options.get('linenos', False)
        code = nodes.literal_block(
            source, source, language="python", linenos=linenos, classes=[])
        set_source_info(self, code)

        source_position = self.options.get('source-position', 'below')

        if source_position == "above":
            result += [code]

        result += [nodes.raw('', script, format="html")]

        if source_position == "below":
            result += [code]

        return result

# -----------------------------------------------------------------------------
# Dev API
# -----------------------------------------------------------------------------


def builder_inited(app):
    app.env.bokeh_plot_auxdir = join(app.env.doctreedir, 'bokeh_plot')
    if app.env.srcdir is not None and "IMPOSSIBLE:TOFIND" not in app.env.srcdir:
        # sphinx/_build/doctrees/bokeh_plot
        # sphinx/_build/doctrees/bokeh_plot
        ensuredir(app.env.bokeh_plot_auxdir)

    if not hasattr(app.env, 'bokeh_plot_files'):
        app.env.bokeh_plot_files = {}


def build_finished(app, exception):
    files = set()

    # Sphinx 3.0.0
    for docpath, element in app.env.bokeh_plot_files.items():
        if len(element) == 4:
            script, js, js_path, source = element
        elif len(element) == 5:
            script, js, js_path, source, docpath = element
        else:
            raise ValueError("\n".join([
                str(type(element)),
                str(len(element)),
                str(element),
            ])) from e
        files.add((js_path, docpath))

    files_iter = status_iterator(sorted(files),
                                 'copying bokeh-plot files... ',
                                 'brown',
                                 len(files),
                                 app.verbosity,
                                 stringify_func=lambda x: basename(x[0]))

    for (file, docpath) in files_iter:
        target = join(app.builder.outdir, docpath, basename(file))
        ensuredir(dirname(target))
        try:
            copyfile(file, target)
        except OSError as e:
            raise SphinxError(
                'cannot copy local file %r, reason: %s' % (file, e))


def setup(app):
    ''' Required Sphinx extension setup function. '''
    app.add_config_value('bokeh_plot_pyfile_include_dirs', [], 'html')
    app.add_directive('bokeh-plot', BokehPlotDirective)
    app.add_config_value('bokeh_missing_google_api_key_ok', True, 'html')
    app.connect('builder-inited', builder_inited)
    app.connect('build-finished', build_finished)

# -----------------------------------------------------------------------------
# Private API
# -----------------------------------------------------------------------------


def _process_script(source, filename, env, js_name, use_relative_paths=False):
    # Explicitly make sure old extensions are not included until a better
    # automatic mechanism is available
    Model._clear_extensions()

    # quick and dirty way to inject Google API key
    if "GOOGLE_API_KEY" in source:
        GOOGLE_API_KEY = getenv('GOOGLE_API_KEY')
        if GOOGLE_API_KEY is None:
            if env.config.bokeh_missing_google_api_key_ok:
                GOOGLE_API_KEY = "MISSING_API_KEY"
            else:
                raise SphinxError("The GOOGLE_API_KEY environment variable is not set. Set GOOGLE_API_KEY to a valid API key, "
                                  "or set bokeh_missing_google_api_key_ok=True in conf.py to build anyway (with broken GMaps)")
        run_source = source.replace("GOOGLE_API_KEY", GOOGLE_API_KEY)
    else:
        run_source = source

    c = ExampleHandler(source=run_source, filename=filename)
    d = Document()
    c.modify_document(d)
    if c.error:
        raise RuntimeError(c.error_detail)

    resources = get_sphinx_resources()
    js_path = join(env.bokeh_plot_auxdir, js_name)
    js, script = autoload_static(d.roots[0], resources, js_name)

    if "IMPOSSIBLE:TOFIND" not in js_path:
        with open(js_path, "w") as f:
            f.write(js)

    return (script, js, js_path, source)

# -----------------------------------------------------------------------------
# Code
# -----------------------------------------------------------------------------
