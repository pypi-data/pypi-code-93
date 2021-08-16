# -*- coding: utf-8 -*-

import boto3
import copy
import pandas as pd

from phcli.ph_data_clean.util.yaml_utils import append_to_file, load_by_dir


BUCKER_NAME = 'ph-origin-files'
LOCAL_CACHE_DIR = r'../../../file/ph_data_clean/s3_primitive_data/'
filter_dir = ['OTHERS']

KEEP_ROW_COUNT = 2

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')


def get_all_file_path():
    """
    获取指定桶中的所有文件信息

    :return: [[filter_file_lst], [all_file_path], [err_file_path]]
        filter_file_lst: 被过滤掉的文件信息
        all_file_path: 可爬取的文件信息
        err_file_path: 无法解析路径的文件信息
    """
    filter_file_lst = []
    all_file_lst = []
    err_file_lst = []

    bucket = s3.Bucket(BUCKER_NAME)
    for obj in bucket.objects.all():
        obj_key = obj.key
        obj_key_lst = obj_key.split("/")

        # 目录过滤掉
        if obj_key.endswith("/"):
            continue

        # 不需要的目录过滤掉
        if obj_key_lst[0] in filter_dir:
            filter_file_lst.append(obj_key)
            continue

        # 正常处理获取文件信息
        if len(obj_key_lst) == 3 and obj_key_lst[2].endswith(".xlsx") or obj_key_lst[2].endswith(".xls"):
            all_file_lst.append({
                "source": repr(obj_key_lst[0]).strip("'"),
                "company": repr(obj_key_lst[1]).strip("'"),
                "file": repr(obj_key).strip("'"),
            })
            continue

        # 如果到这里，证明文件路径问题，加入错误流程
        err_file_lst.append(obj_key)

    return filter_file_lst, all_file_lst, err_file_lst


def load_cache_data():
    """
     获取本地缓存的文件信息

     :return: cache_data_lst: 已经处理的文件信息
     """
    return load_by_dir(LOCAL_CACHE_DIR)


def append_cache_data(parse_sheet_lst):
    """
    向文件中追加新解析的文件信息

    :param parse_file_lst: 解析成功的页信息
    """
    if len(parse_sheet_lst):
        append_to_file(parse_sheet_lst, f'''{LOCAL_CACHE_DIR}/{parse_sheet_lst[0]["source"]}-{parse_sheet_lst[0]["company"]}.yaml''')


def get_s3_increment(cache_data_lst, s3_all_file_lst):
    """
    获取 s3 上的增量文件，对于同名但重新上传的文件暂不支持重新处理

    :param cache_data_lst: 缓存的文件列表
    :param s3_all_file_lst: s3 上所有可解析的文件列表

    :return: increment_file_lst: 增量文件列表
    """
    # 利用 map 去重当前缓存的所有 file
    cache_file_map = {}
    for cache_data in cache_data_lst:
        source = cache_data['source']
        company = cache_data['company']

        # 记录 source
        if source not in cache_file_map.keys():
            cache_file_map[source] = {}

        # 记录 company
        if company not in cache_file_map[source].keys():
            cache_file_map[source][company] = []

        # 追加文件
        if cache_data['file'] not in cache_file_map[source][company]:
            # 看source里面是否存在对应company信息，若有返回对应value（即文件名.xlsx）,否则返回空list
            lst = cache_file_map[source].get(company, [])
            lst.append(cache_data['file'])
            cache_file_map[source][company] = lst  # 所有文件名储存在list里面，这个list是cache_file_map[source][company]的value

    increment_file_lst = []
    for s3_file in s3_all_file_lst:
        source = s3_file['source']
        company = s3_file['company']

        if source in cache_file_map.keys() \
                and company in cache_file_map[source].keys() \
                and s3_file['file'] in cache_file_map[source][company]:
            continue

        increment_file_lst.append(s3_file)
    return increment_file_lst


def parse_s3_execl(obj):
    """
    解析每个 execl 的全部 sheet

    :return: sheets_info: 每个 sheet 的信息
    """
    sheets_info = []
    response = s3_client.get_object(
        Bucket=BUCKER_NAME,
        Key=obj["file"],
    )
    excel_data = pd.ExcelFile(response['Body'].read())

    if not len(excel_data.sheet_names):
        cp_obj = copy.deepcopy(obj)
        cp_obj["length"] = 0
        cp_obj["data"] = {}
        cp_obj["err"] = 'sheet number is 0'
        sheets_info.append(cp_obj)
        del cp_obj
        return sheets_info

    for sheet_name in excel_data.sheet_names:
        cp_obj = copy.deepcopy(obj)
        cp_obj["length"] = excel_data.parse(sheet_name).shape[0]
        cp_obj["sheet"] = sheet_name
        cp_obj["data"] = excel_data.parse(sheet_name, nrows=KEEP_ROW_COUNT).to_dict()
        sheets_info.append(cp_obj)
        del cp_obj

    return sheets_info


if __name__ == '__main__':
    cache_data_lst = load_cache_data()  # 本地已缓存的文件信息
    print(f"当前缓存了 {len(cache_data_lst)} 条数据（包含 sheet）")
    print()

    filter_file_lst, s3_all_file_lst, err_file_lst = get_all_file_path()
    if len(filter_file_lst):
        print(f"存在过滤掉的文件 {len(filter_file_lst)} 个，信息如下：")
        print()
    #
    if len(err_file_lst):
        print(f"存在无法解析路径或后缀的文件 {len(err_file_lst)} 个，信息如下：")
        print()

    increment_lst = get_s3_increment(cache_data_lst, s3_all_file_lst)
    print(increment_lst)
    if len(increment_lst):
        print(f"存在增量文件 {len(increment_lst)} 个，信息如下：")
        print()
    else:
        print(f"不存在新增文件")

    for index, obj in enumerate(increment_lst, 1):
        print(f"{index}/{len(increment_lst)} 开始解析 {obj['file']}")
        append_cache_data(parse_s3_execl(obj))
