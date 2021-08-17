
import requests
import json
import asyncio
import websocket 

class manager_config(object):
    def __init__(self,token,domain):
        self.token = token
        self.domain = domain

    def group_config(self):
        link = self.domain + 'CfgRequestGroup'
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()
    
    def holiday_config(self):
        link = self.domain + 'CfgRequestHoliday'
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()
    
    def symbol_config(self):
        link = self.domain + 'CfgRequestSymbol'
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()   

    def specific_group_config(self,group):
        link = self.domain + 'CfgRequestGroup/' + group
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()   

    def gateway_markup_config(self):
        link = self.domain + 'CfgRequestGatewayMarkup'
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()
            
    def dateway_account_config(self):
        link = self.domain + 'CfgRequestGatewayAccount'
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()

    def gateway_rule_config(self):
        link = self.domain + 'CfgRequestGatewayRule'
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()    

    def symbol_group_config(self):
        link = self.domain + 'CfgRequestSymbolGroup'
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()    

