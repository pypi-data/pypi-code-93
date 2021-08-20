#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the pylint-ignore project
# https://github.com/mbarkhau/pylint-ignore
#
# Copyright (c) 2020-2021 Manuel Barkhau (mbarkhau@gmail.com) - MIT License
# SPDX-License-Identifier: MIT
"""CLI for pylint-ignore.

This module wraps the pylint runner and supresses individual
messages if configured via a pylint-ignore.md file.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import os
import re
import sys
import shutil
import typing as typ
import getpass
import hashlib
import logging
import datetime as dt
import tempfile
import functools as ft
import subprocess as sp
import multiprocessing as mp
import pathlib2 as pl
try:
    import builtins
except ImportError:
    import __builtin__ as builtins
import pylint.lint
str = getattr(builtins, 'unicode', str)
from . import ignorefile
try:
    import pretty_traceback
    pretty_traceback.install(envvar='ENABLE_PRETTY_TRACEBACK')
except ImportError:
    pass
try:
    from pylint.message.message_handler_mix_in import MessagesHandlerMixIn
except ImportError:
    from pylint.utils import MessagesHandlerMixIn
MessageDef = typ.NamedTuple('MessageDef', [('msg', str), ('msgid', str), (
    'symbol', str), ('scope', str), ('descr', str), ('old_names', typ.List[
    str])])
TESTDEBUG = False


def _pylint_msg_defs(linter, msgid):
    if hasattr(linter.msgs_store, 'get_message_definitions'):
        msg_defs = linter.msgs_store.get_message_definitions(msgid)
        if TESTDEBUG:
            assert isinstance(msg_defs, list)
            assert all(hasattr(m, 'msg') for m in msg_defs)
            assert all(hasattr(m, 'symbol') for m in msg_defs)
        return typ.cast(typ.List[MessageDef], msg_defs)
    elif hasattr(linter.msgs_store, 'get_message_definition'):
        return [linter.msgs_store.get_message_definition(msgid)]
    else:
        return [linter.msgs_store.check_message_id(msgid)]


logger = logging.getLogger('pylint_ignore')
ExitCode = int
USAGE_ERROR = 32
MaybeLineNo = typ.Optional[int]
DEFAULT_IGNOREFILE_PATH = pl.Path('.') / 'pylint-ignore.md'


def _run(cmd):
    cmd_parts = cmd.split()
    try:
        output = sp.check_output(cmd_parts)
    except OSError:
        return ''
    except sp.CalledProcessError:
        return ''
    return output.strip().decode('utf-8')


_HG_USERNAME_CMD = 'hg config ui.username'


def get_author_name():
    """Do a best effort to get a meaningful author name."""
    hg_username = _run(_HG_USERNAME_CMD)
    git_email = _run('git config user.email')
    git_name = _run('git config user.name')
    if git_email and '<' in git_email and '>' in git_email:
        git_username = git_email
    elif git_name and git_email:
        git_username = git_name + ' <' + git_email + '>'
    elif git_name:
        git_username = git_name
    elif git_email:
        git_username = git_email
    else:
        git_username = ''
    is_hg_repo = pl.Path('.hg').exists()
    is_git_repo = pl.Path('.git').exists()
    if is_hg_repo and hg_username:
        return hg_username
    if is_git_repo and git_username:
        return git_username
    if hg_username:
        return hg_username
    if git_username:
        return git_username
    return getpass.getuser()


IS_FORK_METHOD_AVAILABLE = sys.platform != 'win32'


class PylintIgnoreDecorator(object):
    ignorefile_path = None
    is_update_mode = None
    pylint_run_args = None
    default_author = None
    default_date = None
    old_catalog = None
    new_catalog_dir = None
    _pylint_is_message_enabled = None
    _pylint_add_message = None
    _last_added_msgid = None
    _cur_msg_args = None

    def __init__(self, args):
        self.ignorefile_path = DEFAULT_IGNOREFILE_PATH
        self.is_update_mode = False
        self.pylint_run_args = []
        self._init_from_args(args)
        self.old_catalog = ignorefile.load(self.ignorefile_path)
        if self.is_update_mode:
            self.new_catalog_dir = pl.Path(tempfile.mkdtemp())
        else:
            self.new_catalog_dir = pl.Path(tempfile.gettempdir())
        self.default_author = get_author_name()
        self.default_date = dt.datetime.now().isoformat().split('.')[0]
        self._last_added_msgid = None
        self._cur_msg_args = []

    def _init_from_args(self, args):
        arg_i = 0
        while arg_i < len(args):
            arg = args[arg_i]
            if arg == '--update-ignorefile':
                self.is_update_mode = True
            elif arg == '--ignorefile':
                self.ignorefile_path = pl.Path(args[arg_i + 1])
                arg_i += 1
            elif arg.startswith('--ignorefile='):
                self.ignorefile_path = pl.Path(arg.split('=', 1)[-1])
            else:
                is_jobs_arg = arg.startswith('--jobs') or arg.startswith('-j')
                if is_jobs_arg and not IS_FORK_METHOD_AVAILABLE:
                    if '=' not in arg:
                        arg_i += 1
                else:
                    self.pylint_run_args.append(arg)
            arg_i += 1
        if not IS_FORK_METHOD_AVAILABLE:
            self.pylint_run_args.insert(0, '--jobs=1')
        if not self.ignorefile_path.exists() and not self.is_update_mode:
            sys.stderr.write('Invalid path, does not exist: {0}\n'.format(
                self.ignorefile_path))
            raise SystemExit(USAGE_ERROR)

    def _new_entry(self, key, old_entry, msg_text, msg_extra, srctxt):
        if old_entry:
            author = old_entry.author
            date = old_entry.date
        else:
            author = self.default_author
            date = self.default_date
        return ignorefile.Entry(key.msgid, key.path, key.symbol, msg_text,
            msg_extra, author, date, srctxt)

    def _dump_entry(self, entry):
        if not self.is_update_mode:
            return
        entry_text = ignorefile.dumps_entry(entry)
        catalog_file = self.new_catalog_dir / '{0}.md'.format(os.getpid())
        with catalog_file.open(mode='a', encoding='utf-8') as fobj:
            fobj.write(entry_text)

    def cleanup(self):
        assert self.new_catalog_dir != pl.Path(tempfile.gettempdir())
        shutil.rmtree(str(self.new_catalog_dir))

    def is_enabled_entry(self, msgid, path, symbol, msg_text, msg_extra, srctxt
        ):
        """Return false if message is in the serialized catalog.

        Side effect: Track new entries for serialization.
        """
        pwd = pl.Path('.').absolute()
        rel_path = str(pl.Path(path).absolute().relative_to(pwd).as_posix())
        if srctxt:
            source_line = srctxt.source_line
        else:
            source_line = hashlib.sha1(msg_extra.strip().encode('utf-8')
                ).hexdigest()
        key = ignorefile.Key(msgid, rel_path, symbol, msg_text, source_line)
        old_entry = ignorefile.find_entry(self.old_catalog, key)
        new_entry = self._new_entry(key, old_entry, msg_text, msg_extra, srctxt
            )
        self._dump_entry(new_entry)
        is_ignored = old_entry is not None or self.is_update_mode
        return not is_ignored

    def _fmt_msg(self, msg_def):
        if len(self._cur_msg_args) >= msg_def.msg.count('%'):
            msg_text = msg_def.msg % tuple(self._cur_msg_args)
        else:
            msg_text = msg_def.msg
        if '\n' in msg_text:
            msg_text_parts = msg_text.split('\n', 1)
            msg_text = msg_text_parts[0]
            msg_extra = msg_text_parts[1].strip()
        else:
            msg_extra = ''
        return msg_text, msg_extra

    def _add_message_wrapper(self):

        @ft.wraps(self._pylint_add_message)
        def add_message(linter, msgid, line=None, node=None, args=None,
            confidence=None, col_offset=None):
            self._last_added_msgid = msgid
            del self._cur_msg_args[:]
            if isinstance(args, tuple):
                self._cur_msg_args.extend(args)
            elif isinstance(args, (bytes, str)):
                self._cur_msg_args.append(args)
            if col_offset is None:
                self._pylint_add_message(linter, msgid, line, node, args,
                    confidence)
            else:
                self._pylint_add_message(linter, msgid, line, node, args,
                    confidence, col_offset)
        return add_message

    def _is_message_enabled_wrapper(self):

        def is_any_message_def_enabled(linter, msgid, line):
            srctxt = ignorefile.read_source_text(linter.current_file, line,
                line) if line else None
            for msg_def in _pylint_msg_defs(linter, msgid):
                msg_text, msg_extra = self._fmt_msg(msg_def)
                assert not (msg_extra and srctxt)
                _is_enabled = self.is_enabled_entry(msgid, linter.
                    current_file, msg_def.symbol, msg_text, msg_extra, srctxt)
                if not _is_enabled:
                    return False
            return True

        @ft.wraps(self._pylint_is_message_enabled)
        def is_message_enabled(linter, msg_descr, line=None, confidence=None):
            try:
                is_enabled = self._pylint_is_message_enabled(linter,
                    msg_descr, line, confidence)
                last_msgid = self._last_added_msgid
                if last_msgid is None:
                    return bool(is_enabled)
                if not is_enabled:
                    return False
                is_always_enabled = re.match('\\w\\d{1,5}', msg_descr) is None
                if is_always_enabled:
                    return True
                return is_any_message_def_enabled(linter, msg_descr, line)
            finally:
                self._last_added_msgid = None
                del self._cur_msg_args[:]
        return is_message_enabled

    def monkey_patch_pylint(self):
        self._pylint_is_message_enabled = (MessagesHandlerMixIn.
            is_message_enabled)
        self._pylint_add_message = MessagesHandlerMixIn.add_message
        MessagesHandlerMixIn.is_message_enabled = (self.
            _is_message_enabled_wrapper())
        MessagesHandlerMixIn.add_message = self._add_message_wrapper()

    def monkey_unpatch_pylint(self):
        if MessagesHandlerMixIn is None:
            return
        MessagesHandlerMixIn.is_message_enabled = (self.
            _pylint_is_message_enabled)
        MessagesHandlerMixIn.add_message = self._pylint_add_message


def main(args=sys.argv[1:]):
    is_fork_method_setable = IS_FORK_METHOD_AVAILABLE and hasattr(mp,
        'get_start_method') and mp.get_start_method(allow_none=True) is None
    if is_fork_method_setable:
        mp.set_start_method('fork')
    exit_code = 1
    dec = PylintIgnoreDecorator(args)
    try:
        dec.monkey_patch_pylint()
        try:
            pylint.lint.Run(dec.pylint_run_args)
            exit_code = 0
        except SystemExit as sysexit:
            exit_code = sysexit.code
        except KeyboardInterrupt:
            return 1
    finally:
        dec.monkey_unpatch_pylint()
    if dec.is_update_mode:
        try:
            new_catalog = ignorefile.load_dir(dec.new_catalog_dir)
            is_catalog_dirty = dec.old_catalog != new_catalog
            if is_catalog_dirty:
                ignorefile.dump(new_catalog, dec.ignorefile_path)
        finally:
            dec.cleanup()
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
