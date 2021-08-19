# -*- coding: utf-8 -*-

"""
DateTime   : 2021/04/05 10:27
Author     : ZhangYafei
Description: 高清壁纸下载
网址：https://pic.netbian.com
"""
import os
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

from lxml import etree
from prettytable import PrettyTable
from requests import Session, Response
from tqdm import tqdm
from zyf.timer import timeit

from zyf.color import print_color, Foreground


class NetbianCrawler:
    def __init__(self, dir_path: str):
        self.url = 'https://pic.netbian.com/'
        self.history_file = None
        self.history_file_path = 'history/history_netbian.txt'
        self.image_dir = dir_path
        self.image_type_info = {}
        self.image_data_list = set()
        self.downloaded_images = set()
        self.downloaded_count = 0
        self.success_count = 0
        self.tips_info_table = None
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
        self.session = Session()

        self.init_session()
        self.init_tips_info()
        self.init_history_file()

    def init_session(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 Edg/89.0.774.68',
            # 'cookie': '__yjs_duid=1_40c45bce96b64d1badda44f4241d15f91616333696156; Hm_lvt_14b14198b6e26157b7eba06b390ab763=1616333697; Hm_lvt_526caf4e20c21f06a4e9209712d6a20e=1616333709,1617451949,1617503745; zkhanecookieclassrecord=%2C53%2C54%2C66%2C; PHPSESSID=sau1j48j542hiat5qn0bs3asg5; zkhanmlusername=qq_%D5%C5%D1%C7%B7%C9; zkhanmluserid=4768831; zkhanmlgroupid=1; zkhanmlrnd=hYphhT5AqLXZ1mjospge; zkhanmlauth=870a8e483a168356225331aa420bcd17; zkhandownid26903=1; Hm_lpvt_526caf4e20c21f06a4e9209712d6a20e=1617590788'
        }
        self.session.headers = headers

    def init_history_file(self):
        if not os.path.exists('history'):
            os.mkdir('history')
        self.history_file = open(
            self.history_file_path,
            mode='a+',
            encoding='utf-8')
        if os.path.exists(self.history_file_path):
            self.history_file.seek(0)
            self.downloaded_images = {line.strip()
                                      for line in self.history_file}

    def init_tips_info(self):
        self.image_type_info = {
            1: '4kfengjing', 2: '4kmeinv', 3: '4kyouxi', 4: '4kdongman',
            5: '4kyingshi', 6: '4kmingxing', 7: '4kqiche', 8: '4kdongwu',
            9: '4krenwu', 10: '4kmeishi', 11: '4kzongjiao', 12: '4kbeijing',
        }
        self.image_tip_info = {
            1: '4K风景', 2: '4K美女', 3: '4K游戏', 4: '4K动漫',
            5: '4K影视', 6: '4K明星', 7: '4K汽车', 8: '4K动物',
            9: '4K人物', 10: '4K美食', 11: '4K宗教', 12: '4K背景',
        }

        self.tips_info_table = PrettyTable(['序号1', '壁纸分类1', '序号2', '壁纸分类2'])
        row = []
        for index, key in enumerate(self.image_tip_info, start=1):
            row.extend([key, self.image_tip_info[key]])
            if len(row) == 4:
                self.tips_info_table.add_row(row)
                row.clear()
                continue
            if index == len(self.image_type_info):
                row.extend(['-', '-'])
                self.tips_info_table.add_row(row)

    def get_image_data(self, url: str, image_type_desc: str, page_num: int):
        """
        获取图片数据
        :param url: 请求url
        :param image_type_desc: 壁纸分类描述
        :param page_num: 请求页
        :return:
        """
        url = url if page_num == 1 else f'{url}/index_{page_num}.html'

        response = self.session.get(url)
        html = etree.HTML(response.content)

        for li in html.xpath('//*[@id="main"]/div[3]/ul/li'):
            href = li.xpath('a/@href')[0]
            uid = href.rsplit('/', maxsplit=1)[1].replace('.html', '')
            title = li.xpath('a/img/@alt')[0].replace(' ', '_')
            response = self.session.get(urljoin(self.url, href))
            html = etree.HTML(response.content)
            img_url = urljoin(
                self.url, html.xpath('//a[@id="img"]/img/@src')[0])
            filepath = f'{self.image_dir}/{image_type_desc}/{title}_{uid}.jpg'
            if filepath not in self.downloaded_images:
                self.image_data_list.add((img_url, filepath))
            else:
                self.downloaded_count += 1

    @timeit
    def start_download(self, page_nums: int):
        if len(self.image_data_list) > 20:
            print_color('正在开启多线程加速下载')
            workers = page_nums if page_nums >= 4 else 4
            data_list = [set() for _ in range(workers)]
            for index, image in enumerate(self.image_data_list):
                remainder = index % workers
                data_list[remainder].add(image)
            with ThreadPoolExecutor(max_workers=workers) as pool:
                pool.map(self.download_images, data_list)
            print_color(f'\n\n{self.success_count} 张图片下载成功!', foreground=Foreground.Green)
        else:
            self.download_images(data_list=self.image_data_list)
            print_color(f'{self.success_count} 张图片下载完成!', foreground=Foreground.Green)

    def download_images(self, data_list: set = None):
        if not data_list:
            return
        task_progress = tqdm(data_list, ncols=100)
        for index, task in enumerate(task_progress, start=1):
            url, filepath = task
            task_progress.set_description(f"正在下载第 {index} 张图片")
            response = self.session.get(url=url)
            self.save_to_file(response, filepath=filepath)
            self.success_count += 1

    def save_to_file(self, response: Response, filepath: str):
        with open(filepath, mode='wb') as f:
            f.write(response.content)
        self.history_file.write(f'{filepath}\n')

    @timeit
    def search_images(self, image_type: int, page_nums: int):
        if image_type != 0:
            url = urljoin(self.url, self.image_type_info[image_type])
            image_type_desc = self.image_tip_info[image_type]
        else:
            url = self.url
            image_type_desc = '最新壁纸'

        if not os.path.exists(f'{self.image_dir}/{image_type_desc}'):
            os.mkdir(f'{self.image_dir}/{image_type_desc}')

        print_color(f'正在检索 - {self.image_tip_info[image_type]} - 请稍等 - 马上开始下载')
        if page_nums > 1:
            with ThreadPoolExecutor(max_workers=page_nums) as pool:
                pool.map(self.get_image_data, (url for _ in range(page_nums)),
                         (image_type_desc for _ in range(page_nums)), range(1, page_nums + 1))
        else:
            self.get_image_data(url=url, image_type_desc=image_type_desc, page_num=1)

    def run(self):
        print(self.tips_info_table)
        while True:
            image_type = input('请选择下载的壁纸分类(序号,默认为最新壁纸) >>  ')
            if image_type:
                if not image_type.isdecimal() or int(image_type) not in self.image_type_info:
                    print('您输入的分类序号有误，请重新确认后输入')
                    continue
                else:
                    image_type = int(image_type)
            else:
                image_type = 0
            break
        while True:
            page_nums = input('请输入下载页数（整数，默认为1，每页20）>> ')
            if page_nums:
                if not page_nums.isdecimal():
                    print('您输入的页数有误，必须为整数，请重新输入')
                    continue
                else:
                    page_nums = int(page_nums)
            else:
                page_nums = 1
            break

        self.search_images(image_type=image_type, page_nums=page_nums)

        if self.downloaded_count == 0:
            print_color(
                f'共检索到 {len(self.image_data_list)} 张图片, 开始下载', foreground=Foreground.Green)
        elif len(self.image_data_list) == 0:
            print_color(
                f'共检索到 {self.downloaded_count} 张图片, 已全部下载完成！',
                foreground=Foreground.Green)
            return
        else:
            print_color(
                f'共检索到 {len(self.image_data_list) + self.downloaded_count} 张图片, 已下载 {self.downloaded_count} 张, 还需下载 {len(self.image_data_list)} 张, 开始下载',
                foreground=Foreground.Green)

        self.start_download(page_nums)

    def __del__(self):
        self.history_file.close()
