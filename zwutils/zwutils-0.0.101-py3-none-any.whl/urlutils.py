
import re
import socket
import mimetypes
from urllib.parse import parse_qs, urljoin, urlparse, urlsplit, urlunsplit
import unicodedata
import logging

def remove_args(url, keep_params=(), frags=False):
    """
    Remove all param arguments from a url.
    """
    parsed = urlsplit(url)
    filtered_query = '&'.join(
        qry_item for qry_item in parsed.query.split('&')
        if qry_item.startswith(keep_params)
    )
    if frags:
        frag = parsed[4:]
    else:
        frag = ('',)
    return urlunsplit(parsed[:3] + (filtered_query,) + frag)

def get_redirect(url, param_name='url'):
    """Get redirect url from url with given param name('url' default)
    """
    parse_data = urlparse(url)
    query = parse_data.query

    query_item = parse_qs(query)
    if query_item.get(param_name):
        return query_item[param_name][0]
    return url

def redirect_back(url, source_domain):
    """
    Some sites like Pinterest have api's that cause news
    args to direct to their site with the real news url as a
    GET param. This method catches that and returns our param.
    """
    parse_data = urlparse(url)
    domain = parse_data.netloc
    # If our url is even from a remotely similar domain or
    # sub domain, we don't need to redirect.
    if source_domain in domain or domain in source_domain:
        return url
    url = get_redirect(url)
    return url

def get_absolute_redirect_url(url, source_url=None):
    """
    Operations that purify a url, removes arguments,
    redirects, and merges relatives with absolutes.
    """
    proper_url = None
    try:
        if source_url is not None:
            source_domain = urlparse(source_url).netloc
            proper_url = urljoin(source_url, url)
            proper_url = redirect_back(proper_url, source_domain)
        else:
            proper_url = url
    except ValueError as ex:
        logging.error('url %s failed on err %s', url, str(ex))
        proper_url = None
    return proper_url

def get_domain(abs_url, **kwargs):
    """
    returns a url's domain
    """
    if abs_url is None:
        return None
    return urlparse(abs_url, **kwargs).netloc

def get_scheme(abs_url, **kwargs):
    """
    """
    if abs_url is None:
        return None
    return urlparse(abs_url, **kwargs).scheme

def get_path(abs_url, **kwargs):
    """
    """
    if abs_url is None:
        return None
    return urlparse(abs_url, **kwargs).path

def get_base(abs_url, **kwargs):
    return '%s://%s' % ( get_scheme(abs_url, **kwargs),get_domain(abs_url, **kwargs) )

def is_abs_url(url):
    """
    this regex was brought to you by django!
    """
    regex = re.compile(
        r'^(?:http|ftp)s?://'                                                                 # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'                                                                         # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'                                                # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'                                                        # ...or ipv6
        r'(?::\d+)?'                                                                          # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    c_regex = re.compile(regex)
    return (c_regex.search(url) is not None)

def url_to_filetype(abs_url, allowed=None):
    """
    Input a URL and output the filetype of the file
    specified by the url. Returns None for no filetype.
    'http://blahblah/images/car.jpg' -> 'jpg'
    'http://yahoo.com'               -> None
    """
    path = str(urlparse(abs_url).path)
    allowed = allowed or []
    # Eliminate the trailing '/', we are extracting the file
    if path.endswith('/'):
        path = path[:-1]
    path_chunks = [x for x in path.split('/') if len(x) > 0]
    if len(path_chunks) == 0:
        # 'http://yahoo.com'
        return None
    last_chunk = path_chunks[-1].split('.')  # last chunk == file usually
    if len(last_chunk) < 2:
        return None
    file_type = last_chunk[-1]
    # Assume that file extension is maximum 5 characters long
    if len(file_type) <= 5 or file_type.lower() in allowed:
        return file_type.lower()
    return None

def resolve_url(url):
    '''From https://stackoverflow.com/questions/4317242/python-how-to-resolve-urls-containing/40536115#40536115
    >>> resolve_url('http://example.com/../thing///wrong/../multiple-slashes-yeah/.')
    'http://example.com/thing///multiple-slashes-yeah/'

    '''
    if url is None:
        return None
    parts = list(urlsplit(url))
    parts[2] = resolve_url_path(parts[2])
    return urlunsplit(parts)

def resolve_url_path(path):
    segments = path.split('/')
    segments = [segment + '/' for segment in segments[:-1]] + [segments[-1]]
    resolved = []
    for segment in segments:
        if segment in ('../', '..'):
            if resolved[1:]:
                resolved.pop()
        elif segment not in ('./', '.'):
            resolved.append(segment)
    return ''.join(resolved)

def is_url_image(path):
    mt, _ = mimetypes.guess_type(path)
    return mt is not None and mt.startswith('image/')

def subdomain_compare(urla, urlb):
    urla, urlb = urlparse(urla), urlparse(urlb)
    urla, urlb = urla.netloc, urlb.netloc
    a, b = urla.split('.'), urlb.split('.')
    a.reverse(), b.reverse()
    minlen = min(len(a), len(b))
    rtn = 0
    for i in range(minlen):
        sa, sb = a[i], b[i]
        if sa != sb:
            break
        else:
            rtn +=1
    return rtn

def domain2ip(domain):
    rtn = None
    if domain.startswith('http'):
        url = urlparse(domain)
        domain = url.netloc
    try:
        rtn = socket.gethostbyname(domain)
    except:
        pass
    return rtn

def slugify(value):
    """
    URL to filename
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    val = unicodedata.normalize('NFKD', value).encode('utf-8', 'ignore')
    val = val.decode()
    val = re.sub(r'[^\w\s-]', '', val).strip().lower()
    val = re.sub(r'[-\s]+', '-', val)
    return val