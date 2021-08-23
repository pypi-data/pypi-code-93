import re
import json
import logging
from IPy import IP, IPSet
from tld import get_tld
from .html import get_html, post_data

logger = logging.getLogger(__name__)

INTERNAL_IP_LIST = ['10.0.0.0/8', '127.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', '100.64.0.0/10']

MASK = [128, 192, 224, 240, 248, 252, 254, 255]


def get_addr_from_ip_by_whois(ip):
    try:
        api = f'http://whois.pconline.com.cn/ipJson.jsp?ip={ip}&json=true'
        info = get_html(api)
        info = json.loads(info)
        info = json.loads(info)
        res = info
    except Exception as e:
        logger.warning(e, exc_info=True)
        res = False
    return res


def get_jw_from_addr_by_mapqq(city):
    try:
        api = 'https://apis.map.qq.com/jsapi?qt=poi&wd=' + city
        info = get_html(api)
        info = json.loads(info)
        pointx = info['detail']['city']['pointx']
        pointy = info['detail']['city']['pointy']
    except Exception as e:
        logger.warning(e, exc_info=True)
        pointx = 0
        pointy = 0
    return pointx, pointy


def get_fingerprint_from_ip_by_whatweb(target):
    api = 'http://whatweb.bugscaner.com/what.go'
    _data = {'url': target, 'location_capcha': 'no'}
    try:
        info = post_data(api, _data)
        print('获取信息', info)
        if info:
            res = info
        else:
            res = False
    except Exception as e:
        logger.warning(e)
        res = False
    return json.loads(res.text)


def is_domain(domain, use_tld=False):
    """判断是否是域名,use_tld会判断的更加精准一些，但是会耗费时间（大概20倍）"""
    res = True

    if '.' not in domain:
        return False
    if not use_tld:
        if re.match('(.+?\.)+[a-zA-Z0-9]+', domain):
            pass
        else:
            return False
    else:
        try:
            res = get_tld(domain)
        except Exception as e:
            if "didn't match any existing TLD name" in str(e):
                try:
                    if domain.startswith('http') and re.search(
                            r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}', domain):
                        return True
                except:
                    pass
            return False
    return res


def is_ip(target):
    """判断是否是ip"""
    try:
        res = IP(target)
        return res if res and res.len() == 1 else False
    except ValueError:
        return False


def is_ipv6(target):
    """判断是否是IPv6"""
    try:
        tmp = is_ip(target)
        return tmp and tmp.version() == 6
    except Exception:
        return False


def is_ipv4(target):
    """判断是否是IPv4"""
    try:
        tmp = is_ip(target)
        return tmp and tmp.version() == 4
    except Exception:
        return False


def is_ipv4_cidr(target):
    """判断是否是IPv4的网段"""
    return re.search(
        r'^((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}\/(([12]{0,1}[0-9])|(3[0-2]))$',
        target)


# ########################分割IP段部分#########################


def split(ip_str: str):
    try:
        if is_ipv4_cidr(ip_str):
            ip, mask = ip_str.split('/')
            tmp = IP(ip).make_net(mask)
            ip_str = str(tmp)
        return split_cidr(ip_str)
    except:
        if len(ip_str.split('.')) == 4:
            return split_star_and_sections(ip_str)
        elif len(ip_str.split('.')) == 7 and '-' in ip_str:
            return split_ip_s_ip(ip_str)
        else:
            raise ValueError('{} is a invalid ip like str'.format(ip_str))


def split_star_and_sections(ip: str):
    """
    处理各处带星号、带横杠的单ip
    :param ip: 192.168.1.*   192.168.1-5.*
    """
    ips = list(ip.split('.'))
    for index, num in enumerate(ips):
        if '-' in num:
            try:
                start, end = num.split('-')
                assert start.isdigit(), end.isdigit()
                ips[index] = [x for x in range(int(start), int(end) + 1)]
            except (ValueError, AssertionError):
                ips[index] = [x for x in range(1, 256)]
        elif num.isdigit():
            ips[index] = [num]
        else:
            ips[index] = [x for x in range(1, 256)]

    return ['{}.{}.{}.{}'.format(n0, n1, n2, n3) for n3 in ips[3] for n2 in ips[2] for n1 in ips[1] for n0 in ips[0]]


def split_ip_s_ip(ip2ip_str):
    """
    处理两个具体ip的范围
    :param ip2ip_str: 形如192.168.1.250-192.168.2.5
    """
    ipx = ip2ip_str.split('-')
    ip2num = lambda x: sum([256 ** i * int(j) for i, j in enumerate(x.split('.')[::-1])])
    num2ip = lambda x: '.'.join([str(x // (256 ** i) % 256) for i in range(3, -1, -1)])
    a = [num2ip(i) for i in range(ip2num(ipx[0]), ip2num(ipx[1]) + 1) if not ((i + 1) % 256 == 0 or i % 256 == 0)]
    return a


def split_cidr(ip):
    """
    处理标准ip段
    :param ip: 192.168.1.0/24
    """
    return [str(i) for i in IP(ip)]


def get_ip_set(ip_list: list) -> IPSet:
    ip_set = IPSet()
    for ip in ip_list:
        if is_ipv4_cidr(ip):
            ip, mask = ip.split('/')
            ip = str(IP(ip).make_net(mask))
        try:
            ip_set.add(IP(ip))
        except:
            """单IP随意区间、单IP不标准区间"""
            if len(ip.split('.')) == 4:
                [ip_set.add(IP(x)) for x in split_star_and_sections(ip)]
            elif len(ip.split('.')) == 7 and '-' in ip:
                [ip_set.add(IP(x)) for x in split_ip_s_ip(ip)]
            else:
                raise ValueError('{} is a invalid ip like str'.format(ip))
    return ip_set


# ########################判断是否存在ip包含关系#########################

def is_overlap_internal_cidr(target):
    """判断所选IP、IP段中是否有保留地址"""
    res = []
    for internal in INTERNAL_IP_LIST:
        if IP(target).overlaps(internal):
            res.append(INTERNAL_IP_LIST)
    return res or False


# ########################format#########################


def format_target(target_str: str):
    assets = []
    for t in target_str.replace(',', ' ').replace('，', ' ').split():
        if t.isdigit():
            assets.append(str(IP(t)))
        elif is_ip(t):
            assets.append(t)
        elif is_ipv4_cidr(t):
            ip, mask = t.split('/')
            t = [str(x) for x in IP(ip).make_net(mask)]
            assets.extend(t)
        elif len(t.split('.')) == 4:
            assets.extend(split_star_and_sections(t))
        elif len(t.split('.')) == 7 and '-' in t:
            assets.extend(split_ip_s_ip(t))
        elif is_domain(t):
            assets.append(t)
        else:
            raise ValueError
    return ','.join(assets)
