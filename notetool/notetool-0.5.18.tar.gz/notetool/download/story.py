# coding: utf-8
import os
import queue
import sqlite3
import sys
import threading
import urllib.parse
from time import sleep

import requests
from Crypto.Cipher import AES
from requests.adapters import HTTPAdapter

from notetool.tool import log

logger = log('download')
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


def info(msg):
    logger.info(msg)


def get_session(pool_connections, pool_maxsize, max_retries):
    """构造session"""
    session = requests.Session()
    adapter = HTTPAdapter(pool_connections=pool_connections, pool_maxsize=pool_maxsize, max_retries=max_retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


class m3u8Dataset:
    def __init__(self, db_path='story_resource.table', table_name='movie_m3u8'):
        self.db_path = db_path

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.table_name = table_name
        self.__init()

    def __init(self):
        self.execute("""
        create table if not exists {} (
            id                  integer primary key AUTOINCREMENT
           ,movie_url           varchar(200) 
           ,movie_name          varchar(200)
           ,is_download         integer       DEFAULT (0)
           ,param1              varchar(200)  DEFAULT ('')
           ,param2              varchar(200)  DEFAULT ('')
           ,param3              varchar(200)  DEFAULT ('')
           )
        """.format(self.table_name))

    def close(self):
        self.cursor.close()
        self.conn.close()

    def print(self):
        print(self.cursor.rowcount)

    def test(self):
        res = self.execute(
            """insert into {} (movie_url, movie_name,is_download) values (\'url\',\'name\', 0)""".format(
                self.table_name)
        )
        return res

    def all(self):
        res = self.execute(
            """select * from  {}""".format(self.table_name))

        for line in res:
            print(line)

        return res

    def execute(self, sql):
        # print('sql:{}'.format(sql))
        self.conn.commit()
        return self.cursor.execute(sql)

    def insert(self, url='', name='', param1='', param2='', param3=''):
        name = name.replace("'", '')
        res = self.execute(
            """
            insert into {} (movie_url, movie_name,param1,param2,param3) 
            values ('{}','{}','{}','{}','{}')
            """.format(self.table_name, url, name, param1, param2, param3)
        )
        return res

    def update(self, url='', name='', param1='', param2='', param3=''):
        conf = self.condition(url=url, name=name, param1=param1, param2=param2, param3=param3)

        res = self.execute(
            """
            UPDATE {} set is_download = 1 where {}
            """.format(self.table_name, conf)
        )
        return res

    def condition(self, url='', name='', param1='', param2='', param3=''):
        conf = []
        name = name.replace("'", '')
        conf.append("movie_url='{}'".format(url)) if url else None
        conf.append("movie_name='{}'".format(name)) if name else None
        conf.append("param1='{}'".format(param1)) if param1 else None
        conf.append("param2='{}'".format(param2)) if param2 else None
        conf.append("param3='{}'".format(param3)) if param3 else None
        return ' and '.join(conf)

    def exists(self, url='', name='', param1='', param2='', param3=''):
        conf = self.condition(url=url, name=name, param1=param1, param2=param2, param3=param3)

        res = self.execute(
            """select * from  {} where {}""".format(self.table_name, conf))
        for _ in res:
            return True

        return False

    def select(self, size=50):
        res = self.execute(
            """select * from  {} where is_download=0 limit {} 
            """.format(self.table_name, size))

        urls = []
        for line in res:
            urls.append((line[1], line[2]))
        return urls


class m3u8File:
    def __init__(self, url="", origin="", file_name="", file_dir="", queue_size=196):
        self.url = url
        self.origin = origin

        self.file_dir = file_dir
        self.file_name = file_name
        self.ts_list = []
        self.ts_path = os.path.join(self.file_dir, self.file_name)

        self.queue_work = queue.Queue(queue_size)
        self.queue_lock = threading.Lock()
        self.exit_flag = 0

        self.count_total = 0
        self.count_complete = 0

        self.key = ""

        if file_dir and not os.path.isdir(file_dir):
            os.makedirs(file_dir)

        if self.ts_path and not os.path.isdir(self.ts_path):
            os.makedirs(self.ts_path)

    def show_progress(self):
        self.count_complete += 1
        percent = self.count_complete / self.count_total

        bar_length = 50
        hashes = '#' * int(percent * bar_length)
        spaces = ' ' * (bar_length - len(hashes))
        sys.stdout.write("\rPercent: [%s] %.2f%%" % (hashes + spaces, percent * 100))
        sys.stdout.flush()

    # 填充队列
    def fill_queue(self, name_list):
        self.queue_lock.acquire()
        for word in name_list:
            self.queue_work.put(word)
            name_list.remove(word)
            if self.queue_work.full():
                break
        self.queue_lock.release()

    # 将TS文件整合在一起
    def merge_file(self):
        self.count_complete = 0
        file_output = os.path.join(self.file_dir, self.file_name + '.mp4')

        with open(file_output, 'wb') as outfile:
            for index in range(0, self.count_total):
                file_name = self.ts_list[index].split('/')[-1].split('?')[0]
                file_input = os.path.join(self.ts_path, file_name)

                self.show_progress()
                if not os.path.exists(file_input):
                    continue

                with open(file_input, 'rb') as infile:
                    outfile.write(infile.read())

                # 删除临时ts文件
                os.remove(file_input)
        os.rmdir(self.ts_path)


class m3u8Downloader:
    def __init__(self, session=None, thread_size=64):
        self.thread_size = thread_size

        self.session = session or get_session(50, 50, 3)
        self.thread_list = []
        for i in range(self.thread_size):
            self.thread_list.append("Thread-" + str(i))

        self.file = None
        pass

    class downloadThread(threading.Thread):
        def __init__(self, session, thread_id, file: m3u8File):
            threading.Thread.__init__(self)
            self.threadID = thread_id
            self.session = session

            self.file = file

        def run(self):
            # logger.info("开启线程：" + self.name)
            self.download_data(self.file)
            # logger.info("退出线程：" + self.name)

        # 下载数据
        def download_data(self, file: m3u8File):
            while not self.file.exit_flag:
                file.queue_lock.acquire()
                if not file.queue_work.empty():
                    data = file.queue_work.get()
                    file.queue_lock.release()
                    # logger.info("%s 使用了 %s" % (threadName, data) + '\n', end='')
                    url = data
                    file_name = url.split('/')[-1].split('?')[0]
                    file_path = os.path.join(self.file.ts_path, file_name)
                    if os.path.exists(file_path):
                        file.show_progress()
                        continue

                    retry = 5
                    while retry:
                        try:
                            r = self.session.get(url, timeout=20, headers=headers)
                            if r.ok:
                                with open(file_path, 'wb') as f:
                                    if len(file.key) > 0:
                                        cryptor = AES.new(file.key, AES.MODE_CBC, file.key)
                                        f.write(cryptor.decrypt(r.content))
                                    else:
                                        f.write(r.content)
                                file.show_progress()
                                break
                        except Exception as e:
                            retry -= 1
                    if retry == 0:
                        print('[FAIL]%s' % url)
                else:
                    file.queue_lock.release()

    def get_real_url(self, m3u8_url):
        r = self.session.get(m3u8_url, timeout=10)
        if r.ok:
            body = r.content.decode()
            if body:
                ts_url = ''
                body_list = body.split('\n')
                for n in body_list:
                    if n and not n.startswith("#"):
                        ts_url = urllib.parse.urljoin(m3u8_url, n.strip())
                if ts_url != '':
                    return ts_url
        else:
            print(r.status_code)

    def download(self, file: m3u8File):
        threads = []
        thread_id = 1
        # 创建新线程
        for _ in self.thread_list:
            thread = self.downloadThread(self.session, thread_id, file)
            thread.start()
            threads.append(thread)
            thread_id += 1
        ts_list_tem = file.ts_list.copy()
        file.fill_queue(ts_list_tem)
        # 等待队列清空
        while not file.queue_work.empty() or len(ts_list_tem) > 0:
            if file.queue_work.full():
                sleep(1)
                pass
            else:
                file.fill_queue(ts_list_tem)
        # 通知线程是时候退出
        file.exit_flag = 1
        # 等待所有线程完成
        for t in threads:
            t.join()
        return True

    def start(self, m3u8_url, file_dir, video_name):
        real_url = self.get_real_url(m3u8_url)
        file = m3u8File(url=real_url, origin=m3u8_url, file_name=video_name, file_dir=file_dir, queue_size=96)
        self.start_file(file)

    def start_file(self, file: m3u8File):
        self.file = file

        r = self.session.get(self.file.url, timeout=10, headers=headers)

        if r.ok:
            body = r.content.decode()

            if body:
                body_list = body.split('\n')
                for line in body_list:
                    if "#EXT-X-KEY" in line:  # 找解密Key
                        method_pos = line.find("METHOD")
                        comma_pos = line.find(",")
                        method = line[method_pos:comma_pos].split('=')[1]
                        print("Decode Method：", method)

                        uri_pos = line.find("URI")
                        quotation_mark_pos = line.rfind('"')
                        key_path = line[uri_pos:quotation_mark_pos].split('"')[1]

                        key_url = file.url.rsplit("/", 1)[0] + "/" + key_path  # 拼出key解密密钥URL
                        res = requests.get(key_url, headers=headers)
                        file.key = res.content
                        print("key：", file.key)

                    if line and not line.startswith("#"):
                        file.ts_list.append(urllib.parse.urljoin(file.url, line.strip()))
                if file.ts_list:
                    file.count_total = len(file.ts_list)
                    info('ts的总数量为：' + str(file.count_total) + '个')

                    info('开始下载文件')
                    res = self.download(file)

                    if res:
                        info('开始合并文件')
                        file.merge_file()
                        info("下载完成")

                    else:
                        logger.warn('下载失败')
        else:
            logger.error(r)
