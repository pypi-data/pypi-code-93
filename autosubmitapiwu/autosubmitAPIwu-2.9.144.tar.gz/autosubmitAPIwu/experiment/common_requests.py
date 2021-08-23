#!/usr/bin/env python

# Copyright 2015 Earth Sciences Department, BSC-CNS

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

"""
Module containing functions to manage autosubmit's experiments.
"""
import os
import sys
import string
import time
import pickle
import traceback
import textwrap
import sqlite3
import datetime
import copy
import math
import json
import multiprocessing
import subprocess
import numpy as np
from collections import deque

# try:
#     import tkinter
# except:
#     import Tkinter as tkinter


import autosubmitAPIwu.database.db_common as db_common
from autosubmitAPIwu.job.job_list import JobList
from autosubmitAPIwu.job.job import Job
from autosubmitAPIwu.job.job_utils import SubJobManager, SubJob, SimpleJob, datechunk_to_year, tostamp, calculate_SYPD_perjob
from autosubmitAPIwu.job.job_package_persistence import JobPackagePersistence
from autosubmitAPIwu.job.job_grouping import JobGrouping
from autosubmitAPIwu.monitor.monitor import Monitor
from autosubmitAPIwu.job.job_common import Status, Type
from autosubmitAPIwu.experiment.statistics import ExperimentStats
import autosubmitAPIwu.experiment.common_db_requests as DbRequests
import autosubmitAPIwu.database.db_jobdata as JobData
from autosubmitAPIwu.config.basicConfig import BasicConfig
from autosubmitAPIwu.config.config_common import AutosubmitConfig
from bscearth.utils.config_parser import ConfigParserFactory
from bscearth.utils.log import Log
from bscearth.utils.date import date2str
from autosubmitAPIwu.autosubmit import Autosubmit
import autosubmitAPIwu.database.db_structure as DbStructure
from autosubmitAPIwu.database.db_jobdata import JobDataStructure, ExperimentGraphDrawing
from autosubmitAPIwu.database.db_jobdata import DB_VERSION_SCHEMA_CHANGES
import socket

SAFE_TIME_LIMIT = 300
SAFE_TIME_LIMIT_STATUS = 180


# def get_experiment_stats_from_historical(expid, filter_period, filter_type):
#     """
#     """
#     error = False
#     error_message = ""
#     period_end = None
#     period_start = None
#     try:
#         if filter_period:
#             filter_period = int(filter_period)
#             period_end = datetime.datetime.now().replace(second=0, microsecond=0)
#             if filter_period > 0:
#                 period_start = period_end - \
#                     datetime.timedelta(hours=filter_period)

#     except Exception as exp:
#         pass


def get_experiment_stats(expid, filter_period, filter_type):
    """
    Lite version of the stats generator from Autosubmit autosubmit.py
    """
    error = False
    error_message = ""
    period_fi = ""
    period_ini = ""
    otherstats = list()
    notallJobs = list()
    jobs = list()
    results = None
    try:
        if filter_period:
            filter_period = int(filter_period)
        # Basic paths
        BasicConfig.read()
        path_structure = BasicConfig.STRUCTURES_DIR
        path_local_root = BasicConfig.LOCAL_ROOT_DIR

        as_conf = AutosubmitConfig(expid, BasicConfig, ConfigParserFactory())
        as_conf.reload()
        # if not as_conf.relo():
        #     raise Exception(
        #         'Autosubmit GUI might not have permission to access necessary configuration files.')
        # notransitive as False by default
        job_list = Autosubmit.load_job_list(expid, as_conf, False)
        # job_list = [job for job in job_list.get_job_list() if job.section not in [Status.READY, Status.WAITING]]
        if filter_type:
            ft = filter_type
            if ft == 'Any':
                notallJobs = job_list.get_job_list()
            else:
                notallJobs = [job for job in job_list.get_job_list()
                              if job.section == ft]
        else:
            ft = 'Any'
            notallJobs = job_list.get_job_list()

        jobs_considered = [job for job in notallJobs if job.status not in [
            Status.READY, Status.WAITING]]

        period_fi = datetime.datetime.now().replace(second=0, microsecond=0)
        if filter_period and filter_period > 0:
            period_ini = period_fi - datetime.timedelta(hours=filter_period)
            jobs_considered = [job for job in jobs_considered if
                               job.check_started_after(period_ini) or job.check_running_after(period_ini)]
        else:
            period_ini = None

        # Get package information
        job_to_package, package_to_jobs, _, _ = JobList.retrieve_packages(
            BasicConfig, expid, [job.name for job in job_list.get_job_list()])
        db_file = os.path.join(path_local_root, "ecearth.db")
        conn = DbRequests.create_connection(db_file)
        # Job information from worker database
        job_times = DbRequests.get_times_detail_by_expid(
            conn, expid)
        # Job information from job historic data
        # print("Get current job data structure...")
        job_data, warning_messages = JobDataStructure(
            expid).process_current_run_collection(job_list.get_job_list(), job_times)

        # Retrieve current job_list structure (dependencies)
        current_table_structure = {}
        if (job_to_package):
            current_table_structure = DbStructure.get_structure(
                expid, path_structure)
        # Model jobs
        subjobs = list()
        job_name_to_job_info = {}
        for job in job_list.get_job_list():
            job_info = JobList.retrieve_times(
                job.status, job.name, job._tmp_path, make_exception=False, job_times=job_times, seconds=True, job_data_collection=job_data)
            # if job_info:
            job_name_to_job_info[job.name] = job_info
            time_total = (job_info.queue_time +
                          job_info.run_time) if job_info else 0
            subjobs.append(SubJob(job.name, job_to_package.get(job.name, None), job_info.queue_time if job_info else 0,
                                  job_info.run_time if job_info else 0, time_total, job_info.status if job_info else Status.UNKNOWN))

        manager = SubJobManager(subjobs, job_to_package,
                                package_to_jobs, current_table_structure)

        if len(jobs_considered) > 0:
            # Getting those predefined stats
            general_stats = []

            general_stats_path = os.path.join(
                BasicConfig.LOCAL_ROOT_DIR, expid, "tmp", expid + "_GENERAL_STATS")
            if os.path.exists(general_stats_path):
                parser = AutosubmitConfig.get_parser(
                    ConfigParserFactory(), general_stats_path)
                for section in parser.sections():
                    general_stats.append((section, ''))
                    general_stats += parser.items(section)
                otherstats = general_stats

            # Handle Wrappers in Queue and Run time calculation

            results = ExperimentStats(
                jobs_considered, period_ini, period_fi, manager.get_collection_of_fixes_applied())

            jobs = [job.name for job in results._jobs_list]
        else:
            raise Exception("There are no {0} jobs in the period from {1} to {2}...".format(
                ft, period_ini, period_fi))

    except Exception as e:
        print(traceback.format_exc())
        error_message = str(e)
        error = True

    return {
        'error': error,
        'error_message': error_message,
        'periodo_fin': period_fi,
        'periodo_ini': period_ini,
        'otherstats': otherstats,
        'jobs': jobs,
        'stats': {
            'max_time': results.max_time if results is not None else "",
            'max_fail': results.max_fail if results is not None else "",
            'queued': results.queued if results is not None else "",
            'run': results.run if results is not None else "",
            'failed_jobs': results.failed_jobs if results is not None else "",
            'fail_queued': results.fail_queued if results is not None else "",
            'fail_run': results.fail_run if results is not None else "",
            'threshold': results.threshold if results is not None else "",
            'totals': results._totals if results is not None else "",
        }
    }


def get_experiment_data(expid):
    """
    Get data of the experiment. Depends on the worker that updates ecearth.db.
    """
    path = 'Not found'
    owner_id = 0
    owner_name = 'Not found'
    datetime_lastAccess = '1900-01-01 00:00:00'
    datetime_lastMod = '1900-01-01 00:00:00'
    error_message = 'None'
    contents = list()
    description = 'None'
    version = 'None'
    model = 'None'
    branch = 'None'
    hpc = 'None'
    updateTime = 10
    error = False
    running = False
    pkl_timestamp = 1000000
    reading = ""
    db_historic_version = None
    total_jobs = completed_jobs = 0
    # chunk_size = 0
    # date_list = []
    # member_list = []

    BasicConfig.read()
    path = BasicConfig.LOCAL_ROOT_DIR + '/' + expid

    if (os.path.exists(path)):
        try:
            as_conf = AutosubmitConfig(
                expid, BasicConfig, ConfigParserFactory())
            if as_conf.check_conf_files() == False:
                raise Exception(
                    'Autosubmit GUI might not have permission to access necessary configuration files.')
            updateTime = as_conf.get_safetysleeptime()
            project_type = as_conf.get_project_type()
            if project_type != "none":
                if not as_conf.check_proj():
                    raise Exception(
                        'Autosubmit GUI might not have permission to access necessary configuration files.')
            if (as_conf.get_svn_project_url()):
                model = as_conf.get_svn_project_url()
                branch = as_conf.get_svn_project_url()
            else:
                model = as_conf.get_git_project_origin()
                branch = as_conf.get_git_project_branch()
            if model is "":
                model = "Not Found"
            if branch is "":
                branch = "Not Found"

            submitter = Autosubmit._get_submitter(as_conf)
            hpc = as_conf.get_platform()

            # date_list = as_conf.get_date_list()
            # member_list = as_conf.get_member_list()
            # chunk_size = as_conf.get_num_chunks()

            resultBase = db_common.get_experiment_by_id(expid)
            description = resultBase['description']
            # Now get version from conf # resultBase['version']
            version = as_conf.get_version()
            path_pkl_file = path + '/pkl/job_list_{0}.pkl'.format(expid)

            if os.path.exists(path_pkl_file):
                pkl_timestamp = int(os.stat(path_pkl_file).st_mtime)

            status = os.stat(path)
            owner_id = status.st_uid
            owner_name = os.popen('id -nu ' + str(owner_id)).read().strip()

            time_lastAccess = int(status.st_atime)
            datetime_lastAccess = datetime.datetime.utcfromtimestamp(
                time_lastAccess).strftime('%Y-%m-%d %H:%M:%S')
            time_lastMod = int(status.st_mtime)
            datetime_lastMod = datetime.datetime.utcfromtimestamp(
                time_lastMod).strftime('%Y-%m-%d %H:%M:%S')

            # Getting some extra data
            job_structure = JobDataStructure(expid)
            db_historic_version = job_structure.db_version
            if job_structure.db_version >= DB_VERSION_SCHEMA_CHANGES:
                # Try getting total and completed from historic database
                experiment_run = job_structure.get_max_id_experiment_run()
                total_jobs = experiment_run.total
                completed_jobs = experiment_run.completed
                if total_jobs == 0:
                    _, total_jobs, completed_jobs = DbRequests.get_experiment_times_by_expid(
                        expid)
            else:
                _, total_jobs, completed_jobs = DbRequests.get_experiment_times_by_expid(
                    expid)

        except Exception as e:
            error_message = str(e)
            error = True
            pass
    else:
        error_message = str(expid) + " not found in " + \
            str(BasicConfig.LOCAL_ROOT_DIR)

    result = {
        'expid': expid,
        'path': path,
        'owner_id': owner_id,
        'owner': owner_name,
        'time_last_access': datetime_lastAccess,
        'time_last_mod': datetime_lastMod,
        'error_message': error_message,
        'description': description,
        'version': version,
        'model': model,
        'branch': branch,
        'hpc': hpc,
        'updateTime': updateTime,
        'error': error,
        'running': running,
        'pkl_timestamp': pkl_timestamp,
        # 'chunk_size': chunk_size,
        # 'date_list': date_list,
        # 'member_list': member_list,
        'total_jobs': total_jobs,
        'completed_jobs': completed_jobs,
        'db_historic_version': db_historic_version}

    return result


def get_current_status_log_plus(expid):
    """
    Get the current status, name of current log, last time modified, and last 5 lines of the latest log of the experiment.
    Presents _is_exp_running as a JSON object.
    """
    error, error_message, is_running, timediff, log_path = _is_exp_running(
        expid)
    return {"error": error,
            "error_message": error_message,
            "is_running": is_running,
            "timediff": timediff,
            "log_path": log_path}


def _is_exp_running(expid, time_condition=300):
    """
    Tests if experiment is running
    :param expid: Experiment name
    :param time_condition: Time constraint, 120 by default. Represents max seconds before an experiment is considered as NOT RUNNING
    :return: (error (true if error is found, false otherwise), error_message, is_running (true if running, false otherwise), timediff, path_to_log)
    :rtype: tuple (bool, string, bool, int)
    """
    is_running = False
    error = False
    error_message = ""
    timediff = 0
    definite_log_path = None
    try:
        BasicConfig.read()
        pathlog_aslog = BasicConfig.LOCAL_ROOT_DIR + '/' + expid + '/' + \
            BasicConfig.LOCAL_TMP_DIR + '/' + BasicConfig.LOCAL_ASLOG_DIR
        pathlog_tmp = BasicConfig.LOCAL_ROOT_DIR + '/' + \
            expid + '/' + BasicConfig.LOCAL_TMP_DIR
        # Basic Configuration
        look_old_folder = False
        current_version = None
        try:
            as_conf = AutosubmitConfig(
                expid, BasicConfig, ConfigParserFactory())
            as_conf.reload()
            current_version = as_conf.get_version()
        except Exception as exp:
            # print(exp)
            pass
        look_old_folder = True if current_version is not None and (str(current_version).startswith(
            "3.11") or str(current_version).startswith("3.9") or str(current_version).startswith("3.12")) else False

        pathlog_first = pathlog_aslog if look_old_folder == False else pathlog_tmp
        pathlog_second = pathlog_aslog if look_old_folder == True else pathlog_tmp
        # print("Experiment {0} version {1} \nLook {2} \nLook {3}".format(
        #     expid, current_version, pathlog_first, pathlog_second))
        # print(pathlog)
        reading = os.popen(
            'ls -t ' + pathlog_first + ' | grep "_run.log"').read() if (os.path.exists(pathlog_first)) else ""

        #print("Length {0}".format(len(reading)))
        if (reading) and len(reading) > 0:
            log_file_name = reading.split()[0]
            definite_log_path = pathlog_first + '/' + log_file_name
            current_stat = os.stat(definite_log_path)
            timest = current_stat.st_mtime
            # system_stat = os.stat(BasicConfig.LOCAL_ROOT_DIR)
            timesys = time.time()
            timediff = int(timesys - timest)
            # print(timediff)
            if (timediff < time_condition):
                is_running = True
            else:
                is_running = False
            return (error, error_message, is_running, timediff, definite_log_path)

        # print(pathlog)
        reading = os.popen(
            'ls -t ' + pathlog_second + ' | grep "_run.log"').read() if (os.path.exists(pathlog_second)) else ""
        #print("Second reading {0}".format(reading))
        if (reading) and len(reading) > 0:
            log_file_name = reading.split()[0]
            definite_log_path = pathlog_second + '/' + log_file_name
            current_stat = os.stat(definite_log_path)
            timest = current_stat.st_mtime
            # system_stat = os.stat(BasicConfig.LOCAL_ROOT_DIR),
            timesys = time.time()
            timediff = int(timesys - timest)
            if (timediff < time_condition):
                is_running = True
            else:
                is_running = False
            return (error, error_message, is_running, timediff, definite_log_path)
        # If nothing is found
        return (error, error_message, is_running, timediff, definite_log_path)

    except Exception as ex:
        error = True
        is_running = False
        timediff = time_condition
        error_message = str(ex)
        # print(traceback.format_exc())
        # print("Error in test: " + error_message)
        return (error, error_message, is_running, timediff, definite_log_path)


def get_experiment_summary(expid):
    """
    Gets job summary for the experiment. Consider seconds.
    :param expid: Name of experiment
    :rtype expid: str
    :return: Object
    """
    BasicConfig.read()

    running = suspended = queuing = failed = submitted = total_q_time = total_r_time = 0
    q_count = r_count = 0
    # avg_q_time = avg_r_time = sim_avg_q_time = sim_avg_r_time =
    avg_q_time = avg_r_time = sim_avg_q_time = sim_avg_r_time = 0
    str_avg_q_time = str_avg_r_time = str_sim_avg_q_time = str_sim_avg_r_time = "NA"
    sim_q_count = sim_r_count = sim_total_q_time = sim_total_r_time = sim_count = 0
    # type_avg_q_time = type_avg_r_time = type_sim_avg_q_time = type_sim_avg_r_time = "min"
    failed_list = list()
    error = False
    error_message = ""
    try:
        # Basic paths
        BasicConfig.read()
        path = BasicConfig.LOCAL_ROOT_DIR + '/' + expid + '/pkl'
        tmp_path = os.path.join(
            BasicConfig.LOCAL_ROOT_DIR, expid, BasicConfig.LOCAL_TMP_DIR)
        pkl_filename = "job_list_" + str(expid) + ".pkl"
        path_pkl = path + "/" + pkl_filename
        # Try to get packages
        job_to_package = dict()
        package_to_jobs = dict()
        package_to_package_id = dict()
        package_to_symbol = dict()
        job_to_package, package_to_jobs, package_to_package_id, package_to_symbol = JobList.retrieve_packages(
            BasicConfig, expid)
        # Basic data
        job_running_to_seconds = dict()
        job_running_to_runtext = dict()
        jobs_in_pkl = dict()
        fakeAllJobs = list()

        if os.path.exists(path_pkl):
            fd = open(path_pkl, 'r')
            for item in pickle.load(fd):
                status_code = int(item[2])
                job_name = item[0]
                priority = item[3]
                id_number = item[1]
                out = str(item[8]) if len(item) >= 9 else ""
                err = str(item[9]) if len(item) >= 10 else ""
                status_color = Monitor.color_status(status_code)
                status_text = str(Status.VALUE_TO_KEY[status_code])
                jobs_in_pkl[job_name] = (
                    status_code, status_color, status_text, out, err, priority, id_number)
                fakeAllJobs.append(
                    SimpleJob(job_name, tmp_path, status_code))
            job_running_to_seconds, job_running_to_runtext, _ = JobList.get_job_times_collection(
                BasicConfig, fakeAllJobs, expid, job_to_package, package_to_jobs, timeseconds=True)

        # Getting job times data
        # path_local_root = BasicConfig.LOCAL_ROOT_DIR
        # db_file = os.path.join(path_local_root, "ecearth.db")
        # conn = DbRequests.create_connection(db_file)
        # job_times = DbRequests.get_times_detail_by_expid(conn, expid)
        # if not (job_times):
        #     raise Exception("Couldn't complete request.")
        # Main Loop
        if len(job_running_to_seconds.keys()) > 0:
            for job_name in jobs_in_pkl.keys():
                # print(value)
                job_info = job_running_to_seconds[job_name] if job_name in job_running_to_seconds.keys(
                ) else None
                queue_seconds = job_info.queue_time if job_info else 0
                running_seconds = job_info.run_time if job_info else 0
                status = job_info.status if job_info else "UNKNOWN"
                energy = job_info.energy if job_info else 0
                # Identifying SIM
                name_components = job_name.split('_')
                if "SIM" in name_components:
                    # print(name_components)
                    sim_count += 1
                    if status in ["QUEUING"]:
                        sim_q_count += 1
                        sim_total_q_time += queue_seconds
                        # print(sim_total_q_time)
                    elif status in ["COMPLETED", "RUNNING", "FAILED"]:
                        sim_q_count += 1
                        sim_r_count += 1
                        sim_total_q_time += queue_seconds
                        sim_total_r_time += running_seconds

                # print(str(key) + " ~ " + str(status))
                if status == "FAILED":
                    failed += 1
                    q_count += 1
                    r_count += 1
                    total_q_time += queue_seconds
                    total_r_time += running_seconds
                    failed_list.append(job_name)
                elif status == "SUBMITTED":
                    submitted += 1
                    q_count += 1
                    total_q_time += queue_seconds
                elif status == "QUEUING":
                    queuing += 1
                    q_count += 1
                    total_q_time += queue_seconds
                elif status == "SUSPENDED":
                    suspended += 1
                elif status == "RUNNING":
                    running += 1
                    q_count += 1
                    r_count += 1
                    total_q_time += queue_seconds
                    total_r_time += running_seconds
                elif status == "COMPLETED":
                    q_count += 1
                    r_count += 1
                    total_q_time += queue_seconds
                    total_r_time += running_seconds
        # All jobs: Average queuing time
        avg_q_time = int(total_q_time / q_count) if q_count > 0 else 0
        str_avg_q_time = str(datetime.timedelta(seconds=avg_q_time))

        # All jobs: Average running time
        avg_r_time = int(total_r_time / r_count) if r_count > 0 else 0
        str_avg_r_time = str(datetime.timedelta(seconds=avg_r_time))

        # Sim jobs: Average queuing time
        sim_avg_q_time = int(sim_total_q_time /
                             sim_q_count) if sim_q_count > 0 else 0
        str_sim_avg_q_time = str(datetime.timedelta(seconds=sim_avg_q_time))

        # Sim jobs: Average running time
        sim_avg_r_time = int(sim_total_r_time /
                             sim_r_count) if sim_r_count > 0 else 0
        str_sim_avg_r_time = str(datetime.timedelta(seconds=sim_avg_r_time))
    except Exception as exp:
        error = True
        error_message = str(exp)

    return {
        'n_running': running,
        'n_suspended': suspended,
        'n_queuing': queuing,
        'n_failed': failed,
        'n_submitted': submitted,
        'avg_queue_time': str_avg_q_time,
        'avg_run_time': str_avg_r_time,
        'n_sim': sim_count,
        'avg_sim_queue_time': str_sim_avg_q_time,
        'avg_sim_run_time': str_sim_avg_r_time,
        'sim_queue_considered': sim_q_count,
        'sim_run_considered': sim_r_count,
        'failed_jobs': failed_list,
        'error': error,
        'error_message': error_message
    }


def quick_test_run(expid):
    """
    Quick test run that queries the database
    :param expid: Experiment name
    :type expid: str
    :return: running status
    :rtype: JSON object
    """
    running = True
    error = False
    error_message = ""

    try:
        name, status = DbRequests.get_specific_experiment_status(expid)
        # print(status)
        if status != "RUNNING":
            running = False
    except Exception as exp:
        error = True
        error_message = str(exp)
        print(traceback.format_exc())
        # print(error_message)

    return {
        'running': running,
        'error': error,
        'error_message': error_message
    }


def test_run(expid):
    """
    Tests if experiment is running.\n
    :param expid: Experiment name
    :type expid: str
    :return: running status
    :rtype: JSON object
    """
    running = False
    error = False
    error_message = ""
    timediff = 0

    try:
        error, error_message, running, timediff, _ = _is_exp_running(
            expid, time_condition=120)
    except Exception as ex:
        error = True
        error_message = str(ex)

    return {'running': running,
            'error': error,
            'error_message': error_message}


def get_experiment_run(expid):
    """
    Gets last 150 lines of the log content
    """
    # Initializing results:
    log_file_name = ""
    found = False
    log_file_lastmodified = ""
    timest = ""
    error = False
    error_message = ""
    logcontent = []
    reading = ""

    try:
        BasicConfig.read()
        path = BasicConfig.LOCAL_ROOT_DIR + '/' + expid + '/' + \
            BasicConfig.LOCAL_TMP_DIR + '/' + BasicConfig.LOCAL_ASLOG_DIR
        # print(path)
        reading = os.popen(
            'ls -t ' + path + ' | grep "run.log"').read() if (os.path.exists(path)) else ""

        # Finding log files
        if len(reading) == 0:
            path = BasicConfig.LOCAL_ROOT_DIR + '/' + \
                expid + '/' + BasicConfig.LOCAL_TMP_DIR
            reading = os.popen(
                'ls -t ' + path + ' | grep "run.log"').read() if (os.path.exists(path)) else ""

        if len(reading) > 0:
            # run_logs.sort(reverse = True)
            log_file_name = reading.split()[0]
            print(log_file_name)
            current_stat = os.stat(path + '/' + log_file_name)
            timest = current_stat.st_mtime
            log_file_lastmodified = datetime.datetime.utcfromtimestamp(
                timest).strftime('%Y-%m-%d %H:%M:%S')
            found = True
            # line = subprocess.check_output(['tail', '-50', path+'/'+log_file_name])
            request = 'tail -150 ' + path + '/' + log_file_name
            print(request)
            last50 = os.popen(request)

            i = 0
            for item in last50.readlines():
                logcontent.append({'index': i, 'content': item[0:-1]})
                i += 1
    except Exception as e:
        error = True
        error_message = str(e)

    return {
        'logfile': log_file_name,
        'found': found,
        'lastModified': log_file_lastmodified,
        'timeStamp': timest,
        'error': error,
        'error_message': error_message,
        'logcontent': logcontent}


def get_job_log(expid, logfile, nlines=150):
    """
    Returns the last 150 lines of the log file. Targets out or err.
    :param logfilepath: path to the log file 
    :type logfilepath: str
    :return: List of string 
    :rtype: list
    """
    # Initializing results:
    # log_file_name = ""
    found = False
    log_file_lastmodified = ""
    timest = ""
    error = False
    error_message = ""
    logcontent = []
    reading = ""
    BasicConfig.read()
    logfilepath = os.path.join(BasicConfig.LOCAL_ROOT_DIR, expid,
                               BasicConfig.LOCAL_TMP_DIR, "LOG_{0}".format(expid), logfile)
    try:
        if os.path.exists(logfilepath):
            current_stat = os.stat(logfilepath)
            timest = int(current_stat.st_mtime)
            log_file_lastmodified = datetime.datetime.utcfromtimestamp(
                timest).strftime('%Y-%m-%d %H:%M:%S')
            found = True
            request = "tail -{0} {1}".format(nlines, logfilepath)
            # print(request)
            last50 = os.popen(request)
            # print(type(last50))
            i = 0
            for item in last50.readlines():
                logcontent.append({'index': i, 'content': item[0:-1]})
                i += 1
    except Exception as e:
        error = True
        error_message = str(e)

    return {
        'logfile': logfilepath,
        'found': found,
        'lastModified': log_file_lastmodified,
        'timeStamp': timest,
        'error': error,
        'error_message': error_message,
        'logcontent': logcontent}


def get_experiment_pkl(expid, modTimestamp):
    """
    Gets the current state of the pkl in a format proper for graph update
    """
    pkl_file_name = ""
    error = False
    error_message = ""
    has_changed = False
    pkl_content = list()
    timest = 1000000
    try:
        BasicConfig.read()
        # Chunk info
        as_conf = AutosubmitConfig(
            expid, BasicConfig, ConfigParserFactory())
        as_conf.reload()
        chunk_unit = as_conf.get_chunk_size_unit()
        chunk_size = as_conf.get_chunk_size()
        path = BasicConfig.LOCAL_ROOT_DIR + '/' + expid + '/pkl'
        reading = os.popen(
            'ls -t ' + path + ' | grep ".pkl"').read() if (os.path.exists(path)) else ""
        # pkl_contents = os.listdir(path) if (os.path.exists(path)) else list()
        # pkl_files = list(filter(lambda x: x.endswith(expid + '.pkl'), pkl_contents))
        tmp_path = os.path.join(
            BasicConfig.LOCAL_ROOT_DIR, expid, BasicConfig.LOCAL_TMP_DIR)
        path_to_logs = os.path.join(
            BasicConfig.LOCAL_ROOT_DIR, expid, "tmp", "LOG_" + expid)
        if len(reading) > 0:
            pkl_file_name = reading.split()[0]
            current_stat = os.stat(path + '/' + pkl_file_name)
            timest = int(current_stat.st_mtime)
            # print(timest)
            if timest - int(modTimestamp) > 0:
                has_changed = True
        else:
            raise Exception('Empty pkl directory.')

        if has_changed == True:
            # Completed Times
            path_local_root = BasicConfig.LOCAL_ROOT_DIR
            #path_structure = BasicConfig.STRUCTURES_DIR
            db_file = os.path.join(path_local_root, "ecearth.db")
            #conn = DbRequests.create_connection(db_file)
            #job_times = DbRequests.get_times_detail_by_expid(conn, expid)
            # End Completed Times
            # Results
            job_running_to_min = dict()
            job_running_to_runtext = dict()
            # End Results
            # Dealing with packages
            job_to_package = dict()
            package_to_jobs = dict()
            package_to_package_id = dict()
            package_to_symbol = dict()
            #current_table_structure = dict()
            job_to_package, package_to_jobs, package_to_package_id, package_to_symbol = JobList.retrieve_packages(
                BasicConfig, expid)
            # Structure if packages
            # if (job_to_package):
            #     current_table_structure = DbStructure.get_structure(
            #         expid, path_structure)
            # End of packages
            jobs_in_pkl = dict()
            fakeAllJobs = list()
            path_pkl = os.path.join(path, pkl_file_name)
            # print(path_pkl)

            if os.path.exists(path_pkl):
                fd = open(path_pkl, 'r')
                for item in pickle.load(fd):
                    status_code = int(item[2])
                    job_name = item[0]
                    priority = item[3]
                    id_number = item[1]
                    chunk = item[7]
                    out = str(item[8]) if len(item) >= 9 else ""
                    err = str(item[9]) if len(item) >= 10 else ""
                    status_color = Monitor.color_status(status_code)
                    status_text = str(Status.VALUE_TO_KEY[status_code])
                    jobs_in_pkl[job_name] = (
                        status_code, status_color, status_text, out, err, priority, id_number, chunk)
                    fakeAllJobs.append(
                        SimpleJob(job_name, tmp_path, status_code))
                job_running_to_min, job_running_to_runtext, _ = JobList.get_job_times_collection(
                    BasicConfig, fakeAllJobs, expid, job_to_package, package_to_jobs)

            if len(jobs_in_pkl.keys()) > 0:
                # Loop through jobs in pkl
                for job_name in jobs_in_pkl.keys():
                    status_code, status_color, status_text, out, err, priority, id_number, job_chunk = jobs_in_pkl[
                        job_name]

                    # time_queue, time_run, status_retrieved, energy = job_running_to_min[job_name] if job_name in job_running_to_min.keys(
                    # ) else (0, 0, status_text, 0)

                    job_info = job_running_to_min[job_name] if job_name in job_running_to_min.keys(
                    ) else None
                    # time_queue = job_info.queue_time if job_info else 0
                    # time_run = job_info.run_time if job_info else 0
                    # status_retrieved = job_info.status if job_info else status_text
                    # energy = job_info.energy if job_info else 0

                    running_text = job_running_to_runtext[job_name] if job_name in job_running_to_runtext.keys(
                    ) else ("")
                    pkl_content.append({'name': job_name,
                                        'rm_id': id_number,
                                        'status_code': status_code,
                                        'SYPD': calculate_SYPD_perjob(chunk_unit, chunk_size, job_chunk, job_info.run_time if job_info else 0),
                                        'minutes': job_info.run_time if job_info else 0,
                                        'minutes_queue': job_info.queue_time if job_info else 0,
                                        'submit': job_info.submit if job_info else None,
                                        'start': job_info.start if job_info else None,
                                        'finish': job_info.finish if job_info else None,
                                        'running_text': running_text,
                                        'dashed': True if job_name in job_to_package else False,
                                        'shape': package_to_symbol[job_to_package[job_name]] if job_name in job_to_package else 'dot',
                                        'package': job_to_package.get(job_name, None) if job_to_package else None,
                                        'status': status_text,
                                        'status_color': status_color,
                                        'out': path_to_logs + "/" + out,
                                        'err': path_to_logs + "/" + err,
                                        'priority': priority})
            else:
                raise Exception('File {0} does not exist'.format(path))

    except Exception as e:
        error = True
        error_message = str(e)

    return {
        'pkl_file_name': pkl_file_name,
        'error': error,
        'error_message': error_message,
        'has_changed': has_changed,
        'pkl_content': pkl_content,
        'pkl_timestamp': timest,
        'packages': package_to_jobs if has_changed == True else {},
    }


def get_experiment_tree_pkl(expid, modTimestamp):
    """
    Gets the current state of the pkl in a format for tree update
    """
    pkl_file_name = ""
    error = False
    error_message = ""
    # has_changed = False
    # For Refresh purposes, it always changes
    has_changed = True
    pkl_content = list()
    package_to_jobs = {}
    timest = 1000000
    source = JobList.get_sourcetag()
    target = JobList.get_targettag()
    sync = JobList.get_synctag()
    check_mark = JobList.get_checkmark()
    try:
        BasicConfig.read()
        # Chunk info
        as_conf = AutosubmitConfig(
            expid, BasicConfig, ConfigParserFactory())
        as_conf.reload()
        chunk_unit = as_conf.get_chunk_size_unit()
        chunk_size = as_conf.get_chunk_size()
        # years_per_sim = datechunk_to_year(chunk_unit, chunk_size)
        path = BasicConfig.LOCAL_ROOT_DIR + '/' + expid + '/pkl'
        path_to_logs = os.path.join(
            BasicConfig.LOCAL_ROOT_DIR, expid, "tmp", "LOG_" + expid)
        tmp_path = os.path.join(
            BasicConfig.LOCAL_ROOT_DIR, expid, BasicConfig.LOCAL_TMP_DIR)
        reading = os.popen(
            'ls -t ' + path + ' | grep ".pkl"').read() if (os.path.exists(path)) else ""
        # path_structure = BasicConfig.STRUCTURES_DIR
        # pkl_contents = os.listdir(path) if (os.path.exists(path)) else list()
        # pkl_files = list(filter(lambda x: x.endswith(expid + '.pkl'), pkl_contents))
        # Checking pkl
        if len(reading) > 0:
            pkl_file_name = reading.split()[0]
            current_stat = os.stat(path + '/' + pkl_file_name)
            timest = int(current_stat.st_mtime)
            # print(timest)
            if timest - int(modTimestamp) > 0:
                has_changed = True
        else:
            raise Exception('Empty pkl directory.')

        if has_changed == True:
            # Completed Times
            path_local_root = BasicConfig.LOCAL_ROOT_DIR
            db_file = os.path.join(path_local_root, "ecearth.db")
            # conn = DbRequests.create_connection(db_file)
            # job_times = DbRequests.get_times_detail_by_expid(conn, expid)
            # End Completed Times
            # Results
            job_running_to_min = dict()
            job_running_to_runtext = dict()
            # End Results
            # Try to get packages
            job_to_package = dict()
            package_to_jobs = dict()
            package_to_package_id = dict()
            package_to_symbol = dict()
            #current_table_structure = dict()
            job_to_package, package_to_jobs, package_to_package_id, package_to_symbol = JobList.retrieve_packages(
                BasicConfig, expid)
            # if (job_to_package):
            #     current_table_structure = DbStructure.get_structure(
            #         expid, path_structure)
            path_pkl = os.path.join(path, pkl_file_name)
            # print(path_pkl)
            jobs_in_pkl = dict()
            fakeAllJobs = list()
            if os.path.exists(path_pkl):
                fd = open(path_pkl, 'r')
                for item in pickle.load(fd):
                    status_code = int(item[2])
                    job_name = item[0]
                    priority = item[3]
                    id_number = item[1]
                    chunk = item[7]
                    out = str(item[8]) if len(item) >= 9 else ""
                    err = str(item[9]) if len(item) >= 10 else ""
                    status_color = Monitor.color_status(status_code)
                    status_text = str(Status.VALUE_TO_KEY[status_code])
                    jobs_in_pkl[job_name] = (
                        status_code, status_color, status_text, out, err, priority, id_number, chunk)
                    fakeAllJobs.append(
                        SimpleJob(job_name, tmp_path, status_code))
                job_running_to_min, job_running_to_runtext, _ = JobList.get_job_times_collection(
                    BasicConfig, fakeAllJobs, expid, job_to_package, package_to_jobs)

            if len(jobs_in_pkl.keys()) > 0:
                # fd = open(path_pkl, 'r')
                for job_name in jobs_in_pkl.keys():
                    status_code, status_color, status_text, out, err, priority, id_number, job_chunk = jobs_in_pkl[
                        job_name]
                    wrapper_tag = ""
                    wrapper_id = 0
                    wrapper_name = None
                    if job_name in job_to_package:
                        wrapper_name = job_to_package[job_name]
                        wrapper_id = package_to_package_id[job_to_package[job_name]]
                        wrapper_tag = " <span class='badge' style='background-color:#94b8b8'>Wrapped " + \
                            wrapper_id + "</span>"
                        # for job_wrapped in package_to_jobs[wrapper_name]:

                    # time_queue, time_run, status_retrieved, energy = job_running_to_min[job_name] if job_name in job_running_to_min.keys(
                    # ) else (0, 0, status_text, 0)

                    job_info = job_running_to_min[job_name] if job_name in job_running_to_min.keys(
                    ) else None
                    # time_queue = job_info.queue_time if job_info else 0
                    # time_run = job_info.run_time if job_info else 0
                    # status_retrieved = job_info.status if job_info else status_text
                    # energy = job_info.energy if job_info else 0

                    running_text = job_running_to_runtext[job_name] if job_name in job_running_to_runtext.keys(
                    ) else ("")
                    pkl_content.append({'name': job_name,
                                        'rm_id': id_number,
                                        'status_code': status_code,
                                        'SYPD': calculate_SYPD_perjob(chunk_unit, chunk_size, job_chunk, job_info.run_time if job_info else 0),
                                        'minutes': job_info.run_time if job_info else 0,
                                        'minutes_queue': job_info.queue_time if job_info else 0,
                                        'submit': job_info.submit if job_info else None,
                                        'start': job_info.start if job_info else None,
                                        'finish': job_info.finish if job_info else None,
                                        'running_text': running_text,
                                        'status': status_text,
                                        'status_color': status_color,
                                        'wrapper': wrapper_name,
                                        'wrapper_tag': wrapper_tag,
                                        'wrapper_id': wrapper_id,
                                        'out': path_to_logs + "/" + out,
                                        'err': path_to_logs + "/" + err,
                                        'title': Job.getTitle(job_name, status_color, status_text) + ((" ~ " + running_text) if status_code not in [Status.WAITING, Status.WAITING] else ""),
                                        'priority': priority})
            else:
                raise Exception('File {0} does not exist'.format(path))

    except Exception as e:
        error = True
        error_message = str(e)

    return {
        'pkl_file_name': pkl_file_name,
        'error': error,
        'error_message': error_message,
        'has_changed': has_changed,
        'pkl_content': pkl_content,
        'packages': list(package_to_jobs.keys()),
        'pkl_timestamp': timest,
        'source_tag': source,
        'target_tag': target,
        'sync_tag': sync,
        'check_mark': check_mark,
    }


def get_experiment_metrics(expid):
    """
    Gets metrics
    """
    error = False
    error_message = ""
    SYPD = ASYPD = CHSY = JPSY = RSYPD = Parallelization = 0
    seconds_in_a_day = 86400
    list_considered = []
    core_hours_year = []
    warnings_job_data = []
    total_run_time = total_queue_time = total_CHSY = total_JPSY = energy_count = 0

    try:
        # Basic info
        BasicConfig.read()
        path = BasicConfig.LOCAL_ROOT_DIR + '/' + expid + '/pkl'
        tmp_path = os.path.join(
            BasicConfig.LOCAL_ROOT_DIR, expid, BasicConfig.LOCAL_TMP_DIR)
        pkl_filename = "job_list_" + str(expid) + ".pkl"
        path_pkl = path + "/" + pkl_filename

        as_conf = AutosubmitConfig(
            expid, BasicConfig, ConfigParserFactory())
        if not as_conf.check_conf_files():
            # Log.critical('Can not run with invalid configuration')
            raise Exception(
                'Autosubmit GUI might not have permission to access necessary configuration files.')

        # Chunk Information
        chunk_unit = as_conf.get_chunk_size_unit()
        chunk_size = as_conf.get_chunk_size()
        year_per_sim = datechunk_to_year(chunk_unit, chunk_size)
        if year_per_sim <= 0:
            raise Exception("The system couldn't calculate year per SIM value " + str(year_per_sim) +
                            ", for chunk size " + str(chunk_size) + " and chunk unit " + str(chunk_unit))

        # From database
        db_file = os.path.join(BasicConfig.LOCAL_ROOT_DIR, "ecearth.db")
        conn = DbRequests.create_connection(db_file)
        job_times = DbRequests.get_times_detail_by_expid(conn, expid)

        # Job time information
        # Try to get packages
        job_to_package = {}
        package_to_jobs = {}
        job_to_package, package_to_jobs, _, _ = JobList.retrieve_packages(
            BasicConfig, expid)
        # Basic data
        job_running_to_seconds = {}
        # SIM POST TRANSFER jobs (COMPLETED) in experiment
        sim_jobs_in_pkl = []
        post_jobs_in_pkl = []
        transfer_jobs_in_pkl = []
        clean_jobs_in_pkl = []
        sim_jobs_info = []
        post_jobs_info = []
        transfer_jobs_info = []
        clean_jobs_info = []
        sim_jobs_info_asypd = []
        sim_jobs_info_rsypd = []
        outlied = []
        # Get pkl information
        if os.path.exists(path_pkl):
            fd = open(path_pkl, 'r')
            pickle_content = pickle.load(fd)
            # pickle 0: Name, 2: StatusCode
            sim_jobs_in_pkl = [item[0]
                               for item in pickle_content if 'SIM' in item[0].split('_') and int(item[2]) == Status.COMPLETED]
            post_jobs_in_pkl = [item[0]
                                for item in pickle_content if 'POST' in item[0].split('_') and int(item[2]) == Status.COMPLETED]
            transfer_member = [item[0]
                               for item in pickle_content if item[0].find('TRANSFER_MEMBER') > 0 and int(item[2]) == Status.COMPLETED]
            transfer_jobs_in_pkl = [item[0]
                                    for item in pickle_content if 'TRANSFER' in item[0].split('_') and int(item[2]) == Status.COMPLETED and item[0] not in transfer_member]
            clean_member = [item[0]
                            for item in pickle_content if item[0].find('CLEAN_MEMBER') > 0 and int(item[2]) == Status.COMPLETED]
            clean_jobs_in_pkl = [item[0]
                                 for item in pickle_content if 'CLEAN' in item[0].split('_') and int(item[2]) == Status.COMPLETED and item[0] not in clean_member]

            # print(transfer_jobs_in_pkl)
            fakeAllJobs = [SimpleJob(item[0], tmp_path, int(item[2]))
                           for item in pickle_content]
            del pickle_content
            job_running_to_seconds, _, warnings_job_data = JobList.get_job_times_collection(
                BasicConfig, fakeAllJobs, expid, job_to_package, package_to_jobs, timeseconds=True)
            # ASYPD - RSYPD warnings
            if len(post_jobs_in_pkl) == 0:
                warnings_job_data.append(
                    "ASYPD | There are no (COMPLETED) POST jobs in the experiment, ASYPD cannot be computed.")
            if len(transfer_jobs_in_pkl) == 0 and len(clean_jobs_in_pkl) == 0:
                warnings_job_data.append(
                    "RSYPD | There are no TRANSFER nor CLEAN (COMPLETED) jobs in the experiment, RSYPD cannot be computed.")
            if len(transfer_jobs_in_pkl) == 0 and len(clean_jobs_in_pkl) > 0:
                warnings_job_data.append(
                    "RSYPD | There are no TRANSFER (COMPLETED) jobs in the experiment, we resort to use (COMPLETED) CLEAN jobs to compute RSYPD.")

        Parallelization = 0
        try:
            processors_value = as_conf.get_processors("SIM")
            if processors_value.find(":") >= 0:
                # It is an expression
                components = processors_value.split(":")
                Parallelization = int(sum(
                    [math.ceil(float(x) / 36.0) * 36.0 for x in components]))
                warnings_job_data.append("Parallelization parsing | {0} was interpreted as {1} cores.".format(
                    processors_value, Parallelization))
            else:
                # It is int
                Parallelization = int(processors_value)
        except Exception as exp:
            # print(exp)
            warnings_job_data.append(
                "CHSY Critical | Autosubmit API could not parse the number of processors for the SIM job.")
            pass

        # ASYPD
        # Main Loop
        # Times exist
        if len(job_running_to_seconds) > 0:
            # job_info attributes: ['name', 'queue_time', 'run_time', 'status', 'energy', 'submit', 'start', 'finish', 'ncpus']
            sim_jobs_info = [job_running_to_seconds[job_name]
                             for job_name in sim_jobs_in_pkl if job_running_to_seconds.get(job_name, None) is not None]
            sim_jobs_info.sort(key=lambda x: tostamp(x.finish), reverse=True)

            # SIM outlier detection
            data_run_times = [job.run_time for job in sim_jobs_info]
            mean_1 = np.mean(data_run_times) if len(data_run_times) > 0 else 0
            std_1 = np.std(data_run_times) if len(data_run_times) > 0 else 0
            threshold = 2

            # ASYPD Pre
            post_jobs_info = [job_running_to_seconds[job_name]
                              for job_name in post_jobs_in_pkl if job_running_to_seconds.get(job_name, None) is not None and job_running_to_seconds[job_name].finish is not None]
            post_jobs_info.sort(key=lambda x: tostamp(x.finish), reverse=True)
            # End ASYPD Pre
            for job_info in sim_jobs_info:
                # JobRow object
                z_score = (job_info.run_time - mean_1) / \
                    std_1 if std_1 > 0 else 0
                # print("{} : {}".format(job_info.name, z_score, threshold))
                if np.abs(z_score) <= threshold and job_info.run_time > 0:
                    status = job_info.status if job_info else "UNKNOWN"
                    # Energy
                    energy = round(job_info.energy, 2) if job_info else 0
                    if energy == 0:
                        warnings_job_data.append(
                            "Considered | Job {0} (Package {1}) has no energy information and is not going to be considered for energy calculations.".format(job_info.name, job_to_package.get(job_info.name, "")))
                    total_queue_time += int(job_info.queue_time)
                    total_run_time += int(job_info.run_time)
                    seconds_per_year = (Parallelization *
                                        job_info.run_time) / year_per_sim
                    job_JPSY = round(energy / year_per_sim,
                                     2) if year_per_sim > 0 else 0
                    job_SYPD = round((year_per_sim * seconds_in_a_day) /
                                     int(job_info.run_time), 2) if job_info.run_time > 0 else 0
                    job_ASYPD = round((year_per_sim * seconds_in_a_day) / (int(job_info.queue_time) + int(job_info.run_time) + sum(
                        job.queue_time + job.run_time for job in post_jobs_info) / len(post_jobs_info)) if len(post_jobs_info) > 0 else 0, 2)

                    # Maximum finish time
                    # max_sim_finish = tostamp(job_info.finish) if job_info.finish is not None and tostamp(
                    #     job_info.finish) > max_sim_finish else max_sim_finish
                    #     sim_count += 1
                    total_CHSY += round(seconds_per_year / 3600, 2)
                    total_JPSY += job_JPSY
                    if job_JPSY > 0:
                        energy_count += 1
                    # core_hours_year.append(year_seconds/3600)
                    list_considered.append(
                        {"name": job_info.name,
                            "queue": int(job_info.queue_time),
                            "running": int(job_info.run_time),
                            "CHSY": round(seconds_per_year / 3600, 2),
                            "SYPD": job_SYPD,
                            "ASYPD": job_ASYPD,
                            "JPSY": job_JPSY,
                            "energy": energy})
                else:
                    # print("Outlied {}".format(job_info.name))
                    outlied.append(job_info.name)
                    warnings_job_data.append(
                        "Outlier | Job {0} (Package {1} - Running time {2} seconds) has been considered an outlier (mean {3}, std {4}, z_score {5}) and will be ignored for performance calculations.".format(job_info.name, job_to_package.get(job_info.name, ""), str(job_info.run_time), str(round(mean_1, 2)), str(round(std_1, 2)), str(round(z_score, 2))))

            # ASYPD Pre
            sim_jobs_info_asypd = [job for job in sim_jobs_info if job.name not in outlied] if len(
                post_jobs_info) > 0 else []
            sim_jobs_info_asypd.sort(
                key=lambda x: tostamp(x.finish), reverse=True)

            # RSYPD
            transfer_jobs_info = [job_running_to_seconds[job_name]
                                  for job_name in transfer_jobs_in_pkl if job_running_to_seconds.get(job_name, None) is not None and job_running_to_seconds[job_name].finish is not None]
            transfer_jobs_info.sort(
                key=lambda x: tostamp(x.finish), reverse=True)
            if len(transfer_jobs_info) <= 0:
                clean_jobs_info = [job_running_to_seconds[job_name]
                                   for job_name in clean_jobs_in_pkl if job_running_to_seconds.get(job_name, None) is not None and job_running_to_seconds[job_name].finish is not None]
                clean_jobs_info.sort(
                    key=lambda x: tostamp(x.finish), reverse=True)
                sim_jobs_info_rsypd = [job for job in sim_jobs_info if job.name not in outlied and tostamp(job.finish) <= tostamp(
                    clean_jobs_info[0].finish)] if len(clean_jobs_info) > 0 else []
            else:
                sim_jobs_info_rsypd = [job for job in sim_jobs_info if job.name not in outlied and tostamp(job.finish) <= tostamp(
                    transfer_jobs_info[0].finish)]
            sim_jobs_info_rsypd.sort(
                key=lambda x: tostamp(x.finish), reverse=True)
            # print("SIM")
            # print(sim_jobs_info_rsypd[0].submit)
            # print(sim_jobs_info_rsypd[-1].finish)
            # print("POST")
            # print(transfer_jobs_info[0].submit)
            # print(transfer_jobs_info[-1].finish)

            # for job in transfer_jobs_info:
            #     print(job.name)

        SYPD = ((year_per_sim * len(list_considered) * seconds_in_a_day) /
                (total_run_time)) if total_run_time > 0 else 0
        # (
        # year_per_sim * sim_count * seconds_in_a_day)
        SYPD = round(SYPD, 2)
        #  Old
        # ASYPD = ((year_per_sim * len(list_considered) * seconds_in_a_day) /
        #          (total_run_time + total_queue_time) if (total_run_time +
        #                                                  total_queue_time) > 0 else 0)
        # Paper Implementation
        # ASYPD = ((year_per_sim * len(list_considered) * seconds_in_a_day) / (max_sim_finish -
        #                                                                      min_submit)) if (max_sim_finish - min_submit) > 0 else 0
        # ASYPD New Implementation
        ASYPD = (year_per_sim * len(sim_jobs_info_asypd) * seconds_in_a_day) / (sum(job.queue_time + job.run_time for job in sim_jobs_info_asypd) +
                                                                                sum(job.queue_time + job.run_time for job in post_jobs_info) / len(post_jobs_info)) if len(sim_jobs_info_asypd) > 0 and len(post_jobs_info) > 0 else 0

        # RSYPD
        RSYPD = 0
        if len(transfer_jobs_info) > 0:
            RSYPD = (year_per_sim * len(sim_jobs_info_rsypd) * seconds_in_a_day) / (tostamp(transfer_jobs_info[0].finish) - tostamp(sim_jobs_info_rsypd[-1].start)) if len(
                sim_jobs_info_rsypd) > 0 and len(transfer_jobs_info) > 0 and (tostamp(transfer_jobs_info[0].finish) - tostamp(sim_jobs_info_rsypd[-1].start)) > 0 else 0
        else:
            RSYPD = (year_per_sim * len(sim_jobs_info_rsypd) * seconds_in_a_day) / (tostamp(clean_jobs_info[0].finish) - tostamp(sim_jobs_info_rsypd[-1].start)) if len(
                sim_jobs_info_rsypd) > 0 and len(clean_jobs_info) > 0 and (tostamp(clean_jobs_info[0].finish) - tostamp(sim_jobs_info_rsypd[-1].start)) > 0 else 0

        ASYPD = round(ASYPD, 4)
        RSYPD = round(RSYPD, 4)
        CHSY = round(total_CHSY / len(list_considered),
                     2) if len(list_considered) > 0 else total_CHSY
        JPSY = round(
            total_JPSY / energy_count) if energy_count > 0 else total_JPSY
    except Exception as ex:
        print(traceback.format_exc())
        error = True
        error_message = str(ex)
        pass

    return {"SYPD": SYPD,
            "ASYPD": ASYPD,
            "RSYPD": RSYPD,
            "CHSY": CHSY,
            "JPSY": JPSY,
            "Parallelization": Parallelization,
            "considered": list_considered,
            "error": error,
            "error_message": error_message,
            "warnings_job_data": warnings_job_data,
            }


def process_active_graphs():
    """
    Process the list of active experiments to generate the positioning of their graphs
    """
    try:
        # BasicConfig.read()

        currently_running = DbRequests.get_currently_running_experiments()
        # exp_ids = list(currently_running.keys()) if currently_running else []

        for expid in currently_running:
            try:
                experimentGraphDrawing = ExperimentGraphDrawing(expid)
                locked = experimentGraphDrawing.locked
                start_time = time.time()
                print("Start Processing {} with {} jobs".format(
                    expid, currently_running[expid]))
                if not locked:
                    as_conf = AutosubmitConfig(
                        expid, BasicConfig, ConfigParserFactory())
                    as_conf.reload()
                    # JobList construction
                    job_list = Autosubmit.load_job_list(
                        expid, as_conf, notransitive=False)
                    current_data = experimentGraphDrawing.get_validated_data(
                        job_list.get_job_list())
                    if not current_data:
                        print("Must update {}".format(expid))
                        experimentGraphDrawing.calculate_drawing(
                            job_list.get_job_list(), num_chunks=len(job_list._chunk_list))
                else:
                    print("Locked")
                print("Time Spent in {}: {} seconds.".format(expid,
                                                             int(time.time() - start_time)))
            except Exception as exp:
                print(traceback.format_exc())
                print("Error while processing: {}".format(expid))

    except Exception as exp:
        print(traceback.format_exc())
        print("Error while processing graph drawing: {}".format(exp))


def get_experiment_graph(expid, layout='standard', grouped='none'):
    """
    Gets graph representation
    """
    base_list = dict()
    pkl_timestamp = 10000000
    try:
        notransitive = False
        # print("Received " + str(expid) + " ~ " + layout + " ~ " + grouped)
        BasicConfig.read()
        exp_path = os.path.join(BasicConfig.LOCAL_ROOT_DIR, expid)
        tmp_path = os.path.join(exp_path, BasicConfig.LOCAL_TMP_DIR)
        as_conf = AutosubmitConfig(
            expid, BasicConfig, ConfigParserFactory())
        as_conf.reload()
        # Getting platform data
        # Main taget HPC
        hpcarch = as_conf.get_platform()
        # Submitter
        submitter = Autosubmit._get_submitter(as_conf)
        submitter.load_platforms(as_conf)
        # JobList construction
        job_list = Autosubmit.load_job_list(
            expid, as_conf, notransitive=notransitive)

        if job_list.graph == None:
            raise Exception(
                "Graph generation is not possible for this experiment.")

        # Platform update
        for job in job_list.get_job_list():
            if job.platform_name is None:
                job.platform_name = hpcarch
            job.platform = submitter.platforms[job.platform_name.lower(
            )]

        # Chunk unit and chunk size
        chunk_unit = as_conf.get_chunk_size_unit()
        chunk_size = as_conf.get_chunk_size()

        job_list.sort_by_id()
        base_list = job_list.get_graph_representation(
            BasicConfig, layout, grouped, chunk_unit=chunk_unit, chunk_size=chunk_size)
    except Exception as e:
        print(traceback.format_exc())
        return {'nodes': [],
                'edges': [],
                'fake_edges': [],
                'groups': [],
                'groups_data': {},
                'error': True,
                'error_message': str(e),
                'graphviz': False,
                'max_children': 0,
                'max_parents': 0,
                'total_jobs': 0,
                'pkl_timestamp': 0}

    base_list['error'] = False
    base_list['error_message'] = 'None'
    base_list['pkl_timestamp'] = pkl_timestamp
    return base_list


def get_experiment_tree_rundetail(expid, run_id):
    """
    """
    base_list = dict()
    pkl_timestamp = 10000000
    try:
        notransitive = False
        print("Received Tree RunDetail " + str(expid))
        BasicConfig.read()
        # exp_path = os.path.join(BasicConfig.LOCAL_ROOT_DIR, expid)
        # tmp_path = os.path.join(exp_path, BasicConfig.LOCAL_TMP_DIR)
        # as_conf = AutosubmitConfig(
        #     expid, BasicConfig, ConfigParserFactory())
        # if not as_conf.reload():
        #     # Log.critical('Can not run with invalid configuration')
        #     raise Exception(
        #         'Autosubmit GUI might not have permission to access necessary configuration files.')

        # job_list = Autosubmit.load_job_list(
        #     expid, as_conf, notransitive=notransitive)
        # print("Job List loaded")
        # job_list.sort_by_id()
        # base_list['tree'] = job_list.get_tree_representation().traverse_format()
        # chunk_unit = as_conf.get_chunk_size_unit()
        # chunk_size = as_conf.get_chunk_size()

        tree_structure, current_collection, reference = JobList.get_tree_structured_from_previous_run(expid,
                                                                                                      BasicConfig, run_id=run_id)
        base_list['tree'] = tree_structure
        base_list['jobs'] = current_collection
        base_list['total'] = len(current_collection)
        base_list['reference'] = reference
    except Exception as e:
        print(traceback.format_exc())
        return {'tree': [], 'jobs': [], 'total': 0, 'reference': [], 'error': True, 'error_message': str(e), 'pkl_timestamp': 0}
    base_list['error'] = False
    base_list['error_message'] = 'None'
    base_list['pkl_timestamp'] = pkl_timestamp
    return base_list


def get_experiment_tree_structured(expid):
    """
    Current version of the tree visualization algorithm.
    :param expid: Name of experiment
    :type expid: String
    :return: Dictionary [Variable Name] to Value
    :rtype: Dictionary Key: String, Value: Object
    """
    base_list = dict()
    pkl_timestamp = 10000000
    try:
        notransitive = False
        print("Received Tree Request " + str(expid))
        BasicConfig.read()
        exp_path = os.path.join(BasicConfig.LOCAL_ROOT_DIR, expid)
        tmp_path = os.path.join(exp_path, BasicConfig.LOCAL_TMP_DIR)
        as_conf = AutosubmitConfig(
            expid, BasicConfig, ConfigParserFactory())
        as_conf.reload()
        # Getting platform data
        # Main taget HPC
        hpcarch = as_conf.get_platform()
        # Submitter
        submitter = Autosubmit._get_submitter(as_conf)
        submitter.load_platforms(as_conf)
        # JobList construction
        job_list = Autosubmit.load_job_list(
            expid, as_conf, notransitive=notransitive)
        # Platform update
        for job in job_list.get_job_list():
            if job.platform_name is None:
                job.platform_name = hpcarch
            job.platform = submitter.platforms[job.platform_name.lower(
            )]
        # Chunk Unit and Size
        chunk_unit = as_conf.get_chunk_size_unit()
        chunk_size = as_conf.get_chunk_size()

        tree_structure, current_collection, reference = job_list.get_tree_structured(
            BasicConfig, chunk_unit=chunk_unit, chunk_size=chunk_size)

        base_list['tree'] = tree_structure
        base_list['jobs'] = current_collection
        base_list['total'] = len(current_collection)
        base_list['reference'] = reference
    except Exception as e:
        print(traceback.format_exc())
        return {'tree': [], 'jobs': [], 'total': 0, 'reference': [], 'error': True, 'error_message': str(e), 'pkl_timestamp': 0}
    base_list['error'] = False
    base_list['error_message'] = 'None'
    base_list['pkl_timestamp'] = pkl_timestamp
    return base_list


def retrieve_all_pkl_files():
    """
    Retrieves a list of all pkl files in /esarchive/autosubmit/*/pkl/ with timestamps for comparison purposes
    :return: Dictionary Key: expid, Value: 2-tuple (timestamp, path_to_pkl)
    """
    all_pkl = os.popen(
        "find /esarchive/autosubmit/*/pkl/ -name \"*.pkl\"  -printf \"%p %Ts\n\"").read()
    all_pkl = all_pkl.split("\n")
    # print(all_pkl)
    exp_to_pkl = dict()
    #exp_to_modified = dict()
    for item in all_pkl:
        try:
            honk = item.split()
            timestamp = int(honk[1])
            file_name = str(honk[0]).split("/")
            exp_to_pkl[str(file_name[3])] = (timestamp, str(honk[0]))
            print(file_name[3] + " ~ " +
                  str(timestamp) + " :: " + str(honk[0]))
        except Exception as exp:
            pass
    return exp_to_pkl


def process_completed_times(time_condition=60):
    """
    Tests for completed jobs of all autosubmit experiments and updates their completion times data in job_times and experiment_times.
    :param time_condition: Time difference in seconds that qualifies a experiment as out of date.
    :type time_condition: Integer
    """
    try:
        t0 = time.time()
        DEBUG = False
        BasicConfig.read()
        path = BasicConfig.LOCAL_ROOT_DIR
        # Time test for data retrieval
        start_time_data = time.time()
        # All experiment from file system
        currentDirectories = subprocess.Popen(['ls', '-t', path],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT) if (os.path.exists(path)) else None
        stdOut, stdErr = currentDirectories.communicate(
        ) if currentDirectories else (None, None)
        # Building connection to ecearth
        db_file = os.path.join(path, "ecearth.db")
        conn = DbRequests.create_connection(db_file)
        current_table = DbRequests.prepare_completed_times_db()
        # Build list of all folder in /esarchive/autosubmit which should be considered as experiments (although some might not be)
        # Pre process
        _preprocess_completed_times()
        # raise Exception("Test finished")
        # Pre process completed
        experiments = stdOut.split() if stdOut else []
        # total_process = len(experiments)
        counter = 0
        # Retrieving all pkl timestamps
        # return None
        t_data = time.time() - start_time_data

        # Get current `details` from ecearth.db  and convert to set for effcient contain test
        details_table_ids_set = set(
            DbRequests.get_exps_detailed_complete(conn).keys())
        # Get current `experiments` from ecearth.db
        experiments_table = DbRequests.get_exps_base(conn)
        for expid in experiments:
            # Experiment names should be 4 char long
            if (len(expid) != 4):
                counter += 1
                continue
            # Experiment names must correspond to an experiment that contains a .pkl file
            full_path = os.path.join(
                path, expid, "pkl", "job_list_{0}.pkl".format(expid))
            timest = 0
            if os.path.exists(full_path):
                timest = int(os.stat(full_path).st_mtime)
            else:
                counter += 1
                continue
            counter += 1
            experiments_table_exp_id = experiments_table.get(expid, None)
            start_time_local = time.time()
            if current_table.get(expid, None) is None:
                # Pkl exists but is not registered in the table
                # INSERT
                current_id = _process_pkl_insert_times(
                    conn, expid, full_path, timest, BasicConfig, DEBUG)
                _process_details_insert_or_update(
                    expid, experiments_table_exp_id, experiments_table_exp_id in details_table_ids_set, conn)
            else:
                exp_id, created, modified, total_jobs, completed_jobs = current_table[expid]
                time_diff = int(timest - modified)
                if time_diff > time_condition:
                    # Update table
                    _process_pkl_update_times(
                        expid, full_path, timest, BasicConfig, exp_id, DEBUG)
                    _process_details_insert_or_update(
                        expid, experiments_table_exp_id, experiments_table_exp_id in details_table_ids_set, conn)
                DbRequests.update_experiment_times_only_modified(
                    exp_id, timest)
            t1 = time.time()
            # Timer safeguard
            if (t1 - t0) > SAFE_TIME_LIMIT:
                raise Exception(
                    "Time limit reached {0:06.2f} seconds on process_completed_times while processing {1}. Time spent on reading data {2:06.2f} seconds.".format((t1 - t0), expid, t_data))
    except Exception as ex:
        print(traceback.format_exc())
        print(ex.message)


def _process_details_insert_or_update(expid, exp_id, current_details, conn):
    """
    Decides whether the experiment should be inserted or updated in the details table.  
    :param expid: name of experiment  
    :type expid: str  
    :param exp_id: id of experiment  
    :type exp_id: int  
    :param current_details: True if it exp_id exists in details table, False otherwise  
    :rtype: bool  
    :result: True if successful, False otherwise  
    :rtype: bool 
    """
    result = False
    if exp_id:
        user, created, model, branch, hpc = Autosubmit.describe(expid)
        if current_details:
            # Update
            result = DbRequests._update_ecearth_details(
                conn, exp_id, user, created, model, branch, hpc)
        else:
            # Insert
            _Id = DbRequests._insert_into_ecearth_details(
                conn, exp_id, user, created, model, branch, hpc)
            result = True if _Id else False
    return result


def _preprocess_completed_times():
    """
    Preprocess table to get rid of possible conflicts
    :param current_table: table experiment_times from as_times.db
    """
    BasicConfig.read()
    path = BasicConfig.LOCAL_ROOT_DIR
    db_file = os.path.join(path, "ecearth.db")
    conn = DbRequests.create_connection(db_file)
    # current_experiment_base = DbRequests.get_exps_base(conn)
    #print("Pre process")
    current_table = DbRequests.get_experiment_times_group()
    # print(current_table)
    for name, _ids in current_table.items():
        #print(name + " : " + str(_ids))
        if len(_ids) > 1:
            print(str(name) + " has more than 1 register.")
            # print(_ids)
            for i in range(0, len(_ids) - 1):
                _id = _ids[i]
                #print("Deleting " + str(_id))
                deleted_outdated = DbRequests.delete_experiment_data(_id)
                # if(deleted_outdated):
                #     print("Deleted outdated " + str(_id) + "\t" + str(name))


def _process_pkl_update_times(expid, path_pkl, timest_pkl, BasicConfig, exp_id, debug=False):
    """
    Updates register in job_times and experiment_times for the given experiment.
    :param expid: Experiment name
    :type expid: String
    :param path_pkl: path to the pkl file
    :type path_pkl: String
    :param timest_pkl: Timestamp of the last modified date of the pkl file
    :type timest_pkl: Integer
    :param BasicConfig: Configuration of AS
    :type BasicConfig: Object
    :param exp_id: Id of experiment
    :type exp_id: Integer
    :param debug: Flag (testing purposes)
    :type debug: Boolean
    :return: Nothing
    """
    # debug = True
    try:
        found_in_pkl = list()
        BasicConfig.read()
        path = BasicConfig.LOCAL_ROOT_DIR
        # Build connection to as_times.db
        db_file = os.path.join(path, DbRequests.DB_FILE_AS_TIMES)
        conn = DbRequests.create_connection(db_file)
        # Build path to tmp folder of experiment. Required later.
        tmp_path = os.path.join(
            BasicConfig.LOCAL_ROOT_DIR, expid, BasicConfig.LOCAL_TMP_DIR)
        job_times_db = dict()
        total_jobs = 0
        completed_jobs = 0
        fd = None
        t_start = time.time()
        # Get current detail from database
        experiment_times_detail = DbRequests.get_times_detail(exp_id)
        t_seconds = time.time() - t_start
        must_update_header = False
        if os.path.exists(path_pkl):
            fd = []
            with open(path_pkl, 'rb') as f:
                fd = pickle.load(f)
            to_update = []
            to_create = []
            for item in fd:
                total_jobs += 1
                status_code = int(item[2])
                job_name = str(item[0])
                found_in_pkl.append(job_name)
                status_text = str(Status.VALUE_TO_KEY[status_code])
                if (status_code == Status.COMPLETED):
                    completed_jobs += 1
                if (experiment_times_detail) and job_name in experiment_times_detail.keys():
                    # If job in pkl exists in database, retrieve data from database
                    submit_time, start_time, finish_time, status_text_in_table, detail_id = experiment_times_detail[
                        job_name]
                    if (status_text_in_table != status_text):
                        # If status has changed
                        # print(str(job_name) + " previous status " + str(status_text_in_table) + " -> " + str(status_text))
                        submit_time, start_time, finish_time, status_text_res = JobList._job_running_check(
                            status_code, job_name, tmp_path)
                        submit_ts = int(time.mktime(submit_time.timetuple())) if len(
                            str(submit_time)) > 0 else 0
                        start_ts = int(time.mktime(start_time.timetuple())) if len(
                            str(start_time)) > 0 else 0
                        finish_ts = int(time.mktime(finish_time.timetuple())) if len(
                            str(finish_time)) > 0 else 0
                        # if status_text_in_table == "RUNNING" and status_text == "COMPLETED":
                        #     # Changing from running to completed
                        #     if
                        # UPDATE
                        must_update_header = True
                        to_update.append((int(timest_pkl),
                                          submit_ts,
                                          start_ts,
                                          finish_ts,
                                          status_text,
                                          detail_id))
                        # DbRequests.update_job_times(conn, detail_id,
                        #                             int(timest_pkl),
                        #                             submit_ts,
                        #                             start_ts,
                        #                             finish_ts,
                        #                             status_text,
                        #                             debug)
                else:
                    # Insert only if it is not WAITING nor READY
                    if (status_code not in [Status.WAITING, Status.READY]):
                        submit_time, start_time, finish_time, status_text = JobList._job_running_check(
                            status_code, job_name, tmp_path)
                        must_update_header = True
                        to_create.append((exp_id,
                                          job_name,
                                          int(timest_pkl),
                                          int(timest_pkl),
                                          int(time.mktime(submit_time.timetuple())) if len(
                                              str(submit_time)) > 0 else 0,
                                          int(time.mktime(start_time.timetuple())) if len(
                                              str(start_time)) > 0 else 0,
                                          int(time.mktime(finish_time.timetuple())) if len(
                                              str(finish_time)) > 0 else 0,
                                          status_text))
                        # DbRequests.create_job_times(conn, exp_id,
                        #                             job_name,
                        #                             int(timest_pkl),
                        #                             int(time.mktime(submit_time.timetuple())) if len(
                        #                                 str(submit_time)) > 0 else 0,
                        #                             int(time.mktime(start_time.timetuple())) if len(
                        #                                 str(start_time)) > 0 else 0,
                        #                             int(time.mktime(finish_time.timetuple())) if len(
                        #                                 str(finish_time)) > 0 else 0,
                        #                             status_text,
                        #                             debug)
            # fd.close()
            # Update Many
            if len(to_update) > 0:
                DbRequests.update_many_job_times(conn, to_update)
            # Create Many
            if len(to_create) > 0:
                DbRequests.create_many_job_times(conn, to_create)

            if must_update_header == True:
                exp_id = DbRequests.update_experiment_times(
                    exp_id, int(timest_pkl), completed_jobs, total_jobs, debug)
        # Reviewing for deletes:

        if len(found_in_pkl) > 0 and (experiment_times_detail):
            detail_list = []
            for key in experiment_times_detail:
                if key not in found_in_pkl:
                    # Delete Row
                    submit_time, start_time, finish_time, status_text_in_table, detail_id = experiment_times_detail[
                        key]
                    detail_list.append((detail_id,))
            if len(detail_list) > 0:
                DbRequests._delete_many_from_job_times_detail(detail_list)
                # response = DbRequests._delete_from_job_times_detail(
                #     detail_id)
                # if (response):
                #     print(str(key) + "\t" +
                #           str(detail_id) + "\t" + " deleted.")

    except (socket.error, EOFError):
        # print(str(expid) + "\t EOF Error")
        pass
    except Exception as ex:
        print(expid)
        print(traceback.format_exc())


def _process_pkl_insert_times(conn, expid, path_pkl, timest_pkl, BasicConfig, debug=False):
    """
    Process Pkl contents and insert information into database if status of jobs is not WAITING (to save space).
    :param conn: Connection to database
    :type conn: Sqlite3 connection object
    :param expid: Experiment name
    :type expid: String
    :param path_pkl: Path to the pkl file
    :type path_pkl: String
    :param timest_pkl: Timestamp of the pkl modified date
    :type timest_pkl: Integer
    :param BasicConfig: Configuration data of AS
    :type BasicConfig: Object
    :param debug: Flag (proper name should be test)
    :type debug: Boolean
    """
    BasicConfig.read()
    path = BasicConfig.LOCAL_ROOT_DIR
    db_file = os.path.join(path, DbRequests.DB_FILE_AS_TIMES)
    # Build connection to ecearth.db
    conn = DbRequests.create_connection(db_file)
    db_file_ecearth = os.path.join(path, "ecearth.db")
    conn_ecearth = DbRequests.create_connection(db_file_ecearth)
    # Build tmp path to search for TOTAL_STATS files
    tmp_path = os.path.join(BasicConfig.LOCAL_ROOT_DIR,
                            expid, BasicConfig.LOCAL_TMP_DIR)
    job_times = dict()  # Key: job_name
    total_jobs = 0
    completed_jobs = 0
    status_code = Status.UNKNOWN
    status_text = str(Status.VALUE_TO_KEY[status_code])
    try:
        fd = []
        with open(path_pkl, 'rb') as f:
            fd = pickle.load(f)
        for item in fd:
            total_jobs += 1
            status_code = int(item[2])
            job_name = item[0]
            status_text = str(Status.VALUE_TO_KEY[status_code])
            if (status_code == Status.COMPLETED):
                completed_jobs += 1
            job_times[job_name] = status_code
    except Exception as exp:
        pass

    try:
        # Insert header
        current_id = DbRequests.insert_experiment_times_header(
            expid, int(timest_pkl), total_jobs, completed_jobs, debug, conn_ecearth)
        if(current_id > 0):
            # Insert detail
            to_insert_many = []
            for job_name in job_times:
                # Inserting detail. Do not insert WAITING or READY jobs.
                status_code = job_times[job_name]
                if (status_code not in [Status.WAITING, Status.READY]):
                    submit_time, start_time, finish_time, status_text = JobList._job_running_check(
                        status_code, job_name, tmp_path)
                    to_insert_many.append((current_id,
                                           job_name,
                                           int(timest_pkl),
                                           int(timest_pkl),
                                           int(time.mktime(submit_time.timetuple())) if len(
                                               str(submit_time)) > 0 else 0,
                                           int(time.mktime(start_time.timetuple())) if len(
                                               str(start_time)) > 0 else 0,
                                           int(time.mktime(finish_time.timetuple())) if len(
                                               str(finish_time)) > 0 else 0,
                                           status_text))
                    # DbRequests.create_job_times(conn,
                    #                             current_id,
                    #                             job_name,
                    #                             int(timest_pkl),
                    #                             int(time.mktime(submit_time.timetuple())) if len(
                    #                                 str(submit_time)) > 0 else 0,
                    #                             int(time.mktime(start_time.timetuple())) if len(
                    #                                 str(start_time)) > 0 else 0,
                    #                             int(time.mktime(finish_time.timetuple())) if len(
                    #                                 str(finish_time)) > 0 else 0,
                    #                             status_text,
                    #                             debug)
            if len(to_insert_many) > 0:
                DbRequests.create_many_job_times(conn, to_insert_many)
        else:
            pass
        # conn.commit()
        return current_id
    except Exception as ex:
        print(expid)
        print(traceback.format_exc())
        print(str(ex))
        return 0


def update_running_experiments(time_condition=600):
    """
    Tests if an experiment is running and updates database as_times.db accordingly.\n
    :return: Nothing
    """
    t0 = time.time()
    experiment_to_modified_ts = dict()
    try:
        BasicConfig.read()
        path = BasicConfig.LOCAL_ROOT_DIR
        # List of experiments from pkl
        tp0 = time.time()
        currentDirectories = subprocess.Popen(['ls', '-t', path],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT) if (os.path.exists(path)) else None
        stdOut, stdErr = currentDirectories.communicate(
        ) if currentDirectories else (None, None)
        # readingpkl = os.popen(
        #     'ls -t ' + path).read() if (os.path.exists(path)) else ""

        # Build connection to ecearth.db
        db_file = os.path.join(path, "ecearth.db")
        conn = DbRequests.create_connection(db_file)
        current_table = DbRequests.prepare_status_db()

        readingpkl = stdOut.split() if stdOut else []
        # print(readingpkl)
        # raise Exception("Test")
        tp1 = time.time()
        for item in readingpkl:
            # The name of an experiment directory has len = 4
            if (len(item) != 4):
                continue
            # Read pkl before test
            pkl_path = os.path.join(
                path, item, "pkl", "job_list_{0}.pkl".format(item))
            t1 = time.time()
            # Timer safeguard
            if (t1 - t0) > SAFE_TIME_LIMIT_STATUS:
                raise Exception(
                    "Time limit reached {0:06.2f} seconds on update_running_experiments while processing {1}. Time spent on reading data {2:06.2f} seconds.".format((t1 - t0), item, (tp1 - tp0)))

            # Valid pkl
            if (os.path.exists(pkl_path)):
                # full_path = pkl_path + '/' + (pkl_found[:-1])
                # if (os.path.exists(full_path)):
                current_stat = os.stat(pkl_path)
                timest = int(current_stat.st_mtime)
                timesys = time.time()
                time_diff = int(timesys - timest)
                if (time_diff < time_condition):
                    experiment_to_modified_ts[item] = time_diff
                    if current_table.get(item, None) is not None:
                        # UPDATE RUNNING
                        _exp_id, _status, _seconds = current_table[item]
                        if _status != "RUNNING":
                            DbRequests.update_exp_status(
                                item, "RUNNING", time_diff)
                    else:
                        # Insert new experiment
                        current_id = DbRequests.insert_experiment_status(
                            conn, item, time_diff)
                        current_table[item] = (
                            current_id, 'RUNNING', time_diff)
                elif (time_diff <= 3600):
                    # If it has been running in the last 1 hour
                    # It must have been added before
                    # print("Running in last 10 hours {0}".format(item))
                    error, error_message, is_running, timediff, _ = _is_exp_running(
                        item)
                    if is_running == True:
                        if current_table.get(item, None):
                            # print("{0} was added before.".format(item))
                            _exp_id, _status, _seconds = current_table[item]
                            # item = expid

                            # print("{0} is {1}".format(item, str(is_running)))
                            if _status != "RUNNING" and is_running == True:
                                DbRequests.update_exp_status(
                                    item, "RUNNING", _seconds)
                        else:
                            # print(
                            #     "{0} is running and was not added before.".format(item))
                            current_id = DbRequests.insert_experiment_status(
                                conn, item, time_diff)
                            current_table[item] = (
                                current_id, 'RUNNING', time_diff)

        for expid in current_table:
            exp_id, status, seconds = current_table[expid]
            if status == "RUNNING" and experiment_to_modified_ts.get(expid, None) is None:
                # Perform exhaustive check
                error, error_message, is_running, timediff, _ = _is_exp_running(
                    expid)
                # UPDATE NOT RUNNING
                if (is_running == False):
                    # print("Update NOT RUNNING for " + expid)
                    DbRequests.update_exp_status(
                        expid, "NOT RUNNING", timediff)
    except Exception as e:
        # print(expid)
        print(e.message)
        # print(traceback.format_exc())


def get_experiment_graph_format_test(expid):
    """
    Some testing. Does not serve any purpose now, but the code might be useful.
    """
    base_list = dict()
    pkl_timestamp = 10000000
    try:
        notransitive = False
        print("Received " + str(expid))
        BasicConfig.read()
        exp_path = os.path.join(BasicConfig.LOCAL_ROOT_DIR, expid)
        tmp_path = os.path.join(exp_path, BasicConfig.LOCAL_TMP_DIR)
        as_conf = AutosubmitConfig(
            expid, BasicConfig, ConfigParserFactory())
        if not as_conf.check_conf_files():
            # Log.critical('Can not run with invalid configuration')
            raise Exception(
                'Autosubmit GUI might not have permission to access necessary configuration files.')

        job_list = Autosubmit.load_job_list(
            expid, as_conf, notransitive=notransitive)

        job_list.sort_by_id()
        base_list = job_list.get_graph_representation(BasicConfig)
    except Exception as e:
        return {'nodes': [],
                'edges': [],
                'error': True,
                'error_message': str(e),
                'graphviz': False,
                'max_children': 0,
                'max_parents': 0,
                'total_jobs': 0,
                'pkl_timestamp': 0}
    name_to_id = dict()
    # name_to_weight = dict()
    list_nodes = list()
    list_edges = list()
    i = 0
    with open('/home/Earth/wuruchi/Documents/Personal/spectralgraph/data/graph_' + expid + '.txt', 'w') as the_file:
        for item in base_list['nodes']:
            # the_file.write(str(i) + "\n")
            name_to_id[item['id']] = i
            list_nodes.append(i)
            i += 1
        for item in base_list['edges']:
            the_file.write(str(name_to_id[item['from']]) + " " + str(
                name_to_id[item['to']]) + " " + ("10" if item['is_wrapper'] == True else "1") + "\n")
            list_edges.append(
                (name_to_id[item['from']], name_to_id[item['to']]))
        for item in base_list['fake_edges']:
            the_file.write(str(name_to_id[item['from']]) + " " + str(
                name_to_id[item['to']]) + " " + ("10" if item['is_wrapper'] == True else "1") + "\n")
            list_edges.append(
                (name_to_id[item['from']], name_to_id[item['to']]))
    return list_nodes, list_edges


def generate_all_experiment_data(exp_path, job_path):
    """
    Getting all data from experiments
    """
    target_experiment_file = str(exp_path)
    target_experiment_job_file = str(job_path)
    print("Experiment file path: " + target_experiment_file)
    print("Job file path: " + target_experiment_job_file)
    conn_ecearth = DbRequests.create_connection(
        "/esarchive/autosubmit/ecearth.db")
    conn_as_times = DbRequests.create_connection(
        "/esarchive/autosubmit/as_times.db")
    # print("Getting experiments")
    all_experiments = DbRequests._get_exps_complete(conn_ecearth)
    all_detailed = DbRequests.get_exps_detailed_complete(conn_ecearth)
    experiment_times = DbRequests.get_experiment_times()
    valid_id = dict()
    if (all_detailed) and (all_experiments) and (experiment_times):
        file1 = open(target_experiment_file, "w")
        file1.write(
            "id|name|completed|total|user|as_version|created|model|hpc|wrapper|maxwrap\n")
        for item in all_experiments:
            _id, name, _type, autosubmit_version, description, model_branch, template_name, template_branch, ocean_diag_branch = item
            wrapper_type, maxwrapped = get_auto_conf_data(name)
            #  description = description.replace('|', '~')
            # print(item)
            if _id in all_detailed.keys():
                user, created, model, branch, hpc = all_detailed[_id]

                completed = total = 0
                if name in experiment_times.keys():
                    # Exists register of experiment completed and total jobs
                    total, completed, _ = experiment_times[name]
                    file1.write(str(_id) + "|" + str(name) + "|" + str(completed) + "|" + str(total) + "|" + str(user) + "|" + str(autosubmit_version) + "|" + str(
                        created) + "|" + format_model(str(model)) + "|" + str(hpc) + "|" + str(wrapper_type) + "|" + str(maxwrapped) + "\n")
                    valid_id[_id] = name
        file1.close()
    # First step was successful, prepare to process jobs
    all_job_times = DbRequests.get_completed_times_detail()
    # job_data_structure = JobDataStructure()
    # if (all_job_times):
    file2 = open(target_experiment_job_file, "w")
    file2.write(
        "exp_id|exp_name|job_name|type|submit|start|finish|status|wallclock|procs|threads|tasks|queue|platform\n")
    for exp_id in valid_id.keys():
        expid = valid_id.get(exp_id, None)
        historical_data = JobDataStructure(expid).get_all_current_job_data()
        if historical_data:
            print("Using historical data for {}".format(exp_id))
            for job in historical_data:
                file2.write(str(exp_id) + "|" + str(expid) + "|" + str(job.job_name) + "|" + str(job.member) + "|" + str(
                    job.submit) + "|" + str(job.start) + "|" + str(job.finish) + "|" + str(job.status) + "|" + str(job.wallclock) + "|"
                    + str(job.ncpus) + "|" + str(0) + "|" + str(0) + "|" + str(job.qos) + "|" + str(job.platform) + "\n")
        else:
            print("Using current data for {}".format(exp_id))
            if exp_id in all_job_times.keys():
                # print(exp_id)
                current = all_job_times[exp_id]
                exp_name = valid_id[exp_id]
                # print(exp_name)
                if (current):
                    ###
                    # TODO: Request Autosubmit Config here
                    job_conf = get_job_conf_list(exp_name)
                    ###
                    if (job_conf):
                        for job_name in current.keys():
                            job_conf_info, job_type = old_searcher(
                                job_conf, job_name)
                            if (job_conf_info):
                                submit, start, finish, status, detail_id = current[job_name]
                                wallclock, processors, threads, tasks, memory, mem_task, queue, platform = job_conf_info
                                file2.write(str(exp_id) + "|" + str(exp_name) + "|" + str(job_name) + "|" + str(job_type) + "|" + str(
                                    submit) + "|" + str(start) + "|" + str(finish) + "|" + str(status) + "|" + str(wallclock) + "|"
                                    + str(processors) + "|" + str(threads) + "|" + str(tasks) + "|" + str(queue) + "|" + str(platform) + "\n")
                            else:
                                print(str(exp_name) + "  | job " +
                                      str(job_name) + " no job conf valid found.")
                    else:
                        print(str(exp_name) + " conf not valid.")
    file2.close()


def format_model(url):
    """
    Return model in proper format.
    Considers separator '/es/'
    """
    separator = '/es/'
    sec_separator = '.git'
    model = "NA"
    pos = url.find(separator)
    if pos > 0:
        pos = pos + len(separator)
        model = url[pos:]
        end = model.find(sec_separator)
        if end > 0:
            model = model[0:end]
    return model


def old_searcher(section_list, job_name):
    """
    A very basic implementation to find the type of a job
    """
    for section in section_list.keys():
        t_name = "_" + section
        # print(t_name)
        if job_name.find(t_name) >= 0:
            return section_list[section], section
    return None, None


def get_job_conf_list(expid):
    """
    Gets list of jobs with attributes from parser
    """
    try:
        BasicConfig.read()
        # Basi = "/esarchive/autosubmit/"
        # parser_path = os.path.join(BasicConfig.LOCAL_ROOT_DIR, expid, "conf",
        #                           "expdef_" + expid + ".conf")

        as_conf = AutosubmitConfig(expid, BasicConfig, ConfigParserFactory())
        if not as_conf.check_conf_files():
            print('Can not create with invalid configuration')
            return None
        sections = as_conf.get_jobs_sections()
        result = dict()
        for section in set(sections):
            main_platform = as_conf.get_platform()
            job_platform = as_conf.get_job_platform(section)

            processors = as_conf.get_processors(section)
            threads = as_conf.get_threads(section)
            tasks = as_conf.get_tasks(section)
            memory = as_conf.get_memory(section)
            memory_per_task = as_conf.get_memory_per_task(section)
            queue = as_conf.get_queue(section)
            queue = queue if len(queue) > 0 else (as_conf.get_platform_queue(job_platform) if len(
                job_platform) > 0 else (as_conf.get_platform_queue(main_platform) if len(main_platform) > 0 else ""))
            final_platform = job_platform if len(
                job_platform) > 0 else main_platform
            wallclock = as_conf.get_wallclock(section)
            platform_wallclock = as_conf.get_platform_wallclock(final_platform)
            wallclock = wallclock if len(wallclock) > 0 else (
                platform_wallclock if len(platform_wallclock) > 0 else "")
            result[section] = (wallclock, processors, threads,
                               tasks, memory, memory_per_task, queue, final_platform)
        return result
    except Exception as ex:
        print(str(ex) + "\n" + str(expid) +
              " : failed to retrieve info from jobs conf.\n")
        return None


def get_auto_conf_data(expid):
    """
    Gets autosubmit conf parser information per expid
    """
    try:
        wrapper_type = "None"
        max_wrapped = 0
        BasicConfig.read()
        as_conf = AutosubmitConfig(expid, BasicConfig, ConfigParserFactory())
        if not as_conf.check_conf_files():
            #print('Can not create with invalid configuration')
            return (wrapper_type, max_wrapped)
        wrapper_type = as_conf.get_wrapper_type()
        max_wrapped = as_conf.get_max_wrapped_jobs()
        return (wrapper_type, max_wrapped)
    except Exception as ex:
        print(str(ex) + "\n" + str(expid) +
              " : failed to retrieve info from autosubmit conf.\n")
        return ("None", 0)


def verify_last_completed(seconds=300):
    """
    Verifying last 300 seconds by default
    """
    # Basic info
    t0 = time.time()
    BasicConfig.read()
    # Current timestamp
    current_st = time.time()
    # Connection
    path = BasicConfig.LOCAL_ROOT_DIR
    db_file = os.path.join(path, DbRequests.DB_FILE_AS_TIMES)
    conn = DbRequests.create_connection(db_file)
    # Current latest detail
    td0 = time.time()
    latest_detail = DbRequests.get_latest_completed_jobs(seconds)
    t_data = time.time() - td0
    # Main Loop
    for job_name, detail in latest_detail.items():
        tmp_path = os.path.join(
            BasicConfig.LOCAL_ROOT_DIR, job_name[:4], BasicConfig.LOCAL_TMP_DIR)
        detail_id, submit, start, finish, status = detail
        submit_time, start_time, finish_time, status_text_res = JobList._job_running_check(
            Status.COMPLETED, job_name, tmp_path)
        submit_ts = int(time.mktime(submit_time.timetuple())) if len(
            str(submit_time)) > 0 else 0
        start_ts = int(time.mktime(start_time.timetuple())) if len(
            str(start_time)) > 0 else 0
        finish_ts = int(time.mktime(finish_time.timetuple())) if len(
            str(finish_time)) > 0 else 0
        if (finish_ts != finish):
            #print("\tMust Update")
            DbRequests.update_job_times(conn, detail_id,
                                        int(current_st),
                                        submit_ts,
                                        start_ts,
                                        finish_ts,
                                        status,
                                        debug=False,
                                        no_modify_time=True)
        t1 = time.time()
        # Timer safeguard
        if (t1 - t0) > SAFE_TIME_LIMIT:
            raise Exception(
                "Time limit reached {0:06.2f} seconds on verify_last_completed while reading {1}. Time spent on reading data {2:06.2f} seconds.".format((t1 - t0), job_name, t_data))


def get_experiment_counters(expid):
    """
    Returns status counters of the experiment.
    """
    error = False
    error_message = ""
    total = 0
    experiment_counters = dict()
    BasicConfig.read()
    path_pkl = os.path.join(BasicConfig.LOCAL_ROOT_DIR,
                            expid, "pkl", "job_list_{}.pkl".format(expid))
    # Default counter per status
    experiment_counters = {name: 0 for name in Status.STRING_TO_CODE}
    try:
        if os.path.exists(path_pkl):
            fd = open(path_pkl, 'r')
            for item in pickle.load(fd):
                status_code = int(item[2])
                total += 1
                experiment_counters[Status.VALUE_TO_KEY.get(status_code, "UNKNOWN")] = experiment_counters.get(
                    Status.VALUE_TO_KEY.get(status_code, "UNKNOWN"), 0) + 1

        else:
            raise Exception("PKL file not found.")
    except Exception as exp:
        error = True
        error_message = str(exp)
        # print(traceback.format_exc())
        # print(exp)
    return {"error": error, "error_message": error_message, "expid": expid, "total": total, "counters": experiment_counters}


def get_quick_view(expid):
    """[summary]

    :param expid: Experiment identifier 
    :type expid: str

    Returns:
        [type]: [description]
    """
    pkl_file_name = ""
    error = False
    error_message = ""
    #quick_view = list()
    view_data = []
    quick_tree_view = deque()
    source = JobList.get_sourcetag()
    target = JobList.get_targettag()
    sync = JobList.get_synctag()
    check_mark = JobList.get_checkmark()
    jobs_in_pkl = {}
    fakeAllJobs = []
    total_count = completed_count = failed_count = running_count = queuing_count = 0
    try:
        BasicConfig.read()
        path_pkl = BasicConfig.LOCAL_ROOT_DIR + '/' + expid + '/pkl'
        pkl_file = os.path.join(path_pkl, "job_list_{0}.pkl".format(expid))
        path_to_logs = os.path.join(
            BasicConfig.LOCAL_ROOT_DIR, expid, "tmp", "LOG_" + expid)
        tmp_path = os.path.join(
            BasicConfig.LOCAL_ROOT_DIR, expid, BasicConfig.LOCAL_TMP_DIR)
        # reading = os.popen(pkl_file).read() if (
        #     os.path.exists(pkl_file)) else None
        if os.path.exists(pkl_file):
            # Retrieving packages
            now_ = time.time()
            job_to_package, package_to_jobs, package_to_package_id, package_to_symbol = JobList.retrieve_packages(
                BasicConfig, expid)
            print("Retrieving packages {0} seconds.".format(
                str(time.time() - now_)))

            try:
                fd = open(pkl_file, 'r')
                for item in pickle.load(fd):
                    status_code = int(item[2])
                    # counters
                    if status_code == Status.COMPLETED:
                        completed_count += 1
                    elif status_code == Status.FAILED:
                        failed_count += 1
                    elif status_code == Status.RUNNING:
                        running_count += 1
                    elif status_code == Status.QUEUING:
                        queuing_count += 1
                    # end
                    job_name = item[0]
                    priority = item[3]
                    id_number = item[1]
                    out = str(item[8]) if len(item) >= 9 else ""
                    err = str(item[9]) if len(item) >= 10 else ""
                    status_color = Monitor.color_status(status_code)
                    status_text = str(Status.VALUE_TO_KEY[status_code])
                    jobs_in_pkl[job_name] = (
                        status_code, status_color, status_text, out, err, priority, id_number)
            except Exception as exp:
                raise Exception(
                    "Autosubmit API couldn't open pkl file. If you are sure that your experiment is running correctly, try again.")

                # fakeAllJobs.append(
                #     SimpleJob(job_name, tmp_path, status_code))
            total_count = len(jobs_in_pkl.keys())
            # Retrieving time
            # now_ = time.time()
            # job_running_to_min, job_running_to_runtext = JobList.get_job_times_collection(
            #     BasicConfig, fakeAllJobs, expid, job_to_package, package_to_jobs)
            # print("Retrieving times {0} seconds.".format(
            #     str(time.time() - now_)))

            if len(jobs_in_pkl.keys()) > 0:
                # fd = open(path_pkl, 'r')
                for job_name in jobs_in_pkl.keys():
                    status_code, status_color, status_text, out, err, priority, id_number = jobs_in_pkl[
                        job_name]
                    wrapper_tag = ""
                    wrapper_id = 0
                    wrapper_name = ""
                    if job_name in job_to_package.keys():
                        wrapper_name = job_to_package[job_name]
                        wrapper_id = package_to_package_id[job_to_package[job_name]]
                        wrapper_tag = " <span class='badge' style='background-color:#94b8b8'>Wrapped " + \
                            wrapper_id + "</span>"

                    # job_info = job_running_to_min[job_name] if job_name in job_running_to_min.keys(
                    # ) else None

                    # running_text = job_running_to_runtext[job_name] if job_name in job_running_to_runtext.keys(
                    # ) else ("")

                    view_data.append({'name': job_name,
                                      #    'rm_id': id_number,
                                      #    'status_code': status_code,
                                      #    'minutes': job_info.run_time if job_info else 0,
                                      #    'minutes_queue': job_info.queue_time if job_info else 0,
                                      #    'submit': job_info.submit if job_info else None,
                                      #    'start': job_info.start if job_info else None,
                                      #    'finish': job_info.finish if job_info else None,
                                      #    'running_text': running_text,
                                      #    'status': status_text,
                                      #    'status_color': status_color,
                                      #    'wrapper': wrapper_name,
                                      # 'wrapper_tag': wrapper_tag,
                                      #    'wrapper_id': wrapper_id,
                                      'path_log': path_to_logs,
                                      'out': "/" + out,
                                      'err': "/" + err,
                                      #    'title': Job.getTitle(job_name, status_color, status_text) + ((" ~ " + running_text) if status_code not in [Status.WAITING, Status.WAITING] else "")
                                      # 'title': Job.getTitle(job_name, status_color, status_text)
                                      })
                    if status_code in [Status.COMPLETED, Status.WAITING, Status.READY]:
                        quick_tree_view.append({'title': Job.getTitle(job_name, status_color, status_text) + wrapper_tag,
                                                'refKey': job_name,
                                                'data': 'Empty',
                                                'children': []})
                    else:
                        quick_tree_view.appendleft({'title': Job.getTitle(job_name, status_color, status_text) + wrapper_tag,
                                                    'refKey': job_name,
                                                    'data': 'Empty',
                                                    'children': []})
                # return {}
                quick_tree_view = list(quick_tree_view)
            else:
                raise Exception('File {0} does not exist'.format(path_pkl))
    except Exception as exp:
        error_message = "Exception: {0}".format(str(exp))
        error = True
        print(error_message)
        print(traceback.format_exc())
        pass

    return {"error": error, "error_message": error_message, "view_data": view_data, "tree_view": quick_tree_view, "total": total_count, "completed": completed_count, "failed": failed_count, "running": running_count, "queuing": queuing_count}


def get_job_history(expid, job_name):
    """
    Gets job history.  
    :param job_name: Name of job  
    :type job_name: str  
    :return:  
    :rtype:  
    """
    error = False
    error_message = ""
    result = None
    try:
        job_structure = JobDataStructure(expid)
        result = job_structure.get_historic_job_data_json(job_name)
    except Exception as exp:
        error = True
        error_message = str(exp)
        pass
    return {"error": error, "error_message": error_message, "history": result}


def get_current_configuration_by_expid(expid, valid_user):
    """
    Gets the current configuration by expid. The procedure queries the historical database and the filesystem.
    :param expid: Experiment Identifier  
    :type expdi: str 
    :return: configuration content formatted as a JSON object  
    :rtype: Dictionary
    """
    error = False
    warning = False
    error_message = ""
    warning_message = ""
    currentRunConfig = {}
    currentFileSystemConfig = {}
    try:
        if not valid_user:
            raise Exception(
                "You have to be logged in to access this information.")
        allowedConfigKeys = ['conf', 'exp', 'jobs', 'platforms', 'proj']
        historicalDatabase = JobData.JobDataStructure(expid)
        experimentRun = historicalDatabase.get_max_id_experiment_run()
        currentMetadata = json.loads(
            experimentRun.metadata) if experimentRun and experimentRun.metadata else None
        currentRunId = experimentRun.run_id if experimentRun else None
        # Main keys = conf, exp, jobs, platforms, proj
        # Can we ignore proj by now? Including it.
        # TODO: Define which keys should be included in the answer
        if currentMetadata:
            currentRunConfig = {
                key: currentMetadata[key] for key in currentMetadata if key in allowedConfigKeys}
        currentRunConfig["contains_nones"] = True if not currentMetadata or None in currentMetadata.values(
        ) else False

        BasicConfig.read()
        autosubmitConfig = AutosubmitConfig(
            expid, BasicConfig, ConfigParserFactory())
        try:
            autosubmitConfig.reload()
            currentFileSystemConfigContent = autosubmitConfig.get_full_config_as_dict()
            if currentFileSystemConfigContent:
                currentFileSystemConfig = {
                    key: currentFileSystemConfigContent[key] for key in currentFileSystemConfigContent if key in allowedConfigKeys}
            currentFileSystemConfig["contains_nones"] = True if not currentFileSystemConfigContent or None in currentFileSystemConfigContent.values(
            ) else False

        except Exception as exp:
            warning = True
            warning_message = "The filesystem system configuration can't be retrieved because '{}'".format(
                exp)
            currentFileSystemConfig["contains_nones"] = True
            pass

    except Exception as exp:
        error = True
        error_message = str(exp)
        currentRunConfig["contains_nones"] = True
        currentFileSystemConfig["contains_nones"] = True
        pass
    return {"error": error, "error_message": error_message, "warning": warning, "warning_message": warning_message, "configuration_current_run": currentRunConfig, "configuration_filesystem": currentFileSystemConfig, "are_equal": currentRunConfig == currentFileSystemConfig}


def get_experiment_run_detail(expid, run_id):
    error = False
    error_message = ""
    result = None
    try:
        result = JobDataStructure(expid).get_current_run_job_data_json(run_id)
        tags = {"source": JobList.get_sourcetag(), "target": JobList.get_targettag(), "sync": JobList.get_synctag(), "check": JobList.get_checkmark(
        ), "completed": JobList.get_completed_tag(), "running_tag": JobList.get_running_tag(), "queuing_tag": JobList.get_queuing_tag(), "failed_tag": JobList.get_failed_tag()}
    except Exception as exp:
        error = True
        error_message = str(exp)
        pass
    return {"error": error, "error_message": error_message, "rundata": result}


def get_experiment_runs(expid):
    """ Get runs of the same experiment from historical db

    Args:
        expid ([type]): [description]
    """
    error = False
    error_message = ""
    result = []
    try:
        job_data_structure = JobDataStructure(expid)
        runs = job_data_structure.get_experiment_runs()
        run_dict_SIM = job_data_structure.get_current_job_data_CF_SIM()

        run_dict_POST = job_data_structure.get_current_job_data_CF_POST()

        if runs:
            for experiment_run in runs:
                # print("Process run {}".format(experiment_run.run_id))
                packages_in_run = None
                valid_SIM_in_run = run_dict_SIM.get(
                    experiment_run.run_id, None)

                valid_POST_in_run = run_dict_POST.get(
                    experiment_run.run_id, None)
                if valid_SIM_in_run and len(valid_SIM_in_run) > 0:
                    packages_in_run = job_data_structure.get_job_packages_info_per_run_id(
                        experiment_run.run_id)

                result.append({"run_id": experiment_run.run_id, "created": experiment_run.created, "finish": datetime.datetime.fromtimestamp(experiment_run.finish).strftime('%Y-%m-%d-%H:%M:%S') if experiment_run.finish > 0 else None, "chunk_unit": experiment_run.chunk_unit, "chunk_size": experiment_run.chunk_size,
                               "submitted": experiment_run.submitted, "queuing": experiment_run.queuing, "running": experiment_run.running, "completed": experiment_run.completed, "failed": experiment_run.failed, "total": experiment_run.total, "suspended": experiment_run.suspended, "SYPD": experiment_run.getSYPD(valid_SIM_in_run), "ASYPD": experiment_run.getASYPD(valid_SIM_in_run, valid_POST_in_run, packages_in_run)})
        else:
            error = True
            error_message = "No data"
    except Exception as exp:
        error = True
        error_message = str(exp)
        pass
    return {"error": error, "error_message": error_message, "runs": result}


def read_esarchive(result):
    # t0 = time.time()
    # Using as_times.db as reference
    current_latency = 10000
    current_bandwidth = 10000
    avg_latency = 1000
    avg_bandwidth = 1000
    if os.path.exists('/esarchive/scratch/pbretonn/monitor-esarchive/plot/io-benchmark/stats-io.txt'):
        output = subprocess.check_output(
            ['tail', '-n', '49', '/esarchive/scratch/pbretonn/monitor-esarchive/plot/io-benchmark/stats-io.txt'])

        # lines = lines[:-1]
        # print(lines)
        # print(last_line)

        if len(output) > 0:
            lines = output.split('\n')[:-1]  # Get rid of last line
            last_line = lines[-1].split()
            try:
                current_bandwidth = float(last_line[1])
            except IndexError:
                # Default to 90.0
                current_bandwidth = 90.0
            try:
                current_latency = float(last_line[2])
            except IndexError:
                current_latency = 2.0
            try:
                last_day = [line.split() for line in lines[:-1]]
                avg_bandwidth = sum(float(last[1])
                                    for last in last_day if len(last) > 1) / len(last_day)
                avg_latency = sum(float(last[2])
                                  for last in last_day if len(last) > 2) / len(last_day)
            except IndexError:
                avg_bandwidth = 90.0
                avg_latency = 2.0

            # bandwidth_average
        # print(last_day)
        result.append(True)
    else:
        result.append(False)
    result.append(avg_bandwidth)
    result.append(avg_latency)
    result.append(current_bandwidth)
    result.append(current_latency)


def test_esarchive_status():
    try:
        t0 = time.time()
        manager = multiprocessing.Manager()
        result = manager.list()
        p = multiprocessing.Process(
            target=read_esarchive, name="ESARCHIVE", args=(result,))
        p.start()
        p.join(10)
        if p.is_alive():
            print("Test running... killing it")
            p.terminate()
            p.join()
            result = [False, -1.0, -1.0, 0.0, 0.0]
        t1 = time.time()
        #print(t1 - t0)
        rtime = t1 - t0
        # print(result)
        status = result[0]
        abandwith = result[1]
        alatency = result[2]
        cbandwidth = result[3]
        clatency = result[4]
        DbRequests.insert_archive_status(
            status, alatency, abandwith, clatency, cbandwidth, rtime)
    except Exception as exp:
        print(traceback.format_exc())
        # error_message = str(exp)


def get_last_test_archive_status():
    error = False
    error_message = ""
    str_status = "OFFLINE"
    latency_warning = None
    bandwidth_warning = None
    response_warning = None
    try:
        status, alatency, abandwidth, clatency, cbandwidth, rtime, date = DbRequests.get_last_read_archive_status()
        if status == 1:
            str_status = "ONLINE"
            # 4.0 as a standard
            latency_warning = "Higher latency than usual" if clatency > (
                alatency + alatency * 0.1) or clatency > 4.0 else None
            # 90.0  as a standard
            bandwidth_warning = "Lower bandwidth than usual" if cbandwidth < (
                abandwidth - abandwidth * 0.1) or cbandwidth < 90.0 else None
            response_warning = "Higher response times than usual" if int(
                rtime) > 1 else None
        else:
            str_status = "OFFLINE"
    except Exception as exp:
        error = True
        error_message = ""

    return {"status": str_status,
            "error": error,
            "error_message": error_message,
            "avg_latency": alatency,
            "avg_bandwidth": abandwidth,
            "current_latency": clatency,
            "current_bandwidth": cbandwidth,
            "reponse_time": rtime,
            "datetime": date,
            "latency_warning": latency_warning,
            "bandwidth_warning": bandwidth_warning,
            "response_warning": response_warning,
            }
