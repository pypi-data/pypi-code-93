# -*- coding: utf-8 -*-

"""
Author     : ZhangYafei
Description: 北大法宝政策文件下载
使用步骤：
    1. 网页登陆之后将cookie复制，修改settings中的cookie信息
    2. 根据你的检索词和检索时间修改settings中的QueryBased64Request和Year
    3. 运行代码
"""
import json
import os
import time

import requests
from lxml import etree
from urllib.parse import urljoin, urlparse
from pandas import DataFrame, read_excel, merge, concat
from concurrent.futures import ThreadPoolExecutor
from concurrent import futures

from zyf.timer import timeit


class PkulawdCrawler:
    def __init__(self, cookie: str, query_base64_request: dict, year: list = None, page_size: int = 100, data_dir: str = 'data'):
        self.base_url = 'https://www.pkulaw.com'
        self.url = 'https://www.pkulaw.com/law/search/RecordSearch'
        self.level_dict = {'XA01': '法律', 'XG04': '司法解释', 'XC02': '行政法规', 'XE03': '部门规章', 'XQ09': '军事法律法规',
                           'XR12': '党内法规', 'XI05': '团体规定', 'XK06': '行业规定'}
        self.keys = ['标题', '发布部门', '发布日期', '发文字号', '批准部门', '批准日期', '实施日期', '时效性', '效力级别', '法规类别', '失效依据', '本篇引用的法规',
                     '引用本篇的法规 案例 论文']
        self.search_query_based64_request = query_base64_request
        self.search_year = year
        self.query_result = {}
        self.search_result_path = 'search_result_count.json'
        self.search_dir = f'{data_dir}/search'
        self.html_dir = f'{data_dir}/html'
        self.page_size = page_size
        self.session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
            'Cookie': cookie,
        }
        self.session.headers.update(headers)

    def download_search_pages(self, level: str, keyword: str, based64_request: str, page_num: int = 0,
                              year: int = None):
        page_index = page_num + 1 if page_num > 1 else page_num
        old_page = page_index - 1 if page_index > 1 else 0
        data = {
            'Menu': 'law',
            'SearchKeywordType': 'Fulltext',
            'MatchType': 'Exact',
            'RangeType': 'Piece',
            'Library': 'chl',
            'ClassFlag': 'chl',
            'QueryOnClick': False,
            'AfterSearch': True,
            'PreviousLib': 'chl',
            'IsSynonymSearch': 'true',
            'IsAdv': False,
            'ClassCodeKey': f',{level},,,,{year}',
            'Aggs.EffectivenessDic': level,
            'Aggs.IssueDate': year,
            'GroupByIndex': 0,
            'OrderByIndex': 4,
            'RecordShowType': 'List',
            'ShowType': 'default',
            'Pager.PageIndex': page_index,
            'Pager.PageSize': self.page_size,
            'QueryBase64Request': based64_request,
            'isEng': 'chinese',
            'OldPageIndex': old_page,
            'X-Requested-With': 'XMLHttpRequest',
        }
        response = self.session.post(self.url, data=data)
        html = etree.HTML(response.text)
        try:
            count = int(html.xpath('//span[@class="total"]/strong/text()')[0])
            print(f'{keyword} {year} {self.level_dict[level]} 检索结果到 {count} 条记录')
            self.query_result[f'{keyword}_{year}'][level] = [self.level_dict[level], count]
            self.response_to_file(response.text,
                                  f'{self.search_dir}/{keyword}/{year}/{self.level_dict[level]}_{level}_{page_num}.html')
        except IndexError:
            print(f'{keyword} {year} {self.level_dict[level]} 检索结果为空')

    def get_start_search_requests(self):
        if not os.path.exists(self.search_result_path):
            for year in self.search_year:
                for keyword, query in self.search_query_based64_request.items():
                    self.query_result.setdefault(f'{keyword}_{year}', {})
                    levels = list(self.level_dict.keys())
                    self.make_dirs(f'{self.search_dir}/{keyword}/{year}')
                    for level in levels:
                        self.download_search_pages(level=level, keyword=keyword, based64_request=query, page_num=0,
                                                   year=year)
            with open(self.search_result_path, mode='w') as f:
                json.dump(self.query_result, f)
        else:
            with open(self.search_result_path) as f:
                self.query_result = json.load(f)
            change = False
            for year in self.search_year:
                for keyword, query in self.search_query_based64_request.items():
                    if keyword not in self.query_result or not self.query_result.get(keyword):
                        self.query_result.setdefault(f'{keyword}_{year}', {})
                        levels = list(self.level_dict.keys())
                        self.make_dirs(f'{self.search_dir}/{keyword}/{year}')
                        for level in levels:
                            self.download_search_pages(level=level, keyword=keyword, based64_request=query, page_num=0,
                                                       year=year)
                        change = True
            if change:
                with open(self.search_result_path, mode='w') as f:
                    json.dump(self.query_result, f)

    def filter_requests(self):
        requets_sets = set()
        total_count = has_count = 0
        for query in self.query_result:
            keyword, year = query.split('_')
            has_file_sets = {row.strip() for row in os.listdir(f'{self.search_dir}/{keyword}/{year}')}
            has_count += len(has_file_sets)
            level_dict = self.query_result[f'{keyword}_{year}']
            for level in level_dict:
                level_title, count = level_dict[level]
                pages = (count // self.page_size) + 1
                total_count += pages
                for page in range(pages):
                    file = f'{level_title}_{level}_{page}.html'
                    if file not in has_file_sets:
                        requets_sets.add((keyword, year, level, level_title, page))
        print(f'检索页面 共{total_count} 已下载{has_count} 还剩{len(requets_sets)}')
        return requets_sets

    def make_dirs(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def scan_directory_contents(self, dir_path, suffix: str = None):
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

    def download_search_html(self):
        self.get_start_search_requests()
        request_sets = self.filter_requests()
        if request_sets:
            if not os.path.exists(self.html_dir):
                os.makedirs(self.html_dir)
        is_download = False
        while len(request_sets) > 0:
            keyword, year, level, level_title, page_num = request_sets.pop()
            based64_request = self.search_query_based64_request[keyword]
            print(f'start download {keyword} {year} {level_title} 第{page_num}页...')
            self.download_search_pages(level=level, keyword=keyword, based64_request=based64_request, page_num=page_num,
                                       year=year)
            print(f'{keyword} {year} {level_title} 第{page_num}页 download successfully ...')
            is_download = True
        if is_download:
            print('all download successfully...')

    @timeit
    def parse_search_info(self):
        for keyword in self.search_query_based64_request:
            print(f'start parse {keyword} search html...')
            if os.path.exists(f'{self.search_dir}/{keyword}.xlsx'):
                print(f'parse {keyword} had finished ...')
                continue
            data = []
            for path in self.scan_directory_contents(f'{self.search_dir}/{keyword}'):
                path = path.replace('\\', '/')
                response = etree.HTML(self.read(path))
                for block in response.xpath('//div[@class="block"]'):
                    title = ''.join(block.xpath('string(div[@class="list-title"]/h4/a[1])'))
                    href = block.xpath('div[@class="list-title"]/h4/a/@href')[0]
                    url = urljoin(self.base_url, urlparse(href).path)
                    wordcloud = ';;'.join(map(lambda x: x.strip(), block.xpath('ol/li/a[@class="wordCloud"]/text()')))
                    keywords = ';;'.join(map(lambda x: x.xpath('string()'),
                                             block.xpath('div[@class="search-hit-box"]/div[@class="keywords"]/span')))
                    data.append({'title': title, 'url': url, 'wordcloud': wordcloud, 'search-hit': keywords,
                                 'origin_file': path})
            print(f'parse {keyword} successfully, saving to .xlsx file ...')
            df = DataFrame(data=data)
            df.to_excel(f'{self.search_dir}/{keyword}.xlsx', index=False)
            print(f'{keyword} search data has saved to {self.search_dir}/{keyword}.xlsx successfully...')

    def read(self, path):
        with open(path, mode='r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def response_to_file(content: str, file_path: str, encoding: str = 'utf-8', mode: str = 'w'):
        with open(file_path, mode=mode, encoding=encoding) as f:
            f.write(content)

    def download_html(self, url):
        """
        根据url和keyword下载页面
        :param args:
        :return:
        """
        print(f'{url} start downloading ...')
        filename = url.rsplit('/', maxsplit=1)[1].replace('.html', '')
        filepath = f'{self.html_dir}/{filename}.html'
        response = self.session.get(url)
        self.response_to_file(response.text, filepath)
        file_size = os.stat(filepath).st_size / 1024
        if file_size < 100:
            os.remove(filepath)
            print(f'{url} 请求失败 已删除文件 {filepath}')
            time.sleep(1)
        else:
            print(f'{url} downloaded successfully...')

    def filter_policy_request(self, urls) -> set:
        """
        过滤政策请求url
        :param urls:
        :param keyword:
        :return:
        """
        downloaded_urls = set()
        for file in self.scan_directory_contents(self.html_dir, suffix='.html'):
            downloaded_urls.add(urljoin(self.base_url, 'chl/' + str(file.rsplit('\\', maxsplit=1)[1])))
        has_urls = urls - downloaded_urls
        print(f'共 {len(urls)} 已下载{len(downloaded_urls)} 还剩 {len(has_urls)}')
        invalid_urls = downloaded_urls - urls
        if len(invalid_urls) > 0:
            print(f'有{len(invalid_urls)} 个无效文件,正在删除 ...')
            for url in downloaded_urls - urls:
                file = os.path.join(self.html_dir, url.rsplit('/', maxsplit=1)[1])
                os.remove(file)
            print(f'{len(invalid_urls)}个无效文件删除完成 ...')
        return has_urls

    @timeit
    def download_policy_html(self, pool: bool = False):
        """ 下载政策页面 """
        policy_requests = set()

        for file in os.listdir(self.search_dir):
            if not file.endswith('.xlsx'):
                continue
            df = read_excel(f'{self.search_dir}/{file}', engine='openpyxl')
            policy_requests = policy_requests.union(set(df.url))

        policy_requests = self.filter_policy_request(urls=policy_requests)
        if len(policy_requests) == 0:
            print('all policy file has been downloaded...')
            return
        if pool:
            with ThreadPoolExecutor(max_workers=4) as thread_pool:
                futures_list = (thread_pool.submit(self.download_html, url) for url in policy_requests)
                for future in futures.as_completed(futures_list):
                    if future.exception():
                        print(future.exception())
        else:
            for request in policy_requests:
                self.download_html(request)
                time.sleep(0.5)

    @staticmethod
    def process_text(content):
        content = content.replace('\n', '').replace('，', ' ').replace('。', ' ').replace('\t', '')
        content = content.strip(' ').strip('\r\n').replace(u'\u3000', u'').replace(u'\xa0', u'')
        return content

    @timeit
    def parse_policy_info(self, to_file: str = None):
        """ 解析政策html """
        print('start parse policy html...')
        data = []
        for file in self.scan_directory_contents(f'{self.html_dir}'):
            result = {}
            response = etree.HTML(self.read(path=file))
            title = response.xpath('//h2[@class="title"]/text()')[0].strip()
            result['原文链接'] = urljoin(self.base_url, 'chl/' + str(file.rsplit('\\', maxsplit=1)[-1]))
            result['标题'] = title
            for li in response.xpath('//div[@class="fields"]/ul/li/div[@class="box"]'):
                strong = li.xpath('strong/text()')[0].replace('：', '')
                span = ';;'.join(li.xpath('span/@title'))
                title = li.xpath('@title')
                title = title[0] if title else None
                a = li.xpath('a/text()')
                a = a[0] if a else None
                text = li.xpath('text()')
                text = text[0] if text else None
                result[strong] = span or title or a or text
                if not result[strong]:
                    print(strong, result['原文链接'])

            content = response.xpath('string(//div[@id="divFullText"])').strip()
            # content = self.process_text(content)
            result['正文'] = content
            data.append(result)
        print('policy file has parsed successfully...')
        df = DataFrame(data=data)
        search_objs = [read_excel(file, engine='openpyxl') for file in self.scan_directory_contents(self.search_dir, suffix='xlsx')]
        search_data = concat(objs=search_objs, axis=0)
        search_data.drop_duplicates(subset=['url'], inplace=True)
        df = merge(df, search_data, left_on='原文链接', right_on='url', how='left')
        df.drop(columns=['title', 'url', 'origin_file'], inplace=True)
        if not to_file:
            date = time.strftime('%Y_%m_%d')
            to_file = f'data/pkulaw_policy_data_{date}.xlsx'
        df.to_excel(to_file, index=False)
        print(df.info())
        print(f'policy file saved to {to_file}')

    def run(self):
        self.download_search_html()
        self.parse_search_info()
        self.download_policy_html()
        self.parse_policy_info()
