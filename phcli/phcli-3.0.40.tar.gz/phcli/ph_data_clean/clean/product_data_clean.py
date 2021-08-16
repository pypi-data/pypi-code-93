# -*- coding: utf-8 -*-

from phcli.ph_data_clean.clean.common_func import *
from phcli.ph_data_clean.clean.data_clean import DataClean


class ProductDataClean(DataClean):
    """
    product 源数据的清洗规则
    """

    def product_clean_process(self, *args, **kwargs):
        raw_data = args[1]
        final_data = {}

        for raw_data_key in raw_data.keys():
            final_data_key = raw_data_key.split("#")[-1].replace('\n', '').strip()
            final_data[final_data_key] = raw_data[raw_data_key]

        if "_tag" in final_data:
            final_data["TAG"] = final_data.pop("_tag")

        return final_data

    def define_tag_err_for_prod(self, *args, **kwargs):
        mapping = args[0]
        raw_data = args[1]
        final_data = kwargs["prev"]

        # define tag and err msg
        tag_value = Tag.UNDEFINED
        if raw_data == {}:  # 若原始数据为空
            tag_value = Tag.EMPTY_DICT
            error_msg = 'Error message: empty raw_data'
        elif final_data == {}:  # 若最终字典没有内容
            tag_value = Tag.EMPTY_DICT
            error_msg = 'Error message: no mapping found'
        else:
            warning_col_lst = []
            for m in mapping:
                if m["not_null"] and (final_data[m["col_name"]] in [None, "", "/"]):
                    warning_col_lst.append(m["col_name"])

            # 如果是空字典（没有warning）
            if not warning_col_lst:
                tag_value = Tag.SUCCESS
                error_msg = 'Success'

            # 如果不是空字典（有warning）
            else:
                tag_value = Tag.WARNING
                error_msg = 'Warning: col-missing ' + str(warning_col_lst)

        return CleanResult(data=final_data,
                           metadata={},
                           raw_data=raw_data,
                           tag=tag_value,
                           err_msg=error_msg),

    process = [
        product_clean_process,
        define_tag_err_for_prod,
    ]
