import os
import ssl
import json
import time
import requests
import multiprocessing.dummy as mp


class QiemanCrawler(object):
    def __init__(self):
        self.portfolio_url_prefix = 'https://qieman.com/pmdj/v1/pomodels/'
        self.result_dir = './'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15',
            'Accept': 'application/json, text/plain, */*',
            'x-sign': '1602564825201B1482E004AA21C91B8F184BB5524C048',
            'Host': 'qieman.com',
            'Referer': 'https://qieman.com/strategies/earl28/detail',
        }

    def setup_proxy(self):
        # 代理隧道验证信息
        proxyUser = "ZPQZ1677448071229353"
        proxyPass = "6pVOQo0ZgMFx"
        # 代理服务器
        proxyHost = "dyn.horocn.com"
        proxyPort = "50000"
        proxyMeta = f"http://{proxyUser}:{proxyPass}@{proxyHost}:{proxyPort}"
        self.proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }

    def crawl(self, portfolio_id):
        portfolio_id = f'ZH{str(portfolio_id).zfill(6)}'
        url = f'{self.portfolio_url_prefix}{portfolio_id}'

        retry = 0
        while retry < 2:
            if retry > 0:
                print(f'Retry {retry} times for index {portfolio_id}')

            try:
                # Crawl portfolio description
                # try:
                #     # r = requests.get(url=url, headers=self.headers, proxies=self.proxies, timeout=3)
                #     r = requests.get(url=url, headers=self.headers, timeout=3)
                #     result_json = r.json()
                #     if 'code' in result_json and result_json['code'] == "1600":
                #         print(f'Portfolio {portfolio_id} does not exist!')
                #         return True

                #     result_file = os.path.join(self.result_dir, f'{portfolio_id}.json')
                #     with open(result_file, 'w') as fout:
                #         fout.write(json.dumps(result_json, ensure_ascii=False, indent=4))

                # except json.decoder.JSONDecodeError as e:
                #     print(print(f'Failed to parse portfolio "{r}" for {portfolio_id}! {e}'))
                #     return True

                # Crawl portfolio adjustments
                page_index = 0
                finished = False
                while not finished:
                    url = f'{self.portfolio_url_prefix}{portfolio_id}/adjustments?page={page_index}&size=100&format=openapi&isDesc=true'
                    print(url)
                    # url = f'{self.portfolio_url_prefix}{portfolio_id}/nav-history?'
                    try:
                        # r = requests.get(url=url, headers=self.headers, proxies=self.proxies, timeout=3)
                        r = requests.get(url=url, headers=self.headers, timeout=3)
                        result_json = r.json()
                        finished = result_json['last']

                        result_file = os.path.join(self.result_dir, f'{portfolio_id}_adj{page_index}.json')
                        with open(result_file, 'w') as fout:
                            fout.write(json.dumps(result_json, ensure_ascii=False, indent=4))
                        page_index += 1

                    except json.decoder.JSONDecodeError as e:
                        print(print(f'Failed to parse adjustments "{r}" for {portfolio_id}! {e}'))
                        return True

                print(f'Portfolio {portfolio_id} got')
                return True

            except Exception as e:
                print(f'[WARN] at {portfolio_id}, {e}')
                retry += 1

        print(f'[ERROR] for index {portfolio_id}')
        return False

    def test(self, portfolio_id):
        url = 'http://api.ip.sb/ip'
        r = requests.get(url=url, headers=self.headers, proxies=self.proxies, timeout=3)
        print(r.content.decode())

    def parallel_craw(self, start, end):
        p = mp.Pool(3)
        # p.map(self.test, range(start, end))
        p.map(self.crawl, range(start, end))
        p.close()
        p.join()

    def linear_craw(self, start, end):
        for i in range(start, end):
            # self.test(i)
            self.crawl(i)

    def craw_targets(self, pids):
        for i in pids:
            self.crawl(i)
            # self.test(i)

    def parallel_craw_targets(self, pids):
        p = mp.Pool(3)
        p.map(self.crawl, pids)
        p.close()
        p.join()


if __name__ == '__main__':
    crawler = QiemanCrawler()
    # crawler.setup_proxy()

    start = 17252
    end = 17253

    crawler.linear_craw(start, end)
    # crawler.parallel_craw(start, end)

    # cannot be crawled <= 50000
    # pids = [6536, 6910, 7255, 8508, 10261, 17252, 17255, 14162, 17751, 19522, 25902, 25904, 34050, 35300, 35567]
    # pids = [16]
    # crawler.parallel_craw_targets(pids)
