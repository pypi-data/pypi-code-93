# -*- coding: utf-8 -*-

"""
Author     : ZhangYafei
Description: 国务院政策数据下载
第一步：安装依赖包
    pip install requests zyf lxml pandas
第二步：设置关键词
第三步：运行代码
"""
import os
import re
import time

import requests
from zyf.timer import timeit

from lxml import etree
from pandas import DataFrame, read_csv

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
}


class GovPolicyCrawler:
    def __init__(self, data_dir: str = 'data'):
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.search_url = 'http://sousuo.gov.cn/data'
        self.depart_params_map = {'国务院': 'gw', '国务院部门': 'bm', '国务院公报': 'gb'}
        self.depart_response_map = {'国务院': 'gongwen', '国务院部门': 'bumenfile', '国务院公报': 'gongbao'}
        self.data_dir = data_dir
        self.search_dir = f'{data_dir}/search'
        self.search_history = f'{self.search_dir}/search_history.txt'
        self.html_dir = f'{data_dir}/html'

    def remove_html_label(self, html):
        """
        去除html标签
        :param html:
        :return:
        """
        pattern = re.compile(r'<[^>]+>', re.S)
        return pattern.sub('', html)

    @staticmethod
    def response_to_file(file_path: str, response: requests.Response = None, text: str = None, encoding: str = 'utf-8',
                         mode: str = 'w'):
        content = response.text if response else text
        with open(file_path, mode=mode, encoding=encoding) as f:
            f.write(content)

    @staticmethod
    def read(path, mode='r', encoding='utf-8'):
        with open(path, mode=mode, encoding=encoding) as f:
            return f.read()

    @staticmethod
    def process_text(content, word_list: list = None):
        content = content.replace('\n', '').replace('，', ' ').replace('。', ' ').replace('\t', '').replace(' ', '')
        if word_list:
            for word in word_list:
                content = content.replace(word, '')
        content = content.strip('\r\n').replace(u'\u3000', u'').replace(u'\xa0', u'')
        return content

    @staticmethod
    def scan_directory_contents(dir_path, suffix: str = None, return_only_file: bool = False):
        """
        这个函数接收文件夹的名称作为输入参数
        返回该文件夹中文件的路径
        以及其包含文件夹中文件的路径
        """
        for base_path, folders, files in os.walk(dir_path):
            for file in files:
                if suffix and not file.endswith(suffix):
                    continue
                if return_only_file:
                    yield file
                else:
                    yield os.path.join(base_path, file)

    def search(self, keyword: str, min_time: str = None, max_time: str = None, issue_depart: list = None,
               searchfield: str = 'title:content:summary', sort: str = 'pubtime', page_size: int = 50,
               to_file: str = None):
        """
        以指定关键词对国务院政策文件库进行检索，将检索结果保存至文件中
        :param keyword:
        :param min_time:
        :param max_time:
        :param issue_depart:
        :param searchfield:
        :param sort:
        :param page_size:
        :param to_file:
        :return:
        """
        if not os.path.exists(self.search_dir):
            os.makedirs(self.search_dir)
        t = 'zhengcelibrary_' + '_'.join(self.depart_params_map[depart] for depart in issue_depart)
        params = {
            't': t,
            'q': keyword,
            'timetype': 'timezd',
            'mintime': min_time,
            'maxtime': max_time,
            'searchfield': searchfield,
            'n': page_size,
            'sort': sort,
        }
        response = self.session.get(url=self.search_url, params=params)
        json_data = response.json()
        cat_map = json_data['searchVO']['catMap']
        total_count = json_data['searchVO']['totalCount']

        print(f'关键词 {keyword} 共检索到 {total_count} 条记录, 其中 ...')
        total_page = 0
        for depart in issue_depart:
            depart_data = cat_map[self.depart_response_map[depart]]
            depart_total_count = depart_data['totalCount']
            print(f'{depart} 共检索到 {depart_total_count} 条记录 ... ')
            total_page = max(total_page, depart_data['totalCount'] // page_size)

        data = []
        print(f'共 {total_page + 1} 页', end=' ')

        if os.path.exists(self.search_history):
            with open(self.search_history, encoding='utf-8') as f:
                has_pages = {int(line.split(' ')[1].strip()) for line in f if line.startswith(keyword)}
            total_page_set = {page for page in range(total_page + 1)}
            total_page = total_page_set - has_pages
            print(f'已下载 {len(has_pages)} 还剩 {len(total_page)}')
        else:
            total_page = {page for page in range(total_page + 1)}
            print(f'已下载 0 页 还剩 {len(total_page)} 页')

        if len(total_page) == 0:
            print(f'关键词 {keyword} 检索结果 已全部下载完成 ...')
            return

        search_history = open(self.search_history, mode='a')

        for page in total_page:
            print(f'正在请求第 {page} 页...')
            params['p'] = page
            response = self.session.get(url=self.search_url, params=params)
            if response.status_code == 403:
                print(f'ip被封， 第 {page} 页请求失败')
                break
            json_data = response.json()
            cat_map = json_data['searchVO']['catMap']
            for depart in issue_depart:
                depart_data = cat_map[self.depart_response_map[depart]]
                if not depart_data['listVO']:
                    continue
                for item in depart_data['listVO']:
                    title = self.remove_html_label(item['title'])
                    data.append(
                        {'索引号': item['index'], '标题': title, 'url': item['url'], '主题分类': item['childtype'],
                         '发文字号': item['pcode'], '发文机关': item['puborg'], '发布日期': item['pubtimeStr'],
                         '来源': item['source'], '文件类型': item['colname'],
                         })
            search_history.write(f'{keyword} {page}\n')
            time.sleep(0.5)
        print('所有数据请求完成，正在导出到文件中 ...')
        df = DataFrame(data=data)
        to_file = to_file if to_file else f'{self.search_dir}/{keyword}.csv'
        if os.path.exists(to_file):
            df.to_csv(to_file, header=False, index=False, encoding='utf_8_sig', mode='a')
        else:
            df.to_csv(to_file, index=False, encoding='utf_8_sig')
        print(f'导出文件成功，文件保存路径为 {to_file}')
        search_history.close()

    def download_policy_html(self):
        """
        下载政策页面
            1. 获取所有请求，并对请求进行过滤
            2. 打印当前请求数量信息
            3. 对请求进行访问和下载
        :return:
        """
        # 1. 获取所有请求，并对请求进行过滤
        request_set = set()

        has_files = set(self.scan_directory_contents(self.html_dir, return_only_file=True))

        def add_requests(row):
            title = row['标题'].replace('/', '_')
            if title + '.html' not in has_files:
                request_set.add((title, row['url'], row['文件类型']))

        departs = set()
        for file in os.listdir(self.search_dir):
            if file.endswith('csv'):
                path = os.path.join(self.search_dir, file)
                df = read_csv(path)
                departs = departs.union(set(df['文件类型'].unique()))
                df.apply(add_requests, axis=1)
        for depart in departs:
            if not os.path.exists(f'{self.html_dir}/{depart}'):
                os.makedirs(f'{self.html_dir}/{depart}')
        # 2. 打印当前请求数量信息
        print(f'共 {len(has_files) + len(request_set)} 请求 已下载 {len(has_files)} 还剩 {len(request_set)} ...')
        # 3. 对请求进行访问和下载
        while len(request_set) > 0:
            title, url, file_type = request_set.pop()
            response = self.session.get(url)
            self.response_to_file(file_path=f'{self.html_dir}/{file_type}/{title}.html', response=response,
                                  encoding='ISO8859-1')
            print(f'{title} 写入文件成功 ...')
        print('所有文件下载完成 ...')

    @timeit
    def parse_policy_info(self, to_file: str = None):
        """
        解析政策文件
        :param to_file:
        :return:
        """
        data = []
        title_url_map = {}

        def build_map(row):
            title = row['标题'].replace('/', '_')
            if title not in title_url_map:
                title_url_map[title] = row['url']

        for file in os.listdir(self.search_dir):
            if file.endswith('csv'):
                path = os.path.join(self.search_dir, file)
                df = read_csv(path)
                df.apply(build_map, axis=1)
        print('开始解析政策文件 ...')
        for file in self.scan_directory_contents(self.html_dir, suffix='html'):
            file_type = file.split('\\')[1]
            title = file.split('\\')[2].replace('.html', '')
            url = title_url_map[title]
            print(f'{title} 开始解析 ...')
            if file_type == '国务院部门文件':
                self.parse_bumen_policy(file, url, data)
            elif file_type == '国务院文件':
                self.parse_gw_policy(file, url, data)
            print(f'{title} 解析完成 ...')
        print('所有政策文件解析完成,正在输出到文件 ...')
        df = DataFrame(data=data)
        if not to_file:
            date = time.strftime('%Y_%m_%d')
            to_file = f'{self.data_dir}/gov_policy_data_{date}.xlsx'
        df.to_excel(to_file, index=False)
        print(f'解析结果成功输出到文件，文件路径为{to_file}')

    def parse_bumen_policy(self, file, url, data: list):
        """
        解析国务院部门文件
        :param file:
        :param url:
        :param data:
        :return:
        """
        content = self.read(file)
        response = etree.HTML(content)
        file_type = response.xpath('//div[@class="BreadcrumbNav"]/a[4]/text()')[0]

        item = {}
        item['标题'] = response.xpath('//div[@class="policyLibraryOverview_header"]/table/tr[2]/td[2]/text()')[0]
        item['发文机关'] = response.xpath('//div[@class="policyLibraryOverview_header"]/table/tr[2]/td[4]/text()')[
            0].replace(' ', ';')
        issue_num = response.xpath('//div[@class="policyLibraryOverview_header"]/table/tr[3]/td[2]/text()')
        item['发文字号'] = issue_num[0] if issue_num else None
        source = response.xpath('//div[@class="policyLibraryOverview_header"]/table/tr[3]/td[4]/text()')
        item['来源'] = source[0] if source else None
        item['主题分类'] = response.xpath('//div[@class="policyLibraryOverview_header"]/table/tr[4]/td[2]/text()')[0]
        item['公文种类'] = response.xpath('//div[@class="policyLibraryOverview_header"]/table/tr[4]/td[4]/text()')[0]
        item['成文日期'] = response.xpath('//div[@class="policyLibraryOverview_header"]/table/tr[5]/td[2]/text()')[0]
        item['发布日期'] = response.xpath('//div[@class="policyLibraryOverview_header"]/table/tr[5]/td[4]/text()')[0]
        item['文件类型'] = file_type
        item['正文'] = response.xpath('string(//div[@class="pages_content"])').strip().replace('扫一扫在手机打开当前页', '')
        item['url'] = url
        item['文件路径'] = file

        data.append(item)

    def parse_gw_policy(self, file, url, data: list):
        """
        解析国务院文件
        :param file:
        :param url:
        :param data:
        :return:
        """
        content = self.read(file)
        response = etree.HTML(content)

        item = {}
        file_type = response.xpath('//div[@class="BreadcrumbNav"]/a[4]/text()')[0]
        item['索引号'] = response.xpath('//table[@class="bd1"]/tbody/tr[1]/td[2]/text()')[0]
        item['主题分类'] = response.xpath('//table[@class="bd1"]/tbody/tr[1]/td[4]/text()')[0]
        item['发文机关'] = response.xpath('//table[@class="bd1"]/tbody/tr[2]/td[2]/text()')[0]
        date_of_writing = response.xpath('//table[@class="bd1"]/tbody/tr[2]/td[4]/text()')
        item['成文日期'] = date_of_writing[0] if date_of_writing else None
        item['标题'] = response.xpath('//table[@class="bd1"]/tbody/tr[3]/td[2]/text()')[0]
        issue_num = response.xpath('//table[@class="bd1"]/tbody/tr[4]/td[2]/text()')
        item['发文字号'] = issue_num[0] if issue_num else None
        item['发布日期'] = response.xpath('//table[@class="bd1"]/tbody/tr[4]/td[4]/text()')[0]
        topic_words = response.xpath('//table[@class="bd1"][2]/tbody/tr[1]/td[2]/text()')
        item['主题词'] = topic_words if topic_words else None
        item['正文'] = response.xpath('string(//div[@class="wrap"]/table[2]/tbody/tr/td[1])').strip().replace(
            '扫一扫在手机打开当前页', '')
        item['url'] = url
        item['文件类型'] = file_type
        item['文件路径'] = file

        data.append(item)

    def run(self, **kwargs):
        self.search(**kwargs)
        self.download_policy_html()
        self.parse_policy_info()



