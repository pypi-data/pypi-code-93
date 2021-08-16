#  The MIT License (MIT)
#
#  Copyright (c) 2021. Scott Lau
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import logging
import os

import pandas as pd
from sc_utilities import Singleton
from sc_utilities.file_utils import ensure_dir

from sc_excel_splitter.utils import ConfigUtils


class Splitter(metaclass=Singleton):

    def __init__(self):
        pass

    def split(self):
        # 源路径
        config = ConfigUtils.get_config()
        source_file_path = config.get("excel.source_file_path")
        logging.getLogger(__name__).info("源文件路径：{}".format(source_file_path))
        # 输出目标路径
        target_directory = config.get("excel.target_directory")
        logging.getLogger(__name__).info("目标路径：{}".format(target_directory))
        # 确保目标路径存在
        ensure_dir(target_directory)

        source_filename = os.path.basename(source_file_path)
        (filename, ext) = os.path.splitext(source_filename)

        sheet_config_dict = config.get("excel.sheet_config")
        logging.getLogger(__name__).info("Sheet配置：{}".format(sheet_config_dict))
        if type(sheet_config_dict) is not dict:
            logging.getLogger(__name__).info("配置项 'excel.sheet_config' 配置错误")
            return 1
        if len(sheet_config_dict) <= 0:
            logging.getLogger(__name__).info("配置项 'excel.sheet_config' 配置错误，缺少导出Sheet的配置")
            return 1

        with pd.ExcelFile(source_file_path) as xls:
            for sheet_name, sheet_config in sheet_config_dict.items():
                if "other_sheets" == sheet_name and type(sheet_config) == list:
                    # # 其他Sheet直接读取按原样输出
                    # for other_sheet in sheet_config:
                    #     df = pd.read_excel(xls, sheet_name=other_sheet)
                    #     df.to_excel(writer, sheet_name=other_sheet, index=False)
                    continue
                # 如果是需要拆分的Sheet
                logging.getLogger(__name__).info("开始处理Sheet：{}".format(sheet_name))
                df = pd.read_excel(xls, sheet_name=sheet_name, header=sheet_config["header"])
                column_index = sheet_config["split_column"]
                column_name = df.columns[column_index]
                grouped_df = df.groupby(column_name, dropna=False)
                for data in grouped_df[column_name]:
                    group_name = data[0]
                    output_filename = "{}-{}.xlsx".format(filename, group_name)
                    # 如果文件已经存在，则采用追加的模式
                    mode = 'a' if os.path.exists(output_filename) else 'w'
                    # 如果Sheet已经存在则替换原有的Sheet
                    replace_strategy = 'replace' if mode == 'a' else None
                    with pd.ExcelWriter(output_filename, mode=mode, if_sheet_exists=replace_strategy) as writer:
                        sub_group = grouped_df.get_group(group_name)
                        sub_group.to_excel(
                            writer,
                            sheet_name=sheet_name,
                            index=False,
                        )
        return 0
