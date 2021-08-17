from __future__ import unicode_literals
# Remain to be filled with test cases.
from hanlp_downloader import Downloader

import sys

from hanlp_downloader.bin import download_callback


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


downloader = Downloader('http://file.hankcs.com/hanlp/mtl/open_tok_pos_ner_srl_dep_sdp_con_electra_small_20201223_035557.zip', '1.zip', 4, high_speed=False)
downloader.subscribe(download_callback, 256)
downloader.start_sync()

# assert sha1sum('video.mp4') == '5298b02a64cb4ed7cc6e617b0cc2f0b4b36afb6a'