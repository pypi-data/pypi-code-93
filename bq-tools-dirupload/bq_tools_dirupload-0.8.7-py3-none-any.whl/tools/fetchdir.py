#!/usr/bin/env python
#from __future__ import unicode_literals
#from __future__ import print_function
#from builtins import input
#from builtins import range
#from future import standard_library
#standard_library.install_aliases()

import os
import sys
import re
import csv
import fnmatch
import argparse
import logging
import random
import string
import time
import traceback
import posixpath
import copy
from itertools import zip_longest
from collections import OrderedDict

from lxml import etree

import bqapi
from . pool import ProcessManager


def fetch_image(session, args, root, uniq):
    """Send one image to bisque


    :param session: A requests session
    :param args:  an argparse argument object (for flags)
    :param image_path: The path of the file to be uploaded
    :param tagmap:   map for replacing values
                       { 'context-key' : { 'value': 'mapped value' , ... }   # map for specific context
                                           ''            : { 'value': 'mapped value' , ... }   # every context
                       }
    :param a list of fixed tags to be added based on a key fields
                      { context-ley : { 'tag': 'value', ... }

    """
    #args.log.debug ("preping tags %s %s %s %s", root, image_path,   tagmap.keys(), fixedtags.keys())
    # Strip off top level dirs .. except user given root
    #args.log.info ("Fetching %s", uri)
    data_service = session.service("data_service")
    blob_service = session.service('blob_service')

    file_xml = data_service.fetch(path=uniq, render='xml')
    args.log.debug ("Fetched %s", etree.tostring(file_xml))
    if file_xml.tag in ('image', 'file', 'table'):
        outfile = os.path.join (root, file_xml.get('name'))
        if not args.dry_run :
            blob_service.fetch_file (path = uniq,  localpath=outfile)
            args.log.info("Fetched %s to %s", uniq, outfile)
        else:
            args.log.info("Would fetch  %s to %s", uniq, outfile)
    else:
        args.log.warn("Skipping %s resource", file_xml.tag)
    return True


SUCCESS=[]
ERROR = []
SKIPPED = []
UNIQS = []

def append_result_list (request):
    SUCCESS.append (request)
#    resource = request['return_value']
#    UNIQS.append (resource[0].get ('resource_uniq'))


def append_error_list (request):
    ERROR.append (request)
#    if request.get ('return_value') is None:
#        SKIPPED.append (request)
#        return
#    args = request['args'][1]
#    if request.get ('return_value'):
#        args.log.error ("return value %s", etree.tostring (request['return_value'], encoding='unicode'))



DEFAULT_CONFIG='~/bisque/config' if os.name == 'nt' else "~/.bisque/config"



DOC_EPILOG="""
bq-dirfetch -n  --threads 1 dataset_uri



"""



def main():
    parser = bqapi.cmd.bisque_argument_parser ("Fetch files from bisque", formatter_class=argparse.RawDescriptionHelpFormatter, epilog = DOC_EPILOG)
    parser.add_argument('--threads', help='set number of uploader threads', default=8)
    parser.add_argument('datasets', help='datasets to download', default=[], nargs='*' )
    parser.add_argument('--meta', default='tablecsv' , choices=['false', 'xml', 'tablecsv', 'json'], help='fetch metadata of resources: xml, tablecsv or false')
    parser.add_argument('--view', default="deep,clean", help="Metadata view i.e. deep,clean or view=TAG1,TAG2")

    session, args = bqapi.cmd.bisque_session(parser=parser)
    args.log = logging.getLogger("bq.downloader")
    args.log.debug (args)

    def fail (*msg):
        args.log.error (*msg)
        sys.exit (1)
    if session is None:
        fail("Failed to create session.. check credentials")

    if not args.datasets:
        parser.print_help()
        sys.exit(0)

    # Start workers with default arguments
    manager = ProcessManager(limit=int(args.threads), workfun = fetch_image,
                              #is_success = lambda r: r is not None and r[0].get ('name'),
                              on_success = append_result_list,
                              on_fail    = append_error_list)
    # helper function to add a list of paths
    def add_uniq(files, root):
        for f1 in files:
#            if args.include and not any (fnmatch.fnmatch (f1, include) for include in args.include):
#                args.log.info ("Skipping %s: not included", f1)
#                continue
#            if args.exclude and any (fnmatch.fnmatch (f1, exclude) for exclude in args.exclude):
#                args.log.info ("Skipping %s: excluded", f1)
#                continue
            manager.schedule ( args = (session, args, root, f1))

    # Add files to work queue
    data_service = session.service("data_service")
    try:
        for dataset_uri in args.datasets:
            dataset_xml = data_service.fetch(dataset_uri, render='xml')
            dirname = dataset_xml.get('name')
            args.log.info("Creating %s dir", dirname)
            if not os.path.exists(dirname):
                os.makedirs (dirname)
            if args.meta in ('xml', 'tablecsv'):
                data_service.fetch_file ('{dataset_uri}/value?view={view}&format={format}'.format(dataset_uri=dataset_uri,
                                                                                                  format=args.meta,
                                                                                                  view=args.view),
                                         localpath= os.path.join (dirname, dirname + '.' +args.meta))
            for value in dataset_xml:
                uniq = value.text.split ('/')[-1]
                add_uniq ([uniq], dataset_xml.get ('name'))
            # if os.path.isdir(root):
            #     for root, _, files in os.walk (root):
            #         #root = root.replace ('\\', '/')
            #         #print ("In ", root, dirs, files, " Prefix DIR ", args.directory)
            #         add_files ((os.path.join (root, f1).replace ('\\', '/') for f1 in files), root=root.replace('\\', '/'))
            # elif os.path.isfile (root):
            #     add_files ([root.replace('\\', '/')], root='')
            # else:
            #     args.log.error ("argument %s was neither directory or file", root)

        # wait for all workers to stop
        while manager.isbusy(): # wait while queue has work
            time.sleep(1)
        manager.stop() # wait for worker to finish

    except (KeyboardInterrupt, SystemExit) as exc:
        print ("TRANSFER INTERRUPT")
        manager.kill()
        #manager.stop()

    # Store output dataset
#    if args.dataset and UNIQS:
#        datasets = session.service('dataset_service')
#        if args.debug:
#            args.log.debug ('create dataset %s with %s', args.dataset, UNIQS)
#        if not args.dry_run:
#            dataset = datasets.create (args.dataset, UNIQS)
#            if args.debug:
#                args.log.debug ('created dataset %s', etree.tostring(dataset, encoding='unicode') )
    if args.debug:
        for S in SUCCESS:
            args.log.debug ('success %s', S)
        for E in ERROR:
            args.log.debug ('failed %s', E)
            if 'with_exception' in E:
                traceback.print_exception (E['with_exc_type'], E['with_exc_val'], E['with_exc_tb'])
    if not args.quiet:
        print ("Successful uploads: ", len (SUCCESS))
        print ("Failed uploads:", len (ERROR))
        print ("Skipped uploads:", len (SKIPPED))

if __name__ == "__main__":
    main()
