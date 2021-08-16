#!/usr/bin/env python

import json

from click import echo, pass_context, command, argument, option
from tabulate import tabulate

from nextcodecli.utils import dumps, print_tab


@command(help="List pipelines")
@argument('pipeline_name', nargs=-1)
@option('--raw', 'is_raw', is_flag=True, help='Dump raw json for further processing')
@option('-d', '--details', 'is_details', is_flag=True, help='View details about each pipeline')
@option('-m', '--manifest', 'is_manifest', is_flag=True, help='Output a manifest for this pipeline')
@pass_context
def pipelines(ctx, pipeline_name, is_raw, is_details, is_manifest):
    pipelines = ctx.obj.service.get_pipelines()

    _pipeline_names = set()
    if pipeline_name:
        for p in pipelines:
            for pn in pipeline_name:
                if p['name'].startswith(pn):
                    _pipeline_names.add(p['name'])
        pipelines = [p for p in pipelines if p['name'] in _pipeline_names]
        is_details = True

    if is_manifest:
        for pipeline in pipelines:
            manifest = {
                "pipeline_name": pipeline['name'],
                "project_name": "<project_name>",
                "script": None,
                "revision": None,
                "profile": None,
                "params": {},
            }
            for i, p in enumerate(pipeline.get('parameters', [])):
                val = None
                if p.get('required'):
                    val = "<%s>" % p['name']
                manifest['params'][p['name']] = val
            echo(json.dumps(manifest, indent=4))
    elif is_raw:
        echo(dumps(pipelines))
        return

    elif is_details:
        for p in pipelines:
            print_tab("Pipeline Name", p['name'])
            print_tab("Description", p['description'])
            print_tab("Script", p['script'])
            print_tab("Revision", p['revision'] or 'latest')
            print_tab("Storage Type", p['storage_type'] or 'default')
            print_tab("Scheduler", p['scheduler_name'] or 'default')
            for i, p in enumerate(p.get('parameters', [])):
                txt = "%s (%s)" % (p['name'], p['type'])
                if p.get('required'):
                    txt += " - required"
                if p.get('description'):
                    txt += "\t # %s" % (p.get('description'))
                k = "parameters" if i == 0 else ""
                print_tab(k, txt)
            print(" ")
    else:
        fields = ['name', 'script', 'revision']
        table = []
        for pipeline in pipelines:
            lst = []
            for f in fields:
                v = pipeline.get(f) or 'N/A'
                lst.append(v)

            table.append(lst)
        tbl = tabulate(table, headers=fields)
        echo(tbl)
