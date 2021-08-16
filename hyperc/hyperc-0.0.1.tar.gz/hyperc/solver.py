import os
import copy
import subprocess
from os.path import join
import pathlib
from hyperc.settings import DOWNWARD_SCRIPT, STORE_STDOUT
import hyperc.settings
import signal
from hyperc.running import RunningPlanner
import hyperc.running
import logging
import hyperc.sas_shuffle
log = logging.getLogger("hyperc")


def translate_only(max_time, work_dir, term_list=None):
    hyperc.running.downward_translator
    rt = copy.deepcopy(hyperc.running.downward_translator)
    if isinstance(term_list, list):
        term_list.append(rt)
    rt.work_dir = work_dir
    rt.max_time = max_time
    rt.create_dirs()

    #run translator
    assert rt.translator is not None
    rt.runscripts = None
    rt.stdin = None
    try:
        start_proc(rt)
    except Exception as e:
        rt.kill()
        raise e
    return rt

def start_solve_proc(max_time, work_dir, term_list=None, traslate=False):
    running_planners = []
    if isinstance(term_list, list):
        running_planners = term_list
    for search_config in hyperc.settings.HYPERC_SEARCH_CONFIG.split(';'):
        try:
            rp = getattr(hyperc.running, search_config)
        except AttributeError as e:
            raise AttributeError (f"Search configuration {search_config} not found!!!")
        rp = copy.deepcopy(rp)
        rp.work_dir = work_dir
        rp.max_time = max_time
        rp.create_dirs()

        #run translator
        if rp.translator is not None:
            rp_child = copy.deepcopy(rp)
            rp_child.parent = rp
            rp_child.runscripts = None
            rp_child.stdin = None
            running_planners.append(rp_child)
            if hyperc.settings.HYPERC_MAX_PROC_COUNTER >= hyperc.settings.HYPERC_MAX_PROC:
                continue
            try:
                start_proc(rp_child)
            except Exception as e:
                for rp_child in running_planners:
                    rp_child.kill()
                raise e
            hyperc.settings.HYPERC_MAX_PROC_COUNTER += 1
             # continue because translator only one per RunningPlanner
             # If you want to run multiple translators create separate RunningPlanners instance
            continue

        # run search
        running_planners.extend(gen_search_proc(rp))

    return running_planners


def gen_search_proc(rp: RunningPlanner):
    running_planners = []
    lonely = False
    if rp.runscripts is None:
        return []
    if len(rp.runscripts) == 0:
        return []
    if len(rp.runscripts) == 1:
        lonely = True
    for runscript_name in rp.runscripts:
        rp_child = copy.copy(rp)
        rp_child.lonely = lonely
        rp_child.name = runscript_name
        rp_child.parent = rp
        if rp_child.parent.translator is not None:
            rp_child.dir_created = False
            rp_child.work_dir = rp.run_dir
        if rp_child.lonely:
            # rp_child.dir_created = True
            rp_child.run_dir = rp.run_dir
        else:
            rp_child.dir_created = False
            rp_child.run_dir = os.path.join(rp.run_dir, runscript_name)
        rp_child.runscripts = {runscript_name: rp.runscripts[runscript_name]}
        running_planners.append(rp_child)
        if hyperc.settings.HYPERC_MAX_PROC_COUNTER >= hyperc.settings.HYPERC_MAX_PROC:
            continue
        try:
            start_proc(rp_child)
        except Exception as e:
            for rp_child in running_planners:
                rp_child.kill()
            raise e
        hyperc.settings.HYPERC_MAX_PROC_COUNTER += 1
    return running_planners

def spawn_waiters(running_planners):
    for rp in running_planners:
        if rp.proc is not None:
            continue
        if hyperc.settings.HYPERC_MAX_PROC_COUNTER >= hyperc.settings.HYPERC_MAX_PROC:
            return

        try:
            start_proc(rp)
        except Exception as e:
            for rp_child in running_planners:
                rp_child.kill()
            raise e
        hyperc.settings.HYPERC_MAX_PROC_COUNTER += 1

def start_proc(rp: RunningPlanner):
    rp.format()
    rp.create_dirs()
    stdin = subprocess.DEVNULL
    if STORE_STDOUT:
        stdoutf = open("{0}/stdout.log".format(rp.run_dir), "w+")
    else:
        stdoutf = subprocess.DEVNULL

    if rp.translator is None:
        runscript = list(rp.runscripts.values())[0]
        if rp.stdin is not None:
            if hyperc.settings.HYPERC_SAS_RANDOMIZE == '1':
                sf = hyperc.sas_shuffle.SASFile()
                fd = open(rp.stdin)
                sf.load_sas(fd)
                sf.shuffle_operators()
                sas_rnd = os.path.join(rp.run_dir, "rnd.sas")
                of = open(sas_rnd, "w+")
                of.write(sf.gen_sasfile())
                of.close()
                rp.stdin = sas_rnd
            stdin = open(rp.stdin)
    else:
        runscript = rp.translator
    
    rp.reset_timer()
    rp.proc = subprocess.Popen(runscript, shell=False, stdin=stdin, stdout=stdoutf, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True, start_new_session=True)
    rp.main_pid = copy.copy(rp.proc.pid)
