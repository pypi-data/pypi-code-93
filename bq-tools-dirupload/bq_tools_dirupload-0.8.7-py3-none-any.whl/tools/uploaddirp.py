#!/usr/bin/env python
#from __future__ import unicode_literals
#from __future__ import print_function
#from builtins import input
#from builtins import range
#from future import standard_library
#standard_library.install_aliases()

import os
import sys
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

import regex as re   # substitute RE with branches
from lxml import etree

import bqapi
from . pool import ProcessManager


def send_image_to_bisque(session, args, root, image_path,   tagmap=None, fixedtags=None):
    """Send one image to bisque

    Args:
      session (session): A rrequests  session to the destination
      args (Namespace):  an argparse argument object (for flags)
      image_path (str): The abs path of the file to be uploaded
      root (str)      : The abs path of root dir
      tagmap (dict)   :   map for replacing values
                       { 'context-key' : { 'value': 'mapped value' , ... }   # map for specific context
                                           ''            : { 'value': 'mapped value' , ... }   # every context
                       }
     fixtags (dict)   :  a list of fixed tags to be added based on a key fields
                      { context-ley : { 'tag': 'value', ... }
    Returns:
      None on skipped or failed file or an XML resource
    """
    #  args.log.debug ("preping tags %s %s %s %s", root, image_path,   tagmap.keys(), fixedtags.keys())
    #   Strip off top level dirs .. except user given root
    filename = os.path.basename(image_path)
    original_image_path = image_path
    image_path = image_path[len(root)+1:]
    tags = None   # etree resource for uploaded item
    data_service = session.service('data_service')

    ############################################################################
    # Skip pre-existing resources with same filename
    if args.skip_loaded or args.replace_uploaded:
        response = data_service.get(params={'name':filename}, render='etree')
        if len(response) and response[0].get('name') == filename:
            if args.skip_loaded:
                args.log.warn("skipping %s: previously uploaded ", filename)
                return None
            elif args.replace_uploaded:
                tags = response[0]

    ############################################################################
    # Build argument tags into upload xml
    if tags is None:
        tags  = etree.Element ('resource', name=image_path)
    resource_tags = {}
    # add any fixed (default) arguments  (maybe be overridden)
    for tag,value in [ x.split(':') for x in args.tag if '$' not in x ]:
        #etree.SubElement (tags, 'tag', name=tag, value = value)
        resource_tags[tag] = value
    # path elements can be made tags (only match directory portion)
    if args.path_tags:
        for tag,value in zip_longest (args.path_tags, image_path.split ('/')[:-1]):
            if tag  and value :
                #etree.SubElement (tags, 'tag', name=tagmap.get(tag, tag), value = tagmap.get(value, value))
                resource_tags [tag] =  value
                #resource_tags [tagmap.get(tag, tag)] =  tagmap.get(value, value)
    ############################################################################
    # RE over the filename
    if args.re_tags:
        matches = args.re_tags.match (filename)
        if matches:
            for tag, value in matches.groupdict().items():
                if tag  and value :
                    #etree.SubElement (tags, 'tag', name=tagmap.get (tag, tag), value = tagmap.get (value, value))
                    #resource_tags [tagmap.get(tag, tag)] =  tagmap.get(value, value)
                    resource_tags [tag] =  value
        elif args.re_only:
            args.log.warn ("Skipping %s: does not match re_tags", filename)
            return None
        else:
            args.log.warn ("RE did not match %s", filename)
    #####################
    # resource_tags now contains all elements from the path and filename.
    # We now process these to find encoded entries for expansion
    ######################
    # Add fixed tags based on associated tagtable
    for  tagkey, tagtable in fixedtags.items():
        key = None
        if tagkey == 'filename':
            key = filename
        elif tagkey == 'image_path':
            key = image_path
        else:
            key =  resource_tags.get(tagkey)
        if key is None:
            args.log.warn ("Lookup in fixed table: key %s  was not found", tagkey)
            continue
        if key not in tagtable:
            args.log.warn ("Key %s : %s was not present in fixedtable", tagkey, key)
            continue
        for tag,value in tagtable[key].items():
            resource_tags[tag]=value

    #####################
    # Special geotag processing
    geo = {}
    new_resource_tags = copy.deepcopy(resource_tags)
    for tag,value in resource_tags.items():
        if tag in ('lat', 'latitude'):
            geo['latitude'] = value
            del new_resource_tags[tag]
        if tag in ('alt', 'altitude'):
            geo['altitude'] = value
            del new_resource_tags[tag]
        if tag in ('long', 'longitude'):
            geo['longitude'] = value
            del new_resource_tags[tag]
    resource_tags = new_resource_tags
    if geo:
        geotags = etree.SubElement (tags, 'tag', name='Geo')
        coords  = etree.SubElement (geotags, 'tag', name = 'Coordinates')
        center  = etree.SubElement (coords, 'tag', name = 'center')
        for tag,val in geo.items():
            etree.SubElement(center, 'tag', name=tag, value = val)

    # add any templated tag   (maybe be overridden)
    for tag, value in [string.Template(x).safe_substitute(resource_tags).split(':') for x in args.tag if '$' in x]:
        # etree.SubElement (tags, 'tag', name=tag, value = value)
        resource_tags[tag] = value

    #####################
    # fold duplicates and de-reference items
    #
    new_tags =  {}
    for tag,value in resource_tags.items():
        if tag in tagmap:  # We have contextual map for this element  i.e. this tag's value is mapped
            mapper = tagmap[tag]
            if args.mustmap:
                if mapper.get (value) is None:
                    args.log.warn ("Skipping %s:  %s does not match mapper in context:%s", filename, value, tag)
                    return None
        else:
            mapper = tagmap['']
        value = mapper.get(value, value)
        new_tags[tag] = value
    resource_tags = new_tags
    ######################
    #  move tags to xml
    for tag,value in resource_tags.items():
        if tag and value:
            etree.SubElement(tags, 'tag', name=tag, value=value)
    xml = etree.tostring(tags, encoding='unicode')

    ################
    # Prepare to upload
    if args.debug:
        args.log.debug("upload %s with xml %s ", image_path, xml)

    import_service = session.service('import')
    if not args.dry_run:
        try:
            if args.replace_uploaded and tags.get('uri') is not None:
                args.log.info("replacing meatdata for %s", image_path)
                response = data_service.put(path=tags.get('uri'), data=xml, render='xml')
                uploaded = etree.Element('resource', type='uploaded')
                uploaded.append(response)
                response = uploaded
            else:
                with open(original_image_path, 'rb') as fileobj:
                    if os.fstat(fileobj.fileno()).st_size == 0:
                        if not args.empty:
                            args.log.warn("Skipping %s: Empty file", original_image_path)
                            return None
                    response = import_service.transfer(image_path, fileobj=fileobj, xml=xml, render='etree')
        except OSError as exc:
            args.log.error("Skipping %s:  system error %s", original_image_path, exc)
            return None
    else:
        # Return a dry_run response
        response = etree.Element('resource')
        etree.SubElement(response, 'image', name=image_path,
                         resource_uniq='00-%s' % ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)),
                         value=image_path)
    if not args.quiet:
        args.log.info("Uploaded %s with %s", image_path, resource_tags)
    return response



SUCCESS=[]
ERROR = []
SKIPPED = []
UNIQS = []

def append_result_list (request):
    SUCCESS.append (request)
    resource = request['return_value']
    UNIQS.append (resource[0].get ('resource_uniq'))


def append_error_list (request):
    ERROR.append (request)
    if request.get ('return_value') is None:
        SKIPPED.append (request)
        return
    args = request['args'][1]
    if request.get ('return_value'):
        args.log.error ("return value %s", etree.tostring (request['return_value'], encoding='unicode'))



DEFAULT_CONFIG='~/bisque/config' if os.name == 'nt' else "~/.bisque/config"



DOC_EPILOG="""
bq-dirupload -n  --threads 1 --re-tags "(?P<photo_site_code>\w+)_(?P<target_assemblage>\D+)(?P<plot>\d+)_(?P<season>\D+)(?P<year>\d+).+\.JPG" --dataset upload --tagmap target_assemblage:@speciesmap.csv --tagmap photo_site_code:@locationmap.csv --tagmap season:fa=fall --tagmap year:15=2015 --fixedtags photo_site_code:@photo_code_reference_2019_0912.csv

 Magic decoder ring:
    -n : dry run
    --threads 1: one thread for debugging
    --retags :   use filename to create tags: photo_site_code, target_assemblage, season and year.
    --dataset : create a dataset "upload"
    --tagmap target_assemblage:@speciesmap.csv: use value ins speciesmap.csv to rename tag/values for target_assemblage
    --tagmap photo_site_code:@locationmap: Use location map to rename tag/value from photo_site_code
    --tagmap season:fa=fall : rename season 'fa' to 'fall'
    --tagmap year:15=2015 : remame year from '15' to 2015
    --fixedtags photo_site_code:@photo_code_reference_2019_0912.csv  :  use photo_site_code to read a set of fixed tags to be applied to the resource

   A map is consists of [context_tag:]oldval=newval or [context_tag:]@map.csv where csv is a two column table of old value, new value

Other interesting Arguments

    --debug-file somefile :  write actions to somefile
    --path-tags   map components of the file path  to metadata tags i.e. project/site/season   would map ghostcrabs/manua/winter/somefile.jpg
                  would get { project:ghostcrabs, site:manua, season:winter} as tags on somefile.jpg


"""



def main():
    parser = bqapi.cmd.bisque_argument_parser("Upload files to bisque", formatter_class=argparse.RawDescriptionHelpFormatter, epilog = DOC_EPILOG)
    parser.add_argument('--tag', help="Add name:value pair, can be templated with other values mycode:$site$season", action="append", default=[])
    parser.add_argument('--path-tags', help='tag names for a parsible path i.e. /project/date/subject/', default="")
    parser.add_argument('--re-tags', help=r're expressions for tags i.e. (?P<location>\w+)--(?P<date>[\d-]+)')
    parser.add_argument('--re-only', help=r'Accept files only if match re-tags', default = False, action="store_true")
    parser.add_argument('--mustmap', help=r'Contextual tag  must have a value in a tagmap', default = False, action="store_true")
    parser.add_argument('--include', help='shell expression for files to include. Can be repeated', action="append", default=[])
    parser.add_argument('--exclude', help='shell expression for files to exclude. Can be repeated', action="append", default=[])
    parser.add_argument('--dataset', help='create dataset and add files to it', default=None)
    parser.add_argument('--threads', help='set number of uploader threads', default=8)
    parser.add_argument('--empty', help='Allow empty files to be uploaded', action="store_true", default=False)
    parser.add_argument("-s", '--skip-loaded', help="Skip upload if there is file with the same name already present on the server", action='store_true')
    parser.add_argument("-r", "--replace-uploaded", help="Force upload of metadata even if file exists on server", action="store_true")
    parser.add_argument("--tagmap", action="append", default=[], help="Supply a map tag/value -> tag/value found in tag path and re decoder.  [context_key:]carp=carpenteria or [context_key:]@tagmap.csv")
    parser.add_argument("--fixedtags", action="append", default = [],
                        help="key:tag=value or key:@fileoftags fixed tags to add to resource: First column is key: including filename or image_path")
    parser.add_argument('directories', help='director(ies) to upload', default=[], nargs='*' )

    session, args = bqapi.cmd.bisque_session(parser=parser)
    args.log = logging.getLogger("bq.uploader")
    args.log.warn ("Arguments %s", ' '.join (sys.argv[1:]))

    def fail (*msg):
        args.log.error (*msg)
        sys.exit (1)
    if session is None:
        fail("Failed to create session.. check credentials")

    args.path_tags = args.path_tags.split (os.sep)
    if args.re_tags:
        args.re_tags = re.compile (args.re_tags, flags = re.IGNORECASE)
    fixedtags = {}
    for tagtable in  args.fixedtags:
        context, tagtable  = tagtable.split (':')
        if '=' in tagtable:
            fixedtags.setdefault(context, {}).update (dict([tagtable.split('=')]))
            continue
        elif tagtable[0]=='@':
            if not tagtable.endswith('.csv'):
                fail ("fixed tag %s table must be .csv file", tagtable)
            if not os.path.exists (tagtable[1:]):
                fail ("File %s does not exist", tagtable[1:])
        else:
            fail ("%s Must be in form of tag=val or @tableofvalue", tagtable)

        with open (tagtable[1:], 'r') as csvfile:
            reader = csv.reader (csvfile)
            fieldnames = next(reader)
            keyfield = fieldnames[0]
            fieldnames = fieldnames[1:]
            for row in  reader:
                # grab value of first columner and use as key for the rest of the values.
                fixedtags.setdefault(context, {})[row[0]] = OrderedDict (zip_longest (fieldnames, row[1:]))

    # load tag map items (mapping certain values from filename/path to full values)
    tagitems = { '': {} }
    for entry in args.tagmap:
        context = ''
        if ':' in entry:
            context, entry = entry.split(':')
        if entry.startswith('@'):
            if not entry.endswith('.csv'):
                fail ("tagmap %s table must be .csv file", entry[1:])
            if not os.path.exists (entry[1:]):
                fail ("tagmap file %s does not exist", entry[1:])
                continue

            with open (entry[1:], 'r') as csvfile:
                tagitems.setdefault(context, {}).update ( (row[0].strip(), row[1].strip()) for row in csv.reader(csvfile))
            continue
        tagitems.setdefault(context, {}).update (  [ entry.split('=') ] )

    # Start workers with default arguments
    manager = ProcessManager(limit=int(args.threads), workfun = send_image_to_bisque,
                              is_success = lambda r: r is not None and r[0].get ('name'),
                              on_success = append_result_list,
                              on_fail    = append_error_list)
    # helper function to add a list of paths
    def add_files(files, root):
        for f1 in files:
            if args.include and not any (fnmatch.fnmatch (f1, include) for include in args.include):
                args.log.info ("Skipping %s: not included", f1)
                continue
            if args.exclude and any (fnmatch.fnmatch (f1, exclude) for exclude in args.exclude):
                args.log.info ("Skipping %s: excluded", f1)
                continue
            manager.schedule ( args = (session, args, root, f1, tagitems, fixedtags))

    if not args.directories:
        parser.print_help()
        sys.exit(0)

    # Add files to work queue
    try:
        for directory in args.directories:
            root = os.path.abspath(os.path.expanduser(directory))
            # args.directory = os.path.normpath(os.path.expanduser (directory))
            parent = root.replace('\\', '/')
            if os.path.isdir(root):
                for root, _, files in os.walk(root):
                    # root = root.replace ('\\', '/')
                    # print ("In ", root, dirs, files, " Prefix DIR ", args.directory)
                    add_files((os.path.join (root, f1).replace('\\', '/') for f1 in files), root=parent)
            elif os.path.isfile (root):
                add_files ([root.replace('\\', '/')], root=os.path.dirname(root).replace('\\', '/'))
            else:
                args.log.error ("argument %s was neither directory or file", root)

        # wait for all workers to stop
        while manager.isbusy(): # wait while queue has work
            time.sleep(1)
        manager.stop() # wait for worker to finish

    except (KeyboardInterrupt, SystemExit) as exc:
        print ("TRANSFER INTERRUPT")
        manager.kill()
        #manager.stop()

    # Store output dataset
    if args.dataset and UNIQS:
        if args.debug:
            args.log.debug ('create/append dataset %s with %s', args.dataset, UNIQS)
        data = session.service('data_service')
        dataset = data.get("dataset", params={'name': args.dataset}, render='xml')
        dataset_uniq = len(dataset) and dataset[0].get('resource_uniq')   # fetch uri of fist child
        datasets = session.service('dataset_service')
        if not args.dry_run:
            if dataset_uniq:
                response = datasets.append_member(dataset_uniq, UNIQS)
            else:
                response = datasets.create(args.dataset, UNIQS)
            if args.debug and response.status_code == data.codes.ok:
                args.log.debug('created dataset %s', etree.tostring(response.xml(), encoding='unicode'))
    if args.debug:
        for S in SUCCESS:
            args.log.debug('success %s', S)
        for E in ERROR:
            args.log.debug('failed %s', E)
            if 'with_exception' in E:
                traceback.print_exception(E['with_exc_type'], E['with_exc_val'], E['with_exc_tb'])
    if not args.quiet:
        print("Successful uploads: ", len (SUCCESS))
        print("Failed uploads:", len (ERROR))
        print("Skipped uploads:", len (SKIPPED))

if __name__ == "__main__":
    main()
