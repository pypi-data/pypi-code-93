# Standard library imports.
import argparse
import datetime
import json

# pytz package imports.
import pytz

# requests package imports.
import requests

# Local package imports.
from tsofa._views._base import TIME_ZONE
from tsofa._views._base import Command as BC


class Command(BC):

    # Set the templates for dates to empty.  Only datetimes will be
    # parsed.
    tmpls_dates = []

    # The gen_query method below accepts only these argument names.
    pnames = ('pid', 'rpt', 'sdate', 'edate', 'desc', 'limit', 'summarize')

    # The Javascript view emits keys containing the platform ID, data
    # report ID, and a date component with second resolution.  The value
    # emitted should be a Javascript object.
    default_endpoint = '/_design/dsec-prd/_view/dsec-prd/queries'

    # The date component of the returned keys starts after the platform
    # ID and data report ID values.
    key_date_index = 2

    def add_arguments(self, parser):

        BC.add_arguments(self, parser)

        # Create subparsers so that the command can have two modes,
        # where the first mode requires stand-alone arguments, and the
        # second mode requires a list of JSON arguments.
        subparsers = parser.add_subparsers()

        # Specify arguments for the default mode.
        m1 = subparsers.add_parser('default')
        m1.add_argument(
            'pid',
            type = str,
            help = 'Platform ID')
        m1.add_argument(
            'rpt',
            type = str,
            help = 'Data report ID')
        m1.add_argument(
            'sdate',
            type = self.arg_date,
            help = 'List values from this start date')
        m1.add_argument(
            'edate',
            type = self.arg_date,
            help = 'List values up to, and including, this end date')
        m1.add_argument(
            '--tz',
            type = self.arg_tz,
            default = TIME_ZONE,
            help = 'Output dates are localized to this time zone')
        m1.add_argument(
            '--desc',
            action = 'store_true',
            help = 'Reverse the order of the values, by date')
        m1.add_argument(
            '--limit',
            type = int,
            default = 0,
            help = 'Limit the number of values returned')
        m1.add_argument(
            '--summarize',
            action = 'store_true',
            help = 'Summarize the list of data reports')

        # Specify arguments for the multi-output mode.
        m2 = subparsers.add_parser('multi')
        m2.add_argument(
            'params',
            type = self.arg_json,
            help = 'A list of JSON parameters defining multiple output')

        return None

    @staticmethod
    def gen_query(pid, rpt, sdate, edate, **kwargs):

        query = {'reduce': 'false'}

        # Create the start and end key "arrays" for the query,
        # populating the first three elements with the platform ID
        # and report ID values.
        query['startkey'] = [pid, rpt]
        query['endkey'] = [pid, rpt]

        if kwargs.get('desc', False) == True:

            query['startkey'] += BC.gen_date_key(edate) + ['\ufff0']
            query['endkey'] += BC.gen_date_key(sdate)
            query['descending'] = 'true'

        else:

            query['startkey'] += BC.gen_date_key(sdate)
            query['endkey'] += BC.gen_date_key(edate) + ['\ufff0']

        # Limit the output to a given number of JSON documents.
        if type(kwargs.get('limit', None)) == type(0):
            if kwargs['limit'] > 0:
                query['limit'] = kwargs['limit']

        return query

    @staticmethod
    def summarize(lister):

        smry = {}

        for row in lister:

            for vbl in row[1].keys():

                value = row[1][vbl]
                date = row[0]

                if type(row[1][vbl]) == type({}):

                    if 'value' in row[1][vbl].keys():

                        value = row[1][vbl]['value']

                        if 'date' in row[1][vbl].keys():
                            date = row[1][vbl]['date']

                if type(value) in (type(0), type(0.0)):

                    if vbl not in smry.keys():
                        smry[vbl] = {
                            'max': {'value': value, 'date': date},
                            'min': {'value': value, 'date': date},
                            'avg': None,
                            'sum': 0,
                            'count': 0}

                    if value > smry[vbl]['max']['value']:

                        smry[vbl]['max']['value'] = value
                        smry[vbl]['max']['date'] = date

                    if value < smry[vbl]['min']['value']:

                        smry[vbl]['min']['value'] = value
                        smry[vbl]['min']['date'] = date

                    smry[vbl]['sum'] += value
                    smry[vbl]['count'] += 1

        for vbl in smry.keys():
            if smry[vbl]['count'] > 0:
                smry[vbl]['avg'] = smry[vbl]['sum'] / smry[vbl]['count']

        return smry


def main():
    Command.run()

