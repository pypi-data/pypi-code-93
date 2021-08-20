import re
from zwutils.fileutils import writejson

def get_codetree(codes):
    for o in codes:
        pcode = o['parent']
        found_parent = False
        if pcode is None:
            continue
        for p in codes:
            if p == o:
                continue
            elif p['adcode'] == pcode:
                if 'children' not in p:
                    p['children'] = []
                p['children'].append(o)
                found_parent = True
                break
    rtn = next((o for o in codes if o['adcode']==100000 ), None)
    return rtn

def address2adcode(addr, tree):
    re_arr = []
    re_arr.append( (r'(\w+)(省|自治区|特别行政区)(\w+)(市)(\w+)(区|县|市)(\w+)(街道).+', 4) )
    re_arr.append( (r'(\w+)(省|自治区|特别行政区)(\w+)(市)(\w+)(区|县|市).+', 3) )
    re_arr.append( (r'(\w+)(省|自治区|特别行政区)(\w+)(市|区).+', 2) )
    re_arr.append( (r'(\w+)(省|自治区|特别行政区).+', 1) )
    re_arr.append( (r'(北京|天津|上海|重庆)(市)(\w+)(区).+', 2) )

    arr = []
    for o in re_arr:
        pat, lvl = o
        m = re.search(pat, addr)
        if not m:
            continue
        for j in range(1, lvl*2, 2):
            arr.append( m.group(j)+m.group(j+1) )
        break
    codes = tree['children']
    rtn = []
    for o in arr:
        found = False
        for c in codes:
            if o == c['name']:
                rtn.append(c['adcode'])
                codes = c['children'] if 'children' in c else []
                found =True
                break
        if not found:
            return None
    return rtn[-1] if len(rtn)>0 else None







        