
import requests
import json
import asyncio
import websocket 
from .manager_config import manager_config
from .information import information

class APIadmin(object):
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.domain = 'http://47.90.247.3:34338/api/'
        self.refresh_token(username,password)
        self.config = manager_config(self.token,self.domain)
        self.info = information(self.token,self.domain)
        

    def refresh_token(self,username,password):
        login_url = self.domain + 'Auth'
        token = requests.post(login_url, json = {
            "username": username,
            "password": password
        })
        print(token.json())
        self.token = token.json()['token']
    

    def open_order(self,symbol, cmd, volume, price, slippage, stoploss, takeprofit):
        params = {
                "symbol":symbol,
                "cmd":cmd,
                "volume":volume,
                "price":price,
                "slippage":slippage,
                "stoploss":stoploss,
                "takeprofit":takeprofit
            }
        link = self.domain + 'OrderOpen'
        # print(self.token)
        response = requests.post(link, data = params, headers = {'TOKEN': f'{self.token}'})
        return response.json()

    def close_order(self,ticket, lots, price):
        params = {
                "ticket":ticket,
                "lots":lots,
                "price":price
            }
        link = self.domain + 'OrderClose'
        response = requests.post(link,data = params, headers = {'TOKEN': f'{self.token}'})
        return response.json()

    def opened_trades(self, login ):

        link = self.domain + 'TradesRequest' + '/' + str(login) 
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()

    def trades_user_history_by_datetime(self, login , start_time, end_time):

        link = self.domain + 'TradesUserHistory' + '/' + str(login) + '/' + start_time + '/' + end_time
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()

    def trades_user_history_by_unixtime(self, login, start_time_ctm, end_time_ctm):

        link = self.domain + 'TradesUserHistory2' + '/' + str(login) + '/' + str(start_time_ctm) + '/' + str(end_time_ctm)
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()

    def journal(self,start_time,end_time,equipment):
        link = self.domain + 'JournalRequest/0/' + start_time + '/' +end_time + '/' + equipment
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()    
 
    def symbol_ticks(self, symbol, start_time, end_time, equipment):
        link = self.domain + 'TicksRequest/' + symbol + '/' + start_time + '/' + end_time 
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()    

    def performance(self, startime):
        link = self.domain + 'PerformanceRequest/' + startime
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()    

    def server_time(self):
        link = self.domain + 'ServerTime'
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()

    def login_daily_report(self, login, start_time, end_time):
        link = self.domain + 'DailyReportsRequest/' + str(login) + '/' + start_time + '/' + end_time 
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()   
