import pandas as pd
import numpy as np
import os
import datetime
import traceback
import requests
import urllib3
from ...wrapper.mysql import RawDatabaseConnector
from .raw_data_helper import RawDataHelper
from ...view.raw_models import SinaStockMinute


class SinaStockDownloader(object):

    def __init__(self, data_helper, em_stock_list):
        req_batch_count = 5
        self.url_prefix = 'http://hq.sinajs.cn/list='
        self.headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 '
                                      '(KHTML, like Gecko) Version/13.0.5 Safari/605.1.15')}

        self._data_helper = data_helper
        self.sina_stock_list = self.parse_em_stock_list(em_stock_list)
        self.sina_stock_req_batch = self.parse_sina_stock_req_batch(
            self.sina_stock_list, req_batch_count)

    def parse_em_stock_list(self, em_stock_list):
        sina_stock_list = []
        for em_stock_id in em_stock_list:
            sina_stock_id = self.em_stock_id_to_sina(em_stock_id)
            if sina_stock_id:
                sina_stock_list.append(sina_stock_id)

        return sina_stock_list

    def parse_sina_stock_req_batch(self, sina_stock_list, req_batch_count):
        sina_stock_req_content_list = []
        total_count = len(sina_stock_list)
        if req_batch_count < 1 or total_count < req_batch_count:
            print(f'Invalid stock count({total_count}) or batch count({req_batch_count})')
            return None

        req_batch_size = int(total_count / req_batch_count)
        start = 0
        for batch_index in range(req_batch_count):
            if batch_index == req_batch_count - 1:
                end = total_count
            else:
                end = start + req_batch_size
            sina_stock_req_batch_content = ','.join(
                sina_stock_list[start: end])
            start += req_batch_size
            sina_stock_req_content_list.append(sina_stock_req_batch_content)

        return sina_stock_req_content_list

    def sina_stock_id_to_em(self, sina_stock_id):
        if sina_stock_id.startswith('sh'):
            return f'{sina_stock_id[2:]}.SH'
        elif sina_stock_id.startswith('sz'):
            return f'{sina_stock_id[2:]}.SZ'
        else:
            print(f'Unrecognized sina stock code {sina_stock_id}')
            return None

    def em_stock_id_to_sina(self, em_stock_id):
        parts = em_stock_id.split('.')
        if len(parts) != 2:
            print(f'Unrecognized stock code {em_stock_id}')
            return None

        if parts[1] == 'SH':
            return f'sh{parts[0]}'
        elif parts[1] == 'SZ':
            return f'sz{parts[0]}'
        else:
            print(f'Unrecognized stock code {em_stock_id}')
            return None

    def parse_rsp_line(self, line):
        '''
        Below line is a sample:
        var hq_str_sh600687="*ST刚泰,1.360,1.340,1.410,1.410,1.320,1.410,0.000,25705789,35407399.000,86885,1.410,537100,1.400,316000,1.390,271900,1.380,187200,1.370,0,0.000,0,0.000,0,0.000,0,0.000,0,0.000,2020-08-06,15:00:01,00,";
        '''
        if not line:
            return None

        parts = line.split('=')
        if len(parts) != 2:
            print(f'Data error: {line}')
            return None
        sina_stock_id = parts[0].split('_')[-1]
        em_stock_id = self.sina_stock_id_to_em(sina_stock_id)

        right_parts = parts[1].split(',')
        if len(right_parts) < 33:
            print(f'Data error: {line}')
            return None

        if right_parts[32].endswith('";'):
            right_parts[32] = right_parts[32][:-2]

        if right_parts[32] != '00' and right_parts[32] != '00':
            print(f'Status of stock {em_stock_id} is not valid({right_parts[32]})')
            return None

        price = float(right_parts[3])
        dt = datetime.datetime.strptime(f'{right_parts[30]} {right_parts[31]}', '%Y-%m-%d %H:%M:%S')
        
        return [em_stock_id, price, dt]

    def sina_stock_minute(self, to_save):
        try:
            stock_prices = []
            for req_content in self.sina_stock_req_batch:
                url = f'{self.url_prefix}{req_content}'

                r = requests.get(url, headers=self.headers)
                lines = r.text.split('\n')
                for line in lines:
                    result = self.parse_rsp_line(line)
                    if result:
                        stock_prices.append(result)

            df = pd.DataFrame(stock_prices, columns=['stock_id', 'close', 'datetime'])
            if to_save:
                try:
                    self._data_helper._upload_raw(df, SinaStockMinute.__tablename__)
                except Exception as e:
                    print(e)
                    traceback.print_exc()
            return df
        except Exception as e:
            print(e)
            traceback.print_exc()
            return None
