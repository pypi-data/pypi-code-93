#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Synopsis:
    Generate SQLAlchemy models.py from XML schema.
Usage:
    python gends_run_gen_sa.py [options] <schema_file>
Options:
    -h, --help      Display this help message.
    -f, --force     Overwrite the following files without asking:
                        <schema>lib.py
                        <schema>types.py
                        models*.py
                        modelcommon.py
                        main.py
    -p, --path-to-generateDS-script=/path/to/generateDS.py
                    Path to the generateDS.py script.
    -v, --verbose   Display additional information while running.
    -s, --script    Write out (display) the command lines used.  Can
                    be captured and used in a shell script, for example.
    --no-class-suffixes
                    Do not add suffix "_model" to
                    generated class names.
    -a, --artificial-primary-key
                    The field name that will serve the primary key for 
                    the models (the classes that are mapping to tables).
                    multiple occurences are allowed, each containing 
                    either a field name (for all models, default is ID), 
                    or a pair model,field, with the primary key field for 
                    the specified model.
Examples:
    python gends_run_gen_sa.py my_schema.xsd my_other_schema.xsd
    python gends_run_gen_sa.py -f -p ../generateDS.py my_other_schema.xsd

"""


#
# Imports

import sys
import getopt
import os
from subprocess import Popen, PIPE
from glob import glob
from generateDS import cleanupName


#
# Globals and constants


#
# Functions for external use


#
# Classes

class GenerateSQLAlchemyError(Exception):
    pass


#
# Functions for internal use and testing

def generate(options, schema_file_names):
    for schema_file_name in schema_file_names:
        schema_name_stem = cleanupName(
            os.path.splitext(os.path.split(schema_file_name)[1])[0])
        bindings_file_name = '%slib.py' % (schema_name_stem, )
        types_file_name = '%stypes.py' % (schema_name_stem, )
        model_file_name = '%smodel.py' % (schema_name_stem, )
    
        modelcommon_file_name = 'modelcommon.py'
        main_file_name = 'main.py'

        file_names = [
            model_file_name, 
            modelcommon_file_name, 
            main_file_name, 
        ]

        dbg_msg(options, 'schema_name_stem: %s\n' % (schema_name_stem, ))
        dbg_msg(options, 'bindings_file_name: %s\n' % (bindings_file_name, ))
        dbg_msg(options, 'types_file_name: %s\n' % (types_file_name, ))

        if options['force']:
            for file_name in (bindings_file_name, types_file_name):
                file_stem = os.path.splitext(file_name)[0]
                file_names += (
                    glob(file_name) + 
                    glob('%s.pyc' % file_stem) + 
                    glob('__pycache__/%s.*.pyc' % file_stem)
                )
            for file_name in file_names:
                if not os.path.exists(file_name):
                    continue
                dbg_msg(options, 'removing: %s\n' % file_name)
                os.remove(file_name)
        else:
            for file_name in file_names:
                if exists(file_name):
                    return
    
        args = (
            options['path'],
            '-f',
            '-o', '%s' % (bindings_file_name, ),
            '--member-specs=list',
            "--external-encoding=utf-8",
            schema_file_name,
        )
        if not run_cmd(options, args):
            return
        args = (
            './gends_extract_simple_types.py', '-f',
            '--outfile', types_file_name, 
            schema_file_name,
        )
        if not run_cmd(options, args):
            return
    
    args = [
        './gends_generate_sa.py', 
    ]
    if not options['class_suffixes']:
        args.append('--no-class-suffixes')
    for val in options['artificial-primary-key']:
        args.append('-a')
        args.append(val)
    if not run_cmd(options, args + schema_file_names):
        return


def run_cmd(options, args):
    msg = '%s\n' % (' '.join(args), )
    dbg_msg(options, '*** running %s' % (msg, ))
    if options['script']:
        write_msg(options, msg)
    process = Popen(args, stderr=PIPE, stdout=PIPE)
    content1 = process.stderr.read()
    content2 = process.stdout.read()
    if content1:
        sys.stderr.write('*** error ***\n')
        sys.stderr.write(content1.decode('utf-8'))
        sys.stderr.write('*** error ***\n')
    if content2:
        dbg_msg(options, '*** message ***\n')
        dbg_msg(options, content2.decode('utf-8'))
        dbg_msg(options, '*** message ***\n')
    return True


def exists(file_name):
    if os.path.exists(file_name):
        msg = 'File %s exists.  Use -f/--force to overwrite.\n' % (file_name, )
        sys.stderr.write(msg)
        return True
    return False


def dbg_msg(options, msg):
    if options['verbose']:
        if isinstance(msg, str):
            sys.stdout.write(msg)
        else:
            sys.stdout.write(msg.decode('utf-8'))


def write_msg(options, msg):
    if isinstance(msg, str):
        sys.stdout.write(msg)
    else:
        sys.stdout.write(msg.decode('utf-8'))


def usage():
    sys.exit(__doc__)


def main():
    args = sys.argv[1:]
    try:
        opts, args = getopt.getopt(args, 'hvfp:a:s', [
            'help', 'verbose', 'script',
            'force', 'path-to-generateDS-script=',
            'no-class-suffixes', 'artificial-primary-key=', 
        ])
    except:
        usage()
    options = {}
    options['force'] = False
    options['verbose'] = False
    options['script'] = False
    options['path'] = './generateDS.py'
    options['class_suffixes'] = True
    options['artificial-primary-key'] = list()
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-f', '--force'):
            options['force'] = True
        elif opt in ('-v', '--verbose'):
            options['verbose'] = True
        elif opt in ('-s', '--script'):
            options['script'] = True
        elif opt in ('-p', '--path-to-generateDS-script'):
            options['path'] = val
        elif opt in ('-a', '--artificial-primary-key'):
            options['artificial-primary-key'].append(val)
        elif opt == '--no-class-suffixes':
            options['class_suffixes'] = False
    if not os.path.exists(options['path']):
        sys.exit(
            '\n*** error: Cannot find generateDS.py.  '
            'Use "-p path" command line option.\n')
    generate(options, args)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    #import ipdb; ipdb.set_trace()
    main()
