# **************************************************************************** #
#                           This file is part of:                              #
#                                BITSMITHS                                     #
#                           https://bitsmiths.co.za                            #
# **************************************************************************** #
#  Copyright (C) 2015 - 2021 Bitsmiths (Pty) Ltd.  All rights reserved.        #
#   * https://bitbucket.org/bitsmiths_za/bitsmiths                             #
#                                                                              #
#  Permission is hereby granted, free of charge, to any person obtaining a     #
#  copy of this software and associated documentation files (the "Software"),  #
#  to deal in the Software without restriction, including without limitation   #
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
#  and/or sell copies of the Software, and to permit persons to whom the       #
#  Software is furnished to do so, subject to the following conditions:        #
#                                                                              #
#  The above copyright notice and this permission notice shall be included in  #
#  all copies or substantial portions of the Software.                         #
#                                                                              #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL     #
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  #
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
#  DEALINGS IN THE SOFTWARE.                                                   #
# **************************************************************************** #

import copy
import datetime
import dateutil
import os
import os.path

from mettle.lib.xmettle    import xMettle

import bs_monitor

from bs_lib                  import Pod
from bs_lib.sentinel_process import SentinelProcess

from bs_monitor.db.tables import tBatch
from bs_monitor.db.tables import tBatchInst
from bs_monitor.db.tables import tJobInst
from bs_monitor.db.tables import oBatchInstAllChildrenCompleted


class MonitorManager:
    """
    This class does all the monitor monitoring work.  It is designed to be a long live server.
    process.

    Note! There is only meant to be one of these servers running at once.
    """
    SOURCE = '[BS:Monitor]'

    def __init__(self,
                 pod                   : Pod,
                 job_runner_path       : str,
                 max_concurrent_jobs   : int,
                 batch_interval_check  : int,
                 dao_name              : str,
                 dao_path              : str = 'dao'):
        """
        Constructor.

        :param pod: The pod to use.
        :param job_runner_path:  The full path to the job runner program.
        :param max_concurrent_jobs: The maximum number of jobs that can run at once.
        :param batch_interval_check:  The interval check in seconds to check for new batches starting.
        :param dao_name: The dao to use.
        :param dao_path: Optinally overload the dao_path.
        """
        self._dao                  = bs_monitor.dao_by_name(dao_name, dao_path)
        self._pod                  = pod
        self._job_runner_path      = job_runner_path.strip().split()
        self._max_concurrent_jobs  = max_concurrent_jobs
        self._batch_interval_check = batch_interval_check
        self._batch_interval       = 0
        self._running_jobs         = []
        self._job_fails            = 0


    def initialize(self):
        """
        Initialize the monitor manager.  Fails any jobs in strange states.
        """
        self._pod.log.debug('initialize - start')

        for idx in range(0, len(self._job_runner_path)):
            self._job_runner_path[idx] = os.path.expandvars(self._job_runner_path[idx])

        if not os.path.exists(self._job_runner_path[0]) or not os.path.isfile(self._job_runner_path[0]):
            raise xMettle(f'Job runner is not found or not a file: {self._job_runner_path}', self.SOURCE)

        if self._batch_interval_check < 1:
            self._batch_interval_check = 60
            self._pod.log.info(' - Defaulting Batch Interval to 60 seconds as zero is not a valid value.')
        elif self._batch_interval_check > 3600:
            self._batch_interval_check = 3600
            self._pod.log.info(' - Defaulting Batch Interval to 1 hour as the current value is greater than 1 hour.')

        self._batch_interval = self._batch_interval_check

        self._fail_running_jobs_in_state(tJobInst.Status_Couplet.key_waiting)
        self._fail_running_jobs_in_state(tJobInst.Status_Couplet.key_running)
        self._fail_running_jobs_in_state(tJobInst.Status_Couplet.key_none)

        self._pod.log.debug('initialize - done')


    def run(self) -> None:
        """
        The main entry point for the server. This method should be called roughly every second from a calling
        paretn server.

        This function call should be called once every second until the monitor manager is to be shut down.
        """
        if self._job_fails and not self._running_jobs:
            raise xMettle(f'[{self._job_fails}] child jobs processes have failed!.  No child procs should ever fail.'
                          '  Please see the log file for detail, terminating queue!', self.SOURCE)


        self._batch_interval += 1

        if self._batch_interval > self._batch_interval_check:
            self._batch_interval = 0

        self._pod.log.debug(f'run - start [interval:{self._batch_interval}/{self._batch_interval_check}]')

        try:
            if self._batch_interval == 0:
                self._check_in()

                self._complete_finished_batches()

                self._schedule_batches()

                self._create_schedule_items()

            self._check_for_completed_procs()

            self._start_pending_procs()

        except Exception as ex:
            self._pod.log.error(f'Unexpected exception caught in run! [Error: {ex}]')
            raise

        self._pod.log.debug(f'run - done [interval:{self._batch_interval}/{self._batch_interval_check}]')


    def _fail_running_jobs_in_state(self, status: str) -> None:
        """
        Marks all jobs with a specific status as failed.

        :param status: The status to check for an mark as failed.
        """
        self._pod.log.info(f'_fail_running_jobs_in_state - start [status: {status}]')

        run_list = tJobInst.List()
        inst     = self._dao.dJobInst(self._pod.dbcon)
        cnt      = 0
        lock     = self._pod.std_db_lock()

        self._dao.dJobInstByStatus(self._pod.dbcon).exec_deft(status).fetch_all(run_list)

        for rec in run_list:
            try:
                inst.lock_one_deft(rec.id, lock)

                if inst.rec.status != status:
                    self._pod.log.info(f'  - [{cnt}] [jobinst: {rec.id}] has changed status from [{status}] to'
                                       f':{rec.status}]')

                    self._pod.dbcon.rollback()
                    cnt += 1
                    continue

                inst.rec.status   = tJobInst.Status_Couplet.key_failed
                inst.rec.stamp_by = self.SOURCE

                inst.update()
                self._pod.dbcon.commit()

                self._pod.log.info(f'  - [{cnt}] [jobinst: {rec.id}] is not running and has been marked as Failed')
                cnt += 1

            except xMettle as mx:
                if mx.get_error_code() != xMettle.ecode.DBLockNoWaitFailed:
                    raise

                self._pod.dbcon.rollback()
                self._pod.log.info(f'  - [{cnt}] [jobinst: {rec.id}] is still running (locked)')
                cnt += 1

        self._pod.log.info(f'_fail_running_jobs_in_state - done [status: {status}, cnt: {cnt}]')


    def _check_in(self) -> None:
        """
        Do a check in the monitor manger rundate table.
        """
        md = self._dao.dMondate(self._pod.dbcon)

        if md.try_select_one_deft('check-in'):
            md.update_deft('check-in', 'Monitor Manager Check-In', datetime.date.today(), self.SOURCE)
        else:
            md.insert_deft('check-in', 'Monitor Manager Check-In', datetime.date.today(), self.SOURCE)

        self._pod.dbcon.commit()


    def _complete_finished_batches(self) -> None:
        """
        Marks all bactches that have completd as done.
        """
        self._pod.log.debug('_complete_inished_batches - start')

        lock       = self._pod.std_db_lock(100, 1)
        qry        = self._dao.dBatchInstAllChildrenCompleted(self._pod.dbcon)
        batchinst  = self._dao.dBatchInst(self._pod.dbcon)
        batch      = self._dao.dBatch(self._pod.dbcon)
        batch_list = oBatchInstAllChildrenCompleted.List()

        qry.exec().fetch_all(batch_list)

        for rec in batch_list:
            batchinst.lock_one_deft(rec.id, lock)
            batch.lock_one_deft(batchinst.rec.batch_id, lock)

            batchinst.rec.status   = tBatchInst.Status_Couplet.key_completed
            batchinst.rec.end_date = datetime.datetime.now()

            batchinst.update()

            self._increment_rundate(batch.rec)

            batch.update()

        if batch_list:
            self._pod.dbcon.commit()
        else:
            self._pod.dbcon.rollback()

        self._pod.log.debug(f'_completeFinishedBatches - done [cnt: {len(batch_list)}]')


    def _schedule_batches(self) -> None:
        """
        Schedules all batches that are ready to run.
        """
        dtnow = datetime.datetime.now()

        self._pod.log.debug(f'_schedule_batches - start [time: {dtnow}]')

        qry           = self._dao.dBatchForScheduling(self._pod.dbcon)
        not_compl_qry = self._dao.dBatchInstNotCompleted(self._pod.dbcon)
        cnt           = 0

        qry.exec_deft(dtnow)

        while qry.fetch():
            not_compl_qry.exec_deft(qry.orec.id, dtnow)

            if not_compl_qry.fetch():
                self._pod.log.info(f' - Cannot start [batch: {qry.orec.id} - { qry.orec.name}] because batch'
                                   f' instance [id: {not_compl_qry.orec.id}, startdate: {not_compl_qry.orec.start_date}]'
                                   f' is in status [{not_compl_qry.orec.status}]')
                continue

            self._insert_new_batchinst(qry.orec)

            cnt += 1

        if cnt:
            self._pod.dbcon.commit()
        else:
            self._pod.dbcon.rollback()

        self._pod.log.debug(f'_schedule_batches - done [time: {dtnow}, cnt: {cnt}]')


    def _insert_new_batchinst(self, batch: tBatch) -> None:
        """
        Inserts the batch instance and all child batch instances.

        :param batch: The batch in insert the instances for.
        """
        batchinst = self._dao.dBatchInst(self._pod.dbcon)

        batchinst.insert_deft(None,
                              batch.id,
                              tBatchInst.Status_Couplet.key_pending,
                              batch.run_date,
                              None,
                              None)

        self._pod.log.info(f'_insert_new_batchinst - done [batch: {batch.id}, batchinst: {batchinst.rec.id}'
                           f', rundate: {batch.run_date}]')

        self._insert_child_batchinst(batch, batchinst.rec)


    def _insert_child_batchinst(self, batch: tBatch, batchinst: tBatchInst) -> None:
        """
        Insert all the child batch instances for a parent batch.

        :param batch: The batch in insert the instances for.
        :param batchinst: The parent batch instance.
        """
        cnt       = 0
        qry       = self._dao.dBatchByParent(self._pod.dbcon)
        childinst = self._dao.dBatchInst(self._pod.dbcon)

        qry.exec_deft(batch.id)

        while qry.fetch():
            childinst.insert(batchinst.id,
                             batch.id,
                             tBatchInst.Status_Couplet.keyPending,
                             batch.run_date,
                             None,
                             None)

            self._insert_child_batchinst(qry.orec, childinst.rec)

            cnt += 1

        self._pod.log.info(f'_insert_child_batchinst - done [batch: {batch.id}, childinst: {childinst.rec.id}'
                           f', cnt: {cnt}]')


    def _create_schedule_items(self) -> None:
        """
        Inserts the job instance items for batches that require processng.
        """
        self._pod.log.debug('_create_schedule_items - start')

        inst_list = tBatchInst.List()
        cnt       = 0
        dtnow     = datetime.datetime.now()

        self._dao.dBatchInstForProcessing(self._pod.dbcon).exec_deft(dtnow).fetch_all(inst_list)

        for inst in inst_list:
            if inst.parent_id:
                parent = self._dao.dBatchInst(self._pod.dbcon)

                parent.select_one_deft(inst.parent_id)

                if parent.rec.status != tBatchInst.Status_Couplet.key_completed:
                    continue

            self._insert_job_instances(inst)
            cnt += 1

        if cnt:
            self._pod.dbcon.commit()
        else:
            self._pod.dbcon.rollback()

        self._pod.log.debug(f'_create_schedule_items - done [cnt: {cnt}]')


    def _insert_job_instances(self, inst: tBatchInst) -> None:
        """
        Insert all job instances for a batch.
        """
        self._pod.log.debug(f'_insert_job_instances - start [batchinst: {inst.id}]')

        qry            = self._dao.dBatchItemForInserting(self._pod.dbcon)
        batchinst      = self._dao.dBatchInst(self._pod.dbcon)
        jobinst        = self._dao.dJobInst(self._pod.dbcon)
        prev_job_inst  = None
        cnt            = 0

        batchinst.lock_one_deft(inst.id, self._pod.std_db_lock())

        if inst.status != batchinst.rec.status and inst.status != tBatchInst.Status_Couplet.key_pending:
            self._pod.dbcon.rollback()
            return

        qry.exec_deft(inst.batch_id)

        while qry.fetch():
            jobinst.insert_deft(prev_job_inst,
                                qry.orec.job_id,
                                inst.id,
                                inst.run_date,
                                qry.orec.priority,
                                tJobInst.Status_Couplet.key_pending,
                                qry.orec.extra_args,
                                qry.orec.group_job,
                                qry.orec.group_batch,
                                self.SOURCE)

        prev_job_inst = jobinst.rec.id
        cnt += 1

        if prev_job_inst:
            batchinst.rec.start_date = datetime.datetime.now()
            batchinst.rec.status     = tBatchInst.Status_Couplet.key_busy
        else:
            batchinst.rec.status = tBatchInst.Status_Couplet.key_completed

        batchinst.update()
        self._pod.dbcon.commit()

        self._pod.log.debug(f'_insert_job_instances - done [batchinst: {inst.id}, cnt: {cnt}]')


    def _check_for_completed_procs(self) -> None:
        if not self._running_jobs:
            return

        self._pod.log.debug(f'_check_for_completed_procs - start [running: {len(self._running_jobs)}]')

        idx = 0
        cnt = 0

        while idx < len(self._running_jobs):
            item = self._running_jobs[idx]

            if not item.is_alive():
                item = self._running_jobs.pop(idx)

                if item.completed_ok():
                    self._pod.log.info(f' - Job [pid: {item.pid()}, name: {item.name}] completed ok')
                    cnt += 1
                    continue

                self._job_fails += 1
                self._pod.log.error(f' - Job [pid: {item.pid()}, name: {item.name}] failed! - Exception will be thrown!')
                self._pod.log.error(f'      ... details: [rc: {item._rc}, args: {item._proc_args}, stderr: {item._stderr}')
                continue


            idx += 1

        self._pod.log.debug(f'_check_for_completed_procs - done [compl: {cnt}, running: {len(self._running_jobs)}]')


    def _start_pending_procs(self) -> None:
        """
        Starts all job instance processes that are ready.
        """
        running_cnt = len(self._running_jobs)

        self._pod.log.debug(f'_start_pending_procs - start [running: {running_cnt}/{self._max_concurrent_jobs}]')

        if (self._max_concurrent_jobs > 0 and running_cnt >= self._max_concurrent_jobs):
            self._pod.log.debug('_start_pending_procs - done... maxjobs limit reached')
            return

        lock      = self._pod.std_db_lock(100, 1)
        prev_grp  = None
        run_list  = tJobInst.List()
        jobinst   = self._dao.dJobInst(self._pod.dbcon)
        cnt       = 0

        self._dao.dJobInstReadyToRun(self._pod.dbcon).exec().fetch_all(run_list)

        for rec in run_list:
            if prev_grp == rec.group_job:
                continue

            if rec.status != tJobInst.Status_Couplet.key_pending:
                continue

            prev_grp = rec.group_job

            jobinst.lock_one_deft(rec.id, lock)

            if jobinst.rec.status != tJobInst.Status_Couplet.key_pending:
                self._pod.dbcon.rollback()
                continue

            jobinst.rec.status     = tJobInst.Status_Couplet.key_waiting
            jobinst.rec.modifiedBy = self.SOURCE
            jobinst.update()

            self._pod.dbcon.commit()

            jargs = copy.copy(self._job_runner_path)

            jargs.append('--job')
            jargs.append(str(jobinst.rec.id))

            sp = SentinelProcess(jobinst.rec.group_job, jargs, self._pod.log, True, False)

            self._running_jobs.append(sp)
            sp.start()

            self._pod.log.info(f' - Job [pid:{sp.pid()}, name:{sp.name}] started')

            cnt += 1
            running_cnt += 1

            if self._max_concurrent_jobs > 0 and running_cnt >= self._max_concurrent_jobs:
                self._pod.log.debug(' - Max child process limit reached.')
                break

        if cnt:
            self._pod.dbcon.commit()
        else:
            self._pod.dbcon.rollback()

        self._pod.log.debug(f'_start_pending_procs - done [running: {running_cnt}/{self._max_concurrent_jobs}]')


    def _increment_rundate(self, batch: tBatch) -> None:
        """
        Increments the batches rundate by its interval.
        """
        rdate = batch.run_date

        if batch.run_interval < 1:
            self._pod.log.error(f'_increment_rundate - invalid interval detected in batch [{batch}]. Disabling this batch!')

            batch.status   = tBatch.Status_Couplet.key_disabled
            batch.stamp_by = self.SOURCE
            return

        if batch.cycle == tBatch.Cycle_Couplet.key_minute:
            rdate += datetime.timedelta(minutes=batch.run_interval)
        elif batch.cycle == tBatch.Cycle_Couplet.key_hour:
            rdate += datetime.timedelta(hours=batch.run_interval)
        elif batch.cycle == tBatch.Cycle_Couplet.key_day:
            rdate += datetime.timedelta(days=batch.run_interval)
        elif batch.cycle == tBatch.Cycle_Couplet.key_week:
            rdate += datetime.timedelta(weeks=batch.run_interval)
        elif batch.cycle == tBatch.Cycle_Couplet.key_month:
            rdate += dateutil.relativedelta.relativedelta(months=batch.run_interval)
        elif batch.cycle == tBatch.Cycle_Couplet.key_year:
            rdate += dateutil.relativedelta.relativedelta(years=batch.run_interval)
        else:
            self._pod.log.error(f'_increment_rundate- Invalid cycle detected in batch [{batch}]. Disabling this batch!')

            batch.status   = tBatch.Status_Couplet.key_disabled
            batch.stamp_by = self.SOURCE
            return

        if batch.run_time:
            tm = datetime.datetime.strptime(batch.run_time, '%H%M%S').time()

            if batch.cycle == tBatch.Cycle_Couplet.key_minute:
                rdate = rdate.replace(second=tm.second)

            elif batch.cycle == tBatch.Cycle_Couplet.key_hour:
                rdate = rdate.replace(second=tm.second)
                rdate = rdate.replace(minute=tm.minute)
            else:
                rdate = rdate.replace(second=tm.second)
                rdate = rdate.replace(minute=tm.minute)
                rdate = rdate.replace(hour=tm.hour)

        batch.run_date = rdate
