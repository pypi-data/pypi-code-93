#                   Copyright (c) 2021, Serum Studio

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from hype.errors import *

import math
import sys
import threading
import time
import warnings
from contextlib import contextmanager
from itertools import chain
from itertools import islice
from itertools import repeat

try:
    from alive_progress.core.configuration import config_handler
    from alive_progress.animations.utils import spinner_player

    from alive_progress.core.logging_hook import install_logging_hook
    from alive_progress.core.logging_hook import uninstall_logging_hook

    from alive_progress.core.timing import gen_simple_exponential_smoothing_eta
    from alive_progress.core.timing import to_elapsed_text
    from alive_progress.core.timing import to_eta_text

    from alive_progress.core.utils import clear_traces
    from alive_progress.core.utils import render_title
    from alive_progress.core.utils import sanitize_text_marking_wide_chars
    from alive_progress.core.utils import get_terminal_size

except ModuleNotFoundError:
    pass

from hype.cursor import hide as hide_cursor
from hype.cursor import show as show_cursor
from hype.constants import rule_colors
from hype.constants import COLOR_SUPPORTED
from hype.errors import PluginError


@contextmanager
def progressbar(
    total=None, title=None, calibrate=None, bar_color=None, title_color=None, **options
):
    """
    Hype Progressbar inherited from `alive_bar` and add some Features.

    Parameters:
    ---
        Similar to `alive_bar` but then added 2 options:

        - `bar_color (str)`:
            Set the color of the bar.

        - `title_color (str)`:
            Set the title color.


    An alive progress bar to keep track of lengthy operations.
    It has a spinner indicator, elapsed time, throughput and ETA.
    When the operation finishes, a receipt is displayed with statistics.
    If the code is executed in a headless environment, ie without a
    connected tty, all features are disabled but the final receipt.
    Another cool feature is that it tracks the actual count in regard of the
    expected count. So it will look different if you send more (or less) than
    expected.

    Also, the bar installs a hook in the system print function that cleans
    any garbage out of the terminal, allowing you to print() effortlessly
    while using the bar.
    Use it like this:

    >>> from alive_progress import alive_bar
    ... with alive_bar(123, 'Title') as bar:  # <-- expected total and bar title
    ...     for item in <iterable>:
    ...         # process item
    ...         bar()  # makes the bar go forward
    The `bar()` method should be called whenever you want the bar to go forward.
    You usually call it in every iteration, but you could do it only when some
    criteria match, depending on what you want to monitor.
    While in a progress bar context, you have two ways to output messages:
      - the usual Python `print()` statement, which will properly clean the line,
        print an enriched message (including the current bar position) and
        continue the bar right below it;
      - the `bar.text('message')` call, which sets a situational message right within
        the bar, usually to display something about the items being processed or the
        phase the processing is in.
    If the bar is over or underused, it will warn you!
    To test all supported scenarios, you can do this:
    >>> for x in 1000, 1500, 700, 0:
    ...    with alive_bar(x) as bar:
    ...        for i in range(1000):
    ...            time.sleep(.005)
    ...            bar()
    Expected results are these (but you have to see them in motion!):
    |████████████████████████████████████████| 1000/1000 [100%] in 6.0s (167.93/s)
    |██████████████████████████▋⚠            | (!) 1000/1500 [67%] in 6.0s (167.57/s)
    |████████████████████████████████████████✗ (!) 1000/700 [143%] in 6.0s (167.96/s)
    |████████████████████████████████████████| 1000 in 5.8s (171.91/s)
    Args:
        total (Optional[int]): the total expected count

        title (Optional[str]): the title, will be printed whenever there's no custom message

        calibrate (int): maximum theoretical throughput to calibrate animation speed
            (cannot be in the global configuration because it depends on the current mode)

        **options: custom configuration options, which override the global configuration:

            length (int): number of characters to render the animated progress bar

            spinner (Union[str, object]): the spinner to be used in all renditions
                it's a predefined name in `show_spinners()`, or a custom spinner

            bar (Union[str, object]): bar to be used in definite and both manual modes
                it's a predefined name in `show_bars()`, or a custom bar

            unknown (Union[str, object]): bar to be used in unknown mode (whole bar is a spinner)
                it's a predefined name in `show_spinners()`, or a custom spinner

            theme (str): theme name in alive_progress.THEMES

            force_tty (bool): runs animations even without a tty (pycharm terminal for example)

            manual (bool): set to manually control percentage

            enrich_print (bool): includes the bar position in print() and logging messages

            title_length (int): fixed title length, or 0 for unlimited
    """

    if bar_color or title_color and not COLOR_SUPPORTED:
        raise PluginError(
            "You need color plugin inorder to style the bar. Read the docs for more info"
        )

    if total is not None:
        if not isinstance(total, int):
            raise TypeError(
                "integer argument expected, got '{}'.".format(type(total).__name__)
            )
        if total <= 0:
            total = None

    try:
        config = config_handler(**options)
    except NameError:
        raise PluginError(
            """

        -----------------------------------

        Plugin not installed properly:

        `progress`: In order to install the `progress` plugin,
        you may run the commmand `pip install hypecli[progress]`
        or read the documentation.

        https://hype.serum.studio/
        
        -----------------------------------
        """
        )

    def run(spinner):
        player = spinner_player(spinner)
        while thread:
            release_thread.wait()
            alive_repr(next(player))
            time.sleep(1.0 / fps())

    def alive_repr(spin=""):

        elapsed = time.time() - run.init
        run.rate = current() / elapsed if elapsed else 0.0

        if bar_color != None or title_color != None:
            #: Set the color for the progress bar.

            line = " ".join(
                filter(
                    None,
                    (
                        f"{rule_colors[title_color]}{title}{rule_colors['reset']}",
                        f"{rule_colors[bar_color]}{bar_repr(run.percent, end)}{rule_colors['reset']}",
                        spin,
                        monitor(),
                        "in",
                        to_elapsed_text(elapsed, end),
                        stats(),
                        run.text,
                    ),
                )
            )

        else:
            line = " ".join(
                filter(
                    None,
                    (
                        title,
                        bar_repr(run.percent, end),
                        spin,
                        monitor(),
                        "in",
                        to_elapsed_text(elapsed, end),
                        stats(),
                        run.text,
                    ),
                )
            )

        line_len, (cols, _) = len(line), get_terminal_size()
        with print_lock:
            if line_len < run.last_line_len:
                clear_traces()

            sys.__stdout__.write(line[:cols] + (spin and "\r" or "\n"))
            sys.__stdout__.flush()

        run.last_line_len = line_len

    def flush_buffer():
        if print_buffer:
            print()

    def set_text(message):
        run.text = sanitize_text_marking_wide_chars(message)

    if config.manual:
        # FIXME update bar signatures and remove deprecated in v2.
        def bar_handle(perc=None, text=None):
            """Bar handle for manual (bounded and unbounded) modes.
            Only absolute positioning.
            """
            if perc is not None:
                flush_buffer()
                run.percent = max(0.0, float(perc))  # ignores negative numbers.
            else:
                warnings.warn(
                    DeprecationWarning(
                        "percent will be mandatory in manual bar(),"
                        " please update your code."
                    ),
                    stacklevel=2,
                )
            update_hook()
            if text is not None:
                warnings.warn(
                    DeprecationWarning(
                        "use bar.text('') instead of bar(text=''),"
                        " please update your code."
                    ),
                    stacklevel=2,
                )
                set_text(text)

    else:

        def bar_handle(text=None, incr=1):
            """Bar handle for definite and unknown modes.
            Only relative positioning.
            """
            flush_buffer()
            # FIXME it was accepting 0 before, so a user could be using that to change text only
            run.count += max(0, int(incr))  # ignores negative numbers.
            update_hook()
            if text is not None:
                warnings.warn(
                    DeprecationWarning(
                        "use bar.text('') instead of bar(text=''),"
                        " please update your code."
                    ),
                    stacklevel=2,
                )
                set_text(text)

    def print_hook(part):
        if part != "\n":
            # this will generate a sequence of lines interspersed with None, which will later
            # be rendered as the indent filler to align additional lines under the same header.
            gen = chain.from_iterable(zip(repeat(None), part.splitlines(True)))
            print_buffer.extend(islice(gen, 1, None))
        else:
            header = header_template.format(run.count)
            nested = "".join(line or " " * len(header) for line in print_buffer)
            with print_lock:
                clear_traces()
                sys.__stdout__.write("{}{}\n".format(header, nested))
            print_buffer[:] = []

    print_buffer, print_lock = [], threading.Lock()
    header_template = "on {}: " if config.enrich_print else ""
    print_hook.write = print_hook
    print_hook.flush = lambda: None
    print_hook.isatty = sys.__stdout__.isatty

    def start_monitoring(offset=0.0):
        hide_cursor()
        sys.stdout = print_hook
        run.before_handlers = install_logging_hook()
        release_thread.set()
        run.init = time.time() - offset

    def stop_monitoring():
        show_cursor()
        sys.stdout = sys.__stdout__
        uninstall_logging_hook(run.before_handlers)  # noqa
        return time.time() - run.init

    thread, release_thread = None, threading.Event()
    if sys.stdout.isatty() or config.force_tty:

        @contextmanager
        def pause_monitoring():
            release_thread.clear()
            offset = stop_monitoring()
            alive_repr()
            yield
            start_monitoring(offset)

        bar_handle.pause = pause_monitoring
        thread = threading.Thread(target=run, args=(config.spinner(),))
        thread.daemon = True
        thread.start()

    if total or not config.manual:  # we can count items.
        logic_total, rate_spec, factor, current = (
            total,
            "f",
            1.0e6,
            lambda: run.count,
        )  # noqa
    else:  # there's only a manual percentage.
        logic_total, rate_spec, factor, current = (
            1.0,
            "%",
            1.0,
            lambda: run.percent,
        )  # noqa

    bar_handle.text, bar_handle.current = set_text, current
    if total or config.manual:  # we can track progress and therefore eta.
        spec = "({{:.1{}}}/s, eta: {{}})".format(rate_spec)
        gen_eta = gen_simple_exponential_smoothing_eta(0.5, logic_total)
        gen_eta.send(None)
        stats = lambda: spec.format(
            run.rate, to_eta_text(gen_eta.send((current(), run.rate)))
        )
        bar_repr = config.bar(config.length)
    else:  # unknown progress.
        bar_repr = config.unknown(config.length, config.bar)
        stats = lambda: "({:.1f}/s)".format(run.rate)  # noqa
    stats_end = lambda: "({:.2{}}/s)".format(run.rate, rate_spec)  # noqa

    # calibration of the dynamic fps engine.
    # I've started with the equation y = log10(x + m) * k + n, where:
    #   y is the desired fps, m and n are horizontal and vertical translation,
    #   k is a calibration factor, computed from some user input c (see readme for details).
    # considering minfps and maxfps as given constants, I came to:
    #   fps = log10(x + 1) * k + minfps, which must be equal to maxfps for x = c,
    # so the factor k = (maxfps - minfps) / log10(c + 1), and
    #   fps = log10(x + 1) * (maxfps - minfps) / log10(c + 1) + minfps
    # neat! ;)

    min_fps, max_fps = 2.0, 60.0
    calibrate = max(0.0, calibrate or factor)
    adjust_log_curve = 100.0 / min(calibrate, 100.0)  # adjust curve for small numbers
    factor = (max_fps - min_fps) / math.log10((calibrate * adjust_log_curve) + 1.0)

    def fps():
        if run.rate <= 0:
            return 10.0  # bootstrap speed
        if run.rate < calibrate:
            return math.log10((run.rate * adjust_log_curve) + 1.0) * factor + min_fps
        return max_fps

    end, run.text, run.last_line_len = False, "", 0
    run.count, run.percent, run.rate, run.init = 0, 0.0, 0.0, 0.0

    if total:
        if config.manual:

            def update_hook():
                run.count = int(math.ceil(run.percent * total))

        else:

            def update_hook():
                run.percent = run.count / total

        monitor = lambda: "{}{}/{} [{:.0%}]".format(  # noqa
            "(!) " if end and run.count != total else "", run.count, total, run.percent
        )
    elif config.manual:
        update_hook = lambda: None  # noqa
        monitor = lambda: "{}{:.0%}".format(  # noqa
            "(!) " if end and run.percent != 1.0 else "", run.percent
        )
    else:
        run.percent = 1.0
        update_hook = lambda: None  # noqa
        monitor = lambda: "{}".format(run.count)  # noqa

    title = render_title(title, config.title_length)
    start_monitoring()
    try:
        yield bar_handle
    finally:
        flush_buffer()
        stop_monitoring()
        if thread:
            local_copy = thread
            thread = None  # lets the internal thread terminate gracefully.
            local_copy.join()

        end, run.text, stats = True, "", stats_end
        alive_repr()
