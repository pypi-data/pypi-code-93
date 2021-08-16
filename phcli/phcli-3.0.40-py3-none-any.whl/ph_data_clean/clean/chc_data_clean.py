# -*- coding: utf-8 -*-

import re
from phcli.ph_data_clean.clean.common_func import *
from phcli.ph_data_clean.clean.data_clean import DataClean


def pack_qty_unit(final_data_pack_unit):
    """
    将包装单位（数字+单位）转化成纯数字的价格转换比（pack_qty）

    :param final_data_pack_unit: 清洗后的包装单位数值

    :return: pack_qty_int:纯数字价格转换比
    :return: pack_unit_str:纯单位

    """
    pack_qty = re.findall(r"\d+", final_data_pack_unit)
    try:
        pack_qty_int = int(pack_qty[0])
        pack_unit_str = final_data_pack_unit.replace(pack_qty[0], "", 1)
        return pack_qty_int, pack_unit_str
    except IndexError:
        return 0, final_data_pack_unit


class ChcDataClean(DataClean):
    """
    CHC 源数据的清洗规则
    """

    def change_pack_qty_unit(self, *args, **kwargs):
        final_data = kwargs['prev']
        if final_data:
            pack_qty = final_data['PACK_QTY']
            pack_unit = final_data['PACK_UNIT']

            if not pack_unit:
                pass
            elif pack_qty and pack_unit:
                pack_unit = pack_qty_unit(final_data_pack_unit=pack_unit)[1]
            elif not pack_qty and pack_unit:
                pack_qty, pack_unit = pack_qty_unit(final_data_pack_unit=pack_unit)

            final_data['PACK_QTY'] = pack_qty
            final_data['PACK_UNIT'] = pack_unit

        return final_data

    def check_hosp_name_code(self, *args, **kwargs):
        final_data = kwargs['prev']
        if final_data:
            if not final_data['HOSP_CODE'] and final_data['HOSP_NAME']:
                final_data['HOSP_CODE'] = "无"
            elif not final_data['HOSP_NAME'] and final_data['HOSP_CODE']:
                final_data['HOSP_NAME'] = "无"

        return final_data

    def split_spec_pack_unit(self, *args, **kwargs):
        """
        将规格列根据*拆开，前面的写入spec，后面的内容写入pack_unit
        """
        final_data = kwargs['prev']
        if final_data and final_data['SPEC'] \
                and not final_data['PACK_UNIT']\
                and not final_data['PACK_QTY']:
            split_result = final_data['SPEC'].split("*")
            if len(split_result) == 2:
                final_data['PACK_UNIT'] = split_result[1]
                final_data['SPEC'] = split_result[0]

        return final_data

    process = [
        check_format,
        change_key,
        change_year_month,
        change_sales_tag,
        split_spec_pack_unit,  # chc 特有
        change_pack_qty_unit,  # chc 特有
        check_hosp_name_code,  # chc 特有
        reformat_int,
        define_tag_err,
    ]
