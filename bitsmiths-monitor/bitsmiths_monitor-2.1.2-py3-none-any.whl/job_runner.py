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
import datetime
import os
import os.path
import time

from mettle.lib.xmettle    import xMettle

import bs_monitor

from bs_lib                  import Pod
from bs_lib.sentinel_process import SentinelProcess

from bs_monitor.db.tables import tJobInst
from bs_monitor.db.tables import tJobInstMetric


class JobRunner:
    """
    Overloadable class batch that runs jobs for the monitor.
    """
    SOURCE = '[BS:JobRunner]'


    def __init__(self, pod: Pod, dao_name: str, dao_path: str = 'dao'):
        """
        Constructor.

        :param pod: The pod to use.
        :param dao_name: The dao to use.
        :param dao_path: Optinally overload the dao_path.
        """
        self._dao     = bs_monitor.dao_by_name(dao_name, dao_path)
        self._pod     = pod
        self._job     = None
        self._jobinst = None
        self._jobpath = None
        self._jobargs = None



    def notify_jobinst_failed(self) -> None:
        """
        Pure virtual method that is called when a job fails.
        """
        pass


    def notify_jobinst_success(self) -> None:
        """
        Pure virtual method that is called when a job succeeds.
        """
        pass


    def runtime_format(self) -> str:
        """
        Virtual method that gets the runtime format for cmd line args.

        :return: The default command line arg for dates.
        """
        return '%Y-%m-%d %H:%M:%S'


    def run(self, jobinst_id: int) -> int:
        """
        The main entry point to run a job instance.

        :param jobinst_id: The job instance identifier from the jobinst table to run.
        :return: The jobs return code, 0 means success.
        """
        rc = 1

        try:
            self._pod.log.info(f'JobRunner.run - start [jobinst: {jobinst_id}]')

            if not self._lock_jobinst(jobinst_id):
                return 1

            if not self._validate_jobinst():
                return 1

            if not self._validate_jobpath():
                return 1

            rc = self._run_job()

        except Exception as ex:
            self._pod.log.error(f'Error running job [jobinst: {jobinst_id}] - {ex}')
            raise

        self._pod.log.info(f'JobRunner.run - done [rc: {rc}, jobinst: {jobinst_id}]')

        return rc


    def _lock_jobinst(self, jobinst_id: int, recurse: int = 0) -> bool:
        """
        Virtual method, lock the job instance and ensure it is in the correct status.

        :param jobinst_id: The job to lock.
        :return: True if locked ok, or false if not.
        """
        self._pod.log.debug(f'JobRunner._lock_jobinst - start [jobinst: {jobinst_id}, recurse: {recurse}]')

        jobinst        = self._dao.dJobInst(self._pod.dbcon)
        jobinst_cancel = self._dao.dJobInstCancel(self._pod.dbcon)

        jobinst.lock_one_deft(jobinst_id, self._pod.std_db_lock())

        if jobinst.rec.status != tJobInst.Status_Couplet.key_waiting:
            self._pod.log.error(f'JobInst [{jobinst_id}] found in unexpected state [{jobinst.rec.status}'
                                f': {tJobInst.Status_Couplet.get_value(jobinst.rec.status)}] - Marking job as failed'
                                'and aborting.')

            self._commit_status(tJobInst.Status_Couplet.key_failed, False)
            return False

        if jobinst_cancel.try_select_one_deft(jobinst.rec.id):
            jobinst_cancel.delete_one()
            self._pod.dbcon.commit()

            return self._lock_jobinst(jobinst_id, recurse + 1)

        self._jobinst = jobinst.rec

        self._pod.log.debug(f'JobRunner._lock_jobinst - done [jobinst:{jobinst_id}, recurse:{recurse}]')

        return True


    def _validate_jobinst(self) -> bool:
        """
        Validaes that a job instance is a good state to be run.

        :return: True if all good, else False.
        """
        self._pod.log.debug(f'JobRunner._validate_jobinst - start [{self._jobinst}]')

        dtnow = datetime.datetime.now()

        if self._jobinst.process_date > dtnow:
            self._commit_metric_and_status(f'MonJobInst [{self._jobinst.id}], Process DateTime [{self._jobinst.process_date}]'
                                           f' is greater that the current time [{dtnow}]',
                                           tJobInstMetric.Mtype_Couplet.key_error,
                                           tJobInst.Status_Couplet.key_failed,
                                           False)
            return False

        if self._jobinst.parent_id:
            parent = self._dao.dJobInst(self._pod.dbcon)

            if not parent.try_select_one_deft(self._jobinst.parent_id):
                self._commit_metric_and_status(f'Parent MonJobInst {self._jobinst.parent_id}] is missing',
                                               tJobInstMetric.Mtype_Couplet.key_error,
                                               tJobInst.Status_Couplet.key_failed,
                                               False)
                return False

            if parent.rec.status not in (tJobInst.Status_Couplet.key_completed, tJobInst.Status_Couplet.key_forced_okay):
                self._commit_metric_and_status(f'Parent MonJobInst [{parent.rec.id}] should be in completed status - Not status'
                                               f'[{parent.rec.status}: {tJobInst.Status_Couplet.get_value(parent.rec.status)}]',
                                               tJobInstMetric.Mtype_Couplet.key_error,
                                               tJobInst.Status_Couplet.key_failed,
                                               False)


        self._pod.log.debug(f'JobRunner._validate_jobinst - done [{self._jobinst.id}]')

        return True


    def _validate_jobpath(self) -> bool:
        """
        Validates that we can find the job to be run.

        :return: True if job is found else False.
        """
        self._pod.log.debug(f'JobRunner._validate_jobpath - start [job: {self._jobinst.id}]')

        job = self._dao.dJob(self._pod.dbcon)

        if not job.try_select_one_deft(self._jobinst.job_id):
            self._commit_metric_and_status(f'Monitor Job [{self._jobinst.job_id}] is missing',
                                           tJobInstMetric.Mtype_Couplet.key_error,
                                           tJobInst.Status_Couplet.key_failed,
                                           False)
            return False

        self._pod.log.debug(f' - pre  [job: {job.rec}]')

        self._jobargs = job.rec.program_args or ''
        self._jobpath = job.rec.program_path or ''

        self._jobargs = os.path.expandvars(self._jobargs.strip())
        self._jobpath = os.path.expandvars(self._jobpath.strip())

        self._pod.log.debug(f' - post [job_path: {self._jobpath}, job_args: {self._jobargs}]')

        if not os.path.exists(self._jobpath):
            self._commit_metric_and_status(f'Job [{job.rec.id}] program path [{self._jobpath}) not found',
                                           tJobInstMetric.Mtype_Couplet.key_error,
                                           tJobInst.Status_Couplet.key_failed,
                                           False)

            return False


        self._job = job.rec

        self._pod.log.debug(f'JobRunner._validate_jobpath - done [job: {self._jobinst.id}]')

        return True


    def _commit_status(self, new_status: str, relock: bool) -> None:
        """
        Commit a status update on a job and optionally relock the job.

        :param new_status: The new status to set.
        :param relock: If true, attempt to relock the job right away.
        """
        if not self._jobinst:
            return

        self._pod.log.debug(f'JobRunner.commit_status - start [job: {self._jobinst.id}, status: {new_status}, relock: {relock}]')  # noqa

        self._jobinst.status   = new_status
        self._jobinst.stamp_by = self.SOURCE

        self._dao.dJobInst(self._pod.dbcon).update(self._jobinst)

        self._pod.dbcon.commit()

        if new_status == tJobInst.Status_Couplet.key_failed:
            self.notify_jobinst_failed()
        elif new_status == tJobInst.Status_Couplet.key_completed:
            self.notify_jobinst_success()

        if relock:
            jobinst = self._dao.dJobInst(self._pod.dbcon)

            jobinst.lock_one_deft(self._jobinst.id, self._pod.std_db_lock())

            if jobinst.rec.status != self._jobinst.status:
                raise xMettle(f'JobInst [{self._jobinst.id}] - was modified by an outside source unexpectedly! - Expected'
                              f' status [{self.jobinst.rec.status}] != Actual status [{new_status}',  self. SOURCE)

            self._jobinst = jobinst.rec

        self._pod.log.debug(f'JobRunner.commit_status - done [job: {self._jobinst.id}, status: {new_status}, relock: {relock}]')  # noqa


    def _commit_metric_and_status(self, msg: str, metric_type: str, new_status: str, relock: bool) -> None:
        """
        Commit a metric as well as a status change on a job instance.

        :param msg: The message to log with the metric.
        :param metric_type: The metric type we are capturing.
        :param new_status: The new jobinst status.
        :param relock: If true, we relock the job after updating the status.
        """
        if metric_type == tJobInstMetric.Mtype_Couplet.key_error:
            self._pod.log.error(f' - Job Status Change [status: {tJobInst.Status_Couplet.get_value(new_status)}, msg: {msg}]')
        else:
            self._pod.log.debug(f' - Job Status Change [status: {tJobInst.Status_Couplet.get_value(new_status)}, msg: {msg}]')

        self._dao.dJobInstMetric(self._pod.dbcon).insert_deft(self._jobinst.id, metric_type, msg)

        self._commit_status(new_status, relock)


    def _get_job_args(self) -> list:
        """
        Gets the job args and appends any default we need for jobs, like the rundate, runtime and job identifier.

        :return: The job list including the app path..
        """
        args = []

        args += self._jobpath.strip().split(' ')

        if self._jobargs:
            args += self._jobargs.strip().split(' ')

        if self._jobinst.extra_args:
            args += self._jobinst.extra_args.strip().split(' ')

        args.append(f' --job {self._jobinst.id}')

        if self._jobinst.batchinst_id:
            bi = self._dao.dBatchInst(self._pod.dbcon)

            bi.select_one_deft(self._jobinst.batchinst_id)

            args.append(f' --runtime "{bi.rec.run_date.strftime(self.runtime_format())}"')

        return args


    def _run_job(self) -> int:
        """
        Run the job get the return code.

        :return: The jobs system return code.
        """
        cancel_job   = self._dao.dJobInstCancel(self._pod.dbcon)
        cancel_check = 0
        rc           = 1
        args         = self._get_job_args()

        self._pod.log.info(f'JobRunner.run_job - Start [jobinst: {self._jobinst.id}]')
        self._pod.log.debug(f' - args: {args}')

        try:

            self._commit_metric_and_status('Started',
                                           tJobInstMetric.Mtype_Couplet.key_start,
                                           tJobInst.Status_Couplet.key_running,
                                           True)

            self._pod.log.info(f' - running [jobinst: {self._jobinst.id}, path: {self._jobpath}, args: {args}]')

            sp = SentinelProcess(self._job.name, args, self._pod.log, True, False)

            sp.start()

            while sp.is_alive():
                time.sleep(0.1)

                if not sp.is_alive:
                    break

                cancel_check += 1

                if cancel_check % 10:
                    if cancel_job.try_select_one_deft(self._jobinst.id):
                        self._pod.log.info(f' - Job [jobinst: {self._jobinst.id}] cancel_job requested! [user: '
                                           f'{cancel_job.rec.stamp_by}, time: {cancel_job.stamp_tm}, reason: ',
                                           f'f{cancel_job.reason}]')

                        self._dao.dJobMetric(self._pod.dbcon).insert_deft(
                            self._jobinst.id,
                            tJobInstMetric.Mtype_Couplet.key_cancelled,
                            f'user: {cancel_job.rec.stamp_by}, reason: {cancel_job.rec.reason}')

                        sp.shutdown()

                        for i in range(0, 3):
                            time.sleep(0.5)
                            if not sp.is_alive():
                                break
                            self._pod.log.warning(' - [jobinst: {self._jobinst.id}] waiting for terminate...')

                        if sp.is_alive():
                            sp.kill()

                            for i in range(0, 3):
                                time.sleep(0.5)
                                if not sp.is_alive():
                                    break
                                self._pod.log.warning(' - [jobinst: {self._jobinst.id}] waiting for kill...')

                        if sp.is_alive():
                            self._log.warning(f'Job [jobinst: {self._jobinst.id}] would not shutdown or be killed!')
                        else:
                            self._log.info(f'Job [jobinst: {self._jobinst.id}] has been terminated!')

            if sp.completed_ok():
                self._commit_metric_and_status('OK',
                                               tJobInstMetric.Mtype_Couplet.key_completed,
                                               tJobInst.Status_Couplet.key_completed,
                                               False)
                rc = 0
            else:
                stderr = sp.proc_std_err() or '<NONE>'
                stderr = stderr[:512]

                self._commit_metric_and_status(f'Failed [return_code: {sp._rc}, std_err: {stderr}]',
                                               tJobInstMetric.Mtype_Couplet.key_error,
                                               tJobInst.Status_Couplet.key_failed,
                                               False)

                rc = sp._rc or 1

        except Exception as ex:
            self._pod.log.error(f'Unexpected exception occured while running job! [jobinst: {self._jobinst.id}'
                                f', path: {self._jobpath}, args: {args}] - Error: {ex}')

            raise

        self._pod.log.info(f'JobRunner.run_job - done [jobinst: {self._jobinst.id}, rc: {rc}]')
