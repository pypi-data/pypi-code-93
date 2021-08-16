import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed

def multiprocess_cmd(cmds, max_workers=3):
    rtn = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        cmds = list(cmds)
        futures = [executor.submit(subprocess.run, cmd) for cmd in cmds]
        for future in as_completed(futures):
            r = future.result()
            rtn.append(r)
    return rtn

def multiprocess_run(cbfunc, args, max_workers=3):
    rtn = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        args = list(args)
        futures = [executor.submit(cbfunc, *arg) for arg in args]
        for future in as_completed(futures):
            r = future.result()
            rtn.append(r)
    return rtn
