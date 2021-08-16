import re
from datetime import datetime
from difflib import SequenceMatcher

def is_chinese(c):
    '''https://stackoverflow.com/questions/1366068/whats-the-complete-range-for-chinese-characters-in-unicode'''
    if u'\u4E00' <= c < u'\u9FFF' or \
       u'\u3400' <= c < u'\u4DBF' or \
       u'\u20000' <= c < u'\u2A6DF' or \
       u'\u2A700' <= c < u'\u2B73F' or \
       u'\u2B740' <= c < u'\u2B81F' or \
       u'\u2B820' <= c < u'\u2CEAF':
        return True
    else:
        return False

def is_chinese_punctuation(c):
    arr = [
        u'\u3002',u'\uFF1F',u'\uFF01',u'\u3010',u'\u3011',u'\uFF0C',u'\u3001',u'\uFF1B',
        u'\uFF1A',u'\u300C',u'\u300D',u'\u300E',u'\u300F',u'\u2019',u'\u201C',u'\u201D',
        u'\u2018',u'\uFF08',u'\uFF09',u'\u3014',u'\u3015',u'\u2026',u'\u2013',u'\uFF0E',
        u'\u2014',u'\u300A',u'\u300B',u'\u3008',u'\u3009'
    ]
    return c in arr

def is_english_punctuation(c):
    arr = [
        '!', '"', '#', '$', '%', '&',
        "'", '(', ')', '*', '+', ',', '-', 
        '.', '/', ':', ';', '<', '=', '>', 
        '?', '@', '[', '\\', ']', '\^', '_', 
        '`', '{', '|', '}', '~'
    ]
    return c in arr

def hasdigit(s):
    m = re.compile(r'\d')
    return bool(m.search(s))

def remove_space_in_sentence(sentence):
    s = sentence.strip()
    rtn = ''
    for i,c in enumerate(s):
        if c.isspace() and i == len(s)-1:
            continue
        if c.isspace():
            prev_char = rtn[-1] if len(rtn)>0 else ''
            next_char = s[i+1]
            if next_char.isspace():
                continue
            elif is_chinese(next_char) or is_chinese_punctuation(next_char):
                continue
            elif (is_chinese(prev_char) or is_chinese_punctuation(prev_char)) and not is_chinese(next_char):
                continue
            else:
                rtn += c
        else:
            rtn += c
    return rtn

def inner_trim(value, replace=''):
    if isinstance(value, str):
        TABSSPACE = re.compile(r'[\s\t]+')
        # remove tab and white space
        value = re.sub(TABSSPACE, replace, value)
        value = ''.join(value.splitlines())
        return value.strip()
    return ''

class ReplaceSequence(object):
    def __init__(self):
        self.actions = []

    def append(self, pattern, replace_with=None):
        self.actions.append( (pattern, replace_with or '') )
        return self

    def replace(self, string):
        if not string:
            return ''
        mutatedString = string
        for pattern, replace_with in self.actions:
            mutatedString = mutatedString.replace(pattern, replace_with)
        return mutatedString

def find_datestr(s):
    arr = []
    rtn = []
    
    _arr = re.findall(r'(?:\D)([12]\d{3}-\d{1,2}-\d{1,2})(?:\D)*', s)
    _arr = ['%s-%s-%s'%(a.split('-')[0], a.split('-')[1].rjust(2,'0'), a.split('-')[2].rjust(2,'0')) for a in _arr]
    arr.extend(_arr)

    _arr = re.findall(r'(?:\D)([12]\d{3}/\d{1,2}/\d{1,2})(?:\D)*', s)
    _arr = ['%s-%s-%s'%(a.split('/')[0], a.split('/')[1].rjust(2,'0'), a.split('/')[2].rjust(2,'0')) for a in _arr]
    arr.extend(_arr)

    _arr = re.findall(r'(?:\D)([12]\d{3}\d{2}\d{2})(?:\D)*', s)
    _arr = ['%s-%s-%s'%(a[:4], a[4:6], a[6:]) for a in _arr]
    arr.extend(_arr)
    for i,a in enumerate(arr):
        try:
            datetime.strptime(a, '%Y-%m-%d')
            rtn.append(a)
        except Exception:
            arr[i] = None
    arr = [o for o in arr if o]
            
    #TODO update re, get rid of this if
    if len(arr) == 0:
        _arr = re.findall(r'(?:\D)([12]\d{3}-\d{1,2})(?:\D)*', s)
        _arr = ['%s-%s'%(a.split('-')[0], a.split('-')[1].rjust(2,'0')) for a in _arr]
        arr.extend(_arr)

        _arr = re.findall(r'(?:\D)([12]\d{3}/\d{1,2})(?:\D)*', s)
        _arr = ['%s-%s'%(a.split('/')[0], a.split('/')[1].rjust(2,'0')) for a in _arr]
        arr.extend(_arr)
        
        _arr = re.findall(r'(?:\D)([12]\d{3}\d{2})(?:\D)*', s)
        _arr = ['%s-%s'%(a[:4], a[4:6]) for a in _arr]
        arr.extend(_arr)
        for a in arr:
            try:
                datetime.strptime(a, '%Y-%m')
                rtn.append(a)
            except Exception:
                pass
    for i,r in enumerate(rtn):
        year = int(r.split('-')[0])
        if year < 1949:
            rtn[i] = None
    rtn = [r for r in rtn if r]
    return rtn

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()