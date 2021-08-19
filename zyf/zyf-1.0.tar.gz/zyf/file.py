# -*- coding: utf-8 -*-

"""
DateTime   : 2021/02/21 17:13
Author     : ZhangYafei
Description: 
"""
import os
from collections import Counter

import pandas as pd


def scan_directory_contents(dir_path, suffix: str = None):
    """
    这个函数接收文件夹的名称作为输入参数
    返回该文件夹中文件的路径
    以及其包含文件夹中文件的路径
    """
    for base_path, folders, files in os.walk(dir_path):
        for file in files:
            if suffix and not file.endswith(suffix):
                continue
            yield os.path.join(base_path, file)


def count_word_freq(file_path: str, col_name: str, sep='; ', to_col_freq: str = 'freq', to_col_word: str = 'word',
                    to_file: str = None, multi_table=False):
    """
    统计词频
    :param file_path: 读取文件路径
    :param col_name: 统计词频所在列名
    :param to_col_freq: 频数列
    :param to_col_word: 单词列
    :param to_file: 保存文件路径
    :param sep: 词语分割符
    :param multi_table: 是否读取多张表
    :return:
    """
    if not to_file:
        to_file = file_path.replace('.', f'_{col_name}_统计.')
    if multi_table:
        datas = pd.read_excel(file_path, header=None, sheet_name=None)
        with pd.ExcelWriter(path=to_file) as writer:
            for sheet_name in datas:
                df = datas[sheet_name]
                keywords = (word for word_list in df.loc[df[col_name].notna(), col_name].str.split(sep) for word in
                            word_list if word)
                words_freq = Counter(keywords)
                words = [word for word in words_freq]
                freqs = [words_freq[word] for word in words]

                words_df = pd.DataFrame(data={to_col_word: words, to_col_freq: freqs})
                words_df.sort_values(to_col_freq, ascending=False, inplace=True)
                words_df.to_excel(excel_writer=writer, sheet_name=sheet_name, index=False)
            writer.save()
    else:
        df = pd.read_excel(file_path)
        keywords = (word for word_list in df.loc[df[col_name].notna(), col_name].str.split(sep) for word in word_list if
                    word)
        words_freq = Counter(keywords)
        words = [word for word in words_freq]
        freqs = [words_freq[word] for word in words]

        words_df = pd.DataFrame(data={to_col_word: words, to_col_freq: freqs})
        words_df.sort_values(to_col_freq, ascending=False, inplace=True)
        words_df.to_excel(to_file, index=False)
