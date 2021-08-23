#!/usr/bin/env python
# coding=utf-8
import os
import sys
import re
import yaml
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__)))
from test_framework.test_pool import TestPool
from test_framework.test_suite import TestSuite
from test_framework.test_case import TestCase
from test_framework.test_environment import Environment
from rest_server.reset_server import *
from rest_server.resource.models.ftp_server import thread_start_ftp_server
from test_framework.database import update_abnormal_end_tests
from test_framework.node_database import update_env_state
from utils.env import get_env_identify_info
from utils.pip_operation import PIPOperation


def add_sub_argument_group(subparsers, name, handler_function):
    regression_parser = subparsers.add_parser(name, help='%s tests executor'%name)
    regression_required_arguments = regression_parser.add_argument_group('required arguments')
    regression_required_arguments.add_argument('--name', '-n', type=str,
                                               help='test suite ,test case name or operation name',default= "fio", required=False)
    regression_required_arguments.add_argument('--variables', '-v', type=str,  default=None,
                                               help='user variables, format: var1:value1,var2:value3', required=False)
    regression_required_arguments.add_argument('--list', '-l', type=str, default=None,
                                               help='list and filter test case', required=False)
    regression_required_arguments.add_argument('--fw', '-f', type=str, default=None,
                                               help='fw path for upgrade', required=False)
    regression_required_arguments.add_argument('--port', '-p', type=str, default="5000",
                                               help='start server port id', required=False)
    regression_parser.set_defaults(executor_function=handler_function)


def create_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_sub_argument_group(subparsers, 'testsuite', test_suite_handle)
    add_sub_argument_group(subparsers, 'testcase', test_case_handle)
    add_sub_argument_group(subparsers, 'start', start_rest_server)
    return parser


def start_rest_server(args):
    if PIPOperation.have_new_version() is False:
        get_env_identify_info()
        _ = TestPool()
        update_abnormal_end_tests()
        thread_start_ftp_server()
        APP.run(host="0.0.0.0", port=args.port)


def test_suite_handle(args):
    test_suite = TestSuite()
    if args.list is not None:
        rets = test_suite.list_and_filter_tests(args.list)
        for item in rets:
            print(item)
    else:
        test_suite.run(args.name)

def test_case_handle(args):
    test_case = TestCase(args.name)
    if args.list is not None:
        rets = test_case.list_and_filter_tests(args.list)
        for item in rets:
            print(item)
    else:
        test_case.run()

def load_global_config():
    config_file = os.path.join(os.getcwd(), 'config.yml')
    if os.path.exists(config_file):
        conf = yaml.load(open(config_file).read(), Loader=yaml.FullLoader)
        for key, val in conf.items():
            os.environ[key] = val


def add_globals(args):
    load_global_config()
    os.environ["root_path"] = os.path.join(os.path.dirname(__file__))
    os.environ["working_path"] = os.getcwd()
    os.environ["PYTHONPATH"] = os.getcwd()
    os.environ['PYTHONUNBUFFERED'] = "TRUE"
    os.environ["prun_port"] = args.port
    if args.variables is not None:
        str_variable = args.variables
        rets = re.findall("(\w+)\:([^\,]+)", str_variable)
        for item in rets:
            os.environ[str(item[0])] = str(item[1])

def run():
    parser = create_parser()
    args = parser.parse_args()
    try:
        add_globals(args)
        args.executor_function(args)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    run()
