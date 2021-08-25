import pandas as pd
import itertools as it
import collections
import functools
import hashlib
import multiprocessing as mp
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta, date
from typing import Sized

import dateutil
import dateutil.parser

from .. import logger


def reprer(obj):
    if isinstance(obj, dict):
        d = obj
    else:
        d = obj.__dict__
    body = [f"{k:<20}: {('None' if v is None else v)}" for k, v in d.items() if k[0] != '_']
    if body:
        delim = "\n"
    # else: body,delim=["Expired!"]," "
    else:
        body, delim = ['Empty'], " "
    return f'"{obj.__class__.__name__}" item:' + delim + "\n".join(body)


def func_has_classarg(func, args):
    has_classarg = False
    if args:
        funcattr = getattr(args[0], func.__name__, None)
        if funcattr is not None and hasattr(funcattr, '__self__'):
            has_classarg = True
    return has_classarg


def infiterate(iter_obj, max_iter_count=None, next_getter=None, inform_count=8, on_inform=None):
    if on_inform is None: on_inform = lambda *args, **kwargs: True
    if isinstance(iter_obj, int):
        an_iterable, iter_count = range(iter_obj), iter_obj
    else:
        an_iterable = iter_obj
        if isinstance(iter_obj, Sized):
            iter_count = len(iter_obj)
        else:
            assert max_iter_count
            iter_count = max_iter_count
    max_iter_count = max_iter_count or iter_count
    if next_getter is None: next_getter = lambda _obj: _obj
    for i, obj in enumerate(an_iterable):
        if i % (max_iter_count // inform_count) == 0:
            on_inform()
            logger.info('%d%%, i=%d', i / (max_iter_count - 1) * 100, i)

        obj = next_getter(obj)
        yield obj
        if i == max_iter_count - 1:
            on_inform()
            logger.info('%d%%, i=%d', i / (max_iter_count - 1) * 100, i)
            return


class ParallelTasker:

    def __init__(self, func, *args, **kwargs):
        self.partial_func = functools.partial(func, *args, **kwargs)
        self.queue = mp.Queue()
        self._total_proc_count = 0
        pass

    def set_run_params(self, **kwargs):
        val_lengths = {len(v) for v in kwargs.values()}
        assert len(val_lengths) == 1
        val_length = val_lengths.pop()

        for i in range(val_length):
            self.queue.put((i, {k: v[i] for k, v in kwargs.items()}))
            self._total_proc_count += 1
        # simple_logger.info('self._total_proc_count: %s',self._total_proc_count)

        return self

    def __process_func(self, queue, common_list):
        i, kwargs = queue.get()
        result = self.partial_func(**kwargs)
        common_list.append([i, result])

    @staticmethod
    def __join_finished_processes(active_procs, sleep_time):
        while True:
            # simple_logger.info('Process queue is full. Searching for finished processes.')
            for p in active_procs:
                if not p.is_alive():
                    # simple_logger.info('Finished process found. Joining it.')
                    active_procs.remove(p)
                    p.join()
                    # p.terminate()
                    # simple_logger.info('Process successfully removed.')
                    return
            time.sleep(sleep_time)

    def run(self, workers_count=None, sleep_time=1.0):
        workers_count = min(mp.cpu_count() - 1, workers_count or self._total_proc_count)
        manager = mp.Manager()
        common_list = manager.list()
        processes = [mp.Process(target=self.__process_func, args=(self.queue, common_list)) for _ in
                     range(self.queue.qsize())]
        active_procs = list()
        while True:
            # simple_logger.info('loop begins')
            if len(processes) == 0:
                # simple_logger.info('Waiting for the last jobs to finish.')
                for active_p in active_procs:
                    active_p.join()
                break
            if len(active_procs) < workers_count:
                # simple_logger.info('Adding a process')
                proc = processes.pop()
                proc.start()
                active_procs.append(proc)
            else:
                self.__join_finished_processes(active_procs, sleep_time)
            time.sleep(sleep_time)
        return [item[1] for item in sorted(common_list, key=lambda x: x[0])]


def run_shell(*args, non_blocking=False, chdir=None, with_popen=False, ret_triggers=None, **kwargs):
    chdir = chdir or os.getcwd()
    normal_dir = os.getcwd()
    os.chdir(chdir)

    if non_blocking:
        subprocess.Popen(args, stdout=subprocess.PIPE, **kwargs)
    else:
        # output=subprocess.run(args,stdout=subprocess.PIPE,**kwargs).stdout.decode()
        # output=subprocess.run(args,stdout=subprocess.PIPE,**kwargs).stdout.decode()
        if with_popen:
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
            regular_termination = True
            nextline = ''
            while regular_termination:
                nextline = process.stdout.readline().decode()
                # print('nextline:',nextline)
                if nextline == '' and process.poll() is not None:
                    break
                if ret_triggers:
                    for ret_trigger in ret_triggers:
                        if ret_trigger in nextline:
                            regular_termination = False
                            break
                logger.debug(nextline)
                # sys.stdout.write(nextline)
                sys.stdout.flush()
            if regular_termination:
                output = process.communicate()[0]
                exitCode = process.returncode
                if exitCode != 0:
                    raise Exception(args, exitCode, output)
            else:
                logger.info(r'Manual process termination triggered with line:\n%s', nextline)
                logger.debug('Killing process: %s', process.pid)
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                raise Exception('Manual process termination.')
        else:
            subprocess.run(args, stdout=subprocess.PIPE, **kwargs).stdout.decode()
    os.chdir(normal_dir)


def period_within(days=None, start_date=None, end_date=None):
    if isinstance(start_date, str): start_date = dateutil.parser.parse(start_date)
    if isinstance(end_date, str): end_date = dateutil.parser.parse(end_date)
    if days is not None:
        if start_date is not None:
            end_date = start_date + timedelta(days=days)
        elif end_date is not None:
            start_date = end_date - timedelta(days=days)
        else:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
    else:
        end_date = end_date or date.today()
    return start_date, end_date


def datetime_within(start=None, end=None, **timedelta_opts):
    if timedelta_opts:
        if start is not None:
            end = start + timedelta(**timedelta_opts)
        elif end is not None:
            start = end - timedelta(**timedelta_opts)
        else:
            end = datetime.now()
            start = end - timedelta(**timedelta_opts)
    else:
        end = end or datetime.now()
    return start, end


def md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_md5(text):
    return hashlib.md5(str(text).encode('utf-8')).hexdigest()


def run_command(cmd):
    logger.debug('cmd: %s', cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    for c in iter(lambda: process.stdout.read(1), b''):  # replace '' with b'' for Python 3
        sys.stdout.write(c.decode(sys.stdout.encoding, errors='ignore'))


def run_cmd(cmd, debug=False, **kwargs):
    if isinstance(cmd, str):
        steps = [cmd]
    else:
        steps = cmd
    for step in steps:
        if debug: logger.debug('step: %s', step)
        subprocess.run(step, **dict(dict(check=True, shell=True), **kwargs))


def dict_merge(dct, merge_dct, add_keys=True):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param add_keys: add missing keys from merge_dct to dct.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    # for k,v in merge_dct.iteritems():
    # 	if (k in dct and isinstance(dct[k],dict)
    # 			and isinstance(merge_dct[k],collections.Mapping)):
    # 		dict_merge(dct[k],merge_dct[k])
    # 	else:
    # 		dct[k]=merge_dct[k]

    for k, v in merge_dct.items():
        if isinstance(dct.get(k), dict) and isinstance(v, collections.Mapping):
            dct[k] = dict_merge(dct[k], v, add_keys=add_keys)
        else:
            dct[k] = v
    return dct


def get_dist_info(df, dists):
    """
    
    :param df: any object having shape attribute (e.g. pandas Dataframe, numpy array).
    :param dists: the output of from "scipy.spatial.distance.pdist" function.
    :return: pandas Dataframe with ['pair','dist'] columns representing the row indices and distances between them.
    """
    dists_info = pd.DataFrame(zip(it.combinations(range(df.shape[0]), 2), dists), columns=['pair', 'dist'])
    return dists_info
