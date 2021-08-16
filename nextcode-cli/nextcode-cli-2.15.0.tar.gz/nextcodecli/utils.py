#!/usr/bin/env python

import click

import logging

import sys
import json
from jsonpath_rw import parse
import yaml
import dateutil

log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.WARN)

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(console_handler)


def print_error(*txt):
    color_print(*txt, color='red')


def print_warn(*txt):
    color_print(*txt, color='yellow')


def print_success(*txt):
    color_print(*txt, color='green')


def color_print(*args, **kwargs):
    color = kwargs.get('color', 'reset')
    for x in args:
        click.echo(click.style(x, fg=color))


def print_tab(key, val):
    from builtins import str  # py2 backwards compatibility

    val = click.style(str(val), bold=True)
    click.echo("{0:20}{1}".format(key, val))


def print_table(obj):
    try:
        for k, v in obj.items():
            print_tab(k, v)
    except Exception:
        click.echo(obj)


def dumps(obj):
    try:
        return json.dumps(obj, indent=4, sort_keys=True)
    except Exception:
        return repr(obj)


def output_pretty_json(dct, keys):
    ret = ""
    for k in keys:
        jsonpath_expr = parse(k)
        ret = [match.value for match in jsonpath_expr.find(dct)]
        lst = ['']
        if ret:
            if isinstance(ret[0], list) or isinstance(ret[0], dict):
                lst = yaml.dump(ret[0]).split('\n')
            else:
                lst = [str(ret[0])]
        print_tab(k.split('.')[-1], lst[0])
        if len(lst) > 1:
            for v in lst[1:]:
                print_tab("", v)


def get_logger(name='nextcodecli', level=None):
    # TODO - refactor this funtion away - it's useless
    return logging.getLogger(name)


def abort(reason, code=1):
    """
    exit with non-zero exit code and write reason for error to stderr.
    If we are outside a click context and exception will be raised instead
    """
    click.echo(click.style(str(reason), fg='red'), file=sys.stderr)
    ctx_test = click.get_current_context(silent=True)
    if ctx_test:
        sys.exit(code)
    else:
        raise Exception("Abnormal Termination")


def check_profile(ctx):
    if not ctx.obj.client:
        abort(
            "You have no active profile or selected profile is invalid. Run 'nextcode profile add [name]'"
        )


def fmt_date(dt):
    return dateutil.parser.parse(dt).strftime("%Y-%m-%d %H:%M")
