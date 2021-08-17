# -*- coding:utf-8 -*-
# Author: hankcs
# Date: 2021-03-04 19:04
import os
import platform
from hanlp_downloader import Downloader
from hanlp_downloader.log import DownloadCallback
from tests.download_small_file import sha1sum
import sys


def main():
    good = 0
    for i in range(100):
        good += run()
        print(f'{good} / {i + 1}')


def run():
    file_path = 'tmp.zip'
    downloader = Downloader(
        'https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3105/allzip', file_path, 4,
        high_speed=False, headers={
            'User-agent': f'HanLP/2.1.0.a1 ({platform.platform()})'})
    downloader.subscribe(DownloadCallback(out=sys.stdout))
    downloader.start_sync()
    if not sha1sum(file_path) == '79eaddb99a04763f1cce33cb2b1b81c0bbeeb77b':
        return 0
    else:
        os.remove(file_path)
        return 1


if __name__ == '__main__':
    main()
