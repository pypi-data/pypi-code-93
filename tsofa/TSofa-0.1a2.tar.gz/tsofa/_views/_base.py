# Standard library imports.
import argparse
import datetime
import json

# pytz package imports.
import pytz

# requests package imports.
import requests

# Two-Percent package imports.
from twopct.base import Command as BC


# Parse date strings using the list of possible formats.
TMPLS = [
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%dT%H:%M',
    '%Y-%m-%dT%H',
    '%Y-%m-%d',
    '%Y%m%dT%H%M%S',
    '%Y%m%dT%H%M',
    '%Y%m%dT%H',
    '%Y%m%d']

TMPLS_DATES = ['%Y-%m-%d', '%Y%m%d']

# The default time zone string, which is "UTC".  Used to add the tzinfo
# object to "datetime.datetime" objects if another time zone is not
# specified.
TIME_ZONE = 'UTC'


class Command(BC):

    # Specify the acceptable datetime and date templates used to parse
    # a command line date argument.
    tmpls = TMPLS
    tmpls_dates = TMPLS_DATES

    # Specify a list of parameter names accepted by the query method.
    pnames = []

    # Define a default CouchDB view endpoint used in the request method.
    default_endpoint = ''

    # Returned database view keys are an array.  Specify the index where
    # the key should be sliced so that the key contains only the date
    # components.
    key_date_index = 0

    def arg_date(self, str_value):

        date = None
        tmpl = None
        count = 0

        while count < len(self.tmpls):

            try:
                date = datetime.datetime.strptime(str_value, self.tmpls[count])

            except:
                date = None

            if date != None:

                tmpl = TMPLS[count]
                count = len(TMPLS)

            count += 1

        if date is None:
            raise argparse.ArgumentTypeError(
                '{} is not a valid date'.format(str_value))

        elif tmpl in self.tmpls_dates:
            date = date.date()

        return date

    def arg_json(self, str_value):

        params = []

        try:
            params = json.loads(str_value)

        except Exception as e:
            raise argparse.ArgumentTypeError('Invalid JSON')

        return params

    def arg_tz(self, str_value):

        try:
            tz = pytz.timezone(str_value)

        except:
            raise argparse.ArgumentTypeError(
                '{} is not a valid time zone'.format(str_value))

        return str_value

    def add_arguments(self, parser):

        parser.add_argument(
            'db',
            type = str,
            help = 'URL to a CouchDB database containing timeseries data')

        return None

    def clean_date(self, date, tz):

        try:
            output = pytz.timezone(tz).localize(date)

        except:
            output = pytz.UTC.localize(date)

        return output

    def clean(self, **kwargs):

        cleaned = {}

        # If the default argument parser mode is used, add the given
        # keyword argument values to a params dictionary list, and then
        # add that to the cleaned data.
        if 'pid' in kwargs.keys():

            # Create a new params dictionary list from the singular
            # arguments.
            cleaned['params'] = [{}]

            for key in kwargs.keys():
                if key != 'db':
                    cleaned['params'][0][key] = kwargs[key]

            # Get the date arguments from the passed keywords.
            sdate = kwargs['sdate']
            edate = kwargs['edate']
            tz = kwargs['tz']

            cleaned['params'][0]['sdate'] = self.clean_date(sdate, tz)
            cleaned['params'][0]['edate'] = self.clean_date(edate, tz)

        # Verify that the contents of the params list are dictionaries
        # and clean the start and end dates contained in each
        # dictionary.
        elif 'params' in kwargs.keys():

            cleaned['params'] = []

            if type(kwargs.get('params', None)) == type([]):

                for p in kwargs['params']:

                    if type(p) == type({}):

                        # Get the time zone string.
                        tz = self.arg_tz(p.get('tz', TIME_ZONE))

                        p['sdate'] = self.clean_date(
                            self.arg_date(p['sdate']), tz)
                        p['edate'] = self.clean_date(
                            self.arg_date(p['edate']), tz)

                    else:
                        raise ValueError(
                            'Contents of params list must be a dictionary')

                    cleaned['params'].append(p)

            else:
                raise ValueError('Params must be a list')

        return cleaned

    def dumps(self, value, **kwargs):
        return json.dumps(value)

    def gen_queries(self, params):

        # Define the query dictionary needed to perform multiple data
        # requests using a single call to the database.
        queries = {'queries': []}

        for p in params:

            # If an item in the params list is not a dictionary, then
            # create an empty dictionary.
            if type(p) != type({}):
                p = {}

            qka = {}

            for k in self.pnames:
                qka[k] = p.get(k, '')

            queries['queries'].append(self.gen_query(**qka))

        return queries

    def handle(self, *args, **kwargs):

        # Return database data using this variable.
        data = []

        # Generate the queries from the given parameters list.
        queries = self.gen_queries(kwargs['params'])

        # Make the data request.
        results = self.request(kwargs['db'], queries)

        if results is not None:

            # The counter to index into the params list.
            c1 = 0

            while c1 < len(kwargs['params']):

                p = kwargs['params'][c1]
                sdate = p.get('sdate', None)

                if sdate is not None:
                    tz = str(sdate.tzinfo)

                else:
                    tz = TIME_ZONE

                _rows = []

                for r in results['results'][c1]['rows']:
                    _rows.append(
                        [self.parse_date_key(r['key'], tz = tz), r['value']])

                data.append(_rows)

                c1 += 1

        return data

    def parse_date_key(self, key, tz):
        """Returns a date string from the date component of a row key.

        """
        # First, slice the key to the list contents that only contain
        # the date components.
        try:
            key = key[self.key_date_index:]

        except:
            key = []

        # First, if the date key is 7 elements long, add three trailing
        # zeros to the millisecond string, effectively making it a
        # microsecond string.
        if len(key) == 7:
            key[6] += '000'

        # Construct a string of date components.
        dc = ''

        for i in range(0, len(key)):
            dc += str(int(key[i])) + ','

        # Now, try to create the actual datetime or date object.
        try:

            tmpl = '%Y-%m-%d'
            date = eval('datetime.datetime({})'.format(dc))

            if len(key) > 3:

                tmpl = '%Y-%m-%dT%H:%M:%S'

                if len(key) == 7:
                    tmpl += '.%f'

                date = pytz.UTC.localize(date).astimezone(pytz.timezone(tz))

            date = date.strftime(tmpl)

        except:
            date = None

        return date

    def request(self, db, queries, endpoint = None):

        # Set the view endpoint.
        _ep = self.default_endpoint

        if type(endpoint) == type(''):
            _ep = endpoint

        # Perform the database requests.  If any one of the requests
        # fail, no data is returned.
        results = {}

        try:
            results = requests.post(
                db + _ep,
                headers = {'Content-Type': 'application/json'},
                data = json.dumps(queries),
                timeout = 30.0).json()

        except Exception as e:

            results = None
            self.stderr(str(e))

        return results

    @staticmethod
    def gen_date_key(date):

        # Determine if the given date parameter is a "datetime.date"
        # object, or a "datetime.datetime" object.
        #if 'datetime.date' in str(type(date)):
        if type(date) == type(datetime.date.today()):

            # Format and evaluate the UTC date as list.
            tmpl = '["%Y","%m","%d"]'
            key = eval(date.strftime(tmpl))

        #elif 'datetime.datetime' in str(type(date)):
        elif type(date) == type(datetime.datetime.now()):

            # If the given "datetime.datetime" does not have a set
            # tzinfo object, then set the tzinfo as a "pytz.UTC" object.
            if date.tzinfo == None:
                date = pytz.UTC.localize(date)

            # Adjust the "datetime.datetime" to a UTC time zone.
            date = date.astimezone(pytz.UTC)

            # Format and evaluate the UTC date as list.
            tmpl = '["%Y","%m","%d","%H","%M","%S"]'
            key = eval(date.strftime(tmpl))

            # Get the nearest milliseconds from the microsecond
            # attribute of the "datetime.datetime" object.  Only
            # do so if the microseconds are greater than or equal to
            # 1000, or one millisecond.
            if date.microsecond >= 1000:

                ms = int(round(date.microsecond / 1000, 0))

                # Create a zero padded string of milliseconds to add to
                # the key.
                if ms < 10:
                    key.append('00' + str(ms))

                elif ms < 100:
                    key.append('0' + str(ms))

                else:
                    key.append(str(ms))

        else:
            key = []

        return key

    @staticmethod
    def gen_query(**kwargs):
        return {}

