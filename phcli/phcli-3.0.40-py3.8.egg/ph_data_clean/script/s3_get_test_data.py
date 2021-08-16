# -*- coding: utf-8 -*-

import os
import yaml
from phcli.ph_data_clean.util.yaml_utils import load_by_file

LOCAL_CACHE_DIR = r'../../../file/ph_data_clean/s3_primitive_data/'
TEST_CACHE_DIR = r'../../../file/ph_data_clean/s3_test_data/'


def get_s3_valid_data(s3_data):
    """
    筛选出s3非空数据

    :param s3_data: 爬取的s3所有数据: type = list
    :return: s3_valid_data: 爬取的s3非空数据: type = list
             null_data_name: 检测出的测试无法使用的空数据路径和sheet name: type = list
    """
    null_data_lst = []
    null_data_name = []
    s3_valid_data = []
    ignore = False

    for data in s3_data:
        for values in data['data'].values():
            if len(values.keys()) <= 1:
                ignore = True
        if len(data['data']) <= 9 or ignore == True:
            null_data_name.append(data['file'])
            # null_data_name.append(data['sheet'])
            null_data_lst.append(data)
            continue
        flag = True
        for key in data['data'].keys():
            if not flag:
                continue
            if 'Unnamed' in key.split(':')[0]:
                null_data_name.append(data['file'])
                null_data_name.append(data['sheet'])
                null_data_lst.append(data)
                flag = False
                continue

    for data in s3_data:
        if data not in null_data_lst:
            s3_valid_data.append(data)

    return s3_valid_data, null_data_name


def get_test_data(s3_valid_data):
    """
    生成可用测试数据

    :param s3_valid_data: 爬取的s3非空数据 type = list
    :return: test_data_lst: 最终测试数据 type = list
    """
    test_data_lst = []
    for data in s3_valid_data:
        for i in (0, 1):
            test_data = {'data': {},
                         'metadata': {'fileName': data['file'],
                                      'providers': [data['company'], data['source']],
                                      'sheetName': data['sheet']}}
            for key in data['data'].keys():
                test_data['data'][key] = data['data'][key][i]

            # 加上tag
            test_data['data']['_Tag'] = 'yes'

            test_data_str = str(test_data['data'])
            test_data['data'] = test_data_str

            meta_data_str = str(test_data['metadata'])
            test_data['metadata'] = meta_data_str

            test_data_lst.append(test_data)
    return test_data_lst


def append_test_data(test_data_lst):
    """
    把可用数据写入指定名称的yaml文件

    :param test_data_lst: 拆开的可用数据
    """
    if sub.split('.')[0] + '-test.yaml' not in os.listdir(TEST_CACHE_DIR):
        with open(test_file, 'a', encoding='UTF-8') as file:
            yaml.dump(test_data_lst, file, default_flow_style=False, encoding='utf-8', allow_unicode=True)


if __name__ == '__main__':
    #     for sub in os.listdir(LOCAL_CACHE_DIR):
    sub = 'CHC-Servier.yaml'
    file = LOCAL_CACHE_DIR + sub
    print('筛选：')
    print(file)
    test_file = TEST_CACHE_DIR + sub.split('.')[0] + '-test.yaml'
    print('存入：')
    print(test_file)
    file_lst = load_by_file(file)
    s3_valid_data, null_data_name = get_s3_valid_data(file_lst)
    test_data_lst = get_test_data(s3_valid_data)
    append_test_data(test_data_lst)
    print('finish')
