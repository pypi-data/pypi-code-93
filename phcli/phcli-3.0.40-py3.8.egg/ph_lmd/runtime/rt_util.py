# -*- coding: utf-8 -*-

from phcli.ph_errs.ph_err import PhException
from phcli.ph_lmd.runtime import python_rt
from phcli.ph_lmd.runtime import nodejs_rt
from phcli.ph_lmd.runtime import go_rt


def get_short_rt(runtime):
    if "python" in runtime:
        return "python"
    elif "nodejs" in runtime:
        return "nodejs"
    elif "go" in runtime:
        return "go"
    raise PhException("Invalid runtime")


def get_rt_inst(runtime):
    rt_table = {
        'python': python_rt.PythonRT,
        'nodejs': nodejs_rt.NodejsRT,
        'go': go_rt.GoRT,
    }

    rt = rt_table[get_short_rt(runtime)]
    return rt()
