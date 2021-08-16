# -*- coding: utf-8 -*-

import copy
from phcli.ph_data_clean.clean.common_func import *
from phcli.ph_data_clean.clean.data_clean import DataClean
from phcli.ph_data_clean.mapping.universe_mapping import *


def define_tag_err_for_each(raw_data, mapping, final_data):
    tag_value = Tag.UNDEFINED

    if raw_data == {}:  # 若原始数据为空
        tag_value = Tag.EMPTY_DICT
        error_msg = 'Error message: empty raw_data'

    elif final_data == {}:  # 若最终字典没有内容
        tag_value = Tag.EMPTY_DICT
        error_msg = 'Error message: no mapping found'

    else:
        error_msg_flag = False
        warning_msg_flag = False
        error_msg = 'Col_missing:'
        warning_lst = []
        for maps in mapping:
            null_data_lst = ["#N/A", "-", "#########", "", "0", "0.0", 0, None]
            # 若某些必须有的列缺失数据
            if (maps['not_null']) and (maps['msg_type'] == 'err') \
                    and (final_data[maps['col_name']] in null_data_lst):
                error_msg_flag = True
                tag_value = Tag.MISSING_COL
                error_msg += ' / err: ' + maps['col_name']
                final_data[maps['col_name']] = reformat_null(data_type=maps['type'])
                # continue

            elif (maps['not_null']) and (maps['msg_type'] == 'warning') \
                    and (final_data[maps['col_name']] in null_data_lst):
                warning_msg_flag = True
                error_msg += ' / warning: ' + maps['col_name']
                warning_lst.append(maps['col_name'])

            elif (not maps['not_null']) and \
                    (final_data[maps['col_name']] in null_data_lst):
                final_data[maps['col_name']] = reformat_null(data_type=maps['type'])

        # 只有warning，没有err的情况
        if (not error_msg_flag) and warning_msg_flag:
            tag_value = Tag.WARNING
            error_msg = 'Warning: ' + str(warning_lst)

        # 没有warning和err， 也就是全部success的情况
        elif (not error_msg_flag) and (not warning_msg_flag):
            tag_value = Tag.SUCCESS
            error_msg = 'Success'

        return CleanResult(data=final_data,
                           metadata={},
                           raw_data=raw_data,
                           tag=tag_value,
                           err_msg=error_msg)


class UniverseDataClean(DataClean):
    """
    universe 源数据的清洗规则
    """

    def change_key_for_blue(self, *args, **kwargs):
        mapping = args[0]
        raw_data = kwargs['prev']

        # standardise column name
        new_key_name = {}
        for raw_data_key in raw_data.keys():
            old_key = raw_data_key.strip()  # remove unwanted symbols
            for m in mapping:
                if old_key.lower() in [key.lower() for key in m["candidate"]]:
                    new_key = m["col_name"]
                    if new_key not in new_key_name:
                        new_key_name[new_key] = raw_data[raw_data_key]  # write new key name into dict

        # create ordered new dict
        final_data = {}
        for m in mapping:
            for n in new_key_name.keys():
                if m["col_name"] == n:
                    final_data[m["col_name"]] = new_key_name[n]
                elif m["col_name"] not in final_data.keys():
                    final_data[m["col_name"]] = None
        final_data["UPDATE_LABEL"] = '2013_updated'

        return final_data

    def change_key_for_grey_orange(self, *args, **kwargs):
        raw_data = args[1]
        final_data_blue = kwargs['prev']
        final_data_for_three = []
        final_data_gery = copy.deepcopy(final_data_blue)
        final_data_orange = copy.deepcopy(final_data_blue)
        blue_grey_mapping = universe_blue_grey_mapping()
        blue_orange_mapping = universe_blue_orange_mapping()

        # 基于蓝色数据改2011年（灰色）数据
        for m in blue_grey_mapping:
            for name in m['grey_col_name']:
                if m["blue_col_name"] in final_data_gery and name in raw_data:
                    final_data_gery[m["blue_col_name"]] = raw_data[name]
        final_data_gery["UPDATE_LABEL"] = '2011_initial'

        # 基于蓝色数据改2019年（橙色）数据
        for m in blue_orange_mapping:
            for name in m['orange_col_name']:
                if m["blue_col_name"] in final_data_orange and name in raw_data:
                    final_data_orange[m["blue_col_name"]] = raw_data[name]
        final_data_orange["UPDATE_LABEL"] = '2019_updated'

        final_data_for_three.append(final_data_blue)  # 2013
        final_data_for_three.append(final_data_gery)  # 2011
        final_data_for_three.append(final_data_orange)  # 2019

        return final_data_for_three

    def reformat_true(self, *args, **kwargs):
        mapping = args[0]
        final_data_for_three = kwargs['prev']

        for final_data in final_data_for_three:
            for m in mapping:
                if m["type"] == "Boolean" and final_data[m["col_name"]] in [1, 1.0, "1", "1.0"]:
                    final_data[m["col_name"]] = True

        return final_data_for_three

    def define_tag_err_for_three(self, *args, **kwargs):
        mapping = args[0]
        raw_data = args[1]
        final_data_for_three = kwargs['prev']
        clean_result = {}

        for final_data in final_data_for_three:
            clean_result[final_data["UPDATE_LABEL"]] = \
                define_tag_err_for_each(raw_data=raw_data, mapping=mapping, final_data=final_data)

        return clean_result["2013_updated"], clean_result["2011_initial"], clean_result["2019_updated"]

    process = [
        check_format,
        change_key_for_blue,
        change_key_for_grey_orange,
        reformat_true,
        define_tag_err_for_three,
    ]
