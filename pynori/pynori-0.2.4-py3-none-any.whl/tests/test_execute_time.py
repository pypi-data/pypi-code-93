
"""
    Usage:
        python -m pynori.tests.test_execute_time
"""

import os
import sys
import random
from pathlib import Path

from konlpy.tag import Hannanum
from konlpy.tag import Kkma
from konlpy.tag import Komoran
from konlpy.tag import Okt

from pynori.korean_analyzer import KoreanAnalyzer
from pynori.utils import *


file_path = Path(os.path.dirname(os.path.abspath(__file__)))
workspace_path = file_path.parent.parent.parent
dataset_path = workspace_path.joinpath('dataset')
pynori_test_path = dataset_path.joinpath('pynori_test')

news_path = str(pynori_test_path) + '/news_body_1m.csv'
shopping_path = str(pynori_test_path) + '/shopping_title_1m.csv'

#print(workspace_path)
#print(shopping_path)

@calc_execution_time
def run_analyzer_with_data(analyzer_obj, data):
    cname = analyzer_obj.__class__.__name__
    print(cname)
    err_cnt = 0 
    for x in data:
        try:
            if cname == 'KoreanAnalyzer':
                analyzer_obj.do_analysis(x)
            else:
                analyzer_obj.pos(x)
        except:
            err_cnt += 1
            pass
    print('err_cnt: ', err_cnt)
    return


if __name__ == '__main__':

    hannanum = Hannanum()
    kkma = Kkma()
    komoran = Komoran()
    okt = Okt()
    nori = KoreanAnalyzer(decompound_mode='MIXED',
                          discard_punctuation=True,
                          output_unknown_unigrams=True,
                          pos_filter=False,
                          stop_tags=['JKS', 'JKB', 'VV', 'EF'])

    news_data = load_lines(news_path)
    shop_data = load_lines(shopping_path)
    data = news_data + shop_data
    random.seed(7)
    data = random.sample(data, 1000000)
    print('number of total data: ', len(data))
    print()

    for idx in [
        100, 
        1000, 
        10000, 
        100000, 
        1000000
    ]:
        sample_data = data[:idx]
        print('\n number of sample data: ', len(sample_data))

        for analyzer in [hannanum, kkma, komoran, okt, nori]:
            run_analyzer_with_data(analyzer, sample_data)
            print()