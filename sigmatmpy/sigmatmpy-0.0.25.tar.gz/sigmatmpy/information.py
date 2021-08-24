
import requests
import json
import asyncio
import websocket 

class information(object):
    def __init__(self,token,domain):
        self.token = token
        self.domain = domain


    def all_groups_info(self):
        link = self.domain + 'GroupRequest'
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()    

    def specific_groups_info(self, groups):
        groups = ','.join(groups)
        link = self.domain + 'GroupRequest/' + groups
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()    

    def all_users_info(self):
        link = self.domain + 'UsersRequest'
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()

    def user_info(self, login):
        link = self.domain + 'UsersRequest/' +str(login)
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()

    def online_info(self, login):
        link = self.domain + 'OnlineRequest'
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()

    def account_info(self, login):

        link = self.domain + 'Margin' + '/' + str(login) 
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()

    def symbol_info(self, symbol):

        link = self.domain + 'SymbolsGet' + '/' + symbol
        response = requests.get(link, headers = {'TOKEN': f'{self.token}'})
        return response.json()