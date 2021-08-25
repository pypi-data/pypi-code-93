import os
import sys
import time
import json
import datetime
import functools
from concurrent.futures  import ProcessPoolExecutor

def timely_info(green_text, normal_text, adjust=40):
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '\033[92m[INFO]\033[0m', '\033[92m{}\033[0m'.format(green_text).rjust(40, ' '), normal_text)

def get_cpu_count():
    return os.cpu_count()

def parallel_run(func, *iterables, max_workers):

    with ProcessPoolExecutor(max_workers) as executor:
        result = executor.map(func, *iterables)

    return [i for i in result]

def execute_multi_tasks(func, *iterables, parallel):
    if parallel == 0:
        result = []
        for args in zip(*iterables):
            result.append(func(*args))
        return result
    else:
        if parallel == -1:
            max_workers = get_cpu_count()
        else:
            max_workers = parallel
        return parallel_run(func, *iterables, max_workers=max_workers)


def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        print('INFO: All jobs have finished. Total time taken: {:.3f} s'.format(run_time))
        return value
    return wrapper_timer

def stdout_print(msg):
    sys.__stdout__.write(msg + '\n')
    
def redirect_stdout(logfile_path):
    import ROOT
    sys.stdout = open(logfile_path, 'w')
    ROOT.gSystem.RedirectOutput(logfile_path)

def restore_stdout():
    import ROOT
    if sys.stdout != sys.__stdout__:
        sys.stdout.close()
    sys.stdout = sys.__stdout__
    ROOT.gROOT.ProcessLine('gSystem->RedirectOutput(0);')

def redirect_stdout_test(func):
    """Redirect stdout to a log file"""
    import ROOT
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        logfile_path = kwargs.get('logfile_path', None)
        if logfile_path is not None:
            sys.stdout = open(logfile_path, 'w')
            ROOT.gSystem.RedirectOutput(logfile_path)
            value = func(*args, **kwargs)
            sys.stdout.close()
            sys.stdout = sys.__stdout__
            ROOT.gROOT.ProcessLine('gSystem->RedirectOutput(0);')
            return value
        else:
            return func(*args, **kwargs)
    return wrapper_timer

def json_load(fp, *args, **kwargs):
    try:
        data = json.load(fp, *args, **kwargs)
    except:
        raise RuntimeError(f"broken json input: {fp}")
    return data