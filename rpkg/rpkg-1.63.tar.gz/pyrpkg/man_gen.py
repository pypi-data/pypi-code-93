# Print a man page from the help texts.
#
# Copyright (C) 2011 Red Hat Inc.
# Author(s): Jesse Keating <jkeating@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.


import datetime
import os
import sys

# We could substitute the "" in .TH with the rpkg version if we knew it
man_header = """\
.\\" man page for %(identity)s
.TH %(identity)s 1 "%(today)s" "" "rpm\\-packager"
.SH "NAME"
%(identity)s \\- RPM Packaging utility
.SH "SYNOPSIS"
.B "%(identity)s"
[
.I global_options
]
.I "command"
[
.I command_options
]
[
.I command_arguments
]
.br
.B "%(identity)s"
.B "help"
.br
.B "%(identity)s"
.I "command"
.B "\\-\\-help"
.SH "DESCRIPTION"
.B "%(identity)s"
is a script to interact with the RPM Packaging system.
"""

man_footer = """\
.SH "SEE ALSO"
.UR "%(sourceurl)s"
.BR "%(sourceurl)s"
"""


class ManFormatter(object):

    def __init__(self, man, identity, sourceurl):
        self.man = man
        self.identity = identity
        self.sourceurl = sourceurl

    def write(self, data):
        for line in data.split('\n'):
            self.man.write('  %s\n' % line)

    @property
    def constants(self):
        """Global constants for man file templates"""
        today = datetime.date.today()
        today_manstr = today.strftime(r'%Y\-%m\-%d')
        return {'today': today_manstr,
                'identity': self.identity,
                'sourceurl': self.sourceurl}


def strip_usage(s):
    """Strip "usage: " string from beginning of string if present"""
    if s.startswith('usage: '):
        return s.replace('usage: ', '', 1)
    else:
        return s


def generate(parser, subparsers, identity, sourceurl):
    """\
    Generate the man page on stdout

    Given the argparse based parser and subparsers arguments, generate
    the corresponding man page and write it to stdout.
    """

    # Not nice, but works: Redirect any print statement output to
    # stderr to avoid clobbering the man page output on stdout.
    man_file = sys.stdout
    sys.stdout = sys.stderr

    # default argparse help width is 80 chars and man indent help text
    # by 10 chars => 80+10 > 80(default terminal width). New help width must be
    # 70 to fit in terminal
    # argparse get columns value from enviroment variable
    os.environ['COLUMNS'] = '70'

    mf = ManFormatter(man_file, identity, sourceurl)

    choices = subparsers.choices
    k = sorted(choices.keys())

    man_file.write(man_header % mf.constants)

    helptext = parser.format_help()
    helptext = strip_usage(helptext)
    helptextsplit = helptext.split('\n')
    helptextsplit = [line for line in helptextsplit
                     if not line.startswith('  -h, --help')]

    man_file.write('.SS "%s"\n' % ("Global Options",))

    outflag = False
    for line in helptextsplit:
        if line == "optional arguments:":
            outflag = True
        elif line == "":
            outflag = False
        elif outflag:
            man_file.write("%s\n" % line)

    help_texts = {}
    for pa in subparsers._choices_actions:
        help_texts[pa.dest] = getattr(pa, 'help', None)

    man_file.write('.SH "COMMAND OVERVIEW"\n')

    for command in k:
        cmdparser = choices[command]
        if not cmdparser.add_help:
            continue
        usage = cmdparser.format_usage()
        usage = strip_usage(usage)
        usage = ''.join(usage.split('\n'))
        usage = ' '.join(usage.split())
        if help_texts[command]:
            man_file.write('.TP\n.B "%s"\n%s\n' % (usage, help_texts[command]))
        else:
            man_file.write('.TP\n.B "%s"\n' % (usage))

    man_file.write('.SH "COMMAND REFERENCE"\n')
    for command in k:
        cmdparser = choices[command]
        if not cmdparser.add_help:
            continue

        man_file.write('.SS "%s"\n' % cmdparser.prog)

        help = help_texts[command]
        if help and not cmdparser.description:
            if not help.endswith('.'):
                help = "%s." % help
            cmdparser.description = help

        h = cmdparser.format_help()
        mf.write(h)

    man_file.write(man_footer % mf.constants)
