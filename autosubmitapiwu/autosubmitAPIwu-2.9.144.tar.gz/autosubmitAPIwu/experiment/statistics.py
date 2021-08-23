#!/usr/bin/env python

# Copyright 2017 Earth Sciences Department, BSC-CNS

# This file is part of Autosubmit.

# Autosubmit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Autosubmit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Autosubmit.  If not, see <http://www.gnu.org/licenses/>.

import datetime
from autosubmitAPIwu.job.job import Job
from autosubmitAPIwu.monitor.utils import FixedSizeList
from bscearth.utils.log import Log


def timedelta2hours(deltatime):
    return deltatime.days * 24 + deltatime.seconds / 3600.0


class ExperimentStats(object):

    def __init__(self, jobs_list, start, end, queue_time_fixes):
        """
        queue_time_fixes expects a ditionary: Job Name -> Size of Queue time fix (int)
        """
        self._jobs_list = jobs_list
        self._queue_time_fixes = queue_time_fixes
        self._start = start
        self._end = end
        # Max variables
        self._max_timedelta = 0
        self._max_time = 0
        self._max_fail = 0
        # Totals variables
        self._total_jobs_submitted = 0
        self._total_jobs_run = 0
        self._total_jobs_failed = 0
        self._total_jobs_completed = 0
        self._total_queueing_time = datetime.timedelta()
        self._cpu_consumption = datetime.timedelta()
        self._real_consumption = datetime.timedelta()
        self._expected_cpu_consumption = 0
        self._expected_real_consumption = 0
        self._threshold = 0
        # Totals arrays
        self._totals = []
        self._start_times = [datetime.timedelta()] * len(jobs_list)
        self._end_times = [datetime.timedelta()] * len(jobs_list)
        self._run = [datetime.timedelta()] * len(jobs_list)
        #print([datetime.timedelta()] * len(jobs_list))
        # print(datetime.timedelta())
        self._queued = [datetime.timedelta()] * len(jobs_list)
        self._failed_jobs = [0] * len(jobs_list)
        self._fail_queued = [datetime.timedelta()] * len(jobs_list)
        self._fail_run = [datetime.timedelta()] * len(jobs_list)
        # Do calculations
        self._calculate_stats()
        self._calculate_maxs()
        self._calculate_totals()
        self._format_stats()

    @property
    def totals(self):
        return self._totals

    @property
    def max_time(self):
        return self._max_time

    @property
    def max_fail(self):
        return self._max_fail

    @property
    def threshold(self):
        return self._threshold

    @property
    def start_times(self):
        return self._start_times

    @property
    def end_times(self):
        return self._end_times

    @property
    def run(self):
        return FixedSizeList(self._run, 0.0)

    @property
    def queued(self):
        return FixedSizeList(self._queued, 0.0)

    @property
    def failed_jobs(self):
        return FixedSizeList(self._failed_jobs, 0.0)

    @property
    def fail_queued(self):
        return FixedSizeList(self._fail_queued, 0.0)

    @property
    def fail_run(self):
        return FixedSizeList(self._fail_run, 0.0)

    def _calculate_stats(self):
        """
        Main statistics calculation.
        Considers queue time adjusment by wrapper
        """
        # for name in self._queue_time_fixes:
        #     print("{} -> queue {}".format(name,
        #           datetime.timedelta(seconds=self._queue_time_fixes[name])))
        queued_by_name = dict()
        for i, job in enumerate(self._jobs_list):
            last_retrials = job.get_last_retrials()
            processors = job.total_processors
            # print("Start {}".format(job.name))
            for retrial in last_retrials:
                submit_time = None
                start_time = None
                finish_time = None
                try:
                    submit_time = retrial[0]
                    start_time = retrial[1]
                    finish_time = retrial[2]
                except:
                    continue
                if not type(submit_time) == type(start_time) == type(finish_time):
                    # Not timedeltas, continue
                    continue
                # print("{} qtime {}".format(job.name, start_time - submit_time))
                if Job.is_a_completed_retrial(retrial):
                    if job.name not in queued_by_name:
                        print("{} adjust {}".format(job.name, datetime.timedelta(
                            seconds=self._queue_time_fixes.get(job.name, 0))))
                        adjusted_queue = (
                            start_time - submit_time) - datetime.timedelta(seconds=self._queue_time_fixes.get(job.name, 0))
                        adjusted_queue = adjusted_queue if adjusted_queue.seconds >= 0 else 0
                        self._queued[i] += adjusted_queue
                        queued_by_name[job.name] = self._queued[i]
                    else:
                        self._queued[i] += queued_by_name[job.name]
                    self._start_times[i] = start_time
                    self._end_times[i] = finish_time
                    self._run[i] += finish_time - start_time
                    self._cpu_consumption += self.run[i] * int(processors)
                    self._real_consumption += self.run[i]
                    self._total_jobs_completed += 1
                    # print("{} -> {} and {}".format(job.name,
                    #       self._queued[i], queued_by_name[job.name]))
                else:
                    if len(retrial) > 2:
                        self._fail_run[i] += finish_time - start_time
                    if len(retrial) > 1:
                        adjusted_failed_queue = (
                            start_time - submit_time) - datetime.timedelta(seconds=self._queue_time_fixes.get(job.name, 0))
                        adjusted_failed_queue = adjusted_failed_queue if adjusted_failed_queue.seconds >= 0 else 0
                        self._fail_queued[i] += adjusted_failed_queue
                    self._cpu_consumption += self.fail_run[i] * int(processors)
                    self._real_consumption += self.fail_run[i]
                    self._failed_jobs[i] += 1
            self._total_jobs_submitted += len(last_retrials)
            self._total_jobs_run += len(last_retrials)
            self._total_jobs_failed += self.failed_jobs[i]
            self._threshold = max(self._threshold, job.total_wallclock)
            self._expected_cpu_consumption += job.total_wallclock * \
                int(processors)
            self._expected_real_consumption += job.total_wallclock
            self._total_queueing_time += self._queued[i]

    def _calculate_maxs(self):
        max_run = max(max(self._run), max(self._fail_run))
        max_queued = max(max(self._queued), max(self._fail_queued))
        self._max_timedelta = max(
            max_run, max_queued, datetime.timedelta(hours=self._threshold))
        self._max_time = max(self._max_time, self._max_timedelta.days *
                             24 + self._max_timedelta.seconds / 3600.0)
        self._max_fail = max(self._max_fail, max(self._failed_jobs))

    def _calculate_totals(self):
        percentage_consumption = (timedelta2hours(
            self._cpu_consumption) / self._expected_cpu_consumption * 100) if self._expected_cpu_consumption > 0 else 0
        self._totals = ['Period: ' + str(self._start) + " ~ " + str(self._end),
                        'Submitted (#): ' + str(self._total_jobs_submitted),
                        'Run  (#): ' + str(self._total_jobs_run),
                        'Failed  (#): ' + str(self._total_jobs_failed),
                        'Completed (#): ' + str(self._total_jobs_completed),
                        'Queueing time (h): ' +
                        str(round(timedelta2hours(self._total_queueing_time), 2)),
                        'Expected consumption real (h): ' + str(
                            round(self._expected_real_consumption, 2)),
                        'Expected consumption CPU time (h): ' + str(
                            round(self._expected_cpu_consumption, 2)),
                        'Consumption real (h): ' +
                        str(round(timedelta2hours(self._real_consumption), 2)),
                        'Consumption CPU time (h): ' + str(
                            round(timedelta2hours(self._cpu_consumption), 2)),
                        'Consumption (%): ' + str(round(percentage_consumption, 2))]
        Log.result('\n'.join(self._totals))

    def _format_stats(self):
        self._queued = map(lambda y: timedelta2hours(y), self._queued)
        self._run = map(lambda y: timedelta2hours(y), self._run)
        self._fail_queued = map(
            lambda y: timedelta2hours(y), self._fail_queued)
        self._fail_run = map(lambda y: timedelta2hours(y), self._fail_run)
