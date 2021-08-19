#!/usr/bin/env python

import sys
import os
import argparse
import yaml

from npu_compiler import VERSION
from npu_compiler.v100.config import Config as Config_1_0
import npu_compiler.v100.compiler as compiler_1_0
from npu_compiler.v150.config import Config as Config_1_5
import npu_compiler.v150.compiler as compiler_1_5
from npu_compiler.v160.config import Config as Config_1_6
import npu_compiler.v160.compiler as compiler_1_6

def get_config_from_file(config_file):
    if isinstance(config_file, str):
        # input from yaml file
        try:
            with open(config_file) as f:
                config_dict = yaml.safe_load(f)
                config_dir = os.path.dirname(config_file)
        except IOError:
            print("[ERROR] can't open config file: \"%s\"" % config_file)
            sys.exit(1)
    else:
        # input from stdin, e.g. `cat xxx.yaml|gxnpuc`
        config_dict = yaml.safe_load(sys.stdin)
        config_dir = ""
    return config_dir, config_dict

def get_config_from_cmd(config_str):
    config_dict = yaml.safe_load(config_str)
    config_dir = ""
    return config_dir, config_dict

def load_1_0(config_dict, config_para):
    Config_1_0.load_config(config_dict, config_para)

def load_1_5(config_dict, config_para):
    Config_1_5.load_config(config_dict, config_para)

def load_1_6(config_dict, config_para):
    Config_1_6.load_config(config_dict, config_para)

def run_1_0():
    compiler_1_0.run()

def run_1_5():
    compiler_1_5.run()

def run_1_6():
    compiler_1_6.run()

COREMAP = {
    "LEO": {"load": load_1_0, "run":run_1_0},
    "GRUS": {"load": load_1_5, "run":run_1_5},
    "AQUILA": {"load": load_1_6, "run":run_1_6},
    "V100": {"load": load_1_0, "run":run_1_0},
    "V150": {"load": load_1_5, "run":run_1_5},
    "V160": {"load": load_1_6, "run":run_1_6},
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="gxnpuc", description="NPU Compiler")
    parser.add_argument("-V", "--version", action="version", version="gxnpuc %s" % VERSION)
    parser.add_argument("-L", "--list", action="store_true", help="list supported ops")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbosely list the processed ops")
    parser.add_argument("-m", "--meminfo", action="store_true", help="verbosely list memory info of ops")
    parser.add_argument("-c", "--cmd", nargs="+", help="use command line configuration")
    parser.add_argument("-w", "--weights", action="store_true", help="print compressed weights(GRUS only)")
    parser.add_argument("config_filename", nargs="?", default=sys.stdin, help="config file")
    args = parser.parse_args()
    if args.list:
        from npu_compiler.v100.ops import OpsFactory as OpsFactory_1_0
        from npu_compiler.v150.ops import OpsFactory as OpsFactory_1_5
        print(OpsFactory_1_0.get_tf_ops_note())
        print(OpsFactory_1_5.get_tf_ops_note())
        sys.exit(0)
    if args.cmd:
        config_dir, config_dict = get_config_from_cmd(args.cmd[0])
    elif args.config_filename:
        config_dir, config_dict = get_config_from_file(args.config_filename)
    else:
        parser.print_help()
        sys.exit(0)

    config_para = {"VERBOSE": args.verbose, "MEMINFO": args.meminfo, "PRINT_WEIGHTS": args.weights,\
            "CONFIG_DIR": config_dir}
    corename = config_dict.get("CORENAME", "")
    core_funcs = COREMAP.get(corename, {})
    if not core_funcs:
        print("CORENAME not supported!")
        sys.exit(1)

    core_funcs.get("load")(config_dict, config_para)
    core_funcs.get("run")()
