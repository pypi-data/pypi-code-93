import logging
import requests
from requests.exceptions import RequestException


class Wrapper(object):

    def __init__(self, nodeHost, apiKey=''):
        self.nodeHost = nodeHost
        self.apiKey = apiKey

    def request(self, api, postData=''):
        headers = {}
        url = self.nodeHost + api
        if self.apiKey:
            headers['api_key'] = self.apiKey
        headerStr = ' '.join(['--header \'{}: {}\''.format(k, v) for k, v in headers.items()])
        try:
            if postData:
                headers['Content-Type'] = 'application/json'
                dataStr = '-d {}'.format(postData)
                logging.info(f'curl -X POST {headerStr} {dataStr} {url}')
                resp = requests.post(url, data=postData, headers=headers)
                print(f'curl -X POST {headerStr} {dataStr} {url}')
                return resp.json()
            else:
                logging.info(f'curl -X GET {headerStr} {url}')
                return requests.get(url, headers=headers).json()
        except RequestException as e:
            msg = f'Failed to get response: {e}'
            raise Exception(msg)
