import asyncio
import inspect
import logging
import os
import pathlib
import threading

import IPython
from prompt_toolkit.shortcuts import PromptSession


class Debugger:
    quitting = True

    def reset(self):
        pass

    def interaction(self, frame, traceback):
        print(os.linesep)
        testname = None
        while traceback.tb_next is not None:
            traceback = traceback.tb_next
            if testname is None:
                if traceback.tb_frame.f_code.co_filename.startswith(os.getcwd()):
                    print(traceback.tb_frame.f_code.co_name)
                    print(os.linesep)
        filename = traceback.tb_frame.f_code.co_filename
        func = traceback.tb_frame.f_code.co_name
        lineno = traceback.tb_lineno
        file_lines = pathlib.Path(filename).read_text().splitlines()
        print(f'> {filename}({lineno}){func}()')
        print(file_lines[lineno - 1])
        print(os.linesep)
        IPython.start_ipython(argv=[], user_ns=traceback.tb_frame.f_locals)


def threaded(func):
    def wrapper(*args, **kwargs):
        result, exceptions = [], []

        def target():
            try:
                result.append(func(*args, **kwargs))
            except BaseException as e:
                exceptions.append(e)

        thread = threading.Thread(target=target)
        thread.start()
        thread.join()
        if exceptions:
            raise exceptions[0]

        return result[0]

    wrapper.threaded = True
    return wrapper


def set_trace():
    logging.getLogger('asyncio').setLevel(logging.ERROR)
    logging.getLogger('parso.python.diff').setLevel(logging.ERROR)
    try:
        try:
            asyncio.get_running_loop()
        except AttributeError:
            asyncio._get_running_loop()
        if getattr(PromptSession.prompt, 'threaded', None) is None:
            PromptSession.prompt = threaded(PromptSession.prompt)
    except RuntimeError:
        pass
    caller = inspect.currentframe().f_back
    ns = dict(caller.f_globals)
    ns.update(caller.f_locals)
    IPython.start_ipython(argv=[], user_ns=ns)
