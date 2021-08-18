#!/usr/bin/env python
"""
Synopsis:
    Generate SQLAlchemy model definitions.
    Write to models.py and main.py.
Usage:
    python gen_model.py [options]
Options:
    --no-class-suffixes
            Do not add suffix "_model" to generated class names.
    -a, --artificial-primary-key
            Ensure every table has this key field. 
            If missing, add an autoincremented integer field with this name.
    --no-table-prefixes
            Do not add prefix "table_" to generated table names.
    -h, --help
            Show this help message.
"""


from __future__ import print_function
import sys
import os
import getopt
import importlib
import traceback
from generateDS import cleanupName

try:
    import generatedssuper
except ImportError:
    traceback.print_exc()
    sys.exit(
        '\n* Error.  Cannot import generatedssuper.py.\n'
        'Make sure that the version of generatedssuper.py intended\n'
        'for SQLAlchemy support is first on your PYTHONPATH.\n'
    )
if not hasattr(generatedssuper, 'Generate_DS_Super_SA_'):
    sys.exit(
        '\n* Error.  Not the correct version of generatedssuper.py.\n'
        'Make sure that the version of generatedssuper.py intended\n'
        'for SQLAlchemy support is first on your PYTHONPATH.\n'
    )

try:
    from custom_ds import model_filter
except ImportError:
    from generatedssuper import model_filter

#
# Globals
#

#
# Classes
#


class ProgramOptions(object):
    pass


class Writer(object):
    def __init__(self, outfilename, stdout_also=False):
        self.outfilename = outfilename
        self.outfile = open(outfilename, 'w')
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

    def close(self, verbose=False):
        self.outfile.close()
        if verbose:
            print('Wrote %d lines to %s' % (self.get_count(), self.outfilename))

    def remove(self):
        self.close()
        os.unlink(self.outfilename)


#
# Functions
#

def generate_model(options, module_name, class_names, unique_name_map):

    supermod = importlib.import_module('%slib' % module_name)
    modtypes = importlib.import_module('%stypes' % module_name)
    models_file_name = '%smodel.py' % module_name
    secondary_file_name = 'secondary.py'

    models_writer = Writer(models_file_name)
    secondary_writer = Writer(secondary_file_name)
    wrtmodels = models_writer.write
    wrtsecondary = secondary_writer.write
    wrtmodels('\n')
    wrtmodels('\nfrom modelcommon import DeclarativeBase, metadata, sa')
    wrtmodels('\n')
    wrtmodels('\n\nimport secondary\n\n')
    wrtmodels('\n')

    # super initialization
    generatedssuper.init_(
        supermod, modtypes, options, class_names, unique_name_map)

    for class_name in class_names:
        if hasattr(supermod, class_name):
            cls = getattr(supermod, class_name)
            cls.generate_model_(wrtmodels, wrtsecondary)
        else:
            sys.stderr.write('class %s not defined\n' % (class_name, ))
        wrtmodels('\n')

    for writer in (models_writer, secondary_writer):
        writer.close(verbose=True)

    models = open(models_file_name, 'r').read()
    secondary = open(secondary_file_name, 'r').read()
    os.unlink(secondary_file_name)
    models = models.replace('\nimport secondary\n', secondary, 1)
    open(models_file_name, 'w').write(models)
    return supermod


USAGE_TEXT = __doc__


def usage():
    print(USAGE_TEXT)
    sys.exit(1)

minidom_parser = """
def get_root_tag_minidom(supermod, node):
    tag = supermod.Tag_pattern_.match(node.nodeName).groups()[-1]
    rootClass = supermod.GDSClassesMapping.get(tag)
    if rootClass is None:
        rootClass = globals().get(tag)
    return tag, rootClass

def parseSA_minidom(supermod, models, inFileName, dbsession, silence=False):
    parser = None
    doc = parse(inFileName, parser)
    rootNode = doc.documentElement
    rootTag, rootClass = get_root_tag_minidom(supermod, rootNode)
    if rootClass is None:
        rootTag = cleanupName(rootTag)
        rootClass = getattr(supermod, rootTag, None)
    rootObj = rootClass.factory()
    rootObj.buildSA(rootNode, models, dbsession, not silence)
    # Enable Python to collect the space used by the DOM.
    doc = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='',
            pretty_print=True)
    return rootObj

"""

def main():
    args = sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            args, 'ha:s:', [
                'help', 
                'no-class-suffixes', 
                'artificial-primary-key', 
                'no-table-prefixes', ])
    except:
        usage()
    options = ProgramOptions()
    options.class_suffixes = '_model'
    options.pk_= {'': 'ID'}
    options.table_prefix_='table_'
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--no-class-suffixes':
            options.class_suffixes = ''
        elif opt in ('-a', '--artificial-primary-key'):
            model, pk = val.split(',') if ',' in val else ('', val)
            options.pk_[model] = pk
        elif opt == '--no-table-prefixes':
            options.table_prefix_ = ''

    rargs = range(len(args))
    module_names = [
        cleanupName(os.path.splitext(os.path.split(arg)[1])[0]) for arg in args
    ]

    modelcommon_file_name = 'modelcommon.py'
    main_file_name = 'main.py'
    modelcommon_writer = Writer(modelcommon_file_name)
    main_writer = Writer(main_file_name)
    wrtmodelcommon = modelcommon_writer.write
    wrtmain = main_writer.write

    wrtmodelcommon('\n')
    wrtmodelcommon('\nimport sqlalchemy as sa')
    wrtmodelcommon('\nfrom sqlalchemy.ext.declarative import declarative_base')
    wrtmodelcommon('\n')
    wrtmodelcommon('\nclass_registry = dict()')
    wrtmodelcommon('\nDeclarativeBase = declarative_base(class_registry=class_registry)')
    wrtmodelcommon('\nmetadata = DeclarativeBase.metadata')
    wrtmodelcommon('\n')
    wrtmodelcommon('\nclass ProgramOptions(object):')
    for key, value in vars(options).items():
        wrtmodelcommon('\n    %s = %s' % (key, repr(value)))
    wrtmodelcommon('\noptions = ProgramOptions()')
    wrtmodelcommon('\n')

    module_class_names = list()
    class_names = list()
    all_class_names = list()
    sa_attrs = list()
    for c, module_name in enumerate(module_names):
        supermod = importlib.import_module('%slib' % module_name)
        module_class_names = model_filter(supermod, args[c])
        class_names.append(module_class_names)
        all_class_names += [
            cls['sa_name'] for cls in module_class_names.values() \
            if cls.get('generate', True)
        ]
    unique_name_map = generatedssuper.make_unique_name_map(all_class_names)
    for c, module_name in enumerate(module_names):
        supermod_ = generate_model(
            options, module_name, class_names[c], unique_name_map)
        sa_attrs.append(supermod_.__sa_attrs__)

    wrtmain('\nimport sys')
    wrtmain('\nimport importlib')
    wrtmain('\nfrom generateDS import AnyTypeIdentifier, mapName, cleanupName')
    wrtmain('\nfrom modelcommon import sa, metadata, class_registry, options\n')

    models = ', '.join(['models%d' % c for c in rargs])
    supermods = ', '.join(['supermod%d' % c for c in rargs])
    modelszip = '[%s]' % \
        ', '.join(['(models%d, supermod%d, "%s")' % (
            c, c, args[c]) for c in rargs])
    for c, module_name in enumerate(module_names):
        wrtmain('\nsupermod%d = importlib.import_module("%slib")' % (
            c, module_name))
#        wrtmain('\nsupermod%d.__sa_attrs__ = %s' % (
#            c, repr(sa_attrs[c])))
        wrtmain('\nmodtypes%d = importlib.import_module("%stypes")' % (
            c, module_name))
        wrtmain('\nmodels%d = importlib.import_module("%smodel")' % (
            c, module_name))
#    wrtmain('\nimport %s\n' % models)
    wrtmain('\nimport generatedssuper\n')
    wrtmain('\n')

    wrtmain('\ndef parseSA(supermod, models, inFileName, dbsession, silence=False):')
    wrtmain('\n    parser = None')
    wrtmain('\n    doc = supermod.parsexml_(inFileName, parser)')
    wrtmain('\n    rootNode = doc.getroot()')
    wrtmain('\n    rootTag, rootClass = supermod.get_root_tag(rootNode)')
    wrtmain('\n    if rootClass is None:')
    wrtmain('\n        rootTag = cleanupName(rootTag)')
    wrtmain('\n        rootClass = getattr(supermod, rootTag, None)')
    wrtmain('\n    rootObj = rootClass.factory()')
    wrtmain('\n    rootObj.buildSA(rootNode, models, dbsession, not silence)')
    wrtmain('\n    # Enable Python to collect the space used by the DOM.')
    wrtmain('\n    doc = None')
    wrtmain('\n    if not silence:')
    wrtmain('\n        sys.stdout.write(\'<?xml version="1.0" ?>\')')
    wrtmain('\n        rootObj.export(')
    wrtmain('\n            sys.stdout, 0, name_=rootTag,')
    wrtmain('\n            namespacedef_=\'\',')
    wrtmain('\n            pretty_print=True)')
    wrtmain('\n    return rootObj')
    wrtmain('\n\n')

    wrtmain(minidom_parser)
    
    wrtmain('\n# activate the database engine')
    wrtmain('\ntry:')
    wrtmain('\n    from custom_ds import rdbms')
    wrtmain('\nexcept ImportError:')
    wrtmain("\n    #rdbms = 'sqlite:///:memory:'")
    wrtmain("\n    rdbms = 'sqlite:///test.sqlite'")
    wrtmain('\n')
    wrtmain("\nengine = sa.create_engine(rdbms)")
    wrtmain("\nmetadata.create_all(engine)")
    wrtmain("\nSession = sa.orm.sessionmaker(bind=engine)")
    wrtmain("\ndbsession = Session()")
    wrtmain('\n\n')
    
    for c in rargs:
        wrtmain('\ngeneratedssuper.prepare_(supermod%d, options, %s)\n' % (
            c, repr(sa_attrs[c])))
#        wrtmain('\ngeneratedssuper.init_(supermod%d, modtypes%d, options)\n' % (
#            c, c))

    wrtmain('\nmodelszip = %s\n' % modelszip)
    wrtmain('\ntry:')
    wrtmain('\n    from custom_ds import custom_parser')
    wrtmain('\n    custom_parser(modelszip, class_registry, dbsession, parseSA, options)')
    wrtmain('\nexcept ImportError:')
    wrtmain('\n    for xml in sys.argv[1:]:')
    wrtmain('\n        parseSA(supermod0, class_registry, xml, dbsession, silence=True)')
    wrtmain('\n    dbsession.commit()')
    wrtmain('\n\n')
    
    for writer in (modelcommon_writer, main_writer):
        writer.close(verbose=True)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    #import ipdb; ipdb.set_trace()
    main()
