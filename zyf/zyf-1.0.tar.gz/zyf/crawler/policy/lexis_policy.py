# -*- coding: utf-8 -*-

"""
Author     : ZhangYafei
Description: 律商网政策数据下载
使用说明：
    1. 网页登陆之后将cookie复制，修改settings中的cookie信息
    2. 根据你的检索信息修改settings中的keyword/start/end/page_size
    3. 运行代码
"""
import json
import os
import re
import time
from concurrent import futures
from concurrent.futures.thread import ThreadPoolExecutor
from urllib.parse import urljoin

import requests
from lxml import etree
from pandas import DataFrame, read_excel
from zyf.timer import timeit

effective_level = {
    '法律': 1,
    '司法解释': 2,
    '行政法规': 4,
    '部门（委）规章': 8,
    '规范性文件': 16,
    '地方法规': 32,
    '行业规定': 64,
    '立法资料': 128,
    '指导性文件': 200,
    '国际条约': 256,
    '党纪法规': 512
}


class LexisNexisCrawler:
    def __init__(self, keywords: str, cookie: str, start: str = None, end: str = None, page_size: int = 100, data_dir: str = None):
        self.search_keywords = keywords
        self.search_start_time = start
        self.search_end_time = end
        self.search_count_file = 'search_result.json'
        self.page_size = page_size
        self.search_dir = f'{data_dir}/search'
        self.search_excel = f'{data_dir}/search_result.xlsx'
        self.policy_html_dir = f'{data_dir}/html'
        self.base_url = 'http://hk.lexiscn.com--dwjj.aaa.gou5juan.com'
        self.session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
            'Cookie': cookie,
        }
        self.session.headers.update(headers)

    def scan_directory_contents(self, dir_path):
        """
        这个函数接收文件夹的名称作为输入参数
        返回该文件夹中文件的路径
        以及其包含文件夹中文件的路径
        """
        for base_path, folders, files in os.walk(dir_path):
            for file in files:
                yield os.path.join(base_path, file)

    def write_to_file(self, path: str, text: str):
        with open(path, mode='w', encoding='utf-8') as f:
            f.write(text)

    def read(self, path, mode='r', encoding='utf-8'):
        with open(path, mode=mode, encoding=encoding) as f:
            return f.read()

    @staticmethod
    def response_to_file(content: str, file_path: str, encoding: str = 'utf-8', mode: str = 'w'):
        with open(file_path, mode=mode, encoding=encoding) as f:
            f.write(content)

    @staticmethod
    def process_text(content):
        content = content.replace('\n', '').replace('，', ' ').replace('。', ' ').replace('\t', '')
        content = content.strip(' ').strip('\r\n').replace(u'\u3000', u'').replace(u'\xa0', u'')
        return content

    @timeit
    def search(self):
        """
        对律商网的政策法规进行检索
            1. 根据检索条件获取检索结果，计算每种效率级别的检索结果页数
            2. 对检索结果页面进行下载
            3. 解析检索页面信息
            4. 将解析结果存储到excel文件中
        :return:
        """
        # 1. 根据检索条件获取检索结果，计算每种效率级别的检索结果页数
        if not os.path.exists(self.search_count_file):
            self.get_search_pages()
        with open('search_result.json') as f:
            level_search_count = json.load(f)
        print('共检索到：', level_search_count)

        # 2. 对检索结果页面进行下载
        level_search_set = set()
        for key in level_search_count:
            pages = level_search_count[key] // self.page_size + 1
            for page in range(1, pages + 1):
                level_search_set.add((key, page))
        if not os.path.exists(self.search_dir):
            os.makedirs(self.search_dir)
        else:
            file_list = {(file.rsplit('\\', maxsplit=1)[1].strip('.html').split('-')[0],
                          int(file.rsplit('\\', maxsplit=1)[1].strip('.html').split('-')[1])) for file in
                         self.scan_directory_contents(self.search_dir) if os.stat(file).st_size / 1024 > 100}
            for key in level_search_count:
                pages = level_search_count[key] // self.page_size + 1
                for page in range(1, pages + 1):
                    if (key, page) in file_list:
                        level_search_set.remove((key, page))
        if level_search_set:
            for level_name, page in level_search_set:
                print(level_name, page)
                self.download_search_page(level_name=level_name, level_val=effective_level[level_name], page_num=page)
        else:
            print('all search pages download successfully...')

        # 3. 解析检索页面信息
        file_list = filter(lambda file: os.stat(file).st_size > 100, self.scan_directory_contents(self.search_dir))
        data = []
        for file in file_list:
            self.parse_search_page(file=file, data=data)
        print(f'all search file has parsed successfully, exporting to file {self.search_excel}')

        # 4. 将解析结果存储到excel文件中
        df = DataFrame(data=data)
        df.to_excel(self.search_excel, index=False)
        print('all search results export to file successfully ...')

    def get_search_pages(self):
        """
        获取检索结果
        :return:
        """
        url = 'http://hk.lexiscn.com--dwjj.aaa.gou5juan.com/law/advanced_search_result.php'
        data = {
            'd': 1,
            'eng': 0,
            'prod_start': self.search_start_time,
            'prod_end': self.search_end_time,
            'content': self.search_keywords,
            'keyword_rem_content': self.search_keywords,
            'effective[]': 0,
            'countryed': '全国',
            'notenum_value': 0,
            'effectiveness_value': 0,
            'search_isEnglish': 0,
            'order': 6,
            'power_level_num': 0,
            'power_level_num_sel': 0,
            'power_level_str': '0,1,2,4,8,16,32,64,128,200,256,512',
            'mode': 'text',
            'mpl': self.page_size,
            'save': 0,
            'searchFilter': 3,
            'searchDisplay': 0,
            'source_come_from': 'lnc_utf-8',
            'display_style': 'list',
            'article_id_from_title': 1,
        }

        response = requests.post(url=url, headers=headers, data=data)

        response = etree.HTML(response.text)
        box = response.xpath('//tr[@id="dis_para"]/td[1]/div[@class="filter-box"]')[0]
        text = box.xpath('string(.)').strip()
        level_count_dict = {}
        for level_name, level_val in re.findall('(.+?) \[(\d+)\]', text):
            level_count_dict[level_name] = int(level_val)
        with open('search_result.json', mode='w') as f:
            json.dump(level_count_dict, f)

    def download_search_page(self, level_name: str, level_val: int, page_num: int):
        """
        下载检索页面
        :param level_name:
        :param level_val:
        :param page_num:
        :return:
        """
        print(f'start download {level_name} page {page_num} ...')
        url = f'http://hk.lexiscn.com--dwjj.aaa.gou5juan.com/law/advanced_search_result.php?eng=0&page={page_num}&crid=2fbf0c51-7114-401e-96ef-af0576414e10&prid=5db1cf2c-e292-45b5-b5b2-46f5a7be02b1'
        data = {
            'd': 1,
            'eng': 0,
            'prod_start': self.search_start_time,
            'prod_end': self.search_end_time,
            'content': self.search_keywords,
            'keyword_rem_content': self.search_keywords,
            'effective[]': 0,
            'countryed': '全国',
            'notenum_value': 0,
            'effectiveness_value': 0,
            'search_isEnglish': 0,
            'order': 6,
            'power_level_num': 0,
            'power_level_num_sel': 0,
            'power_level_str': '0,1,2,4,8,16,32,64,128,200,256,512',
            'mode': 'text',
            'mpl': self.page_size,
            'save': 0,
            'left_jurisdictional_str': level_name,
            'left_jurisdictional_id': level_val,
            'searchFilter': 3,
            'searchDisplay': 0,
            'source_come_from': 'lnc_utf-8',
            'display_style': 'list',
            'article_id_from_title': 1,
        }
        response = requests.post(url=url, headers=headers, data=data)
        file_path = f'{self.search_dir}/{level_name}-{page_num}.html'
        self.write_to_file(file_path, response.text)
        if os.stat(file_path).st_size / 1024 < 100:
            os.remove(file_path)
        print(f'{level_name} page {page_num} download successfully, write to {file_path}')

    def parse_search_page(self, file: str, data: list):
        """
        解析检索页面信息
        :param file:
        :param data:
        :return: None
        """
        level_name, page_num = file.rsplit('\\')[1].replace('.html', '').split('-')
        print(f'start parsing {level_name} page {page_num} ...')
        response = etree.HTML(self.read(file))
        for li in response.xpath('//ul[@id="legal_list"]/li'):
            a_title = li.xpath('span[@class="sr-title"]/a')[0]
            title = a_title.xpath('string()').strip()
            href = urljoin(self.base_url, a_title.xpath('@href')[0])
            data.append({'title': title, 'url': href, 'level': level_name, 'file': file})
        print(f'successful parsed {level_name} page {page_num} ...')

    def filter_policy_request(self, urls, title_url_map: dict) -> set:
        """
        过滤政策请求url
        :param urls:
        :param keyword:
        :return:
        """
        urls = set(urls)
        downloaded_urls = set()
        if not os.path.exists(self.policy_html_dir):
            os.mkdir(self.policy_html_dir)
        else:
            for file in os.listdir(self.policy_html_dir):
                title = file.replace('.html', '')
                if title in title_url_map:
                    downloaded_urls.add(title_url_map[title])
        has_urls = urls - downloaded_urls
        print(f'共 {len(urls)} 已下载{len(downloaded_urls)} 还剩 {len(has_urls)}')
        return has_urls

    def download_html(self, args: tuple):
        """
        根据url和keyword下载页面
        :param args:
        :return:
        """
        url, title = args
        filepath = f'{self.policy_html_dir}/{title}.html'
        response = self.session.get(url)
        if response.status_code != 200:
            print(f'{title} page download failed...')
            return
        self.response_to_file(response.text, filepath)
        file_size = os.stat(filepath).st_size / 1024
        if file_size < 80:
            os.remove(filepath)
            print(f'{url} 请求失败 已删除文件 {filepath}')
            time.sleep(1)
        else:
            print(f'{title} page downloaded successfully...')

    @timeit
    def download_policy_page(self, pool: bool = False):
        """
        下载政策页面
            1. 读取检索结果，构建请求集合
            2. 多请求集合进行过滤
            3. 对请求集合中请求进行下载
        :param pool: 是否使用线程池
        :return:
        """
        # 1. 读取检索结果，构建请求列表
        df = read_excel(self.search_excel)
        title_url_map = {}
        url_title_map = {}

        def build_map(row):
            title_url_map[row.title] = row.url
            url_title_map[row.url] = row.title

        df.apply(build_map, axis=1)

        # 2. 对请求列表进行过滤
        policy_requests = self.filter_policy_request(df.url, title_url_map)

        # 3. 下载政策页面
        if pool:
            with ThreadPoolExecutor(max_workers=4) as thread_pool:
                future_list = [thread_pool.submit(self.download_html, (url, url_title_map[url])) for url in
                               policy_requests]
                for future in futures.as_completed(future_list):
                    if future.exception():
                        print(future.exception())
        else:
            for url in policy_requests:
                print(url, url_title_map[url])
                self.download_html(args=(url, url_title_map[url]))

    @timeit
    def parse_policy_page(self, to_file: str = None):
        """
        解析政策页面数据
        :param to_file:
        :return:
        """
        print('start scan dir files ...')
        file_list = self.scan_directory_contents(self.policy_html_dir)
        print('start build title-level dict ...')
        search_df = read_excel(self.search_excel)
        title_level_map = {}

        def build_map(row):
            title_level_map[row.title.strip()] = (row.level, row.url)

        search_df.apply(build_map, axis=1)

        policy_df = read_excel('data/policy_data.xlsx')

        def build_map2(row):
            if row['标题'].strip() not in title_level_map:
                title_level_map[row['标题'].strip()] = (row['效力级别'], row['原文链接'])

        policy_df.apply(build_map2, axis=1)

        print('start parse file info ...')
        data = []
        for file in file_list:
            response = etree.HTML(self.read(file))
            title = response.xpath('//h1[@class="detailtitle"]/text()')[0].strip()
            level, url = title_level_map[title]
            table = response.xpath('//div[@class="tables"]/table')[0]
            issue_date = table.xpath('tr/td/div[contains(text(), "发文日期")]/../following-sibling::td[1]/text()')[
                0].strip()
            # valid_range = table.xpath('tr/td/div[contains(text(), "有效范围")]/../following-sibling::td[1]/text()')[0].strip()
            issue_authority = table.xpath('tr/td/div[contains(text(), "发文机关")]/../following-sibling::td[1]/text()')[
                0].strip()
            doc_num = table.xpath('tr/td/div[contains(text(), "文号")]/../following-sibling::td[1]/text()')[0].strip()
            timelines = table.xpath('tr/td/div[contains(text(), "时效性")]/../following-sibling::td[1]/text()')[0].strip()
            effective_date = table.xpath('tr/td/div[contains(text(), "生效日期")]/../following-sibling::td[1]/text()')[
                0].strip()
            classification = table.xpath('string(tr/td/div[contains(text(), "分类")]/../following-sibling::td[1])')
            content = response.xpath('string(//div[@id="content-wrap"]/div[@class="txt_content"])').strip()
            # content = self.process_text(content)
            data.append({'标题': title, '发布日期': issue_date, '发文机关': issue_authority, '效力级别': level,
                         '文号': doc_num, '时效性': timelines, '生效日期': effective_date, '分类': classification, '正文': content,
                         '原文链接': url})
        print('parse file info successfully ...')
        print('exporting to file ...')
        df = DataFrame(data=data)
        print(df.info())
        if not to_file:
            date = time.strftime('%Y_%m_%d')
            to_file = f'data/lexis_policy_data_{date}.xlsx'
        df.to_excel(to_file, index=False)
        print(f'exporting to file {to_file} successfully...')

    def run(self):
        self.search()
        self.download_policy_page()
        self.parse_policy_page()
