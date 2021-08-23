# -*- coding: utf-8 -*-
'''
Created on 2020年11月05日
'''
import re
import html

import numpy
import pandas as pd
from bs4 import BeautifulSoup

from k_parse_tool.htmlTemplete.HtmlTableHead import table_title


class HtmlProcess:
    @staticmethod
    def replace_html(html_source):
        cleaned = html.unescape(html_source.strip())

        cleaned = re.sub(r"&amp;", "&", cleaned)
        cleaned = re.sub(r"&lt;", "<", cleaned)
        cleaned = re.sub(r"&gt;", ">", cleaned)
        cleaned = re.sub(r"&middot;", "·", cleaned)
        cleaned = re.sub(r"&shy;", "", cleaned)
        cleaned = re.sub(r"&#160;", " ", cleaned)
        cleaned = re.sub(r"", "", cleaned)
        cleaned = re.sub(r"[ ]", " ", cleaned)
        # 替换html中的<p>
        cleaned = re.sub(r"\s*<p[^>]*?>", "\r\n", cleaned)
        cleaned = re.sub(r"</p>\s*", "\r\n", cleaned)
        cleaned = re.sub(r"\（(相关资料:)\w*\）", "\r\n", cleaned)
        cleaned = re.sub(r"<[/]?center>", "\r\n", cleaned)
        cleaned = re.sub(r"<br\s*?[/]?>", "\r\n", cleaned)
        cleaned = re.sub(r"\[接上页\]", "", cleaned)

        cleaned = HtmlProcess.clean_html(cleaned)
        return cleaned.strip()

    @staticmethod
    def clean_html(html_source):  # 利用nltk的clean_html()函数将html文件解析为text文件
        # First we remove inline JavaScript/CSS:
        cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html_source.strip())
        # Then we remove html comments. This has to be done before removing regular
        # tags since comments can contain '>' characters.
        cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
        # Next we can remove the remaining tags:
        cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
        # Finally, we deal with whitespace
        cleaned = re.sub(r"&nbsp;", " ", cleaned)
        cleaned = re.sub(r"  ", " ", cleaned)
        cleaned = re.sub(r" ", "", cleaned)
        return cleaned.strip()


def is_chinese(text):
    zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
    for ch in text:
        match = zh_pattern.search(ch)
        if (match):
            return True
    return False


def extract_metadata_by_pandas(url_source, header=0, row_index=0, table_title={}):
    soup = BeautifulSoup(url_source, 'lxml')
    table = pd.read_html(soup.prettify(), header=header, na_values='', keep_default_na=True)[0]
    pd.set_option('display.max_rows', None)
    table.columns = [''.join(x.split()) for x in table.columns]
    for x in table.columns:
        if 'float64' == table[x].dtypes:
            table[x].replace(numpy.nan, 0, inplace=True)
            table[x] = table[x].astype('int')
            table[x] = table[x].astype('str')
        elif 'int64' == table[x].dtypes:
            table[x] = table[x].astype('str')
    #table = table.astype(str)
    #print(table.dtypes)
    rows = table.iloc[row_index, :]  # table.iloc[0,:]等价于table.loc[0]
    result = {}
    for columns, columns_title_list in table_title.items():
        for columns_title in columns_title_list:
            try:
                if columns_title in rows:
                    columns_value = rows[columns_title]
                    result[columns] = columns_value.strip()
                    break
            except Exception as e:
                print(e)
    return result


def acquire_row_index(source_code):
    soups = BeautifulSoup(source_code, "lxml")
    soups.prettify()
    head_row_index = 0
    data_row_index = 0
    tr_list = soups.find_all('tr', )
    try:
        for tr_index, tr_tag in enumerate(tr_list):
            row_tr = tr_tag.find_all(re.compile(r"t[dh]"))
            # print(tr_tag.text.strip())
            if len(row_tr) >= 5 and is_chinese(tr_tag.text.strip()):  # len(row_tr) == tr_child_count
                head_row_index = tr_index
                break
            elif tr_tag.name == 'th':
                head_row_index = tr_index
                break
        head_td_count = 0
        for tr_index, tr_tag in enumerate(tr_list):
            row_tr = tr_tag.find_all(re.compile("t[dh]"))
            if len(row_tr) <= 0 : continue
            if tr_index == head_row_index:
                head_td_count = len(row_tr)
                continue
            tr_number = row_tr[0]
            if '1' == tr_number.text.strip():
                data_row_index = tr_index
                break
            elif len(row_tr) >= head_td_count:
                data_row_index = tr_index
                break
    except Exception:
        pass
    return {'head_index': head_row_index, 'data_index': data_row_index}


def get_table_metadata(html_source):
    result = {}
    try:
        index_dict = acquire_row_index(html_source)
        head_index = index_dict['head_index']
        data_index = index_dict['data_index']
        data_index = 0 if data_index == 0 else data_index - head_index
        data_index = 0 if data_index == 0 else data_index - 1
        result = extract_metadata_by_pandas(html_source, header=head_index, row_index=data_index, table_title=table_title)
    except Exception as msg:
        print(f' extract table metadata error : {msg}')
    return result