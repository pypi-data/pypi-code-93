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

from mettle.lib import xMettle
from bs_lib     import Pod
from bs_lib     import query_builder

from bs_lib.auto_transaction import AutoTransaction

import bs_monitor

from . import monitor_util

from bs_monitor.braze     import MonitorServerInterface
from bs_monitor.braze     import bBatchQuery
from bs_monitor.braze     import bBatchInstQuery
from bs_monitor.braze     import bJobInstQuery
from bs_monitor.braze     import bLazyLoad

from bs_monitor.db.tables import tBatch
from bs_monitor.db.tables import oBatchWithLatestInst
from bs_monitor.db.tables import tBatchItem
from bs_monitor.db.tables import tBatchInst
from bs_monitor.db.tables import tJob
from bs_monitor.db.tables import tJobInst
from bs_monitor.db.tables import tJobInstMetric
from bs_monitor.db.tables import oJobInstSearch
from bs_monitor.db.tables import tMondate


class MonitorServerImpl(MonitorServerInterface):

    MODULE = '[MonitorServerImpl]'

    def __init__(self, pod: Pod, dao_name: str, cli_mode: bool = False):
        """
        Constructor.

        :param pod: The pod to use.
        :param dao_name: Database dao name to use.
        :param cli_mode: If true, them we assume we are running form the command line, and not auth checks are done.
        """
        self._shutdown  = False
        self._pod       = pod
        self._log       = pod.log
        self._dao       = bs_monitor.dao_by_name(dao_name)
        self._cli_mode  = cli_mode
        self._tok_data  = None


    def _set_rpc_token_data(self, tdata):
        self._new_tokeusr_idn   = None
        self._tok_data    = tdata
        self._pod.usr_id  = ''
        self._pod.usr_id  = self._usr_id()


    def _usr_id(self):
        if self._pod.usr_id:
            return self._pod.usr_id

        if self._cli_mode:
            return f'[CLI-{os.getenv("USER") or "ANON"}]'

        if not self._tok_data:
            raise Exception('Auth user required for RPC call, but no user is logged in!')

        usr_id = self._tok_data.get('usr')

        if not usr_id:
            raise Exception('Auth user is not set!')

        return usr_id


    # ------------------------------------------------------------------------
    # SERVER INTERFACE METHODS
    # ------------------------------------------------------------------------


    # --- Batch RPCs ---


    def batch_create(self,
                     rec: tBatch) -> tBatch:
        with AutoTransaction(self._pod) as at:
            self._validate_batch(rec)

            dupqry = self._dao.dBatchByName(self._pod.dbcon)

            if dupqry.exec_deft(rec.name).fetch():
                raise xMettle('Batch name already exists')

            dbat = self._dao.dBatch(self._pod.dbcon)
            rec.stamp_by = self._usr_id()

            dbat.insert(rec)
            at.commit()

            return dbat.rec


    def batch_read(self,
                   batch_id: int,
                   batch_name: str) -> tBatch:
        with AutoTransaction(self._pod):
            if batch_id:
                dbat = self._dao.dBatch(self._pod.dbcon)

                if dbat.try_select_one_deft(batch_id):
                    return dbat.rec

            elif batch_name:
                qry = self._dao.dBatchByName(self._pod.dbcon)

                if qry.exec_deft(batch_name).fetch():
                    return qry.orec

        raise xMettle('Not found.')


    def batch_update(self,
                     rec: tBatch) -> tBatch:
        with AutoTransaction(self._pod) as at:
            self._validate_batch(rec)

            dbat = self._dao.dBatch(self._pod.dbcon)

            if not dbat.try_select_one_deft(rec.id):
                raise xMettle('Not found.')

            rec.stamp_by = self._usr_id()

            dbat.update(rec)
            at.commit()

            return dbat.rec


    def batch_delete(self,
                     batch_id: int):
        with AutoTransaction(self._pod) as at:
            dbat = self._dao.dBatch(self._pod.dbcon)

            self._dao.dBatchItemDeleteByBatchId(self._pod.dbcon).exec_deft(batch_id)

            dbat.delete_one_deft(batch_id)
            at.commit()


    def batch_list(self,
                   lazy_load: bLazyLoad,
                   query: bBatchQuery) -> tBatch.List:
        with AutoTransaction(self._pod):
            res  = tBatch.List()
            qry  = self._dao.dBatchSearch(self._pod.dbcon)
            crit = ''

            if query.batch_id:
                crit += query_builder.dyn_crit(query.batch_id, 'b', 'id')

            if query.name:
                crit += query_builder.dyn_crit(query.name, 'b', 'name')

            if query.status:
                crit += query_builder.dyn_list(query.status, 'b', 'status')

            if query.group:
                crit += query_builder.dyn_crit(query.group_job, 'b', 'group_id')

            qry.exec_deft(crit, monitor_util.append_lazy_load(lazy_load))
            qry.fetch_all(res)

            return res


    def batch_latest_inst_list(self,
                               lazy_load: bLazyLoad,
                               query: bBatchQuery) -> oBatchWithLatestInst.List:
        with AutoTransaction(self._pod):
            res  = oBatchWithLatestInst.List()
            qry  = self._dao.dBatchWithLatestInst(self._pod.dbcon)
            crit = ''

            if query.batch_id:
                crit += query_builder.dyn_crit(query.batch_id, 'b', 'id')

            if query.name:
                crit += query_builder.dyn_crit(query.name, 'b', 'name')

            if query.status:
                crit += query_builder.dyn_list(query.status, 'b', 'status')

            if query.group:
                crit += query_builder.dyn_crit(query.group_job, 'b', 'group_id')

            qry.exec_deft(crit, monitor_util.append_lazy_load(lazy_load))
            qry.fetch_all(res)

            for x in res:
                if not x.irec.status:
                    x.irec.status = tBatchInst.Status_Couplet.key_not_applicable

            return res


    # --- Batch Instance RPCs ---


    def batchinst_read(self,
                       batchinst_id: int) -> tBatchInst:
        with AutoTransaction(self._pod):
            return self._dao.dBatchInst(self._pod.dbcon).select_one_deft(batchinst_id).rec


    def batchinst_list(self,
                       lazy_load: bLazyLoad,
                       query: bBatchInstQuery) -> tBatchInst.List:
        with AutoTransaction(self._pod):
            res  = tBatchInst.List()
            qry  = self._dao.dBatchInstSearch(self._pod.dbcon)
            crit = ''

            if query.batch_id:
                crit += query_builder.dyn_crit(query.batch_id, 'bi', 'batch_id')

            if query.status:
                crit += query_builder.dyn_list(query.status, 'bi', 'status')

            qry.exec_deft(query.date_from, query.date_to, crit, monitor_util.append_lazy_load(lazy_load))
            qry.fetch_all(res)

            return res


    # --- Batch Item RPCs ---


    def batchitem_create(self,
                         rec: tBatchItem) -> tBatchItem:
        with AutoTransaction(self._pod) as at:
            self._validate_batchitem(rec)

            bat   = self._dao.dBatch(self._pod.dbcon)
            bitem = self._dao.dBatchItem(self._pod.dbcon)

            bat.lock_one_deft(rec.batch_id, self._pod.std_db_lock())

            all_items = self.batchitem_list(rec.batch_id)

            self._create_shift_space(rec.batch_id, all_items, rec.id)

            rec.stamp_by = self._pod.usr_id

            bitem.insert(rec)
            at.commit()

            return bitem.rec


    def batchitem_read(self,
                       batchitem_id: int,
                       batch_id: int) -> tBatchItem:
        with AutoTransaction(self._pod):
            return self._dao.dBatchItem(self._pod.dbcon).select_one_deft(batchitem_id, batch_id).rec


    def batchitem_update(self,
                         rec: tBatchItem) -> tBatchItem:
        with AutoTransaction(self._pod) as at:
            self._validate_batchitem(rec)

            bat   = self._dao.dBatch(self._pod.dbcon)
            bitem = self._dao.dBatchItem(self._pod.dbcon)

            bat.lock_one_deft(rec.batch_id, self._pod.std_db_lock())

            rec.stamp_by = self._pod.usr_id

            bitem.update(rec)
            at.commit()

            return bitem.rec


    def batchitem_shift(self,
                        batchitem_id: int,
                        batch_id: int,
                        shift_idx: int) -> tBatchItem:
        new_pos = batchitem_id + shift_idx

        if new_pos < 1:
            new_pos = 1

        with AutoTransaction(self._pod) as at:
            bat    = self._dao.dBatch(self._pod.dbcon)
            bitem  = self._dao.dBatchItem(self._pod.dbcon)

            bat.lock_one_deft(batch_id, self._pod.std_db_lock())
            bitem.select_one_deft(batchitem_id, batch_id)

            all_items = self.batchitem_list(batch_id)

            self._create_shift_space(batch_id, all_items, new_pos, batchitem_id)

            bitem.select_one_deft(new_pos, batch_id)

            bitem.rec.stamp_by = self._pod.usr_id
            at.commit()

            return bitem.rec


    def batchitem_delete(self,
                         batchitem_id: int,
                         batch_id: int):
        with AutoTransaction(self._pod) as at:
            bat   = self._dao.dBatch(self._pod.dbcon)
            bitem = self._dao.dBatchItem(self._pod.dbcon)

            bat.lock_one_deft(batch_id, self._pod.std_db_lock())
            bitem.delete_one_deft(batchitem_id, batch_id)
            at.commit()


    def batchitem_list(self,
                       batch_id: int) -> tBatchItem.List:
        with AutoTransaction(self._pod):
            res = tBatchItem.List()
            qry = self._dao.dBatchItemByBatchId(self._pod.dbcon)

            qry.exec_deft(batch_id, '').fetch_all(res)

            return res


    # --- Job RPCs ---


    def job_create(self,
                   rec: tJob) -> tJob:
        with AutoTransaction(self._pod) as at:
            djob = self._dao.dJob(self._pod.dbcon)
            rec.stamp_by = self._usr_id()

            djob.insert(rec)
            at.commit()

            return djob.rec


    def job_read(self,
                 job_id: int,
                 job_name: str) -> tJob:
        with AutoTransaction(self._pod):
            if job_id:
                djob = self._dao.dJob(self._pod.dbcon)

                if djob.try_select_one_deft(job_id):
                    return djob.rec

            elif job_name:
                qry = self._dao.dJobByName(self._pod.dbcon)

                if qry.exec_deft(job_name).fetch():
                    return qry.orec

        raise xMettle('Not found.')


    def job_update(self,
                   rec: tJob) -> tJob:
        with AutoTransaction(self._pod) as at:
            djob = self._dao.dJob(self._pod.dbcon)

            if not djob.try_select_one_deft(rec.id):
                raise xMettle('Not found.')

            rec.stamp_by = self._usr_id()
            djob.update(rec)
            at.commit()

            return djob.rec


    def job_delete(self,
                   job_id: int):
        with AutoTransaction(self._pod) as at:
            djob = self._dao.dJob(self._pod.dbcon)

            djob.delete_one_deft(job_id)
            at.commit()


    def job_list(self,
                 lazy_load: bLazyLoad,
                 wc_job_name: str,
                 wc_group: str) -> tJob.List:
        with AutoTransaction(self._pod):
            res = tJob.List()
            qry = self._dao.dJobSearch(self._pod.dbcon)

            if wc_job_name:
                qry.irec.criteria += query_builder.dyn_crit(wc_job_name, 'j', 'name', always_like = True)

            if wc_group:
                qry.irec.criteria += query_builder.dyn_crit(wc_group, 'j', 'group_id', always_like = True)

            qry.irec.limoff = monitor_util.append_lazy_load(lazy_load)

            qry.exec()
            qry.fetch_all(res)

            return res


    def job_schedule(self,
                     job_id: int,
                     job_name: str,
                     run_date: datetime.datetime,
                     extra_args: str,
                     priority: int,
                     parent_id: int) -> tJobInst:
        with AutoTransaction(self._pod) as at:
            jrec  = self.job_read(job_id, job_name)
            jinst = self._dao.dJobInst(self._pod.dbcon)

            if priority:
                if priority < tJob.Priority_Couplet.key_highest:
                    priority = tJob.Priority_Couplet.key_highest
                elif priority > tJob.Priority_Couplet.key_lowest:
                    priority = tJob.Priority_Couplet.key_lowest

            jinst.insert_deft(parent_id or None,
                              jrec.id,
                              None,
                              run_date,
                              priority or jrec.priority,
                              tJobInst.Status_Couplet.key_pending,
                              extra_args,
                              jrec.group_id,
                              '',
                              self._usr_id())

            at.commit()

            return jinst.rec


    # --- Job Instance RPCs ---


    def jobinst_read(self,
                     jobinst_id: int) -> tJobInst:
        with AutoTransaction(self._pod):
            return self._dao.dJobInst(self._pod.dbcon).select_one_deft(jobinst_id).rec


    def jobinst_rerun(self,
                      jobinst_id: int,
                      force_rerun: bool) -> tJobInst:
        with AutoTransaction(self._pod) as at:
            jobinst = self._dao.dJobInst(self._pod.dbcon)

            jobinst.lock_one_deft(jobinst_id, self._pod.std_db_lock())

            if jobinst.rec.status == tJobInst.Status_Couplet.key_failed or\
                    (jobinst.rec.status == tJobInst.Status_Couplet.key_completed and force_rerun):

                jobinst.rec.status   = tJobInst.Status_Couplet.key_pending
                jobinst.rec.stamp_by = self._usr_id()
                jobinst.update()
                at.commit()

            return jobinst.rec


    def jobinst_force_ok(self,
                         jobinst_id: int,
                         reason: str) -> tJobInst:
        with AutoTransaction(self._pod) as at:
            jobinst = self._dao.dJobInst(self._pod.dbcon)

            jobinst.lock_one_deft(jobinst_id, self._pod.std_db_lock())

            if jobinst.rec.status == tJobInst.Status_Couplet.key_failed:
                jobinst.rec.status   = tJobInst.Status_Couplet.key_forced_okay
                jobinst.rec.stamp_by = self._usr_id()
                jobinst.update()

                self._dao.dJobInstMetric(self._pod.dbcon).insert_deft(
                    jobinst_id,
                    tJobInstMetric.Mtype_Couplet.key_forced_okay,
                    f'[{self._usr_id()}] { reason or "Unknown reason" }')

                at.commit()

            return jobinst.rec


    def jobinst_stop(self,
                     jobinst_id: int,
                     reason: str):
        with AutoTransaction(self._pod) as at:
            ji = self._dao.dJobInst(self._pod.dbcon)

            if not ji.try_select_one_deft(jobinst_id):
                return

            if ji.rec.status != tJobInst.Status_Couplet.key_running:
                return

            jican = self._dao.dJobInstCancel(self._pod.dbcon)

            if jican.try_select_one_deft(jobinst_id):
                return

            jican.insert_deft(jobinst_id, reason or 'Unknown reason', self._usr_id())
            at.commit()


    def jobinst_list(self,
                     lazy_load: bLazyLoad,
                     query: bJobInstQuery) -> oJobInstSearch.List:
        with AutoTransaction(self._pod):
            res  = oJobInstSearch.List()
            qry  = self._dao.dJobInstSearch(self._pod.dbcon)
            crit = ''

            if query.job_id:
                crit += query_builder.dyn_crit(query.job_id, 'j', 'id')

            if query.job_name:
                crit += query_builder.dyn_crit(query.job_name, 'j', 'name')

            if query.jobinst_id:
                crit += query_builder.dyn_list(query.jobinst_id, 'i', 'id')

            if query.jobinst_status:
                crit += query_builder.dyn_list(query.jobinst_status, 'i', 'status')

            if query.group_job:
                crit += query_builder.dyn_crit(query.group_job, 'i', 'group_job')

            if query.group_batch:
                crit += query_builder.dyn_crit(query.group_job, 'i', 'group_batch')

            if query.batch_id:
                crit += query_builder.dyn_crit(query.batch_id, 'bi', 'batch_id')

            if query.batchinst_id:
                crit += query_builder.dyn_crit(query.batchinst_id, 'bi', 'id')

            qry.exec_deft(query.date_from, query.date_to, crit, monitor_util.append_lazy_load(lazy_load))
            qry.fetch_all(res)

            return res


    def jobinst_metrics(self,
                        lazy_load: bLazyLoad,
                        jobinst_id: int) -> tJobInstMetric.List:
        with AutoTransaction(self._pod):
            res = tJobInstMetric.List()
            qry = self._dao.dJobInstMetricByJobInst(self._pod.dbcon)

            qry.exec_deft(jobinst_id, monitor_util.append_lazy_load(lazy_load))
            qry.fetch_all(res)

            return res


    # --- Mondate RPCs ---


    def mondate_create(self,
                       rec: tMondate) -> tMondate:
        with AutoTransaction(self._pod) as at:
            dmon = self._dao.dMondate(self._pod.dbcon)
            rec.stamp_by = self._usr_id()

            dmon.insert(rec)
            at.commit()

            return dmon.rec


    def mondate_read(self,
                     mondate_id: str) -> tMondate:
        with AutoTransaction(self._pod):
            dmon = self._dao.dMondate(self._pod.dbcon)

            if not dmon.try_select_one_deft(mondate_id):
                raise xMettle('Not found.')

            return dmon.rec


    def mondate_update(self,
                       rec: tMondate) -> tMondate:
        with AutoTransaction(self._pod) as at:
            dmon = self._dao.dMondate(self._pod.dbcon)

            if not dmon.try_select_one_deft(rec.id):
                raise xMettle('Not found.')

            rec.stamp_by = self._usr_id()
            dmon.update(rec)
            at.commit()

            return dmon.rec


    def mondate_delete(self,
                       mondate_id: str):
        with AutoTransaction(self._pod) as at:
            dmon = self._dao.dMondate(self._pod.dbcon)

            dmon.delete_one_deft(mondate_id)
            at.commit()


    def mondate_list(self,
                     lazy_load: bLazyLoad,
                     wc_mondate_id: str):
        with AutoTransaction(self._pod):
            res = tMondate.List()
            qry = self._dao.dMondateList(self._pod.dbcon)

            if wc_mondate_id:
                qry.irec.criteria += query_builder.dyn_crit(wc_mondate_id, 'm', 'id', always_like = True)

            qry.irec.limoff = monitor_util.append_lazy_load(lazy_load)

            qry.exec()
            qry.fetch_all(res)

            return res


    def mondate_increment(self,
                          mondate_id: str,
                          days_value: int) -> tMondate:
        with AutoTransaction(self._pod) as at:
            dmon = self._dao.dMondate(self._pod.dbcon)

            dmon.select_one_deft(mondate_id)

            if not days_value:
                return dmon.rec

            dmon.rec.value    += datetime.timedelta(days=days_value)
            dmon.rec.stamp_by  = self._usr_id()

            dmon.update()
            at.commit()

            return dmon.rec


    def mondate_set_value(self,
                          mondate_id: str,
                          value: datetime.date) -> tMondate:
        with AutoTransaction(self._pod) as at:
            dmon = self._dao.dMondate(self._pod.dbcon)

            dmon.select_one_deft(mondate_id)

            dmon.rec.value    = value
            dmon.rec.stamp_by = self._usr_id()

            dmon.update()
            at.commit()

            return dmon.rec


    def purge_history(self,
                      from_date: datetime.date):
        with AutoTransaction(self._pod) as at:
            self._dao.dJobInstMetricPurge(self._pod.dbcon).exec_deft(from_date)
            self._dao.dJobInstCancelPurge(self._pod.dbcon).exec_deft(from_date)
            self._dao.dJobInstPurge(self._pod.dbcon).exec_deft(from_date)
            self._dao.dBatchInstPurge(self._pod.dbcon).exec_deft(from_date)

            at.commit()


    def server_date_time(self) -> datetime.datetime:
        return datetime.datetime.now()


    # ------------------------------------------------------------------------
    # PRIVATE METHODS
    # ------------------------------------------------------------------------


    def _validate_batch(self, rec: tBatch) -> None:
        """
        Ensure a batch record is okay.

        :param rec: The batch to validate.
        """
        if rec.run_interval < 1:
            raise xMettle('Batch run_interval is required')

        if rec.run_interval > 400:
            raise xMettle('Batch run_interval is a little high')

        if not rec.name:
            raise xMettle('Batch name is required')

        if rec.cycle not in tBatch.Cycle_Couplet():
            raise xMettle('Batch cycle is unexpected')

        if rec.status not in tBatch.Status_Couplet():
            raise xMettle('Batch status is unexpected')

        if not rec.run_date:
            raise xMettle('Batch run_date is required')

        if rec.id and rec.parent_id:
            if rec.id == rec.parent_id:
                raise xMettle('Batch cannot be a parent of itself')

            pbat = self._dao.dBatch(self._pod.dbcon)

            parent_id = rec.parent_id

            while parent_id:
                if not pbat.try_select_one_deft(parent_id):
                    raise xMettle(f'Batch parent not found [{parent_id}')

                if pbat.rec.parent_id == rec.id:
                    raise xMettle(f'Batch parent circular refernce detecte with batch [{pbat.rec.id}: {pbat.rec.name}')

                parent_id = pbat.rec.parent_id


    def _validate_batchitem(self, rec: tBatchItem) -> None:
        """
        Ensure a batch item record is okay.

        :param rec: The batch item to validate.
        """
        if rec.id < 1:
            raise xMettle('BatchItem id must be greater than zero')

        if rec.id > 10_000:
            raise xMettle('BatchItem id is insane')

        job = self._dao.dJob(self._pod.dbcon)

        if not job.try_select_one_deft(rec.job_id):
            raise xMettle('Job not found')


    def _create_shift_space(self,
                            batch_id      : int,
                            items         : tBatchItem.List,
                            shift_space   : int,
                            to_move_id    : int = 0) -> None:
        """
        Creates a space inside the bathc items to shift/insert a new record.

        :param batch_id: The parent batch identifier.
        :param items: All the current batch item.
        :param shift_space: The space identifier desired.
        :param to_move_id: The item that wants to move into the space, or zero for an insert.
        """
        is_occupied = False

        for item in items:
            if item.id == shift_space:
                is_occupied = True
                break

        if not is_occupied:
            return

        swop = self._dao.dBatchItemSwopId(self._pod.dbcon)

        if to_move_id:
            swop.exec_deft(batch_id, to_move_id, 0)

        for item in items:
            if item.id >= shift_space:
                swop.exec_deft(batch_id, item.id, 0 - item.id)

        if to_move_id:
            swop.exec_deft(batch_id, 0, shift_space)

        offset = shift_space

        for item in items:
            if item.id >= shift_space:
                offset += 1
                swop.exec_deft(batch_id, 0 - item.id, offset)
