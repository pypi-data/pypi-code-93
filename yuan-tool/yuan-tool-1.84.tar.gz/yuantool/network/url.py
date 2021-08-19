import re
import requests
import copy
import os
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode, urljoin, quote, unquote
from ..enums import PLACE
from ..difinition import DEFAULT_GET_POST_DELIMITER, DEFAULT_COOKIE_DELIMITER
from tld import get_tld
import dns.resolver
import socket
import logging

logger = logging.getLogger(__name__)


def resolve_url(url):
    """处理url的模块，可以返回url的各种信息"""
    tld = get_tld(url, fix_protocol=True, as_object=True)
    return tld


def format_url(url):
    from .ip import is_ip
    res = urlparse(url)
    scheme = res.scheme + '://' if res.scheme else 'http://'
    if res.scheme and not res.hostname:
        scheme = 'http://' if str(res.port) != '443' else 'https://'
        host = str(res.scheme)
        path = str(res.path)
        if res.scheme == 'http':
            port = str(res.port) if res.port else "80"
        else:
            port = str(res.port) if res.port else "443"
    elif res.scheme:
        if res.scheme == 'http':
            port = str(res.port) if res.port else "80"
        else:
            port = str(res.port) if res.port else "443"
        if '/' in str(res.hostname):
            host = str(res.hostname).split('/')[0]
            path = '/' + ''.join(str(res.hostname).split('/')[0:]) + str(res.path)
        else:
            host = str(res.hostname)
            path = str(res.path)
    else:
        port = str(res.port) if res.port else '80'
        if '/' in str(res.path):
            t = str(res.path).split('/')
            host = str(res.path).split('/')[0]
            path = '/' + ''.join(str(res.path).split('/')[1:])
        else:
            host = res.path
            path = ''
    if is_ip(host):
        if path and path != '/':
            return scheme + host + path
        else:
            return scheme + host + ":" + port
    else:
        if host.startswith('www.'):
            r = scheme + host
        elif host.startswith('host.docker.internal'):
            if port != '80' and port != '443':
                r = scheme + host + ':' + port
            else:
                r = scheme + host
        else:
            r = scheme + 'www.' + host
        return r + path


def switch_api_from_url(url, api_path):
    """
    更改api，保留其他参数
    :param url: 原始url
    :param api_path: 新的api地址（不需要一开始的/）
    :return:
    """
    res = urlparse(url)
    # scheme, netloc, path, params, query, fragment
    res_com = (res.scheme, res.netloc, api_path, res.params, res.query, res.fragment)
    res = urlunparse(res_com)
    return res


def parse_params_for_url(url, dic):
    """在原有的url基础上增加新的query参数字典"""
    res = urlparse(url)
    query = urlencode(dic)
    res_com = (res.scheme, res.netloc, res.path, res.params, '{}&{}'.format(res.query, query), res.fragment)
    res = urlunparse(res_com)
    return res


def get_parent_paths(path, domain=True):
    '''
    通过一个链接分离出各种目录
    :param path:
    :param domain:
    :return:
    '''
    netloc = ''
    if domain:
        p = urlparse(path)
        path = p.path
        netloc = "{}://{}".format(p.scheme, p.netloc)
    paths = []
    if not path or path[0] != '/':
        return paths
    # paths.append(path)
    if path[-1] == '/':
        paths.append(netloc + path)
    tph = path
    if path[-1] == '/':
        tph = path[:-1]
    while tph:
        tph = tph[:tph.rfind('/') + 1]
        paths.append(netloc + tph)
        tph = tph[:-1]
    return paths


def get_links(content, domain, limit=True):
    '''
    从网页源码中匹配链接
    :param content: html源码
    :param domain: 当前网址domain
    :param limit: 是否限定于此域名
    :return:
    '''
    p = urlparse(domain)
    netloc = "{}://{}{}".format(p.scheme, p.netloc, p.path)
    match = re.findall(r'''(href|src)=["'](.*?)["']''', content, re.S | re.I)
    urls = []
    for i in match:
        _domain = urljoin(netloc, i[1])
        if limit:
            if p.netloc.split(":")[0] not in _domain:
                continue
        urls.append(_domain)
    return urls


def get_param_from_url(url, *args):
    """
    从url中通过指定参数获取参数的值
    :param url:目标url
    :param args:填写想要获取参数值的key值，填写几个就会返回几个结果
    :return:若存在，返回对应值(string型)；若不存在，返回None
    e.g.
    """
    params = parse_qs(urlparse(url).query)
    res = []
    for item in args:
        try:
            tmp = params[item][0]
            res.append(tmp)
        except KeyError:
            res.append(None)
    return tuple(res) if len(res) > 1 else res[0]


def get_ip_from_target(url):
    """通过url解析其ip"""
    # TODO 多个解析ip情况的处理
    try:
        # 使用tld更好的处理url使其符合后续操作
        tld = get_tld(url, fix_protocol=True, as_object=True)
        try:
            # 先使用socket.getaddrinfo查看是否可以直接gai到
            myaddr = socket.getaddrinfo(tld.fld, tld.subdomain if tld.subdomain else 'http')
            # 处理点1
            return myaddr[0][4][0]
        except socket.gaierror:
            # 若gai不到，则需要dns.resolver去反向解析
            try:
                answers = dns.resolver.resolve(tld.fld, 'A')
                for rdata in answers:
                    if rdata.address == '0.0.0.1':
                        continue
                    # 处理点2
                    return rdata.address
            except dns.resolver.NXDOMAIN as e:
                return None
    except Exception as e:
        # tld socket dnsresolver都有可能报错
        logger.error(e, exc_info=True)
        return None


def get_host_from_url(url):
    """从url中获取host"""
    return urlparse(url).hostname


def prepare_url(url, params):
    """通过request的方式去实际获取该返回的url"""
    req = requests.Request('GET', url, params=params)
    r = req.prepare()
    return r.url


def get_cname(domain, log_flag=True):
    cnames = []
    try:
        answers = dns.resolver.query(domain, 'CNAME')
        for rdata in answers:
            cnames.append(str(rdata.target).strip(".").lower())
    except dns.resolver.NoAnswer as e:
        if log_flag:
            logger.debug(e)
    except Exception as e:
        if log_flag:
            logger.warning("{} {}".format(domain, e))
    return cnames


def domain_parsed(domain, fail_silently=True):
    domain = domain.strip()
    try:
        res = get_tld(domain, fix_protocol=True, as_object=True)
        item = {
            "subdomain": res.subdomain,
            "domain": res.domain,
            "fld": res.fld
        }
        return item
    except Exception as e:
        if not fail_silently:
            raise e

def is_in_scope(src_domain, target_domain):
    def get_fld(domain):
        res = domain_parsed(domain)
        if res:
            return res["fld"]

    fld1 = get_fld(src_domain)
    fld2 = get_fld(target_domain)

    if not fld1 or not fld2:
        return False

    if fld1 != fld2:
        return False

    if src_domain == target_domain:
        return True

    return src_domain.endswith("."+target_domain)


def is_in_scopes(domain, scopes):
    for target_scope in scopes:
        if is_in_scope(domain, target_scope):
            return True

    return False


def generateResponse(resp: requests.Response):
    response_raw = "HTTP/1.1 {} {}\r\n".format(resp.status_code, resp.reason)
    for k, v in resp.headers.items():
        response_raw += "{}: {}\r\n".format(k, v)
    response_raw += "\r\n"
    response_raw += resp.text
    return response_raw


def splitUrlPath(url, all_replace=True, flag='<--flag-->') -> list:
    ''''
    all_replace 默认为True 替换所有路径，False 在路径后面加
    flag 要加入的标记符
    '''
    u = urlparse(url)
    path_split = u.path.split("/")[1:]
    path_split2 = []
    for i in path_split:
        if i.strip() == "":
            continue
        path_split2.append(i)

    index = 0
    result = []

    for path in path_split2:
        copy_path_split = copy.deepcopy(path_split2)
        if all_replace:
            copy_path_split[index] = flag
        else:
            copy_path_split[index] = path + flag

        new_url = urlunparse([u.scheme, u.netloc,
                              ('/' + '/'.join(copy_path_split)),
                              u.params, u.query, u.fragment])
        result.append(new_url)
        sptext = os.path.splitext(path)
        if sptext[1]:
            if all_replace:
                copy_path_split[index] = flag + sptext[1]
            else:
                copy_path_split[index] = sptext[0] + flag + sptext[1]
            new_url = urlunparse([u.scheme, u.netloc,
                                  ('/' + '/'.join(copy_path_split)),
                                  u.params, u.query, u.fragment])
            result.append(new_url)
        index += 1

    return result


def url_dict2str(d: dict, position=PLACE.GET):
    if isinstance(d, str):
        return d
    temp = ""
    urlsafe = "!$%'()*+,/:;=@[]~"
    if position == PLACE.GET or position == PLACE.POST:
        for k, v in d.items():
            temp += "{}={}{}".format(k, quote(v, safe=urlsafe), DEFAULT_GET_POST_DELIMITER)
        temp = temp.rstrip(DEFAULT_GET_POST_DELIMITER)
    elif position == PLACE.COOKIE:
        for k, v in d.items():
            temp += "{}={}{} ".format(k, quote(v, safe=urlsafe), DEFAULT_COOKIE_DELIMITER)
        temp = temp.rstrip(DEFAULT_COOKIE_DELIMITER)
    return temp


def json_to_str(s) -> str:
    ''' 表单转字符串 '''
    return urlencode(s)


def urlEncode(s) -> str:
    return quote(s)


def urlDecode(s) -> str:
    return unquote(s)
