"""Module containing generic utilities."""

from __future__ import annotations

from datetime import datetime
import os
import sys
import time

import numpy as np


__all__ = [
    # Class exports
    'Progbar',
]


class Progbar:  # pragma: no cover
    """Displays a progress bar.

    Arguments:
        target: Total number of steps expected, None if unknown.
        width: Progress bar width on screen.
        verbose: Verbosity mode, 0 (silent), 1 (verbose), 2 (semi-verbose)
        stateful_metrics: Iterable of string names of metrics that should
            *not* be averaged over time. Metrics in this list will be
            displayed as-is. All others will be averaged by the progbar
            before display.
        interval: Minimum visual progress update interval (in seconds).
        unit: Display name for step counts (usually "step" or "sample").

    """

    def __init__(self,
                 target: int,
                 width: int = 30,
                 verbosity: int = 1,
                 interval: int | float = 0.05,
                 stateful_metrics: set | tuple | list | None = None,
                 unit: str = 'step'):

        self.target = target
        self.width = width
        self.verbosity = verbosity
        self.interval = interval
        self.unit = unit

        if stateful_metrics:
            self.stateful_metrics = set(stateful_metrics)
        else:
            self.stateful_metrics = set()

        self._dynamic_display = (
            (hasattr(sys.stdout, 'isatty') and
              sys.stdout.isatty()) or
            'ipykernel' in sys.modules or
            'posix' in sys.modules or
            'PYCHARM_HOSTED' in os.environ)

        self._total_width = 0
        self.progress = 0

        # We use a dict + list to avoid garbage collection
        # issues found in OrderedDict
        self._values = {}
        self._values_order = []
        self._start = time.time()
        self._last_update = 0

        self._time_after_first_step = None

        # Update the bar to zero to show it immediately
        self.update(0)

    def update(
        self,
        current: int,
        values: list[tuple[str, int | float]] | None = None,
        finalize: bool | None = None):

        """Updates the progress bar.

        Arguments:
            current: Index of current step.
            values: List of tuples: `(name, value_for_last_step)`. If
                `name` is in `stateful_metrics`, `value_for_last_step` will
                be displayed as-is. Else, an average of the metric over
                time will be displayed.
            finalize: Whether this is the last update for the progress bar.
                If `None`, defaults to `current >= self.target`.

        """
        # Don't bother updating if we already reached the target
        if self.progress >= self.target:
            return

        if finalize is None:
            if self.target is None:
                finalize = False
            else:
                finalize = current >= self.target

        # Prevent overflow
        if finalize:
            current = self.target

        values = values or []
        for k, v in values:
            if k not in self._values_order:
                self._values_order.append(k)
            if k not in self.stateful_metrics:
                # In the case that progress bar doesn't have a target
                # value in the first epoch, both on_batch_end and
                # on_epoch_end will be called, which will cause 'current'
                # and 'self.progress' to have the same value. Force
                # the minimal value to 1 here, otherwise stateful_metric
                # will be 0s.
                value_base = max(current - self.progress, 1)
                if k not in self._values:
                    self._values[k] = [v * value_base, value_base]
                else:
                    self._values[k][0] += v * value_base
                    self._values[k][1] += value_base

            else:
                # Stateful metrics output a numeric value. This representation
                # means "take an average from a single value" but keeps the
                # numeric formatting.
                self._values[k] = [v, 1]

        self.progress = current

        now = time.time()
        info = ' - %.0fs' % (now - self._start)

        if self.verbosity == 1:
            if now - self._last_update < self.interval and not finalize:
                return

            prev_total_width = self._total_width
            if self._dynamic_display:
                sys.stdout.write('\b' * prev_total_width)
                sys.stdout.write('\r')
            else:
                sys.stdout.write('\n')

            if self.target is not None:
                numdigits = int(np.log10(self.target)) + 1
                bar = ('%' + str(numdigits) + 'd/%d [')
                bar %= (current, self.target)
                prog = float(current) / self.target
                prog_width = int(self.width * prog)
                if prog_width > 0:
                    bar += ('=' * (prog_width - 1))
                    if current < self.target:
                        bar += '>'
                    else:
                        bar += '='
                bar += ('.' * (self.width - prog_width))
                bar += ']'
            else:
                bar = '%7d/Unknown' % current

            self._total_width = len(bar)
            sys.stdout.write(bar)

            time_per_unit = self._estimate_step_duration(current, now)

            if self.target is None or finalize:
                if time_per_unit >= 1 or time_per_unit == 0:
                    info += ' %.0fs/%s' % (time_per_unit, self.unit)
                elif time_per_unit >= 1e-3:
                    info += ' %.0fms/%s' % (time_per_unit * 1e3, self.unit)
                else:
                    info += ' %.0fus/%s' % (time_per_unit * 1e6, self.unit)
            else:
                eta = time_per_unit * (self.target - current)
                if eta > 3600:
                    eta_format = '%d:%02d:%02d' % (
                        eta // 3600, (eta % 3600) // 60, eta % 60)
                elif eta > 60:
                    eta_format = '%d:%02d' % (eta // 60, eta % 60)
                else:
                    eta_format = '%ds' % eta

                info = ' - ETA: %s' % eta_format

            for k in self._values_order:
                info += ' - %s:' % k
                if isinstance(self._values[k], list):
                    avg = np.mean(
                        self._values[k][0] / max(1, self._values[k][1]))
                    if abs(avg) > 1e-3:
                        info += ' %.4f' % avg
                    else:
                        info += ' %.4e' % avg
                else:
                    info += ' %s' % self._values[k]

            self._total_width += len(info)
            if prev_total_width > self._total_width:
                info += (' ' * (prev_total_width - self._total_width))

            if finalize:
                info += '\n'

            sys.stdout.write(info)
            sys.stdout.flush()

        elif self.verbosity == 2:
            if finalize:
                numdigits = int(np.log10(self.target)) + 1
                count = ('%' + str(numdigits) + 'd/%d') % (
                    current, self.target)
                info = count + info
                for k in self._values_order:
                    info += ' - %s:' % k
                    avg = self._values[k][0] / max(1, self._values[k][1])
                    avg = np.mean(avg)

                    if avg > 1e-3:
                        info += ' %.4f' % avg
                    else:
                        info += ' %.4e' % avg

                info += '\n'

                sys.stdout.write(info)
                sys.stdout.flush()

        self._last_update = now

    def add(self, n, values=None):
        if self.progress + n <= self.target:
            self.update(self.progress + n, values)

    def _estimate_step_duration(self, current: int, now: datetime) -> int:
        """Estimate the duration of a single step.

        Given the step number `current` and the corresponding time `now`
        this function returns an estimate for how long a single step
        takes. If this is called before one step has been completed
        (i.e. `current == 0`) then zero is given as an estimate. The
        duration estimate ignores the duration of the (assumed to be
        non-representative) first step for estimates when more steps are
        available (i.e. `current>1`).

        Arguments:
            current: Index of current step.
            now: The current time.

        Returns:
            Estimate of the duration of a single step.

        """
        if current:
            # there are a few special scenarios here:
            # 1) somebody is calling the progress bar
            #    without ever supplying step 1
            # 2) somebody is calling the progress bar and
            #    supplies step one mulitple times, e.g. as part
            #    of a finalizing call
            # in these cases, we just fall back to the simple calculation
            if self._time_after_first_step is not None and current > 1:
                time_per_unit = (now - self._time_after_first_step)
                time_per_unit /= current - 1
            else:
                time_per_unit = (now - self._start) / current

            if current == 1:
                self._time_after_first_step = now
            return time_per_unit

        return 0

    def _update_stateful_metrics(self, stateful_metrics):
        self.stateful_metrics = self.stateful_metrics.union(stateful_metrics)
