# -*- coding:utf-8 -*-
# Author: hankcs
# Date: 2021-03-04 19:04
import os
import platform
from hanlp_downloader import Downloader
from hanlp_downloader.log import DownloadCallback


def sha1sum(file_name):
    import hashlib
    BUF_SIZE = 65536

    sha1 = hashlib.sha1()

    with open(file_name, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()


def main():
    good = 0
    for i in range(1000):
        good += run(i)
        print(f'\r{good} / {i + 1}', end='')


def run(i):
    file_path = 'tmp.zip'
    downloader = Downloader(
        'https://file.hankcs.com/corpus/char_table.json.zip', file_path, 4,
        high_speed=False, headers={
            'User-agent': f'HanLP/2.1.0.a1 ({platform.platform()})'})
    # downloader.subscribe(DownloadCallback())
    downloader.start_sync()
    sha_sum = sha1sum(file_path)
    if not sha_sum == '3e1a3448d60694d4acb2e066206b68658c61ad10':
        os.rename(file_path, f'{i}.zip')
        print(f'File checksum failed: {sha_sum}')
        return 0
    else:
        os.remove(file_path)
        return 1


if __name__ == '__main__':
    main()
