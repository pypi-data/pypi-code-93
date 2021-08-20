# functions for ngutils

import concurrent.futures as pool
from   datetime import datetime
from   dateutil.parser import parse
from   hashlib import blake2b
from   html import unescape
import io
from   lxml.html.clean import Cleaner
import pandas as pd
import re
import requests
import shutil
import sys
from   tqdm import tqdm
from   typing import Union, Optional, Callable
from   unicodedata import normalize

def view_types(data: Union[pd.DataFrame, pd.Series, list, dict], dropna: Optional[bool] = True) -> None:
    """
    Вывод отчета с анализом содержимого объекта data, подсчет представленных типов данных
    
    Parameters
    ----------
    data : DataFrame, Series, dict, list
        Объект DataFrame или приводимый к DataFrame для анализа
    dropna : bool, default True
        Не включать NaN в расчет количества уникальных значений
    Returns
    -------
    None
    """
    data = pd.DataFrame(data)
    columns_exch = {
        "<class 'str'>": 'str', "<class 'int'>": 'int', "<class 'float'>": 'float',
        "<class 'list'>": 'list', "<class 'dict'>": 'dict',
        "<class 'datetime.datetime'>": 'datetime',
        "<class 'pandas._libs.tslibs.timestamps.Timestamp'>": 'Timestamp',
    }
    df_output = pd.DataFrame(
        data[data[c].notna()][c].apply(type).value_counts() for c in data.columns
    ).fillna(0).astype(int)
    if data.isna().any().any():
        df_output['NaN'] = data.isna().sum()
    df_output['(min)'] = None
    df_output['(max)'] = None
    for i, c in enumerate(data.columns):
        try:
            df_output.loc[c,'(min)'] = data[c].dropna().min()
            df_output.loc[c,'(max)'] = data[c].dropna().max()
        except:
            df_output.loc[c,'(min)'] = data[c].dropna().astype(str).min()
            df_output.loc[c,'(max)'] = data[c].dropna().astype(str).max()

    df_output['(unique)'] = [data[c].astype(str).nunique(dropna) for c in data.columns]
    df_output.columns = [columns_exch.get(str(x), x) for x in df_output.columns]
    if jupiter_detected():
        display(df_output.head(60))
    else:
        print(df_output.head(60))
    print("{} rows x {} columns".format(*data.shape))


def read_urls_contents(
    urls_list: list, max_workers: int =10, session: Optional[requests.Session] = None, 
    parser: Optional[Callable] = None, encoding: Optional[str] = None, *, 
    max_retries: Optional[int] = None, timeout : Union[float, tuple, None] = None, 
    error_page_output: Optional[io.StringIO] = None, status_text: Optional[str] = None, 
    output_type: Optional[str] = None, 
    mute: Optional[bool] = False) -> io.StringIO:
    """
    URLs list contents multithread loading to StringIO
    
    Parameters
    ----------
    urls_list : list
        Iterable list of urls.
    max_workers : int, optional
        The maximum number of threads, by default 10.
    session : requests.Session, optional
        Auth session.
    parser : function, optional
        Function for content preprocessing in main thread f(decoded_content: str, final_url: str, source_url: str) -> None.
    encoding : str, optional
        Encoding of the content. By default, the content encoding is determined automatically.
    max_retries : int, optional
        The maximum number of retries for connection. By default, failed connections are not retry.
    timeout : float or tuple, optional
        How many seconds to wait server establish connection and send response. By default, timeout is not define.
    error_page_output : io.StringIO, optional
        StringIO output stream for all runtime errors. By default, the process terminated at the first error.
    status_text : str, optional
        Text for download status, by default 'URLs list download:'.
    mute : boolean, optional
        If mute is True then progress messages will be disabled, default False

    Returns
    -------
    io.StringIO
        String stream for additional processing or use in pd.read_csv
    """
    PROGRESS_WHEEL=r'|/—\|/—\ '

    def url_loader(url: str, session: Optional[requests.Session], timeout: Optional[float], output_type,
                   encoding: Optional[str]) -> str:
        """
        Default function for url download
        """
        r = session.get(url, timeout=timeout)
        if encoding is None:
            return r.text, r.url
        else:
            return r.content.decode(encoding), r.url

    if mute == 'tqdm':
        it = tqdm
    else:
        def it(fn, total): return fn
        
    if session is None:
        session = requests.Session()

    if max_retries is not None:
        session.mount('http://', requests.adapters.HTTPAdapter(max_retries=max_retries))
        session.mount('https://', requests.adapters.HTTPAdapter(max_retries=max_retries))

    if status_text is None:
        status_text = 'URLs download:'

    if output_type == 'StringIO':
        buf = io.StringIO()
    elif output_type == 'BytesIO':
        buf = io.BytesIO()
    else:
        output_type = None

    if (output_type is None) and (parser is None):
        raise Exception("There can't be an undefined `output_type` and `parser` together")
        
    if mute == False:
        print(f"{status_text}     0%"+" "*50, end='\r', flush=True)

    with pool.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_load_url = {executor.submit(url_loader, url, session, timeout, output_type, encoding): url for url in urls_list}
        for i, future in it(enumerate(pool.as_completed(future_load_url)), total=len(urls_list)):
            if mute == False:
                print(f"{status_text} {PROGRESS_WHEEL[i%8]} {i/len(urls_list)*.995:.0%}"+" "*50, end='\r', flush=True)
            url = future_load_url[future]
            try:
                if output_type is None:
                    parser(*future.result(), url)
                else:
                    buf.write(future.result()[0] if parser is None else parser(*future.result(), url))
            except Exception as exc:
                if error_page_output is None:
                    raise Exception(f'Download error\n{url}|{exc}')
                else:
                    error_page_output.write(f'Download error\n{url}|{exc}\n')

    if mute == False:
        print(f"{status_text}   100%"+" "*50)

    if output_type is not None:
        buf.seek(0)
        return buf


def accel_steps(max_degree: Optional[int] = 10):
    """
    Increment yield-counter with acceleration

    Parameters
    ----------
    max_degree : int, optional
        Power of 2 to determine the maximum value of the counter, by default 10.

    Returns
    -------
    int
        counter value
    """
    for i in range(int(max_degree)):
        for j in 1, 2, 5:
            yield j*10**i


def tune_steps(number: Optional[int] = 100):
    """
    Decrement yield-counter fast decrement counter for binary search from [1..number]

    Parameters
    ----------
    number : int, optional
        Upper limit of the search range. By default, 100.

    Returns
    -------
    int
        counter value
    """
    while number>1:
        number -= number//2
        yield number
    yield 1

clean_rules = Cleaner(
    scripts = True,
    javascript = True,
    comments = True,
    style = True,
    links = True,
    meta = False,
    page_structure = False,
    processing_instructions = True,
    embedded = True,
    frames = True,
    forms = True,
    annoying_tags = True,
    remove_tags = frozenset(['abbr', 'acronym', 'b', 'big', 'blockquote', 'cite', 'code', 'del', 'dfn', 'em', 'i', 'ins', 
                   'kbd', 's', 'samp', 'small', 'strike', 'strong', 'sub', 'sup', 'tt', 'u', 'var', ]),
    kill_tags = frozenset(['figure', 'footer', 'img', 'svg', 'template']),
    remove_unknown_tags = False,
    safe_attrs_only = True,
    safe_attrs = frozenset(['alt', 'charset', 'cite', 'class', 'content', 'datetime', 'dir', 'disabled', 'enctype', 'for', 'frame', 
                            'headers', 'href', 'hreflang', 'id', 'itemprop', 'label', 'lang', 'longdesc', 'media', 'method', 
                            'multiple', 'name', 'nohref', 'noshade', 'nowrap', 'prompt', 'property', 'readonly', 'rel', 'rev', 
                            'rows', 'rowspan', 'rules', 'scope', 'selected', 'shape', 'span', 'start', 'summary', 
                            'tabindex', 'target', 'title', 'type', 'usemap', 'value']),
    add_nofollow = False,
)


def hash_hd(something, digest_size=20) -> str:
    """
    Return hash of something
    """
    if isinstance(something, bytes):
        return blake2b(something, digest_size=digest_size).hexdigest()
    else:
        return blake2b(str(something).encode(), digest_size=digest_size).hexdigest()


def reduce_content(text_content: str) -> str:
    """
    Normalize, cleaning and reducing unicode html content
    """
    text_content = clean_rules.clean_html(text_content) # cleaning html
    text_content = normalize('NFKC', text_content) # normalize unicode text
    text_content = unescape(text_content) # change the html-codes to unicode characters
    text_content = re.sub('<p>\s+</p>', ' ', text_content) # reduce blank paragraphs
    text_content = re.sub('\s+', ' ', text_content).strip() # reduce the whitespace
    return text_content


def meta_append(text_content: str, find: str, ins: str = '<meta itemprop="datePublished" content="$">') -> str:
    """
    Append metadata to html ahead </head>
    For example:
    >>> meta_append(text_content, '\\"CreatedOn\\":\\"([^\\]+)')
    """
    match = re.search(find, text_content, re.S)
    if match:
        i = text_content.find('</head>')
        if i>=0:
            text_content = f"{text_content[:i]}{ins.replace('$', match[1])}{text_content[i:]}"
    return text_content


def read_files_contents(
    files_list: list, max_workers: int =10,
    parser: Optional[Callable] = None, encoding: Optional[str] = 'utf-8', *, 
    error_page_output: Optional[io.StringIO] = None, status_text: Optional[str] = None, 
    output_type: Optional[str] = None, 
    mute: Union[bool, str] = False) -> io.BufferedIOBase:
    """
    Files contents multithreaded reading to StringIO or BytesIO

    Parameters
    ----------
    urls_list : list
        Iterable list of files.
    max_workers : int, optional
        The maximum number of threads, by default 10.
    parser : function, optional
        Function for content preprocessing in main thread.
    encoding : string, optional
        Encoding of the content. By default, the content encoding is determined automatically.
    error_page_output : io.StringIO, optional
        StringIO output stream for all runtime errors. By default, the process terminated at the first error.
    status_text : str, optional
        Text for download status, by default 'URLs list download:'.
    output_type : str, optional
        'StringIO' or 'BytesIO'. By default 'StringIO'
    mute : boolean, optional
        If mute is True then progress messages will be disabled, default False

    Returns
    -------
    io.StringIO or io.BytesIO
        String stream for additional processing or use in pd.read_csv
    """
    PROGRESS_WHEEL=r'|/—\|/—\ '

    def file_reader(filepath, output_type, encoding):
        """
        Default function for read the file
        """
        b_content = io.BytesIO()
        with open(filepath,'rb') as f:
            shutil.copyfileobj(f, b_content)
            if output_type=='BytesIO':
                return b_content.getvalue()
            else:
                return b_content.getvalue().decode(encoding=encoding)

    if mute == 'tqdm':
        it = tqdm
    else:
        def it(fn, total): return fn
        
    if status_text is None:
        status_text = 'Files download:'

    if output_type == 'StringIO':
        buf = io.StringIO()
    elif output_type == 'BytesIO':
        buf = io.BytesIO()
    else:
        output_type = None

    if (output_type is None) and (parser is None):
        raise Exception("There can't be an undefined `output_type` and `parser` together")
        
    if mute == False:
        print(f"{status_text}     0%"+" "*50, end='\r', flush=True)

    with pool.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_read_files = {executor.submit(file_reader, filepath, output_type, encoding): filepath for filepath in files_list}
        for i, future in it(enumerate(pool.as_completed(future_read_files)), total=len(files_list)):
            if mute == False:
                print(f"{status_text} {PROGRESS_WHEEL[i%8]} {i/len(files_list)*.995:.0%}"+" "*50, end='\r', flush=True)
            filepath = future_read_files[future]
            try:
                if output_type is None:
                    parser(future.result(), filepath)
                else:
                    buf.write(future.result() if parser is None else parser(future.result(), filepath))
            except Exception as exc:
                if error_page_output is None:
                    raise Exception(f'Read files error\n{filepath}|{exc}')
                else:
                    error_page_output.write(f'Read files error\n{filepath}|{exc}\n')

    if mute == False:
        print(f"{status_text}   100%"+" "*50)

    if output_type is not None:
        buf.seek(0)
        return buf


def flatten(unflat: list) -> list:
    '''
    Flatten list
    '''
    flat = []
    for root in unflat:
        if isinstance(root, (list, tuple)):
            flat.extend(flatten(root))
        else:
            flat.append(root)
    return flat


def json_to_list(unflat: dict) -> list:
    '''
    Flatten dict
    '''
    json_list = []
    def parse(val, path):
        if isinstance(val, dict):
            for x in val:
                parse(val[x], f"{path}.{x}")
        elif isinstance(val, list):
            for i, x in enumerate(val):
                if i==0:
                    parse(x, f"{path}")
                else:
                    parse(x, f"{path}[{i}]")
        else:
            json_list.append([path[1:], val])
    parse(unflat, '')
    return json_list


def jupiter_detected() -> bool:
    return sys.argv[-1].endswith('json')


def host_extract(url: str) -> str:
    return url.replace('//www.', '//').replace('https://', '').replace('http://', '').partition('/')[0]
    # return u.removeprefix('https://').removeprefix('http://').removeprefix('www.').partition('/')[0]
    #          ^ new in python 3.9


def text_beautifier(text: Union[str, list]) -> str:
    """
    Beautifier text in str or list str
    """
    if isinstance(text, list):
        text = '&para;'.join(text) # группируем абзацы в строку
    text = re.sub('\s*(?:&para;\s*)+&para;\s*', '&para;', text) # удаляем пустые строки
    text = re.sub('</?[a-z][^<>]*(>|$)', ' ', text) # удаляем все оставшиеся теги, оставляя содержание
    text = re.sub('\s+', ' ', text).strip() # сжимаем пробелы и удаляем пробелы на границах текста
    text = text.replace('&para;', '\r') # восстанавливаем абзацы
    text = text.replace(' .', '.').replace(' ,', ',').replace(' :', ':').replace(' ;', ';').replace(' ?', '?').replace(' !', '!')
    return text


def datetime_parse(text: str) -> datetime:
    """
    Datetime parsing from str
    Cancel timezone POSIX notation at dateutil.parse
    """
    text = text.upper()
    if ('UTC+' in text) or ('GMT+' in text):
        text = text.replace('+', '-')
    elif ('UTC-' in text) or ('GMT-' in text):
        text = text.replace('-', '+')
    dayfirst = (text[:2] != '20') or (text[4] != '-')
    return parse(text, dayfirst=dayfirst)

