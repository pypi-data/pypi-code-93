#!/usr/bin/python3

# trading212api
# Original GitHub project:
# https://github.com/auino/trading212api

import copy
import seleniumprocessor
from selenium.webdriver.common.keys import Keys

# declaration of classes of exceptions

class ModeNotConfiguredException(Exception): pass
class MarketClosedException(Exception): pass
class LowerPriceException(Exception): pass
class HigherPriceException(Exception): pass

# internal static variables declaration

HOMELOAD_TO = 5
PAGELOAD_TO = 1
PAGEJS_TO = 0.5

FILTER_REAL = 'live'
FILTER_PRACTICE = 'demo'

URL_LOGIN = 'https://www.trading212.com/login'
URL_HOME_BASE = 'https://{}.trading212.com'
URL_HOME = URL_HOME_BASE

# declaration of processes

process_portfolio = [
	{'class_name':'home-icon', 'action':'click', 'sleep':PAGELOAD_TO, 'filter':FILTER_PRACTICE},
	{'class_name':'positions-table-item', 'action':'foreach', 'filter':FILTER_PRACTICE, 'action_parameters':[
		{'class_name':'instrument-name', 'action':'store_text', 'action_parameters':'name'},
		{'class_name':'quantity', 'action':'store_text', 'action_parameters':'shares'},
		{'class_name':'instrument-name', 'action':'click', 'sleep':PAGELOAD_TO},
		{'class_name':'quantity-and-price', 'action':'store_text', 'action_parameters':'quantity_and_price_full', 'context':'whole_page'},
		{'class_name':'formatted-price', 'action':'store_text', 'action_parameters':'value'},
		{'class_name':'position-result', 'action':'store_text', 'action_parameters':'return_value', 'context':'whole_page'},
	]},
	{'class_name':'portfolio-icon', 'action':'click', 'sleep':PAGELOAD_TO, 'filter':FILTER_REAL},
	{'class_name':'investment-item', 'action':'foreach', 'filter':FILTER_REAL, 'action_parameters':[
		{'class_name':'instrument-name', 'action':'store_text', 'action_parameters':'name'},
		{'class_name':'instrument-name', 'action':'click', 'sleep':PAGEJS_TO},
		{'class_name':'ticker', 'action':'store_text', 'action_parameters':'ticker', 'context':'whole_page'},
		{'class_name':'total-value', 'action':'store_text', 'action_parameters':'value'},
		{'class_name':'quantity', 'action':'store_text', 'action_parameters':'shares'},
		{'class_name':'return', 'action':'store_text', 'action_parameters':'return'}
	]}
]

process_stockinfo = [
	{'class_name':'search-icon', 'action':'click', 'sleep':PAGELOAD_TO},
	{'class_name':'search-input', 'action':'click', 'sleep':PAGEJS_TO},
	{'class_name':'search-input', 'index':1, 'action':'send_keys', 'action_parameters':'{TICKER}', 'sleep':PAGELOAD_TO},
	{'class_name':'item-wrapper', 'action':'click', 'sleep':PAGELOAD_TO},
	{'class_name':'sidebar-header-option', 'index':0, 'action':'click', 'sleep':PAGEJS_TO},
	{'class_name':'trading-chart-layout-button', 'action':'click', 'sleep':PAGELOAD_TO, 'filter':FILTER_REAL},
	{'class_name':'instrument-name', 'action':'store_text', 'action_parameters':'name'},
	{'class_name':'ticker', 'action':'store_text', 'action_parameters':'ticker'},
	{'class_name':'market-status', 'action':'store_text', 'action_parameters':'market_status_full'},
	{'class_name':'price-buy', 'action':'store_text', 'action_parameters':'full_price_buy', 'filter':FILTER_PRACTICE},
	{'class_name':'price-sell', 'action':'store_text', 'action_parameters':'full_price_sell', 'filter':FILTER_PRACTICE},
	{'class_name':'priceBuy', 'action':'store_text', 'action_parameters':'full_price_buy', 'filter':FILTER_REAL},
	{'class_name':'priceSell', 'action':'store_text', 'action_parameters':'full_price_sell', 'filter':FILTER_REAL}
]

process_buy = [
	{'class_name':'trading-button', 'index':1, 'action':'click', 'sleep':PAGEJS_TO, 'filter':FILTER_REAL},
	{'class_name':'new-order-icon', 'action':'click', 'sleep':PAGEJS_TO, 'filter':FILTER_PRACTICE},
	{'class_name':'instrument-price', 'index':3, 'action':'click', 'sleep':PAGEJS_TO},
	{'class_name':'input', 'index':1, 'action':'click', 'sleep':PAGEJS_TO, 'filter':FILTER_PRACTICE},
	{'class_name':'input', 'action':'click', 'sleep':PAGEJS_TO, 'filter':FILTER_REAL},
	{'class_name':'input', 'index':1, 'action':'empty_value', 'sleep':PAGEJS_TO, 'filter':FILTER_PRACTICE},
	{'class_name':'input', 'index':1, 'action':'send_keys', 'action_parameters':Keys.BACKSPACE, 'filter':FILTER_PRACTICE},
	{'class_name':'input', 'index':1, 'action':'send_keys', 'action_parameters':"{AMOUNT}", 'sleep':PAGEJS_TO, 'filter':FILTER_PRACTICE},
	{'class_name':'input', 'action':'send_keys', 'action_parameters':"{AMOUNT}", 'sleep':PAGEJS_TO, 'filter':FILTER_REAL},
	{'class_name':'accent-button', 'index':2, 'action':'click', 'sleep':PAGEJS_TO, 'filter':FILTER_PRACTICE},
	{'class_name':'accent-button', 'action':'click', 'sleep':PAGEJS_TO, 'filter':FILTER_REAL}
]

process_sell = copy.deepcopy(process_buy)
for i in range(0, len(process_sell)):
	if process_sell[i].get('class_name') == 'trading-button': process_sell[i]['index'] -= 1
	if process_sell[i].get('class_name') == 'instrument-price': process_sell[i]['index'] -= 1

# internal functions declaration

# returns the content of the URL_HOME variable, by raising an exception if not properly configured (mode is not configured)
def get_urlhome():
	global URL_HOME
	if not FILTER_REAL in URL_HOME and not FILTER_PRACTICE in URL_HOME: raise ModeNotConfiguredException()
	return URL_HOME

# function used to tell if a filter f passes or not
def checkfilterpassed(f):
	return f in get_urlhome()

# external functions declaration

# function to enable real/live mode
def enable_real_mode():
	global URL_HOME
	URL_HOME = URL_HOME_BASE.format(FILTER_REAL)

# function to enable practice/demo mode
def enable_practice_mode():
	global URL_HOME, PAGELOAD_TO, PAGEJS_TO
	URL_HOME = URL_HOME_BASE.format(FILTER_PRACTICE)
	PAGELOAD_TO *= 3
	PAGEJS_TO *= 3

# initiates a connection to URL_HOME
def initiate_connection(webdriverfile, loginrequired=True):
	return seleniumprocessor.initiate_connection(webdriverfile, get_urlhome(), HOMELOAD_TO, loginrequired)

# retrieves information from a stock with a given ticker, optionally, returning home at the begin/end of the method
def get_stock_info(brw, ticker, backtohome_begin=True, backtohome_end=True):
	tmp_process_stockinfo = copy.deepcopy(process_stockinfo)
	for i in range(0, len(tmp_process_stockinfo)):
		if tmp_process_stockinfo[i].get('action_parameters') is None: continue
		if '{TICKER}' in tmp_process_stockinfo[i].get('action_parameters'): tmp_process_stockinfo[i]['action_parameters'] = str(ticker)
	info = seleniumprocessor.run_process(brw, get_urlhome(), HOMELOAD_TO, tmp_process_stockinfo, backtohome_begin, backtohome_end, checkfilterpassed_callback=checkfilterpassed)
	# processing output for better presentation
	if '\n' in info.get('full_price_buy'): info['full_price_buy'] = info.get('full_price_buy').split('\n')[1]
	info['valuta'] = info.get('full_price_buy')[0]
	info['price_buy'] = float(info.get('full_price_buy')[1:].replace(',', ''))
	info['price_sell'] = float(info.get('full_price_sell')[1:].replace(',', ''))
	info['market_open'] = 'open' in info.get('market_status_full').lower()
	del info['full_price_buy']
	del info['full_price_sell']
	del info['market_status_full']
	return info

# retrieves information on the current portfolio
def get_portfolio(brw):
	portfolio = seleniumprocessor.run_process(brw, get_urlhome(), HOMELOAD_TO, process_portfolio, checkfilterpassed_callback=checkfilterpassed)
	# processing output for better presentation
	portfolio = portfolio.get('list')
	for i in range(0, len(portfolio)):
		if portfolio[i].get('quantity_and_price_full') is None:
			portfolio[i]['valuta'] = portfolio[i].get('value')[0]
			portfolio[i]['value'] = portfolio[i].get('value')[1:]
		else:
			portfolio[i]['valuta'] = portfolio[i].get('quantity_and_price_full').split(' ')[2][0]
			portfolio[i]['value'] = portfolio[i].get('quantity_and_price_full').split(' ')[2][1:]
			del portfolio[i]['quantity_and_price_full']
		portfolio[i]['value'] = float(portfolio[i].get('value').replace(',', ''))
		if ' ' in portfolio[i].get('shares'): portfolio[i]['shares'] = float(portfolio[i].get('shares').split(' ')[0].replace(',', ''))
		if not portfolio[i].get('return_value') is None:
			portfolio[i]['return'] = '{} ({}%)'.format(portfolio[i].get('return_value'), float(float(portfolio[i].get('return_value')[1:]) / float(portfolio[i].get('value')) * 100))
			del portfolio[i]['return_value']
		if not portfolio[i].get('return') is None:
			portfolio[i]['return_percentage'] = float(portfolio[i].get('return').split('(')[1].split('%')[0])
		portfolio[i]['return'] = float(portfolio[i].get('return').split(' ')[0][1:])
		return portfolio

# buys a stock identified by its own ticket, specifying the amount to spent (in current valuta) and an optional maximum price
def buy(brw, ticker, amount, max_price=None):
	info = get_stock_info(brw, ticker, backtohome_begin=True, backtohome_end=False)
	if not info.get('market_open'): raise MarketClosedException()
	if max_price != None and info.get('price_buy') > float(max_price): raise HigherPriceException()
	# fixing the amount to be filled in
	tmp_process_buy = copy.deepcopy(process_buy)
	for i in range(0, len(tmp_process_buy)):
		if tmp_process_buy[i].get('action_parameters') is None: continue
		if '{AMOUNT}' in tmp_process_buy[i].get('action_parameters'): tmp_process_buy[i]['action_parameters'] = str(amount)
	seleniumprocessor.run_process(brw, get_urlhome(), HOMELOAD_TO, tmp_process_buy, backtohome_begin=False, checkfilterpassed_callback=checkfilterpassed)
	return True

# sells a stock identified by its own ticket, specifying the amount in terms of number of stocks to sell and an optional minimum price
def sell(brw, ticker, amount=None, min_price=None):
	info = get_stock_info(brw, ticker, backtohome_begin=True, backtohome_end=False)
	if not info.get('market_open'): raise MarketClosedException()
	if min_price != None and info.get('price_sell') < float(min_price): raise LowerPriceException()
	# fixing the amount to be filled in
	tmp_process_sell = copy.deepcopy(process_sell)
	for i in range(0, len(tmp_process_sell)):
		if tmp_process_sell[i].get('action_parameters') is None: continue
		if '{AMOUNT}' in tmp_process_sell[i].get('action_parameters'):
			if amount is None: del tmp_process_sell[i]
			else: tmp_process_sell[i]['action_parameters'] = str(amount)
	seleniumprocessor.run_process(brw, get_urlhome(), HOMELOAD_TO, tmp_process_sell, backtohome_begin=False, checkfilterpassed_callback=checkfilterpassed)
	return True
