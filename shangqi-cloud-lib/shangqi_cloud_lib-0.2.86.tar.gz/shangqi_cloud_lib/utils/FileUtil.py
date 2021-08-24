# coding:utf-8
import csv
import json
import logging
import os

from ruamel import yaml

from shangqi_cloud_lib.context import config


def remove_file(file_name):
    file_path = os.path.join(config.project_path, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)


def write_csv(file_path, data_list, title_list=None, encode="utf-8"):
    if title_list is None:
        title_list = []
    f = open(file_path, 'w', encoding=encode, newline='')
    csv_writer = csv.writer(f)
    if len(title_list) > 0:
        csv_writer.writerow(title_list)
    for item in data_list:
        csv_writer.writerow(item)
    f.close()


def write_json(file_name, data, base_path=None, no_base=False):
    if not base_path:
        base_path = config.project_path
    if no_base:
        file_path = file_name
    else:
        file_path = os.path.join(base_path, file_name)
    path_arr = str(file_name).split(os.path.sep)
    if len(path_arr) > 1:
        path = os.path.join(base_path, os.path.sep.join(path_arr[0:-1]))
    else:
        path = base_path
    if not os.path.exists(path):
        os.makedirs(path)
    if not isinstance(data, str):
        data = json.dumps(data, ensure_ascii=False)
    f = open(file_path, 'w', encoding='utf-8')
    f.write(data)
    f.close()


def read_json(file_name, base_path=None, no_base=False):
    if not base_path:
        base_path = config.project_path
    if no_base:
        file_path = file_name
    else:
        file_path = os.path.join(base_path, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            context = f.read()
            return json.loads(context)
    return {}


# 读取yaml
def read_yaml(file_path):
    try:
        if not os.path.exists(file_path):
            return None
        f = open(file_path, 'r', encoding='utf-8')
        cont = f.read()
        return yaml.round_trip_load(cont)
    except Exception as e:
        logging.error(str(e))
        return None


# 写入yaml
def write_yaml(file_path, data):
    fw = open(file_path, 'w', encoding='utf-8')
    yaml.round_trip_dump(data, fw, allow_unicode=True)


def write_text(file_path, text):
    f = open(file_path, 'w', encoding='utf-8')
    f.write(text)
    f.close()


def read_text(file_path):
    f = open(file_path, 'r', encoding='utf-8')
    text = f.read()
    f.close()
    return text


def file_upload(file_metas, path, check_name_func=None):
    filename = file_metas[0]['filename']
    if not check_name_func(filename):
        raise NameError(f"上传文件{filename}不符合格式！")
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = os.path.join(path, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'wb') as up:
        up.write(file_metas[0]['body'])
    return file_path


def get_files(path, suffix):
    return [os.path.join(root, file) for root, dirs, files in os.walk(path) for file in files if file.endswith(suffix)]
