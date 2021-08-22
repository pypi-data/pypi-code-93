import sys
import argparse
import os
import requests
import json
import yaml
import re
import traceback
import time
import random
import string
from collections import (deque,defaultdict)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_exlist(ex) :
    setex = list()
    if os.path.isfile(ex) :
        for ln in open(ex,"r").readlines() :
            setex.append(ln)
    else :
        for e in ex.split(",") :
            setex.append(e)
    return setex

def get_encoding(txt) :
    if not txt :
        return None
    # <meta HTTP-EQUIV="Content-Type" content="text/html; charset=gb2312" />
    m = re.search(r"<meta\s+.*?\s+charset=(\w+)",txt)
    if m :
        return m.group(1)
    else :
        return None
def build_index(dirbook) :
    from time import strftime,localtime
    if not os.path.isdir(dirbook) :
        return
    content = ""
    content +=("<html>\n")
    content +=("<head>\n")
    content +=("  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n")
    content +=("  <meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\"/>\n")
    content +=("  <title>Novels</title>\n")
    content +=("</head>\n")
    content +=("<body style=\"background-color: #212121;color: #B5B5B5;\">\n")
    content +=("<table border=1 style=\"border-collapse:collapse;\">\n")
    tmstr = strftime("%H:%M",localtime())
    content +=("<tr style=\"background-color:{};\"><td><a href=\".\">{}({})</a></td><td></td></tr>\n".format("#374FB2","Index",tmstr))
    colors = ["#C0C0C0","#B6B6B6","#C6C6C6"]
    ic=0
    for d in sorted(os.listdir(dirbook),reverse=True,key=lambda x:os.path.getmtime(os.path.join(dirbook,x))) :
        if not any([c for c in d if ord(c) > 127]) :
            continue
        rd = os.path.join(dirbook,d)
        if not os.path.isdir(rd) :
            continue
        fidx = os.path.join(rd,"index.html")
        if not os.path.exists(fidx) :
            continue
        ic += 1
        with open(fidx,"r",encoding="UTF-8") as f :
            cnt = 0
            for ln in reversed(f.readlines()) :
                if cnt < 2 and re.search(r"td.*href.*html",ln) :
                    ln = re.sub("href=","href={}/".format(d),ln)
                    ln = ln.replace("<tr>","")
                    ln = ln.replace("</tr>","")
                    ln = ln.replace("\"","")
                    bgcolor = colors [ic % len(colors)]
                    if cnt == 0 :
                        content +=("<tr style=\"background-color:{};\">\n<td><a href=\"{}\">{}</a></td>\n".format(bgcolor,d,d))
                    else :
                        tmstr = strftime("%D %H:%M",localtime(os.path.getmtime(rd))) 
                        content +=("<tr style=\"color:{};background-color:{};\">\n<td align=\"right\">{}</td>\n".format("#00BB00",bgcolor,tmstr))
                    content +=(ln+"</tr>\n")
                    cnt += 1
    content +=("</table>\n")
    content +=("</html>\n")
    with open(os.path.join(dirbook,"index.html"),"w",encoding="UTF-8") as fw  :
        fw.write(content)
    

def adhoc_fetch(title,page,limit=10,tgtdir=os.getcwd(),debug=False,force=0,root=None,exlist=None) :
    def random_useragent() :
        ntvers = ["9.0","10.0","8.0"]
        os = [ "Windows NT "+str(v) for v in ntvers ] + ["Macintosh"] * 3
        firevers  = [str(i)+".0" for i in range(42,51)]
        o = random.choice(os)
        f = random.choice(firevers)
        return "Mozilla/5.0 ({0}; Win64; x64; rv:{1}) Gecko/20100101 Firefox/{1}".format(o,f)
    def cid(c) :
        if type(c) in [list,tuple] :
            s = c[0]
        else :
            s = c
        if not s :
            return 0
        m = re.search(r"(\d+)\.htm",s)
        if m :
            return int(m.group(1))
        else :
            return 0
    ss = requests.Session()
    tgtdir = os.path.expanduser(tgtdir)
    if not os.path.isdir(tgtdir) :
        print("# tgtdir {} is missing.".format(tgtdir),file=sys.stderr,flush=True)
    if not os.path.isdir(os.path.join(tgtdir,title)) :
        os.mkdir(os.path.join(tgtdir,title))
        with open(os.path.join(tgtdir,title,"index.html"),"w",encoding="UTF-8") as f :
            header = """
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>book_title</title>
<body style="background-color: #212121;color: #B5B5B5;">
<table style="border-collapse:collapse">
"""
            f.write(header.replace("book_title",title))
        with open(os.path.join(tgtdir,title, "downloaded.txt"),"w",encoding="UTF-8") as f :
            pass
    downloded = set()
    last = ""
    if os.path.isfile(os.path.join(tgtdir,title, "downloaded.txt")) :
        with open(os.path.join(tgtdir,title, "downloaded.txt"),"r",encoding="UTF-8") as f :
            downloaded = set([ln.rstrip() for ln in f.readlines()])
            if force and len(downloaded) > 1 :
                last = sorted(list(downloaded),key=cid)[-(force+1)]
            elif downloaded :
                last = max(downloaded,key=cid)
            else :
                pass
    try :
        user_agent = {'User-Agent': random_useragent()}
        if debug :
            print("# {}".format(page),file=sys.stderr,flush=True)
            print("# {}".format(user_agent),file=sys.stderr,flush=True)
        rsp = ss.get(page,headers=user_agent,timeout=20,verify=False)
    except :
        print("# {}".format(traceback.format_exc().splitlines()[-1]),file=sys.stderr,flush=True)
        return "# No update."
    xcode = get_encoding(rsp.text) 
    if xcode :
        rsp.encoding = xcode.upper()
    else :
        rsp.encoding = rsp.apparent_encoding
    rtext = rsp.text
    #if debug :
    #    print(rtext)
    chapters = list()
    for m in re.findall(r"(<td|<dd|<li|<span)[^<>]*?>\s*<a\s+href\s*=\s*\"(\S*?\d+\.(htm|html))\".*?>\s*(.*?)\s*</a>",rtext,re.DOTALL) :
        if debug :
            print(m)
        url=m[1].split("/")[-1]
        m2 = re.search(r"(\d+)",url)
        if m2 :
            if len(m2.group(1)) < 4 :
                continue
        else :
            continue
        chapter=m[3]
        chapter = re.sub(r"（.*）","",chapter)
        chapter = re.sub(r"\(.*\)","",chapter)
        chapters.append((url,chapter))
    maxc = "n/a"
    chapters = sorted(list(set(chapters)),key=cid)
    if chapters :
        maxc = chapters[-1][0]
    if debug :
        print(chapters)
        print("max chapter = ",maxc)
    if maxc == last :
        print("# No update.",file=sys.stderr,flush=True)
        return "# No update : {}".format(title)
    report=""
    cdone=0
    for ix, m in enumerate(chapters) :
        if cdone > limit :
            break
        url=m[0]
        cname = url
        # redownload the last chapter to fix the prev/next link
        if cname and cid((cname,)) < cid((last,)) :
            continue
        if page.endswith(".htm") or page.endswith(".html") :
            if root :
                page = root
            else :
                page = "".join(page.split("/")[:-1])
        if not url.startswith("http") :
            url = page.rstrip("/") + "/" + url
        chapter=m[1]
        print("{:60}  ({})".format(url,chapter),file=sys.stderr,flush=True)
        try :
            user_agent = {'User-Agent': random_useragent()}
            if debug :
                print("# {}".format(url),file=sys.stderr,flush=True)
                print("# {}".format(user_agent),file=sys.stderr,flush=True)
            rsp = ss.get(url,headers=user_agent,timeout=20,verify=False)
            xcode = get_encoding(rsp.text) 
            if xcode :
                rsp.encoding = xcode.upper()
            else :
                rsp.encoding = rsp.apparent_encoding
        except :
           print("# {}".format(traceback.format_exc().splitlines()[-1]),file=sys.stderr,flush=True)
           break
        #if debug :
        #    print(rsp.text)
        m = re.search(r"<div (class|id)=\"content\".*?>(.*?)</div>",rsp.text,re.DOTALL)
        context = ""
        divgood = True
        if m :
            if debug :
                print("# matched to div class/id=content", file=sys.stderr, flush=True)
            context = m.group(2)
            if len(context) < 1500 :
                divgood = False
        if not m or not divgood :
            if debug :
                print("# wild match", file=sys.stderr, flush=True)
            lines = [ln for ln in rsp.text.splitlines()]
            started = False
            for _, ln in enumerate(lines) :
                if re.search(r"<\/*br\s*\/*>",ln) :
                    started = True
                    context += ln
                    continue
                if started and re.search(r"</div>",ln)  :
                    break
                if started :
                    context += ln
        if len(context) < 200 :
            print("# context length abnormal. chapter skipped.", file=sys.stderr, flush=True)
            context = "PLACEHOLDER"
        context = re.sub(r"</br>","<br/>",context)
        context = re.sub(r"<br\s+/>","<br/>",context)
        context = context.replace("<br/>","<br/><br/>")
        if re.search(r"<br/>\s*<br/>\s*<br/>",context,flags=re.DOTALL) :
            context = re.sub(r"<br/>\s*<br/>\s*<br/>","<br/>",context,flags=re.DOTALL)
        context = context.replace("<br/>","\n<br/>\n")
        context = context.replace("&nbsp;","")
        context = re.sub(r"\<div\>.*?\<\/div\>","",context,flags=re.DOTALL)
        context = re.sub(r"\<span\>.*?\<\/span\>","",context,flags=re.DOTALL)
        context = context.replace("<div","\n<div")
        context = context.replace("<span","\n<span")
        if exlist :
            newtxt = ""
            for ln in context.splitlines() :
                matched = False
                for p in exlist :
                    if p in ln :
                        matched = True
                        break
                if not matched :
                    newtxt += ln + "\n"
            context = newtxt
        if ix == 0 :
            prevpg = "index.html"
            cdone += 1 
        else :
            prevpg = chapters[ix-1][0]
        if ix == len(chapters)-1 :
            nextpg = "index.html"
        else :
            nextpg = chapters[ix+1][0]
        rtext = "<html>\n"
        rtext += "<head>\n"
        rtext += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        rtext += '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>' + "\n"
        rtext += "<title>{}</title>\n".format(title+":"+chapter)
        ps = """<script type="text/javascript"> var preview_page = "prevpg"; var next_page = "nextpg"; var index_page = "index.html"; function jumpPage() { if (event.keyCode==37) location=preview_page; if (event.keyCode==39) location=next_page; if (event.keyCode==13) location=index_page; } document.onkeydown=jumpPage; </script> </head>\n"""
        rtext += ps.replace("prevpg",prevpg).replace("nextpg",nextpg)
        rtext += "</head>\n"
        rtext += "<body style=\"background-color: #212121;color: #B5B5B5;\">\n"
        rtext += "<a href=\"index.html\">INDEX of {}</a>\n".format(title)
        rtext += "<br/>\n"*2
        rtext += "<a href=\"{}\">PREV CHAPTER</a>\n".format(prevpg)
        rtext += "<br/>\n"*2
        rtext += "<a href=\"{}\">NEXT CHAPTER</a><br/>\n".format(nextpg)
        rtext += "<h3>{}</h3>".format(title) + "\n"
        rtext += "<h4>{}</h4>".format(chapter) + "\n"
        rtext += "<br/>\n"
        rtext += context + "\n"
        rtext += "<br/></br>\n"
        rtext += "<a href=\"{}\">PREV CHAPTER</a>\n".format(prevpg)
        rtext += "<br/>\n"*2
        rtext += "<a href=\"{}\">NEXT CHAPTER</a><br/>\n".format(nextpg)
        rtext += "<br/>\n"*2
        rtext += "<a href=\"index.html\">INDEX of {}</a>\n".format(title)
        rtext += "<br/>\n"*2
        rtext += "<a href=\"{}\">ORIGIN_SOURCE</a><br/>\n".format(url)
        rtext += "<br/>\n"*2
        rtext += "</body>\n"
        rtext += "</html>\n"
        with open(os.path.join(tgtdir,title, cname),"w",encoding="UTF-8") as f :
            f.write(rtext)
        if context != "PLACEHOLDER" :
            with open(os.path.join(tgtdir,title, "downloaded.txt"),"a",encoding="UTF-8") as f :
                f.write(cname+"\n")
        if cname not in downloaded :
            with open(os.path.join(tgtdir,title, "index.html"),"a",encoding="UTF-8") as f :
                hcontent = "<tr><td><a href=\"{}\">{}</a></td></tr>".format(cname,chapter) + "\n"
                f.write(hcontent)
                if not report :
                    report += "# {} :\n   {}".format(title,chapter)
                else :
                    report += ", {}".format(chapter)
            downloaded.add(cname)
        cdone+=1
        time.sleep(0.5+float(random.choice([i for i in range(30)])/10.0))
    report = report.rstrip(",")
    return report


def batch_fetch(cfgfile,num=10,debug=False,force=0,exlist=None) :
    report = "\n"
    with open(cfgfile,"r",encoding="UTF-8") as f :
        thefirst = True
        seconds_wait = 5
        for ln in f.readlines() :
            if not ln or ln.startswith("#") :
                continue
            m = re.search(r"(\S+?)\,(\S+?)\,(\S+)",ln)
            if m :
                if thefirst :
                    thefirst = False
                else :
                    print("# sleep : {}".format(seconds_wait), file=sys.stderr, flush=True)
                    if debug :
                        time.sleep(seconds_wait/10)
                    else :
                        time.sleep(seconds_wait)
                title = m.group(1)
                tgtdir = m.group(2)
                page = m.group(3)
                root = None
                if "," in page :
                    arr = page.split(",")
                    page = arr[0]
                    root = arr[1]
                print("#",title,"@", tgtdir, "from", page, file=sys.stderr, flush=True)
                try :
                    rpt = adhoc_fetch(title,page,num,tgtdir,debug,force,root,exlist) + "\n"
                    report += rpt
                    if not rpt or not re.search(r"\S+",rpt) or re.search(r"No update",rpt,re.IGNORECASE) :
                        seconds_wait = 5
                    else :
                        seconds_wait = 10+random.choice([i for i in range(30)])
                except :
                    traceback.print_exc()
                    seonds_wait = 20
    return report

def novels_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--cfgfile", dest="cfgfile", default="~/.novels/novel.conf", help="input file")
    parser.add_argument("-t", "--title", dest="title", default=None, help="novel title")
    parser.add_argument("-n", "--number", dest="number", type=int, default=10, help="how many chapters to retrieve")
    parser.add_argument("-p", "--page", dest="page", default=None, help="Novel index page",)
    parser.add_argument("-d", "--dir", dest="dir", default=os.getcwd(), help="where to store books",)
    parser.add_argument("-E", "--excludes", dest="excludes", default="~/.novels/excludes.conf", help="pattern or file of patterns to be excluded",)
    parser.add_argument("-r", "--root", dest="root", default=None, help="page root. use it when index page has differnt root then chapters.",)
    parser.add_argument("-I", "--bookindex", dest="bookindex", action="store_true",default=False, help="build index page for latest chapters.",)
    parser.add_argument("-f", "--force", dest="force", action="count", default=0, help="force reload last chapter when no update.",)
    parser.add_argument("-X", "--debug", dest="debug", action="count", default=0, help="debug mode",)
    args = parser.parse_args()

    if args.bookindex and args.dir :
        build_index(args.dir) 
        return

    exlist = None
    if args.excludes :
        args.excludes = os.path.expanduser(args.excludes)
        exlist = get_exlist(args.excludes)

    if args.title :
        adhoc_fetch(args.title,args.page,args.number,args.dir,args.debug,args.force,args.root,exlist)
        return
    args.cfgfile = os.path.expanduser(args.cfgfile)
    if os.path.isfile(args.cfgfile) :
        report = batch_fetch(args.cfgfile,num=args.number,debug=args.debug,force=args.force,exlist=exlist)
        print("# Summary :\n" + report)
    else :
        if not os.path.isdir(os.path.expanduser("~/.novels")) :
            os.mkdir(os.path.expanduser("~/.novels"))
        with open(args.cfgfile,"w",encoding="UTF-8") as f :
            f.write("#title,localdir,bookpage\n")


if __name__ == "__main__" :
    novels_main()
