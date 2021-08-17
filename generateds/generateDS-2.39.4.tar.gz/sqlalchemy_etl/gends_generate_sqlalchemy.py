#!/usr/bin/env python
"""
Synopsis:
    Generate SQLAlchemy model and form definitions.
    Write to sa_models.py.
Usage:
    python gen_model.py [options]
Options:
    -f, --force
            Overwrite sa_models.py without asking.
    --no-class-suffixes
            Do not add suffix "_model" and _form" to generated class names.
    -h, --help
            Show this help message.
"""


from __future__ import print_function
import sys
import os
import getopt
import importlib
import traceback
from generatedssuper import Simple_type_table
# from generatedssuper import \
#     Simple_type_table, \
#     Integer_type_table, \
#     Float_type_table, \
#     String_type_table, \
#     Date_type_table, \
#     DateTime_type_table, \
#     Time_type_table, \
#     Boolean_type_table

from generateds_definedsimpletypes import Defined_simple_type_table


#path = "D:/projects/opendata/generateDS-2.29.14"
#sys.path.append(str(path))

from generateDS import AnyTypeIdentifier, mapName, cleanupName


#
# Globals
#

supermod = None

#
# Classes
#


class ProgramOptions(object):
    def get_force_(self):
        return self.force_

    def set_force_(self, force):
        self.force_ = force
    force = property(get_force_, set_force_)


class Writer(object):
    def __init__(self, outfilename, stdout_also=False):
        self.outfilename = outfilename
        self.outfile = open(outfilename, 'w', encoding='utf-8')
        self.stdout_also = stdout_also
        self.line_count = 0

    def get_count(self):
        return self.line_count

    def write(self, content):
        self.outfile.write(content)
        if self.stdout_also:
            sys.stdout.write(content)
        count = content.count('\n')
        self.line_count += count

    def close(self):
        self.outfile.close()


#
# Functions
#

def generate_model(options, module_name):
    global supermod
#     if options.class_suffixes:
#         model_suffix = '_model'
#     else:
#         model_suffix = ''
    try:
        import generatedssuper
    except ImportError:
        traceback.print_exc()
        sys.exit(
            '\n* Error.  Cannot import generatedssuper.py.\n'
            'Make sure that the version of generatedssuper.py intended\n'
            'for sqlalchemy support is first on your PYTHONPATH.\n'
        )
    if not hasattr(generatedssuper, 'Generate_DS_Super_Marker_'):
        sys.exit(
            '\n* Error.  Not the correct version of generatedssuper.py.\n'
            'Make sure that the version of generatedssuper.py intended\n'
            'for sqlalchemy support is first on your PYTHONPATH.\n'
        )
    supermod = importlib.import_module(module_name)
    models_file_name = 'models_sqa.py'
    if (
            (
                os.path.exists(models_file_name)
            ) and
            not options.force):
        sys.stderr.write(
            '\n{} exists.  '
            'Use -f/--force to overwrite.\n\n'.format(
                models_file_name))
        sys.exit(1)
    models_writer = Writer(models_file_name)
    wrtmodels = models_writer.write
    unique_name_map = make_unique_name_map(supermod.__all__)

    #backrefs_map = make_backrefs_map(supermod, unique_name_map)
    simpletypes_set = make_simpletypes_set(supermod)

    wrtmodels('from sqlalchemy.orm import relationship\n')
    wrtmodels('from sqlalchemy.ext.declarative import declarative_base\n')
    write_simpletypes_imports(wrtmodels, simpletypes_set)
    wrtmodels('\nBase = declarative_base()\n')
    wrtmodels('\n')

    # generate models for all classes definde in module 'module_name'
    for class_name in supermod.__all__:
        if hasattr(supermod, class_name):
            cls = getattr(supermod, class_name)
            cls.generate_sa_model_(
                wrtmodels,
                unique_name_map,
                #backrefs_map,
                options.class_suffixes)
        else:
            sys.stderr.write('class %s not defined\n' % (class_name, ))

    models_writer.close()
    print('Wrote %d lines to models_sa.py' % (models_writer.get_count(), ))


def write_simpletypes_imports(wrtmodels, simpletypes_set):
    """write simple types imports from sqlalchemy to model"""
    wrtmodels('from sqlalchemy import Table, Column, MetaData, ForeignKey, ')

    types_string = ''
    for simpletype in simpletypes_set:
        types_string = '%s%s, ' % (types_string, simpletype)
    if types_string:
        types_string = types_string[:-2]
    wrtmodels(types_string)
    wrtmodels('\n')
    return


def make_unique_name_map(name_list):
    """Make a mapping from names to names that are unique ignoring case."""
    unique_name_table = {}
    unique_name_set = set()
    for name in name_list:
        make_unique_name(name, unique_name_table, unique_name_set)
    return unique_name_table


def make_unique_name(name, unique_name_table, unique_name_set):
    """Create a name that is unique even when we ignore case."""
    new_name = name
    lower_name = new_name.lower()
    count = 0
    while lower_name in unique_name_set:
        count += 1
        new_name = '{}_{:d}'.format(name, count)
        lower_name = new_name.lower()
    unique_name_table[name] = new_name
    unique_name_set.add(lower_name)


#def make_backref(backrefs_table, class_name, super_name):
#    """make single back reference for foreign relationships"""
#    super_backrefs = None
#    if super_name in backrefs_table:
#        super_backrefs = backrefs_table[super_name]
#    if super_backrefs is None:
#        super_backrefs = {}
#        backrefs_table[super_name] = super_backrefs
#    super_backrefs[class_name] = super_name
#    return


#def make_backrefs_for_fields(cls, backrefs_table, unique_name_map):
#    """make back references for foreign relationships for whole class"""
#    class_name = unique_name_map.get(cls.__name__)
#    for spec in cls.member_data_items_:
#        name = spec.get_name()
#        prefix, name = cls.get_prefix_name(name)
#        data_type = spec.get_data_type()
#        prefix, data_type = cls.get_prefix_name(data_type)
#        if data_type in Defined_simple_type_table:
#            data_type = Defined_simple_type_table[data_type]
#            prefix, data_type = cls.get_prefix_name(data_type.type_name)
#        name = mapName(cleanupName(name))
#        if name == 'id':
#            name += 'x'
#        elif name.endswith('_') and not name == AnyTypeIdentifier:
#            name += 'x'
#        clean_data_type = mapName(cleanupName(data_type))
#        if data_type == AnyTypeIdentifier:
#            data_type = 'string'
#        if data_type not in Simple_type_table:
#                mapped_type = unique_name_map.get(clean_data_type)
#                if mapped_type is not None:
#                    clean_data_type = mapped_type
#                make_backref(backrefs_table, class_name, clean_data_type,)


#def make_backrefs_map(supermod, unique_name_map):
#    """make back references maps for foreign relationships for all classes"""
#    backrefs_table = {}
#
#    for name in supermod.__all__:
#        if hasattr(supermod, name):
#            cls = getattr(supermod, name)
#            class_name = unique_name_map.get(name)
#
#            super_name = ''
#            if cls.superclass is not None:
#                super_name = unique_name_map.get(cls.superclass.__name__)
#
#            make_backref(backrefs_table, class_name, super_name)
#            make_backrefs_for_fields(cls, backrefs_table, unique_name_map)
#
#    return backrefs_table


def add_simpletypes_for_members(cls, simpletypes_set):
    """extract information about simple types from class members"""
    for spec in cls.member_data_items_:
        name = spec.get_name()
        prefix, name = cls.get_prefix_name(name)
        data_type = spec.get_data_type()
        prefix, data_type = cls.get_prefix_name(data_type)
        if data_type in Defined_simple_type_table:
            data_type = Defined_simple_type_table[data_type]
            prefix, data_type = cls.get_prefix_name(data_type.type_name)
        name = mapName(cleanupName(name))
        if name == 'id':
            name += 'x'
        elif name.endswith('_') and not name == AnyTypeIdentifier:
            name += 'x'
        #clean_data_type = mapName(cleanupName(data_type))
        if data_type == AnyTypeIdentifier:
            data_type = 'string'
        if data_type in Simple_type_table:
            simpletypes_set.add(Simple_type_table[data_type])
    return


def make_simpletypes_set(supermod):
    """make simple types set to import from sqlalchemy"""
    simpletypes_set = set()
    for name in supermod.__all__:
        if hasattr(supermod, name):
            cls = getattr(supermod, name)
            add_simpletypes_for_members(cls, simpletypes_set)
    return simpletypes_set


USAGE_TEXT = __doc__


def usage():
    print(USAGE_TEXT)
    sys.exit(1)


def main():
    args = sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            args, 'hfs:', [
                'help', 'force',
                'no-class-suffixes', ])
    except getopt.GetoptError:
        usage()
    options = ProgramOptions()
    options.force = False
    options.class_suffixes = True
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-f', '--force'):
            options.force = True
        elif opt == '--no-class-suffixes':
            options.class_suffixes = False
    if len(args) != 1:
        usage()
    module_name = args[0]
    generate_model(options, module_name)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    #import ipdb; ipdb.set_trace()
    main()
