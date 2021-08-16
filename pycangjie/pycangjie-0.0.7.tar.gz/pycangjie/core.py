import requests
from threadwrapper import ThreadWrapper
import threading
import os
import json
from lxml import html


base = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base, r"src")


def gen_params(sword, page):
    return {
        "stype": "Word",
        "detail": "y",
        "sG": "y",
        "sword": "{}*".format(sword),
        "Page": page,
    }


def gen_fp(dir, page):
    return os.path.join(dir, "{}.html".format(str(page).zfill(3)))


def write_to_file(dir, page, content):
    open(gen_fp(dir, page), "wb").write(content)


def fetch():
    tw = ThreadWrapper(threading.Semaphore(2 ** 3))
    url = "https://www.chinesecj.com/cjdict/index.php"
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
    })
    for i in range(65, 65+25):
        if i ==65+23:
            continue
        alphabet = chr(i)
        r = s.get(url, params=gen_params(alphabet, 1))
        cur_dir = os.path.join(src_dir, alphabet)
        try:
            os.makedirs(cur_dir)
        except:
            pass
        write_to_file(cur_dir, 1, r.content)
        r = html.fromstring(r.content.decode())
        last_page = int(r.xpath("//a[contains(@href, 'Page=')]/@href")[-1].split("Page=")[-1])
        print("\r", alphabet, 1, last_page, end="")
        for j in range(2, last_page+1):
            def job(cur_dir, alphabet, j, last_page):
                def _job():
                    print("\r", alphabet, j, last_page, end="")
                    if os.path.exists(gen_fp(cur_dir, j)):
                        return
                    r = s.get(url, params=gen_params(alphabet, j))
                    write_to_file(cur_dir, j, r.content)
                return _job
            tw.add(job(cur_dir, alphabet, j, last_page))
    tw.wait()
    s.close()
    print()
    print()


def parse():
    tw = ThreadWrapper(threading.Semaphore(2 ** 3))
    cjs = {}
    for a, b, c in os.walk(src_dir):
        for d in c:
            def job(a, d):
                def _job():
                    alphabet = os.path.basename(a)
                    j = int(d.split(".")[0])
                    print("\r", a, d, alphabet, j, end="")
                    r = html.fromstring(open(os.path.join(a, d), "rb").read().decode())
                    r = r.xpath("//td/font18/font")[:-2]
                    for _ in r:
                        v = _.xpath("./text()")[0].strip().split("：")[-1].strip()
                        k = _.xpath("../preceding-sibling::*/preceding-sibling::*//font48/font/text()")[0].strip()
                        cjs[k] = v
                return _job
            tw.add(job(a, d))
    tw.wait()
    print(cjs)
    open(os.path.join(base, "pkg_data.json"), "wb").write(json.dumps(cjs).encode())


def convert(strings):
    from string import printable
    cjs = json.loads(open(os.path.join(base, "pkg_data.json"), "rb").read().decode())
    result = [[],[]]
    for character in strings:
        cj = ""
        if character in printable:
            cj = "-"*len(character)
        elif character in cjs:
            cj = cjs[character]
        if cj:
            result[0].append(character)
            result[1].append(cj)
    return result


def gen_table(result, row=5):
    TABLE = []
    def _gen_table(result):
        from unicodedata import east_asian_width
        table = []
        def _len(s):
            length = 0
            for c in s:
                status = east_asian_width(c)
                if status in ["W", "F", "A"]:
                    length += 2
                else:
                    length += 1
            return length
        for row in result:
            table.append([column for column in row])
        column_width = [max(map(_len, column)) for column in zip(*table)]
        for row in table:
            cptd = []
            for i, column in enumerate(row):
                __len = _len(column)
                if (column_width[i] - __len) > 1:
                    a = " " * ((column_width[i] - __len)-(column_width[i] - __len)//2)
                    b = column
                    c = " " * ((column_width[i] - __len)//2)
                else:
                    a = ""
                    b = column
                    c = " " * (column_width[i] - __len)
                cptd.append(" {}{}{} ".format(a, b, c))
            TABLE.append("|".join(cptd))
    for i in range(0, row-1):
        _gen_table([result[0][i*row:i*row+row], result[1][i*row:i*row+row]])
        TABLE.append("")
    return "\n".join(TABLE)

