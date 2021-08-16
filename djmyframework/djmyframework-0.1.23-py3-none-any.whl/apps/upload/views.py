#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# 主页,登录相关
#
# django 常用导入
# =========================================
from django.http import HttpResponse
# ==========================================


import sys
import datetime
from framework.views import notauth
from framework.utils import mkdirs
import traceback
from framework.route import Route
import json
from settings import STATIC_DIR
import os
import time
import shutil
import xlrd


def read_excel(path):
    # goods = {}
    goods = []

    if not os.path.isfile(path):
        return goods

    # 打开文件
    try:
        workbook = xlrd.open_workbook(path)
    except Exception as exc:
        print(exc)
        return goods

    # 获取所有sheet
    sheets = workbook.sheet_names()

    for name in sheets:
        sheet = workbook.sheet_by_name(name)
        # skip first row
        for index in range(1, sheet.nrows):
            row = sheet.row_values(index)
            _id, _name, _price = row[:3]
            try:
                _price = int(_price)
            except:
                _price = ''
            # goods[_id] = dict(name=_name, amount=_price)
            goods.append(dict(key=_id, name=_name, amount=_price))

    return goods


@Route('^upload[/]?$')
@notauth
def upload(request):
    _r = {"code"    : -1,
          "file_url": ""
          }
    now = datetime.datetime.now()
    year = str(now.year)
    mon = str(now.month)
    day = str(now.day)
    the_url = '/'.join(['/static', 'upload', year, mon, day])

    file_type = request.REQUEST.get('file_type', '')

    file_obj = request.FILES.get('uploadedFile', None)
    if file_obj:
        the_file_name = file_obj.name
        the_file_name = '%s_%s' % (int(time.time()), the_file_name)
        file_type = file_type or os.path.splitext(the_file_name)[-1].lstrip('.')
        the_save_dir = os.path.join(STATIC_DIR, 'upload', file_type, year, mon, day)
        mkdirs(the_save_dir)
        the_save_path = os.path.join(the_save_dir, the_file_name)

        file_url = '/'.join(['/static', 'upload', file_type, year, mon, day, the_file_name])
        fp = open(the_save_path, 'wb')
        try:
            for chunk in file_obj.chunks():
                fp.write(chunk)
            fp.close()
            _r['file_url'] = file_url
            _r['code'] = 0
        except Exception as e:
            msg = str(e)
            traceback.print_exc()
            _r['msg'] = msg
        finally:
            fp.close()

    return HttpResponse(json.dumps(_r))


@Route('^new/upload[/]?$')
@notauth
def new_upload(request):
    """nginx预处理版上传"""
    _r = {"code"    : -1,
          "file_url": ""
          }
    now = datetime.datetime.now()
    year = str(now.year)
    mon = str(now.month)
    day = str(now.day)
    the_url = '/'.join(['/static', 'upload', year, mon, day])

    file_type = request.REQUEST.get('file_type', '')

    file_path = request.POST.get('file_path', '')
    file_name = request.POST.get('file_name', '')

    if file_path:
        the_file_name = file_name
        the_file_name = '%s_%s' % (int(time.time()), the_file_name)

        the_save_dir = os.path.join(STATIC_DIR, 'upload', file_type, year, mon, day)
        the_save_path = os.path.join(the_save_dir, the_file_name)
        file_url = '/'.join(['/static', 'upload', file_type, year, mon, day, the_file_name])

        mkdirs(the_save_dir)

        try:

            shutil.copy(file_path, the_save_path)
            _r['file_url'] = file_url
            _r['code'] = 0
        except Exception as e:
            msg = str(e)
            traceback.print_exc()

    return HttpResponse(json.dumps(_r))




