import volatility
vis = volatility.Volatility()

#%%
vis_dict = vis.__dict__

#%%
import datetime as dt
from datetime import timedelta
from pandas.tseries.offsets import BDay

start_date_as_dt = (dt.datetime.today() - timedelta(days=1) - BDay(1)).date()
start_date = str(start_date_as_dt)

#%%
params = vis.params
url = 'https://finance.yahoo.com/quote/'+params['ticker']\
            +'/options?p='+params['ticker']

#%%
import requests
# Define the stock root webpage
url = 'https://finance.yahoo.com/quote/'+params['ticker']\
    +'/options?p='+params['ticker']

#%%
# Create a requests object to extract data from the url
params['requestslink'] = requests.get(url)

#%%
# Collect the text fromthis object
html_doc = params['requestslink'].text

#%%
# Use Beautiful Soup to parse this
soup = BeautifulSoup(html_doc, features="lxml")

# Create a list of all the option dates
option_dates = [a.get_text() for a in soup.find_all('option')]

# Convert this list from string to datetimes
dates_list = [dt.datetime.strptime(date, "%B %d, %Y").date() for date
              in option_dates]

# Convert back to strings in the required format
str_dates = [date_obj.strftime('%Y-%m-%d') for date_obj in dates_list]

# Create a list of all the unix dates used in the url for each
# of these dates
option_pages = [a.attrs['value'] for a in soup.find_all('option')]

# Combine the dates and unixdates in a dictionary
optodict = dict(zip(str_dates, option_pages))

# Create an empty dictionary
url_dict = {}

# For each date and unixdate in the first dictionary
for date_val, page in optodict.items():

    # Create an entry with the date as key and the url plus
    # unix date as value
    url_dict[date_val] = str(
        'https://finance.yahoo.com/quote/'
        +params['ticker']+'/options?date='+page)

#%%
# https://github.com/JECSand/yahoofinancials/blob/9cc2bd1faa7380f6f451f7de9b5d228160627fd3/yahoofinancials/__init__.py#L70

def _get_api_data(self, api_url, tries=0):
    urlopener = UrlOpener()
    response = urlopener.open(api_url)
    if response.getcode() == 200:
        res_content = response.read()
        response.close()
        if sys.version_info < (3, 0):
            return loads(res_content)
        return loads(res_content.decode('utf-8'))
    else:
        if tries < 5:
            time.sleep(random.randrange(10, 20))
            tries += 1
            return self._get_api_data(api_url, tries)
        else:
            return None

#%%
# https://docs.python.org/3/library/urllib.request.html#module-urllib.request
#try:
#from urllib import FancyURLopener
#except:
from urllib.request import FancyURLopener

#%%

# Class used to open urls for financial data
class UrlOpener(FancyURLopener):
    version = 'w3m/0.5.3+git20180125'

#%%
urlopener = UrlOpener()

#%%
response = urlopener.open(url)

#%%
response_content = response.read()

#%%
from bs4 import BeautifulSoup
soup = BeautifulSoup(response_content, "html.parser")

#%%
print(soup.prettify())

#%%
print(soup.get_text())

#%%
htmldoc = response.text

#%%
# Use Beautiful Soup to parse this
soup = BeautifulSoup(response_content, features="lxml")

#%%

# Create a list of all the option dates
option_dates = [a.get_text() for a in soup.find_all('option')]

#%%
# Convert this list from string to datetimes
dates_list = [dt.datetime.strptime(date, "%B %d, %Y").date() for date
              in option_dates]

#%%
# Convert back to strings in the required format
str_dates = [date_obj.strftime('%Y-%m-%d') for date_obj in dates_list]

#%%
# Create a list of all the unix dates used in the url for each
# of these dates
option_pages = [a.attrs['value'] for a in soup.find_all('option')]

#%%
# Combine the dates and unixdates in a dictionary
optodict = dict(zip(str_dates, option_pages))

#%%
# Create an empty dictionary
url_dict = {}

# For each date and unixdate in the first dictionary
for date_val, page in optodict.items():

    # Create an entry with the date as key and the url plus
    # unix date as value
    url_dict[date_val] = str(
        'https://finance.yahoo.com/quote/'
        +params['ticker']+'/options?date='+page)

#%%
import volatility
vis = volatility.Volatility(ticker='AAPL')

#%%
vis_dict = vis.__dict__

#%%
# Create an empty dictionary
option_dict = {}
params['url_except_dict'] = {}

# each url needs to have an option expiry date associated with
# it in the url dict
for input_date, url in params['url_dict'].items():

    # requests function downloads the data
    web = requests.get(url).content

    # wait between each query so as not to overload server
    time.sleep(params['wait'])

    # if data exists
    try:
        # read html data into a DataFrame
        option_frame = pd.read_html(web)

        # Add this DataFrame to the default dictionary, named
        # with the expiry date it refers to
        params['option_dict'][input_date] = option_frame

    # otherwise collect dictionary of exceptions
    except KeyError:
        params['url_except_dict'][input_date] = url


#%%
params = vis.params

#%%
url_dict = params['url_dict']

#%%
urldates = list(url_dict.keys())
urllist = list(url_dict.values())

#%%

urldate1 = urldates[0]
url1 = urllist[0]

#%%
import pandas as pd
web = requests.get(url).content
option_frame = pd.read_html(web)

#%%
web2 = urlopener.open(url1)
web2_content = web2.read()
option_frame2 = pd.read_html(web2_content)

#%%
#for input_date, url in params['url_dict'].items():

urldate1 = urldates[0]
url1 = urllist[0]

# UrlOpener function downloads the data
urlopener = UrlOpener()
weburl = urlopener.open(url1)
web = weburl.read()

# if data exists

# read html data into a DataFrame
option_frame = pd.read_html(web)

#%%

# Add this DataFrame to the default dictionary, named
# with the expiry date it refers to
params['option_dict'][input_date]['calls'] = option_frame[0]
params['option_dict'][input_date]['puts'] = option_frame[1]

#%%
# otherwise collect dictionary of exceptions
except KeyError:
    params['url_except_dict'][input_date] = url

#%%
import copy
vis_bak = copy.deepcopy(vis)

#%%
vis = copy.deepcopy(vis_bak)

#%%
from market_data import Data
vis.params, vis.tables = Data.transform(params=vis.params, tables=vis.tables)

#%%
# Create Days to Maturity column
days = (vis.tables['data']['TTM']*365).astype(int)

#%%
import numpy as np
# Create a column of the Trade Date represented in unixtime
unixtime2 = (vis.tables['data']['Last Trade Date'].view(np.int64) // 10**9)

#%%
vis.params, vis.tables = Data.combine(params=vis.params, tables=vis.tables)

#%%
visdict = vis.__dict__

#%%
from lxml import html
data = urlopener.open(url1)
data_content = data.read()
tree = html.fromstring(data_content)

#%%
priceparse = tree.xpath(
    '//span[@class="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"]/text()')

spot = float([str(p) for p in priceparse][0].replace(',',''))

#%%
urlopener = UrlOpener()
response = urlopener.open(url)

# Collect the text from this object
params['html_doc'] = response.read()

#%%
input_data = copy.deepcopy(vis.tables['data'])

#%%
# For each put strike price
for strike in params['put_strikes']:

    # Assign an option name of ticker plus strike
    opt_name = params['ticker_label']+'_'+str(strike)

    # store the implied vol results for that strike in the
    # option dictionary
    opt_dict[opt_name] = cls._imp_vol_apply(
        params=params, input_data=input_data, K=strike, option='put')

    # store the implied vol results for that strike in the
    # option list
    params['opt_list'].append(opt_dict[opt_name])

    print('Put option: ', opt_name)

#%%
params = vis.params

#%%
put0 = params['put_strikes'][0]

#%%
import warnings
strike=80
aapl80 = _imp_vol_apply(params=params, input_data=input_data, K=strike, option='put')

#%%
def _imp_vol_apply(params, input_data, K, option):

    # Filter data by strike and option type
    input_data = (input_data[(input_data['Strike'] == K)
            & (input_data['Option Type'] == option)])

    # Apply implied vol method to each row
    input_data = input_data.apply(
        lambda x: _imp_vol_by_row(x, params, K, option), axis=1)

    return input_data

#%%
from optionmodels.models import ImpliedVol
def _imp_vol_by_row(row, params, K, option):

    # Suppress runtime warnings caused by bad vol data
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    # For the chosen implied vol method and its method name
    for flag, func_name in params['method_dict'].items():

        # select the method from the dictionary
        if params['method'] == flag:

            # for each of the prices: bid, mid, ask, last
            for input_row, output_row in params['row_dict'].items():

                try:
                    # populate the column using the chosen implied
                    # vol method (using getattr() to select
                    # dynamically)
                    # check if n/a value is returned and print error
                    # message if so
                    output = getattr(ImpliedVol, func_name)(
                        S=params['S'], K=K, T=row['TTM'],
                        r=params['r'], q=params['q'],
                        cm=row[input_row], epsilon=params['epsilon'],
                        option=option, timing=False)

                    output = float(output)
                    row[output_row] = output

                except KeyError:
                    print("Error with option: Strike="+str(K)+
                              " TTM="+str(round(row['TTM'], 3))+
                              " vol="+str(row[input_row])+
                              " option="+option)

    # Return warnings to default setting
    warnings.filterwarnings("default", category=RuntimeWarning)

    return row

#%%
def _imp_vol_by_row(row, params, K, option):

    # Suppress runtime warnings caused by bad vol data
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    func_name = params['method_dict'][params['method']]

    # for each of the prices: bid, mid, ask, last
    for input_row, output_row in params['row_dict'].items():

        #try:
            # populate the column using the chosen implied
            # vol method (using getattr() to select
            # dynamically)
            # check if n/a value is returned and print error
            # message if so
        output = getattr(ImpliedVol, func_name)(
            S=params['spot'], K=K, T=row['TTM'],
            r=params['r'], q=params['q'],
            cm=row[input_row], epsilon=params['epsilon'],
            option=option, timing=False)

        output = float(output)
        row[output_row] = output

        #except KeyError:
        #    print("Error with option: Strike="+str(K)+
        #              " TTM="+str(round(row['TTM'], 3))+
        #              " vol="+str(row[input_row])+
        #              " option="+option)

    # Return warnings to default setting
    warnings.filterwarnings("default", category=RuntimeWarning)

    return row

#%%
func_name = params['method_dict'][params['method']]

#%%
from graph import Graph
params, tables = Graph.line_graph(params=vis.params, tables=vis.tables)

#%%
params, tables = Graph.scatter_3d(params=vis.params, tables=vis.tables)

#%%
        if params['surfacetype'] == 'trisurf':
            fig = cls._trisurf_graph(params=params)

        elif params['surfacetype'] == 'mesh':
            fig = cls._mesh_graph(params=params)

        elif params['surfacetype'] == 'spline':
            fig = cls._spline_graph(params=params, tables=tables)

        elif params['surfacetype'] in ['interactive_mesh',
                                       'interactive_spline']:

#%%
params['surfacetype'] = 'trisurf'
params, tables = Graph.surface_3d(params=vis.params, tables=vis.tables)

#%%
params['surfacetype'] = 'mesh'
params, tables = Graph.surface_3d(params=vis.params, tables=vis.tables)

#%%
params['surfacetype'] = 'spline'
params['scatter'] = True
params, tables = Graph.surface_3d(params=vis.params, tables=vis.tables)

#%%
params['surfacetype'] = 'interactive_mesh'
#params['scatter'] = True
params, tables = Graph.surface_3d(params=vis.params, tables=vis.tables)

#%%
params['surfacetype'] = 'interactive_spline'
#params['scatter'] = True
params, tables = Graph.surface_3d(params=vis.params, tables=vis.tables)

#%%
from volatility import Volatility
spx = Volatility()

#%%
spxdict = spx.__dict__

#%%
from market_data import Data
raw_web_data = Data._extract_web_data(params=spx.params)

#%%
import copy
spxcopy = copy.deepcopy(spx)

#%%
spx.params['raw_web_data'] = raw_web_data
spx.params = Data._read_web_data(params=spx.params)

#%%
import pandas as pd
# Create an empty DataFrame
spx.tables['full_data'] = pd.DataFrame()

# Make a list of all the dates of the DataFrames just stored
# in the default dictionary
spx.params['date_list'] = list(spx.params['option_dict'].keys())
spx.params, spx.tables = Data._process_options(params=spx.params, tables=spx.tables)

#%%
from market_data import Data
spx.params, spx.tables = Data.extractoptions(params=spx.params, tables=spx.tables)

#%%
spx.params, spx.tables = Data.transform(params=spx.params, tables=spx.tables)

#%%
spx.params, spx.tables = Data.combine(params=spx.params, tables=spx.tables)

#%%
from volatility import Volatility
aapl = Volatility(ticker='AAPL')

#%%
aapldict = aapl.__dict__

#%%
aapl.visualize(graphtype='line')

#%%
aapl.visualize(graphtype='scatter')

#%%
aapl.visualize(graphtype='surface', surfacetype='trisurf')

#%%
aapl.visualize(graphtype='surface', surfacetype='mesh')

#%%
aapl.visualize(graphtype='surface', surfacetype='spline')

#%%
aapl.visualize(graphtype='surface', surfacetype='interactive_mesh')

#%%
aapl.visualize(graphtype='surface', surfacetype='interactive_spline')

#%%
from volatility import Volatility
tsla = Volatility(ticker='TSLA')

#%%
tsladict = tsla.__dict__

#%%
params = tsla.params

#%%
from market_data import Data
aapl.params, aapl.tables = Data._process_options(aapl.params, aapl.tables)

#%%
aapl.params, aapl.tables = Data.transform(params=aapl.params, tables=aapl.tables)

#%%
aapl.params, aapl.tables = Data.combine(params=aapl.params, tables=aapl.tables)

#%%
from volvisualizer.volatility import Volatility
amzn = Volatility(ticker='AMZN')

#%%
amzn.linegraph()

#%%
amzn.scatter()

#%%
amzn.surface(surfacetype='spline')

#%%
from volvisualizer.volatility import Volatility
pfe = Volatility(ticker='PFE')

#%%
pfe.linegraph()

#%%
pfe.scatter()

#%%
pfe.surface(surfacetype='spline')

#%%
pfedict = pfe.__dict__

#%%
from volvisualizer.volatility import Volatility

#%%
nvda = Volatility(ticker='NVDA')

#%%
nvdadict = nvda.__dict__

#%%
params = nvda.params

#%%
params = msft.params

#%%
roundspot = (
    round(params['spot'] / params['divisor']) * params['divisor'])

#%%
divisor = 1

#%%
put_min = (round(params['spot']
                 * params['strike_limits'][0]
                 / params['divisor'])
           * params['divisor'])

#%%
put_strikes = list(
    range(put_min, roundspot, params['divisor']))

#%%
import numpy as np
pt2 = list(np.linspace(put_min, roundspot, 45))

#%%
divisor = 2.5
((roundspot - put_min) / divisor) + 1

#%%
divisor = params['divisor']

#%%
import numpy as np
pt3 = np.linspace(put_min, roundspot, int((roundspot - put_min) / divisor) + 1)

#%%
pt4 = np.linspace(roundspot, call_max, int((call_max - roundspot) / divisor) + 1)

#%%
divisor = 1.25

#%%
pfe = Volatility(ticker='PFE')

#%%
from volatility import Volatility
msft = Volatility(ticker='MSFT')

#%%
nvdadict = nvda.__dict__

#%%
strikes = set(nvda.tables['data']['Strike'])

#%%
strikes2 = set(msft.tables['data']['Strike'])

#%%
div2_5 = {x for x in strikes if x%(2.5)==0}

#%%
params = msft.params

#%%
divisor = 10

#%%
put_min = (round(params['spot']
                 * params['strike_limits'][0]
                 / params['divisor'])
           * params['divisor'])

call_max = (round(params['spot']
                  * params['strike_limits'][1]
                  / params['divisor'])
            * params['divisor'])

#%%
div10 = {x for x in strikes if (x%(10)==0 and put_min < x < call_max)}

#%%
avail_strikes = {}
for div in [0.5, 1, 1.25, 2.5, 5, 10]:
    avail_strikes[div] = len(
        {x for x in strikes if (x%(div)==0 and put_min < x < call_max)})

#%%
as2 = {}
for div in [0.5, 1, 1.25, 2.5, 5, 10]:
    as2[div] = len(
        {x for x in strikes2 if (x%(div)==0 and put_min < x < call_max)})

#%%
nvda = Volatility(ticker='NVDA')

#%%
max(avail_strikes, key=avail_strikes.get)

#%%
max(as2, key=as2.get)

#%%
import operator
max(as2.items(), key=operator.itemgetter(1))[0]

#%%

strikes = set(nvda.tables['data']['Strike'])

put_min = (round(params['spot']
                 * params['strike_limits'][0]
                 / divisor)
           * divisor)

call_max = (round(params['spot']
                  * params['strike_limits'][1]
                  / divisor)
            * divisor)


avail_strikes = {}
for div in [0.5, 1, 1.25, 2.5, 5, 10]:
    avail_strikes[div] = len(
        {x for x in strikes if (x%(div)==0 and put_min < x < call_max)})


as2 = avail_strikes

max([divisor for max_strike_count in [
    max(avail_strikes.values())] for divisor, strike_count in avail_strikes.items()
    if strike_count == max_strike_count])

#%%
msft.visualize(graphtype='line')

#%%
from market_data import Data
params = msft.params
msft.params, msft.tables = Data.combine(params=msft.params, tables=msft.tables)

#%%
msftdict = msft.__dict__

#%%
nvda.visualize(graphtype='surface', smooth=True)

#%%
from volatility import Volatility
spx = Volatility(ticker='^SPX', wait=0.5, q=0.013)

#%%
spxdict=spx.__dict__

#%%
spx.visualize(graphtype='line')

#%%
spx.visualize(graphtype='surface', smooth=True)

#%%
gld = Volatility(ticker='GLD')
glddict= gld.__dict__

#%%
gld.visualize(graphtype='line')

#%%
# Create an empty list
date_list = []


#%%
import datetime as dt
params = spx.params

# For each date in the url_dict
for key in params['url_dict'].keys():

    # Format that string as a datetime object
    key_date = dt.datetime.strptime(key, "%Y-%m-%d")

    # Store the year and month as a tuple in date_list
    date_list.append((key_date.year, key_date.month))


#%%
# Create a sorted list from the unique dates in date_list
sorted_dates = sorted(list(set(date_list)))


#%%
# Create an empty list
days_list = []

#%%
import calendar
# Create a calendar object
c = calendar.Calendar(firstweekday=calendar.SATURDAY)


#%%
# For each tuple of year, month in sorted_dates
for tup in sorted_dates:

    # Create a list of lists of days in that month
    monthcal = c.monthdatescalendar(tup[0], tup[1])

    # Extract the date corresponding to the 3rd Friday
    expiry = monthcal[2][-1]

    # Calculate the number of days until that expiry
    ttm = (expiry - dt.date.today()).days

    # Append this to the days_list
    days_list.append(ttm)

#%%
tables = spx.tables
full_day_list = set(tables['full_data']['Days'])

#%%
# For each unique number of days to expiry
for days_to_expiry in set(tables['data']['Days']):

    # if the expiry is not in the list of monthly expiries
    if days_to_expiry not in days_list:

        # Remove that expiry from the DataFrame
        tables['data'] = (
            tables['data'][tables['data']['Days']
                           != days_to_expiry])


#%%
from market_data import Data
par2, tab2 = Data.transform(params=spx.params, tables=spx.tables)

#%%
tab2['data']['AnnTTM'] = tab2['data']['TTM']*365

#%%
(tab2['data']['AnnTTM']).dtype

#%%
import math
tab2['data']['Days2'] = math.floor(tab2['data']['TTM']*365)

#%%
import pandas as pd
from datetime import date
ttm = (pd.to_datetime(tables['data']['Expiry'])
    - pd.to_datetime(date.today())) / (pd.Timedelta(days=1) * 365)

#%%
# Create Days to Maturity column
days = (tables['data']['TTM']*365)#.astype(int)

#%%
days_set = sorted(list(set(days)))

#%%
days_list = []
exps = []
for tup in sorted_dates:

    # Create a list of lists of days in that month
    monthcal = c.monthdatescalendar(tup[0], tup[1])

    # Extract the date corresponding to the 3rd Friday
    expiry = monthcal[2][-1]

    exps.append(expiry)

    # Calculate the number of days until that expiry
    ttm = (expiry - dt.date.today()).days

    # Append this to the days_list
    days_list.append(ttm)


#%%
tab2['data']['ttm1'] = (pd.to_datetime(tab2['data']['Expiry'])
    - pd.to_datetime(date.today())) / (pd.Timedelta(days=1) * 365)

#%%
tab2['data']['today'] = pd.to_datetime(dt.date.today())

#%%
import numpy as np
tab2['data']['ttm2'] = np.array([0.0]*len(tab2['data']))
for row in tab2['data']:
    tab2['data']['ttm2'][row] = (pd.to_datetime(tab2['data']['Expiry'][row]) - tab2['data']['today'][row]).days


#%%
# Create Days to Maturity column
tab2['data']['dt1'] = (tab2['data']['TTM']*365).astype(int)
tab2['data']['dt2'] = np.round(tab2['data']['TTM']*365, 0)
tab2['data']['dt3'] = tab2['data']['TTM']*365

#%%
spx.params, spx.tables = Data.transform(params=spx.params, tables=spx.tables)

#%%
spx.params, spx.tables = Data.combine(params=spx.params, tables=spx.tables)

#%%
amc = Volatility(ticker='AMC')

#%%
amc.visualize(graphtype='line')

#%%
nvda = Volatility(ticker='NVDA', wait=0.5)

#%%
nvda.visualize(graphtype='surface', surfacetype='spline', scatter=True, smoothing=True)

#%%
nvda.visualize(graphtype='surface',surfacetype='interactive_spline', smoothing=True, notebook=False, colorscale='Blues', scatter=True, opacity=0.8)