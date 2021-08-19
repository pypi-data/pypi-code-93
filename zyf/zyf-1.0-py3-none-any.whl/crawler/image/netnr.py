# -*- coding: utf-8 -*-

"""
DateTime   : 2021/04/04 10:54
Author     : ZhangYafei
Description: 高清壁纸下载
网址： https://ss.netnr.com/wallpaper#18
"""
import os
from concurrent.futures import ThreadPoolExecutor

from prettytable import PrettyTable
from requests import Session, Response
from tqdm import tqdm
from zyf.timer import timeit

from zyf.color import print_color, Foreground


class NetnrCrawler:
    def __init__(self, dir_path: str):
        self.url = 'https://bird.ioliu.cn/v2'
        self.history_file = None
        self.history_file_path = 'history/history_netnr.txt'
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

        self.init_tips_info()
        self.init_history_file()

    def init_history_file(self):
        if not os.path.exists('history'):
            os.mkdir('history')
        self.history_file = open(self.history_file_path, mode='a+', encoding='utf-8')
        if os.path.exists(self.history_file_path):
            self.history_file.seek(0)
            self.downloaded_images = {line.strip() for line in self.history_file}

    def init_tips_info(self):
        self.image_type_info = {
            0: '最新壁纸', 6: '美女模特', 30: '爱情美图', 9: '风景大片',
            36: '4K专区', 15: '小清新', 26: '动漫卡通', 11: '明星风尚',
            14: '萌宠动物', 5: '游戏壁纸', 12: '汽车天下', 10: '炫酷时尚',
            29: '月历壁纸', 7: '景视剧照', 35: '文字控', 13: '节日美图',
            22: '军事天地', 16: '劲爆体育', 18: 'BABY秀'
        }

        self.tips_info_table = PrettyTable(['序号1', '壁纸分类1', '序号2', '壁纸分类2'])
        row = []
        for index, key in enumerate(self.image_type_info, start=1):
            row.extend([key, self.image_type_info[key]])
            if len(row) == 4:
                self.tips_info_table.add_row(row)
                row.clear()
                continue
            if index == len(self.image_type_info):
                row.extend(['-', '-'])
                self.tips_info_table.add_row(row)

    @timeit
    def get_image_data(self, start: int = 1, count: int = 50, image_type: int = 0):
        image_type_desc = self.image_type_info[image_type]
        if not os.path.exists(f'{self.image_dir}/{image_type_desc}'):
            os.mkdir(f'{self.image_dir}/{image_type_desc}')
        if image_type == 0:
            url = f'http://wallpaper.apc.360.cn/index.php?c=WallPaper&start={start}&count={count}&from=360chrome&a=getAppsByOrder&order=create_time'
        else:
            url = f'http://wallpaper.apc.360.cn/index.php?c=WallPaper&start={start}&count={count}&from=360chrome&a=getAppsByCategory&cid={image_type}'

        response = self.session.get(url=self.url, params={'url': url})
        result = response.json()

        for image_info in result['data']:
            uid = image_info['id']
            image_url = image_info['url']
            tags = image_info['tag'].replace('_category_', '').replace('_全部_', '').strip('_ ').replace(' ', '')
            size = image_info['resolution'].replace('x', '_')
            filepath = f'{self.image_dir}/{image_type_desc}/{tags}_{uid}_{size}.jpg'
            if filepath not in self.downloaded_images:
                self.image_data_list.add((image_url, filepath))
            else:
                self.downloaded_count += 1

    @timeit
    def start_download(self):
        images_count = len(self.image_data_list)
        if images_count > 20:
            print_color('正在开启多线程加速下载')
            workers = images_count // 20
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

    def run(self):
        print(self.tips_info_table)
        while True:
            image_type = input('请选择下载的壁纸分类(序号,默认回车为0) >>  ')
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
            count = input('请输入下载数量（整数，默认为50）>> ')
            if count:
                if not count.isdecimal():
                    print('您输入的数量有误，必须为整数，请重新输入')
                    continue
                else:
                    count = int(count)
            else:
                count = 50
            break
        self.get_image_data(image_type=image_type, count=count)

        if self.downloaded_count == 0:
            print_color(f'共检索到 {len(self.image_data_list)} 张图片, 开始下载', foreground=Foreground.Green)
        elif len(self.image_data_list) == 0:
            print_color(f'共检索到 {self.downloaded_count} 张图片, 已全部下载完成！', foreground=Foreground.Green)
            return
        else:
            print_color(
                f'共检索到 {len(self.image_data_list) + self.downloaded_count} 张图片, 已下载 {self.downloaded_count} 张, 还需下载 {len(self.image_data_list)} 张, 开始下载',
                foreground=Foreground.Green)

        self.start_download()

    def __del__(self):
        self.history_file.close()
