import re
from bs4 import BeautifulSoup, Tag

def replace_all_space(s):
    return s.strip().replace(' ', '').replace('\xa0', '').replace('\u3000', '')

def find_soup_parent(el, tagnm=None, attrs=None):
    '''Find direct parent
    '''
    if isinstance(el, str) and not tagnm and not attrs:
        return None
    prt = el.parent
    rtn = None
    while prt and prt.name != 'body':
        pnm = False
        pat = False
        if tagnm and prt.name == tagnm:
            pnm = True
        if attrs and hasattr(prt, 'attrs'):
            for p in attrs:
                _t = prt.attrs[p] if p in prt.attrs else None
                _t = ' '.join(_t) if isinstance(_t, list) else _t
                if _t and len( re.findall(attrs[p], _t) )>0:
                    pat = True

        if tagnm and attrs and pnm and pat:
            rtn = prt
            break
        elif tagnm and not attrs and pnm:
            rtn = prt
            break
        elif not tagnm and attrs and pat:
            rtn = prt
            break
        prt = prt.parent
    return rtn

def find_soup_next_sibling(el, tagnm=None, attrs=None):
    if isinstance(el, str) and not tagnm and not attrs:
        return None
    sib = el.next_sibling
    rtn = None
    while sib:
        pnm = False
        pat = False
        if tagnm and sib.name == tagnm:
            pnm = True
        if attrs and hasattr(sib, 'attrs'):
            for p in attrs:
                _t = sib.attrs[p] if p in sib.attrs else None
                _t = ' '.join(_t) if isinstance(_t, list) else _t
                if _t and len( re.findall(attrs[p], _t) )>0:
                    pat = True
        
        if tagnm and attrs and pnm and pat:
            rtn = sib
            break
        elif tagnm and not attrs and pnm:
            rtn = sib
            break
        elif not tagnm and attrs and pat:
            rtn = sib
            break
        sib = sib.next_sibling
    return rtn

def find_soup_by_text(soup, restr):
    def filter_contains_text(el):
        if isinstance(el, Tag):
            r = re.findall(restr, el.text)
            return len(r)>0
        return False
    return soup.find_all(filter_contains_text)

def soup_depth_count(el, stoptag='body'):
    if isinstance(el, str):
        return -1
    prt = el.parent
    count = 0
    while prt and prt.name != stoptag:
        count += 1
        prt = prt.parent
    return count

def soup_calc_child(root, tgnms, stoptag='body'):
    if isinstance(root, str):
        return None

    elems = root.find_all(tgnms)
    for el in elems:
        prt = el.parent
        while prt and prt.name != stoptag:
            pscore = prt.attrs['_my_child_count'] if '_my_child_count' in prt.attrs else 0
            prt.attrs['_my_child_count'] = pscore + 1
            prt = prt.parent
    elems = root.find_all(True)
    elems = [{
        'el': o,
        'child_count': o.attrs['_my_child_count'],
        'depth_count': soup_depth_count(o, stoptag)
    } for o in elems if hasattr(o, 'attrs') and '_my_child_count' in o.attrs]

    for o in elems:
        del o['el'].attrs['_my_child_count']
    return elems

def soup_drop_tag(tag):
    '''Drops the tag, but keeps its children and text.'''
    arr = []
    for c in tag.children:
        if not isinstance(c, str):
            c = c.extract()
        arr.append(c)
    for o in arr:
        tag.insert_before(o)
    tag.decompose()
    a = 0