import json
from yd_addr import frozen

encodings = ['utf-8', 'gbk', 'utf-8-sig', 'GB2312', 'gb18030']
BASE_DIR = frozen.app_path() + "/"

with open(BASE_DIR + r'resources/addr_dict.json', 'r', encoding='gbk') as jf:
    addr_dict = json.load(jf)
name_code_dict = addr_dict['name_code_dict']
code_name_dict = addr_dict['code_name_dict']

for encoding in encodings:
    try:
        with open(BASE_DIR + r'resources/商品品类.txt', 'r', encoding=encoding) as f:
            goods_category = set()   ###定义为set集合类型
            for line in f.readlines():
                line = line.strip('\n')
                goods_category.add(line.upper())
        print('Successfully read goods_category by %s' % encoding)
        break
    except:
        print('Failed to read goods_category by %s' % encoding)


def get_stop_word_list(stop_word_path):
    """
    得到停止词 ‘的地得  语气词 标点符号等’
    :param 空
    :return: 停止词列表
    """
    with open(stop_word_path, "r", encoding="gbk") as f:
        # swl stop word list
        swl = [sw.replace('\n', '') for sw in f.readlines()]
    return swl


stop_word_list = get_stop_word_list(BASE_DIR + r'resources/stopwords3_标点符号.txt')
