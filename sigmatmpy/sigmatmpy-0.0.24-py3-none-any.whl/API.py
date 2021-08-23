name = "sigmatmpy"
import requests
import json
import asyncio
import websocket 
import datetime
import time
from .error import InputError,InvalidAuthorizationError

class API(object):
    def __init__(self,username,password):
        '''Login API via username and password
        
        Parameters:
        username: your username,
        password: your password,
        
        Returns:
        object: API class,
        '''
        self.username = username
        self.password = password
        self.domain = 'https://manager.sigmarisk.com.au:34335/api/'
        self.domain_ws = 'wss://manager.sigmarisk.com.au:34335/api/PriceStream/'
        self.refresh_token(username,password)
        self.price = {}
        self.bars = {}
        

    def refresh_token(self,username,password):
        login_url = self.domain + 'Auth'
        token = requests.post(login_url, json = {
            "username": username,
            "password": password
        })
        if token.json()['token'] == '':
            raise KeyError('Invalid username or password')
        self.token = token.json()['token']

    def open_order(self,symbol, cmd, volume, price, slippage, stoploss, takeprofit, comment):
        '''Open new order
        
        Parameters:
        symbol: Symbol for trading,
        cmd: Operation type: 0 = buy, 1 = sell, 2 = buylimit, 3 = buystop, 4 = selllimit, 5 = sellstop,
        volume: Number of lots,
        price: Order price,
        slippage: Maximum price slippage for buy or sell orders,
        stoploss: Stop loss level,
        takeprofit: Take profit level,
        comment: Order comment text,
        
        Returns:
        dict: result of open order,
        '''
        if cmd not in [0,1,2,3,4,5] or volume <= 0 or price <=0 or slippage < 0 or stoploss < 0 or takeprofit < 0:
            raise InputError('Invalid input(s)')
        params = {"symbol":symbol,"cmd":cmd,"volume":volume,"price":price,"slippage":slippage,"stoploss":stoploss,"takeprofit":takeprofit,"comment":comment}

        link = self.domain + 'OrderOpen'
        
        # print(self.token)
        try:
            response = requests.post(link, data = json.dumps(params), headers = {'TOKEN': f'{self.token}','Content-Type' : 'application/json; charset=utf-8'})
        except:
            time.sleep(1)
            response = requests.post(link, data = json.dumps(params), headers = {'TOKEN': f'{self.token}','Content-Type' : 'application/json; charset=utf-8'})
        return response.json()

    def modify_order(self, ticket, price, stoploss, takeprofit, expiration=0):
        '''Open new order
        
        Parameters:
        symbol: Symbol for trading,
        cmd: Operation type: 0 = buy, 1 = sell, 2 = buylimit, 3 = buystop, 4 = selllimit, 5 = sellstop,
        volume: Number of lots,
        price: Order price,
        slippage: Maximum price slippage for buy or sell orders,
        stoploss: Stop loss level,
        takeprofit: Take profit level,
        comment: Order comment text,
        
        Returns:
        dict: result of open order,
        '''
        if ticket<=0 or price <=0 or stoploss < 0 or takeprofit < 0 or expiration<0:
            raise InputError('Invalid input(s)')
        params = {"ticket":ticket,"price":price,"stoploss":stoploss,"takeprofit":takeprofit,"expiration":expiration}

        link = self.domain + 'OrderModify'
        
        # print(self.token)
        try:
            response = requests.post(link, data = json.dumps(params), headers = {'TOKEN': f'{self.token}','Content-Type' : 'application/json; charset=utf-8'})
        except:
            time.sleep(1)
            response = requests.post(link, data = json.dumps(params), headers = {'TOKEN': f'{self.token}','Content-Type' : 'application/json; charset=utf-8'})
        return response.json()

    def close_order(self, ticket, lots = None, price = None):
        '''Close an existing order
        
        Parameters:
        ticket: Unique number of the order ticket,
        lots: Number of lots,
        price: Closing price

        Returns:
        dict: result of open order,
        '''
        if lots==None and price==None:
            params = {"ticket":ticket}
        elif lots <= 0 or price <0:
            raise InputError('Invalid input(s)')
        else:
            params = {"ticket":ticket,"lots":lots,"price":price}
        link = self.domain + 'OrderClose'
        try:
            response = requests.post(link,data = json.dumps(params), headers = {'TOKEN': f'{self.token}','Content-Type' : 'application/json; charset=utf-8'})
        except:
            time.sleep(1)
            response = requests.post(link,data = json.dumps(params), headers = {'TOKEN': f'{self.token}','Content-Type' : 'application/json; charset=utf-8'})
        return response.json()

    def trades_history_by_datetime(self, start_time, end_time):
        '''Get trade history using datetime string 'YYYY-mm-dd HH:MM:SS'
        
        Parameters: 
        start_time: start time for requested period,
        end_time: end time for requested period,

        Returns:
        list: list of trades in json
        '''
        try:
            datetime.datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')
            datetime.datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise InputError('Invalid datetime format')

        link = self.domain + 'TradesUserHistory' + '/' + start_time + '/' + end_time
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        
        return response.json()

    def trades_history_by_unixtime(self, start_time_ctm, end_time_ctm):
        '''Get trade history using unixtime 
        
        Parameters: 
        start_time_ctm: start time for requested period,
        end_time_ctm: end time for requested period

        Returns:
        list: list of trades in json
        '''
        if start_time_ctm <= 0 or end_time_ctm <= 0:
            raise InputError('Invalid unix timestamp')

        link = self.domain + 'TradesUserHistory2' + '/' + str(start_time_ctm) + '/' + str(end_time_ctm)
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        
        return response.json()

    def live_trades(self):
        '''Get current live trades  
        
        Parameters: 
        start_time_ctm: start time for requested period
        end_time_ctm: end time for requested period

        Returns:
        list: list of trades in json
        '''

        link = self.domain + 'TradesRequest'
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        if type(response.json()) != list:
            print('Request live trades faild')
            return False
        return response.json()

    def account_info(self):
        '''Get account_info 
        
        Returns:
        json: account information
        '''

        link = self.domain + 'Margin' + '/'
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()
    
    def ping(self):
        link = self.domain + 'ServerTime'
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.elapsed.total_seconds()

    def symbol_info(self, symbol):
        '''Get information of one symbol 
        
        Returns:
        json: symbol information
        '''

        link = self.domain + 'SymbolsGet' + '/' + symbol
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            raise InputError('Invalid symbol')
    
    def initialize_price_stream(self, symbol):
        '''
        initialize price stream of one symbol

        Parameters: 
        symbol: symbol that needs to be initialized
        '''
        self.price[symbol] = websocket.create_connection(self.domain_ws + symbol,header={'TOKEN': self.token})


    def current_price(self, symbol):
        '''
        current price of one symbol that already initialized

        Parameters: 
        symbol: target symbol
        '''
        try:
            result = self.price[symbol].recv()
        except:
            self.price[symbol] = websocket.create_connection(self.domain_ws + symbol,header={'TOKEN': self.token})
            result = self.price[symbol].recv()

        return json.loads(result)
    
    def server_time(self):
        '''
        get current server time

        Returns:
        string: server time
        '''
        link = self.domain + 'ServerTime'
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()

    def bar_chart(self, symbol, timeframe):
        '''
        get bar data of one symbol with timeframe

        Returns:
        list: list of bar data dictionaries
        '''
        link = self.domain + 'ChartRequest/' + symbol + '/' + str(timeframe)
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        digit = self.symbol_info(symbol)['Digits']
        try:
            result = response.json()
        except json.decoder.JSONDecodeError:
            raise InputError('Invalid inputs')
        if len(result) == 0:
            raise KeyError('Invalid inputs')
        for key in range(len(result)):
            result[key]['Open'] = round(result[key]['Open'] * (10**-digit), digit)
            result[key]['Close'] = round((result[key]['Close'] * (10**-digit)) + result[key]['Open'], digit)
            result[key]['High'] = round((result[key]['High'] * (10**-digit)) + result[key]['Open'], digit)
            result[key]['Low'] = round((result[key]['Low'] * (10**-digit)) + result[key]['Open'], digit)
        return result

    def check_new_bar(self,symbol,timeframe):
        '''
        Check new bar occurance

        Returns:
        bool: return true when new bar occur
        '''
        if timeframe not in self.bars.keys():
            self.bars[timeframe] = self.bar_chart(symbol, timeframe)[-1]['Ctm']
            return True
        elif self.bar_chart(symbol,timeframe)[-1]['Ctm'] == self.bars[timeframe]:
            return False
        else:
            self.bars[timeframe] = self.bar_chart(symbol,timeframe)[-1]['Ctm'] 
            return True