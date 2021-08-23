# Local package imports.
from tsofa._views._base import TIME_ZONE
from tsofa._views._base import Command as BC


class Command(BC):

    # Set the templates for dates to empty.  Only datetimes will be
    # parsed.
    tmpls_dates = []

    # The parameters accepted by the "gen_query" method.
    pnames = ('pid', 'attr', 'sdate', 'edate', 'desc', 'limit')

    # The Javascript view emits keys containing the platform ID, the
    # platform attribute ID, and a date component with second
    # resolution.  The emitted value should be a Javascript object.
    default_endpoint = '/_design/psec-pad/_view/psec-pad/queries'

    # The date component of the returned keys starts after the platform
    # ID and the platform attribute ID values.
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
            'attr',
            type = str,
            help = 'Platform attribute ID')
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

        # Specify arguments for the multi-output mode.
        m2 = subparsers.add_parser('multi')
        m2.add_argument(
            'params',
            type = self.arg_json,
            help = 'A list of JSON parameters defining multiple output')

        return None

    @staticmethod
    def gen_query(pid, attr, sdate, edate, **kwargs):

        query = {'reduce': 'false'}

        # Create the start and end key "arrays" for the query,
        # populating the first two elements with the platform ID and the
        # platform attribute ID.
        query['startkey'] = [pid, attr]
        query['endkey'] = [pid, attr]

        # Generate the date components for the start and end keys,
        # joining them with the platform ID and attribute ID values.
        # Swap the keys if the descending flag is set.
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


def main():
    Command.run()

