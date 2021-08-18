import json
import pickle
from datetime import datetime

from dsframework.base.common.regex_handler import RegexHandler

regex = RegexHandler

def flatten(d,sep="_"):
    import collections

    obj = collections.OrderedDict()

    def recurse(t, parent_key=""):

        if isinstance(t, dict):
            for k, v in t.items():
                recurse(v, parent_key + sep + k if parent_key else k)
        else:
            obj[parent_key] = t
    recurse(d)
    return obj

def get_from_dict(key, container:dict, default='', delete=False):
    if not container or type(container) is not dict:
        return default
    if key in container:
        val = container[key]
        if delete:
            del container[key]
        return val
    return default

def get_date_time(short=False):
    now = datetime.now()
    form = '%d/%m/%Y %H:%M:%S' if not short else '%d_%m_%Y'
    dt_string = now.strftime(form)
    return dt_string

def load_pickle(path):
    pkl = None
    with open(path, 'rb') as fid:
        pkl =  pickle.load(fid)
    return pkl

def load_json(path):
    jsn = None
    with open(path) as fid:
        jsn =  json.load(fid)
    return jsn 

def save_pickle(obj, path):
    with open(path, 'wb') as fid:
        pickle.dump(obj, fid)

def save_json(obj, path):
    with open(path, 'w') as f:
        json.dump(f, obj)

def remove_empty_leafs(d):
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (remove_empty_leafs(v) for v in d) if v]
    return {k: v for k, v in ((k, remove_empty_leafs(v)) for k, v in d.items()) if v}

def flatten_list(l):
    def get_el(el):
        if type(el) is not list:
            return [el]
        return el
    l2 = [get_el(el) for el in l]
    flatten = lambda l: [item for sublist in l for item in sublist]
    return flatten(l2)

def is_list_of_list(l):
    for el in l:
        if type(el) is list:
            return True
    return False

def ngram_splitter(line, ngram=3,all_grams=False):
    tokens       = line.split(" ")
    loop_index   = 1
    result       = []
    ngram_window = []
    for token in tokens:
        ngram_window.append(token)
        if all_grams==False:
            if loop_index >= ngram:
                result.append(" ".join(ngram_window))
        else:
            for j in range(1,ngram+1):
                if loop_index >=j:
                    if len(result)<j:
                        result.append([" ".join(ngram_window[0:loop_index-1+j])])
                    else:
                        result[j-1].append(" ".join(ngram_window[min(loop_index-j,ngram-j):min(ngram,loop_index+j-1)]))
        if loop_index >= ngram:
            ngram_window = ngram_window[1:]
        loop_index +=1 
    return result
    
def remove_duplicates_lines(lines = []):
    ls = lines 
    lookup = set()  # a temporary lookup set
    ls = [x for x in ls if x not in lookup and lookup.add(x) is None]
    return ls 
    
def get_html_block_elements_list():
    return ['<address', '<article', '<aside', '<blockquote', '<canvas', '<dd', '<div',
            '<dl',
            '<dt', '<fieldset', '<figcaption', '<figure', '<footer', '<form', '<h1',
            '<h2', '<h3',
            '<h4', '<h5', '<h6', '<header', '<hr', '<li', '<main', '<nav',
            '<noscript', '<ol', '<p', '<pre', '<section', '<table', '<tfoot', '<ul',
            '<video']

def get_html_inline_elements_list():
    return ['<a', '<abbr', '<acronym', '<b', '<bdo', '<big', '<br', '<button', '<cite',
            '<code', '<dfn', '<em',
            '<i', '<img', '<input', '<kbd', '<label', '<map', '<object', '<output',
            '<q', '<samp', '<script',
            '<select', '<small', '<span', '<strong', '<sub', '<sup', '<textarea',
            '<time', '<tt', '<var']
