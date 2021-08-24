import re

import requests
from lxml import html


# 获取搜索页面资源
def get_html(keywd, url):
    param = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0',

    }  # cookie相带就带
    Url = url % keywd
    html = requests.get(Url, params=param).content.decode('utf8')
    return html


def get_movielink(text):
    tree = html.fromstring(text)
    ctree = tree.xpath('//div[@class="clearfix search-item"]')
    link = []
    for item in ctree:
        print(item.xpath('em/text()')[0], item.xpath('div[2]/div/a/strong/text()')[0], ':',
              item.xpath('div[2]/div/a/@href')[0])
        link.append((item.xpath('div[2]/div/a/@href')[0], item.xpath('em/text()')[0]))
    return link  # 元组的列表，元组第一个元素是资源类型（如电影）


def get_downloadlink(link):
    if type_link == '电视剧':
        from_url = 'http://www.zimuzu.tv/resource/index_json/rid/%s/channel/tv' % link.split('/')[-1]
    else:
        from_url = 'http://www.zimuzu.tv/resource/index_json/rid/%s/channel/movie' % link.split('/')[-1]

    param = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0',
        # ‘cookie’可以有
        'Referer': 'http://www.zimuzu.tv%s' % link,
    }
    data = requests.get(from_url, params=param).content.decode('utf8')
    data = ''.join(data.split('=')[1:])
    print(data)
    # pattern='<h3><a href="(.*?)" target'
    pattern = '<h3><a href(.*?) target'
    # print(re.findall(pattern,data)[0].replace('\\',''))
    url = re.findall(pattern, data)[0].replace('\\', '').replace('"', '').strip()
    return url  # 获取的跳转到百度云等下载资源页面链接


def get_download(url):
    # 电驴在div[id="tab-g1-MP4"]/ul/li/ul/li[2]/a/@href下,磁力是第三个
    # 百度云在div[id="tab-g1-APP"]/ul/li/div/ul/li[2]/a/@href

    if 'zmz' not in url:  # 资源页面还包含一种跳转到种子站的链接，如https://rarbg.is/torrents.php?searchBattlestar%20Galactica%3A%20Blood%20and%20Chrome%20
        print('非下载页面：', url)
        pass
    param = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0',
    }
    res = requests.get(url, params=param).content.decode('utf-8')
    tree = html.fromstring(res)
    tree1 = tree.xpath('//div[@class="tab-content info-content"]//div[@class="tab-content info-content"]')
    if tree1:
        downloadList = []
        for item in tree1:
            ed2k = item.xpath('div[2]//ul[@class="down-links"]/li[2]/a/@href')  # 电驴
            name = item.xpath('div[1]//div[@class="title"]/span[1]/text()')  # name
            bdy = item.xpath('div[1]//div[@class="title"]/ul/li[2]/a/@href')  # 百度云
            for i, j, k in zip(name, bdy, ed2k):
                downloadList.append(dict(name=i, bdy=j, ed2k=k))
    print(downloadList)


get_download('http://got001.com/resource.html?code=WasT62')

# /api/v1/static/resource/detail?code=
# http://got001.com/api/v1/dynamic/resource/update_downloads?id=1273422572
