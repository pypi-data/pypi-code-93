import pandas as pd
import numpy as np
from ...util.config import Configurator
from aip import AipNlp
from .keyword_parser import KeywordParser
import pkuseg
import json
import os
import pprint

class QaBot():
    def __init__(self):
        # Initialize Baidu NLP client SDK
        app_id = Configurator().config['bot']['baidu_aip']['app_id']
        api_key = Configurator().config['bot']['baidu_aip']['api_key']
        secret_key = Configurator().config['bot']['baidu_aip']['secret_key']
        self.baidu_client = AipNlp(app_id, api_key, secret_key)

        self.keyword_parser = KeywordParser()

        data_path = Configurator().config['bot']['data_path']

        # Initialize segmentation toolkit (pkuseg)
        self.seg = pkuseg.pkuseg(
            model_name = 'default', 
            user_dict = os.path.join(data_path, 'pkuseg_symbols.txt'),
            postag = True)

        self.keyword_type_dict = {}
        keywords = pd.read_csv(os.path.join(data_path, 'keywords.csv'))
        for keyword, msg_type in keywords.values:
            self.keyword_type_dict[keyword.strip()] = msg_type.strip()

        with open(os.path.join(data_path, 'fund_name.json'), 'r') as f:
            self.fund_info = json.load(f)
        
        with open(os.path.join(data_path, 'fund_inverted_index.json'), 'r') as f:
            self.inverted_index = json.load(f)
    
    def text_parser(self, text):
        # Default type is 'not_available'
        result = {
            'type': 'not_available',
            'data': {
                'message': text
            }
        }

        # doc: https://ai.baidu.com/ai-doc/NLP/zk6z52hds
        # sentiment: 表示情感极性分类结果，0:负向，1:中性，2:正向
        emotion = self.baidu_client.sentimentClassify(text)
        if 'items' in emotion:
            result['emotion'] = emotion['items']
        else:
            print(f'Baidu emotion analysis failed: {emotion}')

        word_tuples = self.seg.cut(text)

        # query fund (exact match)
        for tp in word_tuples:
            if tp[1] == 'n' and tp[0] in self.fund_info.keys():
                result['type'] = 'hqzx'
                result['data']['target'] = 'fund'
                result['data']['fund'] = self.fund_info[tp[0]]
                return result
        
        # query fund (fuzzy match)
        fm = self.fuzzy_match(word_tuples)
        if fm:
            values = list(fm.values())
            if len(values) > 0:
                result['type'] = 'hqzx'
                result['data']['target'] = 'fund'
                result['data']['fund'] = values[0]
                return result

        # keyword parse
        self.keyword_parser.parse(word_tuples, text, result)

         # If None is met above, try keyword matching
        for tp in word_tuples:
            if tp[0] in self.keyword_type_dict:
                result['type'] = self.keyword_type_dict[tp[0]]
                return result

        return result
    
    def fuzzy_match(self, word_tuples, threshold=3):
        phase = []
        index = 0
        length = len(word_tuples)
        while index < length:
            cur_idx = index
            tmp = []
            while 'n' in word_tuples[cur_idx][1] or 'v' in word_tuples[cur_idx][1] or 'j' in word_tuples[cur_idx][1] or 'a' in word_tuples[cur_idx][1]:
                tmp.append(word_tuples[cur_idx][0])
                cur_idx += 1
                if cur_idx >= length:
                    break

            if len(tmp) > 0:
                phase.append(tmp)
            index = cur_idx
            index += 1

        new_phase = []
        for key_ws in phase:
            length = len(key_ws)
            if length > 1:
                for i in range(1, length):
                    new_phase.append(key_ws[i:])
                for i in range(length, 0, -1):
                    new_phase.append(key_ws[:i])

        phase = phase + new_phase
        final_phase = [x for x in phase if len(x) > 1]

        records = []
        for key_ws in final_phase:
            key_len = len(key_ws)
            
            try:
                cur_dict = self.inverted_index[key_ws[0]].copy()
            except:
                continue
            
            for i in range(1, key_len):
                try:
                    tmp_dict = self.inverted_index[key_ws[i]].copy()
                except:
                    break
                
                removed_key = []
                for k in cur_dict.keys():
                    if k not in tmp_dict.keys():
                        removed_key.append(k)
                for k in removed_key:      
                    del cur_dict[k]
                        
                if len(cur_dict.keys()) <= 0:
                    break
            
            if len(cur_dict.keys()) <= 0 or i <= 1:
                continue
            
            records.append((cur_dict, len(cur_dict.keys())))
        
        if len(records) > 0:
            sr_records = sorted(records, key=lambda x: x[1])
            opt = sr_records[0][0]
            opt_num = sr_records[0][1]
            if opt_num > threshold:
                return None
            else:
                return opt
        else:
            return None


if __name__ == '__main__':
    qr = QaBot()
    while True:
        data = input('Q: ')
        result = qr.text_parser(data)
        pprint.pprint(result)
