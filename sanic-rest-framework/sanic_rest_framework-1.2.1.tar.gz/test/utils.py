"""
@Author：WangYuXiang
@E-mile：Hill@3io.cc
@CreateTime：2021/1/29 16:38
@DependencyLibrary：无
@MainFunction：无
@FileDoc： 
    utils.py
    文件说明
@ChangeHistory:
    datetime action why
    example:
    2021/1/29 16:38 change 'Fix bug'
        
"""
import datetime


class TestDataMixin:
    min_int = 1
    max_int = 9999
    min_float = 0.01
    max_float = 9999.99
    pi = 3.1415926
    str_min_int = '1'
    str_max_int = '9999'
    str_min_float = '0.01'
    str_max_float = '9999.99'
    str_pi = '3.1415926'
    str_chinese_w = ' 测试字符 '
    str_chinese = '测试字符'
    str_england = 'Test String'
    str_england_w = ' Test String '
    bool_True = True
    bool_False = False
    str_bool_True = 'True'
    str_bool_False = 'False'
    long_str = '996' * 600
    str_datetime = '2019-12-18 08:21:25'
    str_datetime_bad_y = '99999-12-18 08:21:25'
    str_datetime_bad_ym = '2019-13-18 08:21:25'
    str_datetime_bad_d = '2019-12-32 08:21:25'
    str_datetime_bad_h = '2019-12-18 25:21:25'
    str_datetime_bad_hm = '2019-12-18 08:61:25'
    str_datetime_bad_s = '2019-12-18 08:21:61'
    str_date = '2019-12-18'
    str_date_bad_y = '99999-12-18'
    str_date_bad_m = '2019-13-18'
    str_date_bad_d = '2019-12-32'
    str_time = '08:21:25'
    str_time_bad_h = '25:59:25'
    str_time_bad_m = '08:61:25'
    str_time_bad_s = '08:59:61'
    obj_datetime = datetime.datetime(2019, 12, 18, 8, 21, 25)
    obj_date = datetime.date(2019, 12, 18)
    obj_time = datetime.time(8, 21, 25)
