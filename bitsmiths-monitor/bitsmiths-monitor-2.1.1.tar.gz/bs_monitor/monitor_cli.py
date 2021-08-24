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
import sys

import mettle.db

from bs_lib import Pod

from bs_monitor.monitor_server_impl  import MonitorServerImpl

from bs_monitor.braze   import bBatchQuery
from bs_monitor.braze   import bBatchInstQuery
from bs_monitor.braze   import bJobInstQuery
from bs_monitor.braze   import bLazyLoad

from bs_monitor.db.tables import tBatch
from bs_monitor.db.tables import tBatchInst
from bs_monitor.db.tables import tJobInst
from bs_monitor.db.tables import tJobInstMetric
from bs_monitor.db.tables import oJobInstSearch


class MonitorCliArgs:
    """
    This a class that defines the standard command line arguements for the standard monitor client.  This
    class could be extended by anyone implementing the monitor.
    """

    USAGE_MASK    = '  --%-16.16s  %-15.15s  %s'
    DT_FMT        = '%Y-%m-%d'
    TIMESTAMP_FMT = '%Y-%m-%d %H:%M:%S'

    def __init__(self):
        """
        Constrcutor define all the args.
        """
        self.arg_tuple = None
        self.opt_arg   = None
        self.opt_targ  = None
        self.opt_val   = None


    def _get_known_args(self) -> list:
        """
        A virtual method that returns a list of arguements that can be accepted.
        """
        return [
            ('batch-list',    '',                'List all the batches',                                           None,    None),  # noqa
            ('batch-status',  '',                'Get all batches and their current instance status',              None,    None),  # noqa
            ('batch-jobs',    '[BID]',           'List the job items the batch BID has',                           'BID',   None),  # noqa
            ('batch-last',    '[BID] [CNT]',     'List the last CNT batch instances for a batch BID',              'BID',   int),   # noqa
            ('batch-rerun',   '[BID]',           'Rerun the last failed job for this batch BID',                   'BID',   None),  # noqa
            ('batch-forceok', '[BID] [REASON]',  'Force OK the last failed job for this batch BID, give a REASON', 'BID',   str),   # noqa
            (),
            ('batchinst-jobs',    '[BIID]',           'Show all the job instances for this batch instance BIID',                  'BIID', None),  # noqa
            ('batchinst-rerun',   '[BIID]',           'Rerun the last failed job for this batch instance BIID',                   'BIID', None),  # noqa
            ('batchinst-forceok', '[BIID] [REASON]',  'Force OK the last failed job for this batch instance BIID, give a REASON', 'BIID', str),   # noqa
            (),
            ('job-list',      '',                'List all the jobs',                                   None,    None),
            ('job-spawn',     '[JID] [ARGS]',    'Spawn a new instance of this job with ARGS',          'JID',   str),
            (),
            ('jobinst-failed',    '[CNT]',           'List the failed job instances',                     'CNT',   None),
            ('jobinst-last',      '[CNT]',           'List the last CNT job instances',                   'CNT',   None),
            ('jobinst-lastdate',  '[CNT] [DATE]',    'List the last CNT job instances from process DATE', 'CNT',   datetime.date),  # noqa
            ('jobinst-rerun',     '[JID]',           'Rerun the job instance JID',                        'JID',   None),
            ('jobinst-forceok',   '[JID] [REASON]',  'Force OK the job instance JID, give a REASON',      'JID',   str),
            ('jobinst-stop',      '[JID] [REASON]',  'Stop a running job instance, give a REASON',        'JID',   str),
            ('jobinst-metrics',   '[JID]',           'Show all the metrics for a job instance ',          'JID',   None),
            ('jobinst-read',      '[JID]',           'Read the specified job instance',                   'JID',   None),
            (),
            ('mondate-list',  '',                'List all the monitor dates',                          None,    None),
            ('mondate-incr',  '[MDATE] [INCR]',  'Increment the MDATE monitor date with an INCR value', 'MDATE', int),
            ('mondate-set',   '[MDATE] [DATE]',  'Set the MDATE monitor date to the value of DATE',     'MDATE', datetime.date),  # noqa
            (),
            ('help',          '',                'This help',                                           None,    None),
        ]


    def read_next_arg(self) -> tuple:
        """
        Reads the next arguement in the argv list.
        """


    def show_usage(self) -> None:
        """
        Shows the usage for the monitor client.
        """
        known_args = self._get_known_args()

        print('Monitor CLI')
        print()
        print(f'usage: {sys.argv[0]} [OPTION]...')
        print()
        print('Options:')

        for ka in known_args:
            if ka:
                print(self.USAGE_MASK % ka[0:3])
            else:
                print()

        print()
        print('   * Please note that the date format it YYYY-MM-DD')
        print()


    def read_args(self, argv: list) -> int:
        """
        Reads the args from the argv.  Returns zero on success or the return code to exit with
        if something was wrong.

        :param argv: The argv list to read the args from.
        :return: The return code for an error, or zero for success.
        """
        if len(argv) < 1 or len(argv[0]) <= 2:
            return 2

        self.arg_tuple = None
        self.opt_arg   = argv[0][2:]

        for ka in self._get_known_args():
            if not ka:
                continue

            if ka[0] == self.opt_arg:
                self.arg_tuple = ka
                break

        if not self.arg_tuple:
            return 2

        if ka[3]:
            if len(argv) < 2:
                print(f'  {ka[3]} target expected\n')
                return 2

            self.opt_targ = argv[1]

        if ka[4]:
            if len(argv) < 3:
                print(f'  {ka[2]} value expected\n')
                return 2

            self.opt_val = argv[2]

            if ka[4] == int:
                if not self.opt_val.isdigit() and not (self.opt_val.startswith('-') and self.opt_val[1:].isdigit()):
                    print(f'  {ka[2]} is not a number\n')
                    return 2

                self.opt_val = int(self.opt_val)

            if ka[4] == datetime.date:
                self.opt_val = datetime.datetime.strptime(self.opt_val, self.DT_FMT)

        if self.opt_arg == 'help':
            return 2

        return 0


class ConsoleCols:
    """
    A helper class to auto space out console ouput.
    """

    def __init__(self):
        self.columns = []
        self.rows    = []


    def append(self, in_row: tuple):
        """
        Adds a new row of items.
        """
        idx = 0
        val = None
        row = []

        for item in in_row:
            if item is None:
                val = ''
            if isinstance(item, str):
                val = item
            elif isinstance(item, int):
                val = str(item)
            elif isinstance(item, float):
                val = '%.2f' % item
            elif isinstance(item, datetime.datetime):
                val = item.strftime(MonitorCliArgs.TIMESTAMP_FMT)
            elif isinstance(item, datetime.date):
                val = item.strftime(MonitorCliArgs.DT_FMT)
            else:
                val = str(val)

            if idx >= len(self.columns):
                self.columns.append(len(val))
            else:
                self.columns[idx] = max(self.columns[idx], len(val))

            idx += 1
            row.append(val)

        self.rows.append(row)


    def print(self):
        if not self.columns or not self.rows:
            return

        mask  = ''
        clen  = len(self.columns)

        for val in self.columns:
            mask += '  %%-%d.%ds' % (val, val)

        print()

        for row in self.rows:
            while len(row) < clen:
                row.append('')

            print(mask % tuple(row))

        print()


class MonitorCli:
    """
    This represents the standard monitor command line interface batch that could be
    implemented on a system. Typically this command line batch is used to inspect the running batches,
    increment the monitor "rundate" by 1 each night at midnight, and even purge old history.

    Typically this batch is overloaded with its database connection. See the py tests overload as a working
    example of how to implimit that.
    """

    def __init__(self, pod: Pod, dao_name: str, args: MonitorCliArgs, db_conn_str: str = None):
        """
        Constructor.  This is uses to initialize the monitor command line batch with a Pod for a db connector and
        logging object, a dao_name so we know which database objects to use, and an instance of the args
        object so we know what we need to do.
        """
        self.args   = args
        self._pod   = pod
        self._dao   = dao_name
        self._mcli  = None
        self._dbcon = None
        self._cstr  = db_conn_str


    def run(self, argv: list) -> int:
        """
        The main running entry point that the batch will hit.

        :param argv: The list of parameters to run for.
        :return: The return code for the batch, zero means sucess.
        """
        rc = self.args.read_args(argv)

        if rc:
            self.args.show_usage()
            return rc

        rc = self._proc_cust_arg_opt()

        if rc != 0:
            rc = self._proc_arg_opt()

        if rc == 2:
            print(f' Arguements [{self.args.opt_arg}, {self.args.opt_targ}, {self.args.opt_val}] not handled\n')

        return rc


    def _init_db_connection(self) -> mettle.db.IConnect:
        """
        Virtual class to connect to the database. This is the one function that each overloading object
        must/should overload.
        """
        from mettle.db.psycopg2.connect import Connect as Psycopg2Connect

        conn = Psycopg2Connect()

        conn.connect(self._db_connection_str())

        return conn


    def _db_connection_str(self) -> str:
        """
        Virtual method to return the database connection string ot use for the monitor.

        :return: The connection string ot be used.
        """
        return self._cstr or 'postgresql://bs:dev@127.0.0.1/bs'


    def _proc_cust_arg_opt(self) -> int:
        """
        A pure virtual function where you can add your own custom argument handling.

        :return: Make this function return zero to handle your customr args.
        """
        return 2


    def _proc_arg_opt(self) -> int:
        """
        A virtual method to process the main arguement option that was passed in.

        :return: If the command was okay or not. Return 2 if arguement not found.
        """
        if self.args.opt_arg == 'batch-list':
            return self._batch_list()

        if self.args.opt_arg == 'batch-status':
            return self._batch_status()

        if self.args.opt_arg == 'batch-jobs':
            return self._batch_jobs()

        if self.args.opt_arg == 'batch-last':
            return self._batch_last()

        if self.args.opt_arg == 'batch-rerun':
            return self._batch_rerun()

        if self.args.opt_arg == 'batch-forceok':
            return self._batch_forceok()

        if self.args.opt_arg == 'batchinst-jobs':
            return self._batchinst_jobs()

        if self.args.opt_arg == 'batchinst-rerun':
            return self._batchinst_rerun()

        if self.args.opt_arg == 'batchinst-forceok':
            return self._batchinst_forceok()

        if self.args.opt_arg == 'job-list':
            return self._job_list()

        if self.args.opt_arg == 'job-spawn':
            return self._job_spawn()

        if self.args.opt_arg == 'jobinst-failed':
            return self._jobinst_failed()

        if self.args.opt_arg == 'jobinst-last':
            return self._jobinst_last()

        if self.args.opt_arg == 'jobinst-lastdate':
            return self._jobinst_lastdate()

        if self.args.opt_arg == 'jobinst-rerun':
            return self._jobinst_rerun()

        if self.args.opt_arg == 'jobinst-forceok':
            return self._jobinst_forceok()

        if self.args.opt_arg == 'jobinst-stop':
            return self._jobinst_stop()

        if self.args.opt_arg == 'jobinst-metrics':
            return self._jobinst_metrics()

        if self.args.opt_arg == 'jobinst-read':
            return self._jobinst_read()

        if self.args.opt_arg == 'mondate-list':
            return self._monitor_date_list()

        if self.args.opt_arg == 'mondate-incr':
            return self._monitor_date_incr()

        if self.args.opt_arg == 'mondate-set':
            return self._monitor_date_set()

        return 2


    def _monitor_client(self) -> MonitorServerImpl:
        """
        Gets and if needed initializes the monitor server.
        """
        if not self._pod.dbcon:
            self._pod.dbcon = self._init_db_connection()

        if not self._mcli:
            self._mcli = MonitorServerImpl(self._pod, self._dao, True)

        return self._mcli


    def _batch_list(self) -> int:
        mcli  = self._monitor_client()
        blist = mcli.batch_list(bLazyLoad(), bBatchQuery())
        ccols = ConsoleCols()

        print('\n Batches:')
        ccols.append(('ID', 'PARENT', 'NAME', 'GROUP', 'STATUS', 'RUN DATE', 'TIME', 'CYCLE', 'EXTRA DATA'))

        for rec in blist:
            ccols.append((rec.id,
                          rec.parent_id,
                          rec.name,
                          rec.group_id,
                          tBatch.Status_Couplet.get_value(rec.status),
                          rec.run_date,
                          rec.run_time,
                          f'{tBatch.Cycle_Couplet.get_value(rec.cycle)}:{rec.run_interval}',
                          rec.ext_data))

        ccols.print()
        return 0


    def _batch_status(self) -> int:
        mcli  = self._monitor_client()
        blist = mcli.batch_latest_inst_list(bLazyLoad(), bBatchQuery())
        ccols = ConsoleCols()

        print('\n Batches & Instance Status:')
        ccols.append(('BATCH ID', 'PARENT', 'NAME', 'GROUP', 'STATUS', 'RUN DATE', 'INST ID', 'INST STATUS', 'START DATE', 'END DATE'))  # noqa

        for rec in blist:
            ccols.append((rec.brec.id,
                          rec.brec.parent_id,
                          rec.brec.name,
                          rec.brec.group_id,
                          tBatch.Status_Couplet.get_value(rec.brec.status),
                          rec.brec.run_date,
                          rec.irec.id,
                          tBatchInst.Status_Couplet.get_value(rec.irec.status),
                          rec.irec.start_date,
                          rec.irec.end_date))

        ccols.print()
        return 0


    def _batch_jobs(self) -> int:
        mcli  = self._monitor_client()
        brec  = mcli.batch_read(self._arg_targ_id(), self._arg_targ_name())
        blist = mcli.batchitem_list(brec.id)
        ccols = ConsoleCols()

        print(f'\n [{brec.name}] Batch Jobs:')
        ccols.append(('IDX', 'JOB ID', 'JOB NAME', 'JOB GROUP', 'EXTRA ARGS'))

        for rec in blist:
            jrec = mcli.job_read(rec.job_id, '')
            ccols.append((rec.id, rec.job_id, jrec.name, jrec.group_id, rec.extra_args))

        ccols.print()
        return 0


    def _batch_last(self) -> int:
        mcli  = self._monitor_client()
        brec  = mcli.batch_read(self._arg_targ_id(), self._arg_targ_name())
        blist = mcli.batchinst_list(bLazyLoad(0, self.args.opt_val), bBatchInstQuery(None, None, brec.id))
        ccols = ConsoleCols()

        print(f'\n [{brec.name}] Batches Instances:')
        ccols.append(('ID', 'PARENT', 'STATUS', 'RUN DATE', 'START DATE', 'END DATE'))

        for rec in blist:
            ccols.append((rec.id,
                          rec.parent_id,
                          tBatchInst.Status_Couplet.get_value(rec.status),
                          rec.run_date,
                          rec.start_date,
                          rec.end_date))

        ccols.print()
        return 0


    def _batch_rerun(self) -> int:
        mcli  = self._monitor_client()
        brec  = mcli.batch_read(self._arg_targ_id(), self._arg_targ_name())
        qry   = bJobInstQuery(batch_id = brec.id)

        qry.jobinst_status.append(tJobInst.Status_Couplet.key_failed)

        jlist = mcli.jobinst_list(bLazyLoad(), qry)

        if not jlist:
            print('\n  - No failed jobs found to rerun...\n')
            return 0

        ccols = ConsoleCols()

        print(f'\n {len(jlist)} [{brec.name}] jobs to be marked for rerun :')
        ccols.append(('JOBINST ID', 'JOB NAME', 'JOB_ID', 'PROCESS DATE', 'BATCHINST ID', 'BATCH DATE'))

        jlist.reverse()

        for rec in jlist:
            mcli.jobinst_rerun(rec.inst_rec.id, False)
            ccols.append((rec.inst_rec.id,
                          rec.job_name,
                          rec.job_id,
                          rec.inst_rec.process_date,
                          rec.batchinst_id,
                          rec.batchinst_run_date))

        ccols.print()
        return 0


    def _batch_forceok(self) -> int:
        mcli  = self._monitor_client()
        brec  = mcli.batch_read(self._arg_targ_id(), self._arg_targ_name())
        qry   = bJobInstQuery(batch_id = brec.id)

        qry.jobinst_status.append(tJobInst.Status_Couplet.key_failed)

        jlist = mcli.jobinst_list(bLazyLoad(), qry)

        if not jlist:
            print('\n  - No failed jobs found to force ok...\n')
            return 0

        ccols = ConsoleCols()

        print(f'\n {len(jlist)} [{brec.name}] jobs to be force ok :')
        ccols.append(('JOBINST ID', 'JOB NAME', 'JOB_ID', 'PROCESS DATE', 'BATCHINST ID', 'BATCH DATE'))

        jlist.reverse()

        for rec in jlist:
            mcli.jobinst_force_ok(rec.inst_rec.id, self.args.opt_val)
            ccols.append((rec.inst_rec.id,
                          rec.job_name,
                          rec.job_id,
                          rec.inst_rec.process_date,
                          rec.batchinst_id,
                          rec.batchinst_run_date))

        ccols.print()
        return 0


    def _batchinst_jobs(self) -> int:
        mcli  = self._monitor_client()
        brec  = mcli.batchinst_read(self._arg_targ_id())
        qry   = bJobInstQuery(batchinst_id = brec.id)
        jlist = mcli.jobinst_list(bLazyLoad(), qry)

        if not jlist:
            print('\n  - No jobs found for batch instance...\n')
            return 0

        ccols = ConsoleCols()

        print(f'\n {brec} jobs :')
        ccols.append(('JOBINST ID', 'STATUS', 'JOB NAME', 'JOB_ID', 'EXTRA ARGS', 'PROCESS DATE', 'GROUP', 'PRIORITY', 'TIMESTAMP'))  # noqa

        for rec in jlist:
            ccols.append((rec.inst_rec.id,
                          tJobInst.Status_Couplet.get_value(rec.inst_rec.status),
                          rec.job_name,
                          rec.job_id,
                          rec.inst_rec.extra_args,
                          rec.inst_rec.process_date,
                          rec.inst_rec.group_job,
                          rec.inst_rec.priority,
                          rec.inst_rec.stamp_tm))

        ccols.print()
        return 0


    def _batchinst_rerun(self) -> int:
        mcli  = self._monitor_client()
        brec  = mcli.batchinst_read(self._arg_targ_id())
        qry   = bJobInstQuery(batchinst_id = brec.id)

        qry.jobinst_status.append(tJobInst.Status_Couplet.key_failed)

        jlist = mcli.jobinst_list(bLazyLoad(), qry)

        if not jlist:
            print('\n  - No failed jobs found to rerun for batch instance...\n')
            return 0

        ccols = ConsoleCols()

        print(f'\n {len(jlist)} {brec} jobs to be marked for rerun:')
        ccols.append(('JOBINST ID', 'JOB NAME', 'JOB ID', 'PROCESS DATE', 'TIMESTAMP'))

        jlist.reverse()

        for rec in jlist:
            mcli.jobinst_rerun(rec.inst_rec.id, False)
            ccols.append((rec.inst_rec.id, rec.job_name, rec.job_id, rec.inst_rec.process_date, rec.inst_rec.stamp_tm))

        ccols.print()
        return 0


    def _batchinst_forceok(self) -> int:
        mcli  = self._monitor_client()
        brec  = mcli.batchinst_read(self._arg_targ_id())
        qry   = bJobInstQuery(batchinst_id = brec.id)

        qry.jobinst_status.append(tJobInst.Status_Couplet.key_failed)

        jlist = mcli.jobinst_list(bLazyLoad(), qry)

        if not jlist:
            print('\n  - No failed jobs found to force ok for batch instance...\n')
            return 0

        ccols = ConsoleCols()

        print(f'\n {len(jlist)} {brec} jobs to be marked to be forced ok:')
        ccols.append(('JOBINST ID', 'JOB NAME', 'JOB ID', 'PROCESS DATE', 'TIMESTAMP'))

        jlist.reverse()

        for rec in jlist:
            mcli.jobinst_force_ok(rec.inst_rec.id, self.args.opt_val)
            ccols.append((rec.inst_rec.id, rec.job_name, rec.job_id, rec.inst_rec.process_date, rec.inst_rec.stamp_tm))

        ccols.print()
        return 0


    def _job_list(self) -> int:
        mcli  = self._monitor_client()
        jlist = mcli.job_list(bLazyLoad(), '', '')
        ccols = ConsoleCols()

        print('\n Jobs:')
        ccols.append(('ID', 'NAME', 'GROUP', 'PRIORITY', 'PATH', 'ARGS'))

        for rec in jlist:
            ccols.append((rec.id, rec.name, rec.group_id, str(rec.priority), rec.program_path, rec.program_args))

        ccols.print()
        return 0


    def _job_spawn(self) -> int:
        mcli  = self._monitor_client()
        jrec  = mcli.job_schedule(self._arg_targ_id(),
                                  self._arg_targ_name(),
                                  datetime.datetime.now(),
                                  self.args.opt_val,
                                  10,
                                  None)

        print(f'\n Job instance created: {jrec}\n')
        return 0


    def _jobinst_failed(self) -> int:
        mcli  = self._monitor_client()
        qry   = bJobInstQuery()

        qry.jobinst_status.append(tJobInst.Status_Couplet.key_failed)

        jlist = mcli.jobinst_list(bLazyLoad(0, self._arg_targ_cnt()), qry)

        if not jlist:
            print('\n No failed jobs found...\n')
        else:
            print('\n Failed Job Instances:')
            self._print_jobsinst(jlist)

        return 0


    def _jobinst_last(self) -> int:
        mcli  = self._monitor_client()
        qry   = bJobInstQuery()

        jlist = mcli.jobinst_list(bLazyLoad(0, self._arg_targ_cnt()), qry)

        if not jlist:
            print('\n No jobs found...\n')
        else:
            print(f'\n Last [{self._arg_targ_cnt()}] Job Instances:')
            self._print_jobsinst(jlist)

        return 0


    def _jobinst_lastdate(self) -> int:
        mcli  = self._monitor_client()
        qry   = bJobInstQuery()
        dt    = self.args.opt_val

        qry.date_to = datetime.datetime(dt.year, dt.month, dt.day, 23, 59, 59)

        jlist = mcli.jobinst_list(bLazyLoad(0, self._arg_targ_cnt()), qry)

        if not jlist:
            print('\n No jobs found...\n')
        else:
            print(f'\n Last [{self._arg_targ_cnt()}] for [{self.args.opt_val} Job Instances:')
            self._print_jobsinst(jlist)

        return 0


    def _jobinst_rerun(self) -> int:
        mcli = self._monitor_client()
        jrec = mcli.jobinst_rerun(self._arg_targ_id(), True)

        print(f'\n Job set for rerun:\n\n  {jrec}\n')
        return 0


    def _jobinst_forceok(self) -> int:
        mcli = self._monitor_client()
        jrec = mcli.jobinst_force_ok(self._arg_targ_id(), self.args.opt_val)

        print(f'\n Job forced ok:\n\n  {jrec}\n')
        return 0


    def _jobinst_stop(self) -> int:
        mcli = self._monitor_client()
        mcli.jobinst_stop(self._arg_targ_id(), self.args.opt_val)

        print('\n Job stop has been requested:\n')
        return 0


    def _jobinst_metrics(self) -> int:
        mcli  = self._monitor_client()
        mlist = mcli.jobinst_metrics(bLazyLoad(), self._arg_targ_id())
        ccols = ConsoleCols()

        print(f'\n [{self._arg_targ_id()}] Job Instance Metrics:')

        ccols.append(('TIMESTAMP', 'TYPE', 'MESSAGE'))

        for rec in mlist:
            ccols.append((rec.stamp_tm, tJobInstMetric.Mtype_Couplet.get_value(rec.mtype), rec.msg))

        ccols.print()
        return 0


    def _jobinst_read(self) -> int:
        mcli = self._monitor_client()
        jrec = mcli.jobinst_read(self._arg_targ_id())

        print(f'\n {jrec}\n')
        return 0


    def _monitor_date_list(self) -> int:
        mcli  = self._monitor_client()
        mlist = mcli.mondate_list(bLazyLoad(), '')
        ccols = ConsoleCols()

        print('\n Monitor Dates:')
        ccols.append(('ID', 'DATE', 'DESCRIPTION'))

        for rec in mlist:
            ccols.append((rec.id, rec.value, rec.descr))

        ccols.print()
        return 0


    def _monitor_date_incr(self) -> int:
        mcli  = self._monitor_client()
        rec   = mcli.mondate_increment(self.args.opt_targ, self.args.opt_val)

        print(f'\n [{rec.id}] date has changed to: {rec.value.strftime(MonitorCliArgs.DT_FMT)}\n')
        return 0


    def _monitor_date_set(self) -> int:
        mcli  = self._monitor_client()
        rec   = mcli.mondate_set_value(self.args.opt_targ, self.args.opt_val)

        print(f'\n [{rec.id}] date has been set to: {rec.value.strftime(MonitorCliArgs.DT_FMT)}\n')
        return 0


    def _arg_targ_id(self) -> int:
        return int(self.args.opt_targ) if self.args.opt_targ.isdigit() else 0


    def _arg_targ_name(self) -> str:
        return self.args.opt_targ  if not self.args.opt_targ.isdigit() else ''


    def _arg_targ_cnt(self) -> int:
        if not self.args.opt_targ.isdigit():
            raise 'CNT is not a number'

        return int(self.args.opt_targ)


    def _print_jobsinst(self, jlist: oJobInstSearch.List) -> None:
        ccols = ConsoleCols()

        ccols.append(('JOBINST ID',
                      'PARENT',
                      'STATUS',
                      'PROCESS DATE',
                      'EXTRA ARGS',
                      'TIMESTAMP',
                      'JOB NAME',
                      'JOB ID',
                      'BATCHINST ID',
                      'BATCH NAME',
                      'BATCH ID'))

        for rec in jlist:
            ccols.append((rec.inst_rec.id,
                          rec.inst_rec.parent_id,
                          tJobInst.Status_Couplet.get_value(rec.inst_rec.status),
                          rec.inst_rec.process_date,
                          rec.inst_rec.extra_args,
                          rec.inst_rec.stamp_tm,
                          rec.job_name,
                          rec.job_id,
                          rec.inst_rec.batchinst_id,
                          rec.batch_name,
                          rec.batch_id))

        ccols.print()


#
# Below is a typical example of how to implement this monitor cli batch.  You would need
# to overload the MonitorCli class to provide the correct db connector and connection string.
#


if __name__ == '__main__':
    pod  = Pod(None, None, None)
    mcli = MonitorCli(pod, 'postgresql', MonitorCliArgs())
    rc   = mcli.run(sys.argv[1:])

    if rc:
        sys.exit(rc)
