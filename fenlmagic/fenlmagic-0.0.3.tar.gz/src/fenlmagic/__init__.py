#!/bin/python

"""
Copyright (C) 2021 Kaskada Inc. All rights reserved.

This package cannot be used, copied or distributed without the express 
written permission of Kaskada Inc.

For licensing inquiries, please contact us at info@kaskada.com.
"""

from __future__ import print_function
from IPython.core.error import UsageError
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic, needs_local_scope)
from IPython.core.magic_arguments import (argument, magic_arguments,
    parse_argstring)

import tempfile
import requests
import subprocess
import json
import os
import pandas
import argparse

import kaskada as kda
from kaskada import compute
import kaskada.api.v1alpha.compute_pb2 as pb

from google.protobuf.json_format import MessageToJson


@magics_class
class FenlMagics(Magics):

    client = None
    tables = {}
    views = {}

    def __init__(self, shell, client):
        super(FenlMagics, self).__init__(shell)
        self.client = client

    @line_magic
    @magic_arguments()
    @argument('--plaintext', default=False, action='store_true', help='Connects to the given endpoint without TLS encryption')
    @argument('--legacy', default=False, action='store_true', help='Uses the legacy compute engine')
    @argument('--endpoint', default="api.kaskada.com:50051", type=str, help='The Kaskada endpoint and port.')
    @argument('--exchange-endpoint', default="prod-kaskada.us.auth0.com", type=str, help='The Auth endpoint to use when obtaining a JWT.')
    @argument('--audience', default="https://api.prod.kaskada.com", type=str, help='The Auth audience to use when obtaining a JWT.')
    @argument('client_id', metavar='client-id', type=str, help='The Kaskada credential Client-ID.')
    @argument('client_secret', metavar='client-secret', type=str, help='The Kaskada credential Client-Secret.')
    def fenl_auth(self, arg):
        "fenl API client id"

        args = parse_argstring(self.fenl_auth, arg)

        self.client = kda.client(
            client_id = args.client_id,
            client_secret = args.client_secret,
            endpoint = args.endpoint,
            exchange_endpoint = args.exchange_endpoint,
            audience = args.audience,
            is_secure = not args.plaintext,
            engine = "LEGACY" if args.legacy else None
        )

    @cell_magic
    @magic_arguments()
    @argument('name', type=str, help='The table name.')
    @argument('schema', type=str, help='The table schema.')
    @argument('entity', type=str, help='The table entity expression.')
    @argument('time', type=str, help='The table time expression.')
    def fenl_table(self, arg, cell):
        "adds a named table to all subsequent fenl queries"

        args = parse_argstring(self.fenl_table, arg)
        name = args.name.strip('"').strip("'")
        entity = args.entity.strip('"').strip("'")
        time = args.time.strip('"').strip("'")
        schema = args.schema.strip('"').strip("'")

        t = pb.WithTable(
            name = name,
            entity = entity,
            time = time,
        )
        t.json_values.schema = schema.strip('"').strip("'")
        t.json_values.values.extend(cell.splitlines())

        self.tables[args.name] = t

    @magic_arguments()
    @argument('--var', help='Assigns the body to a local variable with the given name')
    @argument('--as-view', help='adds the body as a view with the given name to all subsequent fenl queries.')
    @argument('--output', help='Output format for the query results. One of "df" (default), "json", "parquet" or "redis"')
    @argument('--to-redis', help='If provided, write the query results to the given redis host. Implies --output redis')
    @argument('--debug', default=False, help='Shows debugging information')
    @cell_magic
    @line_cell_magic
    @needs_local_scope
    def fenl(self, arg, cell = None, local_ns = None):
        "fenl query magic"

        args = parse_argstring(self.fenl, arg)
        if args.to_redis is not None:
            args.output = 'redis'

        with_tables = []
        with_views = []

        if cell == None:
            with_views.extend(self.views.values())
            query = arg

        else:
            if args.var is not None:
                local_ns[args.var] = cell

            if args.as_view is not None:
                view = args.as_view.strip('"').strip("'")
                v = pb.WithView(
                    name = view,
                    expression = cell,
                )
                self.views[view] = v

                query = view

            else:
                query = cell

        with_tables.extend(self.tables.values())
        with_views.extend(self.views.values())

        query_args = {
            "query" : query,
            "with_tables" : with_tables,
            "with_views" : with_views,
            "client" : self.client,
        }
        if args.output == 'json':
            query_args["response_as"] = "json_values"
        elif args.output == 'redis':
            query_args["response_as"] = "redis_bulk"
        else:
            query_args["response_as"] = "parquet"

        try:
            resp = compute.query(**query_args)
            if args.to_redis is not None:
                r = requests.get(resp.redis_bulk.path)
                p = subprocess.run(["redis-cli", "-h", args.to_redis, "--pipe"], input=r.content, capture_output=True)
                return p.stdout
            elif args.output == 'json':
                return pandas.json_normalize([json.loads(v) for v in resp.json_values.results])
            elif args.output == 'redis':
                return resp.redis_bulk.path
            elif args.output == 'parquet':
                return resp.parquet.path
            else:
                df = pandas.read_parquet(resp.parquet.path, engine='pyarrow')
                if args.debug:
                    return df
                
                return df.drop(['_time', '_subsort', '_key_hash'], axis=1)
        except Exception as e:
            raise UsageError(e)

def load_ipython_extension(ipython):
    if kda.KASKADA_DEFAULT_CLIENT is None:
        if os.getenv('KASKADA_CLIENT_ID') and os.getenv('KASKADA_CLIENT_SECRET'):
            kda.init()

    magics = FenlMagics(ipython, kda.KASKADA_DEFAULT_CLIENT)
    ipython.register_magics(magics)

# def unload_ipython_extension(ipython):
