"""
Copyright (c) 2020 cyrxdzj
PyCheer is licensed under Mulan PSL v2.
You can use this software according to the terms and conditions of the Mulan PSL v2.
You may obtain a copy of Mulan PSL v2 at:
         http://license.coscl.org.cn/MulanPSL2
THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
See the Mulan PSL v2 for more details.
"""
# import some modules
from flask import Flask, request, make_response  # 主服务Flask引用
from urllib.request import unquote, quote  # 解析或编码有特殊字符的URLimport os  # 引用此模块，用于文件（夹）的其它功能。
import sys  # 获取命令行参数及自身目录
import json  # 解析json
import time  # 获取当前时间
import hashlib  # 制作token
import webbrowser  # 启动浏览器
import threading  # 使用线程启动浏览器

try:  # 获取SVG
    from svg import *
except:
    from .svg import *

try:
    from git import Repo, Git  # 用于Git相关功能
    import_git_successful=True;
except:
    print("\033[31mFailed to introduce Git module. This may be because Git is not installed on your computer.\033[0m")
    print("\033[31mIf you don't want to start Git using PyCheer, you can ignore this information.\033[0m")
    import_git_successful=False;

__version__ = "V1.0.7"

# 用来默认展示的。
show_str = r'''
 _____  __    __  _____   _   _   _____   _____   _____   
|  _  \ \ \  / / /  ___| | | | | | ____| | ____| |  _  \  
| |_| |  \ \/ /  | |     | |_| | | |__   | |__   | |_| |  
|  ___/   \  /   | |     |  _  | |  __|  |  __|  |  _  /  
| |       / /    | |___  | | | | | |___  | |___  | | \ \  
|_|      /_/     \_____| |_| |_| |_____| |_____| |_|  \_\ 
AUTHOR:cyrxdzj
LICENSE:MulanPSL-2.0
VERSION:%s
A WEB editor.
Please see https://gitee.com/cyrxdzj/PyCheer
You can type "pycheer run" to launch this application.
You can type "pycheer help" for help.
''' % __version__

mydir = os.path.dirname(__file__)
workdir = os.getcwd()

help_str = r'''
##############################
pycheer version
View the version of this software.
------------------------------
No additional parameters are required.

##############################
pycheer run
Start pycheer in this directory.
------------------------------
-p  --port      Set the run port of PyCheer.
-b  --browser   Let PyCheer run and then automatically open the browser.

##############################
pycheer help
Get help.
------------------------------
No additional parameters are required.
'''


def get_suffix(file_path: str):  # 文件获取后缀。
    strs = file_path.split("/")
    if not strs[-1]:
        return ''
    file_name_strs = strs[-1].split(".")
    if len(file_name_strs) == 0:
        return ''
    if not file_name_strs[-1]:
        return ''
    return file_name_strs[-1]


def run(params):
    def open_browser(url):
        time.sleep(1)
        webbrowser.open(url=url)

    app = Flask("PyCheer Server")
    token = hashlib.sha256(
        time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()).encode(encoding="UTF-8", errors="strict")).hexdigest()
    print("The token for this run is\033[34m %s\033[0m." % token)
    print("Running at:\033[32m %s\033[0m" % ("http://localhost:%s/begin?token=%s" % (params["-p"], token)))
    if params['-b']:
        t = threading.Thread(target=open_browser, args=("http://localhost:%s/begin?token=%s" % (params["-p"], token),))
        t.start()

    # ------------------------------DO GET------------------------------
    @app.route("/", methods=["GET"])
    @app.route("/index", methods=['GET'])
    def index_handler():
        if request.args.get("token") != token and request.cookies.get("token") != token:
            return '', 302, [("Location", "begin")]
        response = make_response('')
        response.status = 302
        response.headers['Location'] = 'tree'
        if request.args.get("token") == token:
            response.set_cookie("token", token)
        return response

    @app.route("/begin", methods=['GET'])
    def begin_handler():
        if request.cookies.get("token") == token:
            return '', 302, [("Location", request.args.get("go_url") or "/index")]
        if request.args.get("token") == token:
            response = make_response("")
            response.status = 302
            response.set_cookie("token", token)
            response.headers["Location"] = request.args.get("go_url") or "/index"
            return response
        return open(os.path.join(mydir, "./html/begin.html"), encoding="UTF-8").read(), 200

    @app.route("/see", methods=["GET"])
    def see_handler():
        if request.args.get("token") != token and request.cookies.get("token") != token:
            return '', 302, [
                ("Location", "begin?go_url=" + (quote("/see?path=" + request.args.get("path","").encode("ISO-8859-1").decode("utf-8"))))]
        file_path = request.args.get('path')
        if not file_path:
            response = make_response('403 Forbidden')
            response.status = 403
            if request.args.get("token") == token:
                response.set_cookie("token", token)
            return response
        file_path = unquote(file_path)
        if not os.path.isfile(file_path):
            response = make_response("404 Not Found")
            response.status = 404
            if request.args.get("token") == token:
                response.set_cookie("token", token)
            return response
        if get_suffix(file_path) == 'py':
            response_data = open(os.path.join(mydir, "./html/editpy.html"), encoding="UTF-8").read().replace(
                "<init_code>", quote(open(file_path, encoding="UTF-8").read()))
            response = make_response(response_data)
            response.status = 200
            if request.args.get("token") == token:
                response.set_cookie("token", token)
            response.headers["Content-Type"] = "text/html;charset=utf-8"
            return response
        elif get_suffix(file_path) == 'png':
            response = make_response(open(file_path, "rb").read())
            response.status = 200
            if request.args.get("token") == token:
                response.set_cookie("token", token)
            response.headers["Content-Type"] = "image/png"
            return response
        elif get_suffix(file_path) == 'jpg':
            response = make_response(open(file_path, "rb").read())
            response.status = 200
            if request.args.get("token") == token:
                response.set_cookie("token", token)
            response.headers["Content-Type"] = "image/jpg"
            return response
        elif get_suffix(file_path) == 'jpeg':
            response = make_response(open(file_path, "rb").read())
            response.status = 200
            if request.args.get("token") == token:
                response.set_cookie("token", token)
            response.headers["Content-Type"] = "image/jpeg"
            return response
        elif get_suffix(file_path) == 'mp3':
            response = make_response(open(file_path, "rb").read())
            response.status = 200
            if request.args.get("token") == token:
                response.set_cookie("token", token)
            response.headers["Content-Type"] = "audio/mp3"
            return response
        elif get_suffix(file_path) == 'md':
            response_data = open(os.path.join(mydir, "./html/editmd.html"), encoding="UTF-8").read().replace(
                "<init_code>", quote(open(file_path, encoding="UTF-8").read()))
            response = make_response(response_data)
            response.status = 200
            if request.args.get("token") == token:
                response.set_cookie("token", token)
            response.headers["Content-Type"] = "text/html;charset=utf-8"
            return response
        elif get_suffix(file_path) == 'html':
            response_data = open(os.path.join(mydir, "./html/edithtml.html"), encoding="UTF-8").read().replace(
                "<init_code>", quote(open(file_path, encoding="UTF-8").read()))
            response = make_response(response_data)
            response.status = 200
            if request.args.get("token") == token:
                response.set_cookie("token", token)
            response.headers["Content-Type"] = "text/html;charset=utf-8"
            return response
        elif get_suffix(file_path) == 'css':
            response_data = open(os.path.join(mydir, "./html/editcss.html"), encoding="UTF-8").read().replace(
                "<init_code>", quote(open(file_path, encoding="UTF-8").read()))
            response = make_response(response_data)
            response.status = 200
            if request.args.get("token") == token:
                response.set_cookie("token", token)
            response.headers["Content-Type"] = "text/html;charset=utf-8"
            return response
        elif get_suffix(file_path) == 'txt':
            response_data = open(os.path.join(mydir, "./html/edittxt.html"), encoding="UTF-8").read().replace(
                "<init_code>", quote(open(file_path, encoding="UTF-8").read()))
            response = make_response(response_data)
            response.status = 200
            if request.args.get("token") == token:
                response.set_cookie("token", token)
            response.headers["Content-Type"] = "text/html;charset=utf-8"
            return response
        elif get_suffix(file_path) == 'js':
            response_data = open(os.path.join(mydir, "./html/editjs.html"), encoding="UTF-8").read().replace(
                "<init_code>", quote(open(file_path, encoding="UTF-8").read()))
            response = make_response(response_data)
            response.status = 200
            if request.args.get("token") == token:
                response.set_cookie("token", token)
            response.headers["Content-Type"] = "text/html;charset=utf-8"
            return response
        elif get_suffix(file_path) == 'c' or get_suffix(file_path) == 'cpp' or get_suffix(file_path) == 'h' or get_suffix(file_path) == 'hpp':
            response_data = open(os.path.join(mydir, "./html/editc_series.html"), encoding="UTF-8").read().replace(
                "<init_code>", quote(open(file_path, encoding="UTF-8").read()))
            response = make_response(response_data)
            response.status = 200
            if request.args.get("token") == token:
                response.set_cookie("token", token)
            response.headers["Content-Type"] = "text/html;charset=utf-8"
            return response
        else:
            response = make_response(open(file_path, encoding="UTF-8").read())
            response.status = 200
            if request.args.get("token") == token:
                response.set_cookie("token", token)
            response.headers["Content-Type"] = "text/plain;charset=utf-8"
            return response

    @app.route("/js/<js_path>", methods=['GET'])
    def js_handler(js_path=""):
        if not os.path.isfile(os.path.join(mydir, "./js/%s" % js_path)):
            response = make_response("404 Not Found")
            response.status = 404
        else:
            response = make_response(open(os.path.join(mydir, "./js/%s" % js_path), encoding="UTF-8").read())
            response.status = 200
            response.headers["Content-type"] = "text/script"
        if request.args.get("token") == token:
            response.set_cookie("token", token)
        return response

    @app.route("/css/<css_path>", methods=["GET"])
    def css_handler(css_path=""):
        if not os.path.isfile(os.path.join(mydir, "./css/%s" % css_path)):
            response = make_response("404 Not Found")
            response.status = 404
        else:
            response = make_response(open(os.path.join(mydir, "./css/%s" % css_path), encoding="UTF-8").read())
            response.status = 200
            response.headers["Content-type"] = "text/css"
        if request.args.get("token") == token:
            response.set_cookie("token", token)
        return response

    @app.route("/main-control1.html", methods=["get"])
    def mc1_handler():
        if request.args.get("token") != token and request.cookies.get("token") != token:
            return '', 302, [("Location", '/begin?go_url=' + quote("/main-control1.html"))]
        response = make_response(open(os.path.join(mydir, "./html/main-control1.html"), 'r', encoding="UTF-8").read())
        response.headers["Content-type"] = "text/html"
        if request.args.get("token") == token:
            response.set_cookie("token", token)
        return response

    @app.route("/main-control2.html", methods=["get"])
    def mc2_handler():
        if request.args.get("token") != token and request.cookies.get("token") != token:
            return '', 302, [("Location", '/begin?go_url=' + quote("/main-control2.html"))]
        response = make_response(open(os.path.join(mydir, "./html/main-control2.html"), 'r', encoding="UTF-8").read())
        response.headers["Content-type"] = "text/html"
        if request.args.get("token") == token:
            response.set_cookie("token", token)
        return response

    @app.route("/head.html", methods=["get"])
    def head_handler():
        if request.args.get("token") != token and request.cookies.get("token") != token:
            return '', 302, [("Location", '/begin?go_url=' + quote("/head.html"))]
        response = make_response(open(os.path.join(mydir, "./html/head.html"), 'r', encoding="UTF-8").read())
        response.headers["Content-type"] = "text/html"
        if request.args.get("token") == token:
            response.set_cookie("token", token)
        return response

    @app.route("/tree")
    def tree_handler():
        # 这个函数应该会很长，因为这个函数实在是太多功能了，需要动态加载。
        if request.args.get("token") != token and request.cookies.get("token") != token:
            return '', 302, [
                ("Location", '/begin?go_url=' + quote("/tree?path=%s" % quote(request.args.get("path", ""))))]
        if ".git" in os.listdir(".") and import_git_successful:
            git_button = '<button class="btn btn-outline-primary" onclick="window.open(`/git`)"><svg t="1626613019227" class="icon" viewBox="0 0 1025 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="8529" width="20" height="20"><path d="M1004.728 466.4l-447.104-447.072c-25.728-25.76-67.488-25.76-93.28 0l-103.872 103.872 78.176 78.176c12.544-5.984 26.56-9.376 41.376-9.376 53.024 0 96 42.976 96 96 0 14.816-3.36 28.864-9.376 41.376l127.968 127.968c12.544-5.984 26.56-9.376 41.376-9.376 53.024 0 96 42.976 96 96s-42.976 96-96 96-96-42.976-96-96c0-14.816 3.36-28.864 9.376-41.376l-127.968-127.968c-3.04 1.472-6.176 2.752-9.376 3.872l0 266.976c37.28 13.184 64 48.704 64 90.528 0 53.024-42.976 96-96 96s-96-42.976-96-96c0-41.792 26.72-77.344 64-90.528l0-266.976c-37.28-13.184-64-48.704-64-90.528 0-14.816 3.36-28.864 9.376-41.376l-78.176-78.176-295.904 295.872c-25.76 25.792-25.76 67.52 0 93.28l447.136 447.072c25.728 25.76 67.488 25.76 93.28 0l444.992-444.992c25.76-25.76 25.76-67.552 0-93.28z" fill="#007BFF" p-id="8530"></path></svg>启动Git</button>'
        else:
            git_button = ""
        path = unquote(request.args.get("path", "")).replace("\\", "/")  # 将反斜杠统一为正斜杠。
        if len(path) > 0:
            if path[0] == '/':
                path = ''.join(list(path)[1:])
        if not os.path.isdir("./" + path):
            return '404 dir not found.', 404
        path_split = path.split("/")
        if path_split[-1] == '':
            del path_split[-1]
        if len(path_split) > 0:
            if path_split[0] == '':
                del path_split[0]
        breadcrumb_code = ""
        if len(path_split) > 0:
            breadcrumb_code += '<ul class="breadcrumb" style="width:60%;"><li><a href="/tree">（根目录）</a></li>'
            for i in range(len(path_split) - 1):
                now_path = ""
                for j in range(i + 1):
                    now_path += "/" + path_split[j]
                breadcrumb_code += '<li><a href="/tree?path=%s">&nbsp;/&nbsp;%s</a></li>' % (quote(now_path), path_split[i])
            breadcrumb_code += '<li class="active">&nbsp;/&nbsp;%s</li>' % path_split[-1]
            breadcrumb_code += "</ul>"
        dir_content = os.listdir("./" + path)
        with open(os.path.join(mydir, "./html/view_files_code_item_tpl.html").replace("\\.", ""),
                  encoding="UTF-8") as fobj:
            view_files_code_item_tpl = fobj.read()
        view_files_code = ""
        if len(path_split) > 0:
            view_files_code += view_files_code_item_tpl.replace("svg-icon", svg_by_type["folder"]).replace("file_name",
                                                                                                           "..（上一级目录）").replace(
                "file_link", 'tree?path=%s' % quote('/'.join(tuple(path_split[:-1]))))
        if len(dir_content) == 0:
            view_files_code += '<li class="list-group-item"><div style="width:100%;height:20px;padding:2px 0px;border:0px;margin:0px;"><a>此文件夹空空如也~</a></div></li>'
        for item in dir_content:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                view_files_code += view_files_code_item_tpl.replace("svg-icon", get_svg(item_path)).replace(
                    "file_name", item).replace("file_link", "tree?path=%s" % quote(item_path))
        for item in dir_content:
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                view_files_code += view_files_code_item_tpl.replace("svg-icon", get_svg(item_path)).replace(
                    "file_name", item).replace("file_link", "see?path=%s\" target=\"_blank" % quote(item_path))
        # 以上两个循环主要是将文件与文件夹做一下区分，文件夹在上。
        return open(os.path.join(mydir, "./html/tree_tpl.html"), "r", encoding="UTF-8").read().replace("{breadcrumb}",
                                                                                                       breadcrumb_code).replace(
            "{view_files}", view_files_code).replace("{git_button}", git_button)

    @app.route("/logo/logo.png", methods=["GET"])
    def logo_handler():
        response = make_response(open(os.path.join(mydir, "./logo/logo.png"), "rb").read())
        return response, 200, [("Cache-Control", "public, max-age=86400")]

    @app.route("/logo.ico", methods=["GET"])
    def icon_handler():
        response = make_response(open(os.path.join(mydir, "./logo/logo.ico"), "rb").read())
        return response, 200, [("Cache-Control", "public, max-age=86400"), ("Content-Type", "image/x-icon")]

    @app.route("/git", methods=["GET"])
    def git_handler():
        if request.args.get("token") != token and request.cookies.get("token") != token:
            return '', 302, [("Location", '/begin?go_url=' + quote("/head.html"))]
        if not import_git_successful:
            response = make_response("因为引入Git模块失败，暂时不可使用Git。")
            response.status = 403
            response.headers["Content-Type"] = "text/html;charset=utf-8"
            return response
        if not ".git" in os.listdir("."):
            response = make_response("检测到.git文件夹不存在，因此PyCheer无法调用Git。")
            response.status = 404
            response.headers["Content-Type"] = "text/html;charset=utf-8"
            return response
        git_repo = Repo('.')
        git_branches = ""
        for branch in [str(b) for b in git_repo.branches]:
            if branch == str(git_repo.active_branch):
                git_branches += '<li class="list-group-item" style="background:green;color:white;">%s<a style="float:right;" title="当前分支"><svg t="1626612810303" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2012" width="16" height="16"><path d="M510.912 0.192c18.304 0 33.152 14.848 33.152 33.152v74.304a404.672 404.672 0 0 1 370.048 370.112h74.24a33.152 33.152 0 1 1 0 66.304h-74.24A404.672 404.672 0 0 1 544 914.112v74.24a33.152 33.152 0 1 1-66.368 0v-74.24A404.672 404.672 0 0 1 107.712 544H33.408a33.152 33.152 0 0 1 0-66.368h74.24a404.672 404.672 0 0 1 370.112-370.048V33.408c0-18.368 14.784-33.216 33.152-33.216z m0 172.48a338.24 338.24 0 1 0 0 676.48 338.24 338.24 0 0 0 0-676.48z m0 125.952a212.224 212.224 0 1 1 0 424.512 212.224 212.224 0 0 1 0-424.512z" p-id="2013" fill="#ffffff"></path></svg></li></a>' % branch
            else:
                git_branches += '<li class="list-group-item">%s<a onclick="javascript:checkout(`%s`)" style="float:right;" title="切换至此分支"><svg t="1626613395918" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="9474" width="16" height="16"><path d="M619.5 200v140.4c0 12.5-10.1 22.7-22.7 22.7H88.3c-12.5 0-22.7 10.1-22.7 22.7v39.9c0 12.5 10.1 22.7 22.7 22.7H900c20.9 0 30.7-25.9 14.9-39.7L657.1 183c-14.6-12.9-37.6-2.5-37.6 17z m-213 624.4V684c0-12.5 10.1-22.7 22.7-22.7h508.6c12.5 0 22.7-10.1 22.7-22.7v-39.9c0-12.5-10.1-22.7-22.7-22.7H126c-20.9 0-30.7 25.9-14.9 39.7l257.8 225.6c14.6 13 37.6 2.6 37.6-16.9z" p-id="9475" fill="#2c2c2c"></path></svg></a></li>' % (
                branch, branch)
        git_remotes = ""
        for remote in [str(b) for b in git_repo.remotes]:
            git_remotes += '<li class="list-group-item">%s<div style="float:right"><a style="margin-right:5px;" onclick="javascript:push(`%s`,`%s`);" title="推送当前分支至这个远程分支"><svg t="1626694392516" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4288" width="16" height="16"><path d="M389.013333 958.72c-9.386667 0-18.346667-3.733333-25.066666-10.346667-6.613333-6.613333-10.346667-15.68-10.346667-24.96V600.426667c0-10.666667 4.8-20.693333 13.12-27.413334l286.506667-232.213333c15.146667-12.266667 37.44-10.026667 49.706666 5.12s10.026667 37.44-5.12 49.706667L424.32 617.28V817.066667l85.973333-114.56c10.56-13.973333 29.653333-18.24 45.12-9.92l142.506667 76.373333 169.066667-606.933333c2.453333-8-0.213333-16.64-6.72-21.973334-6.293333-5.44-15.146667-6.613333-22.613334-2.986666l-641.066666 300.8 83.093333 47.786666c10.986667 6.293333 17.706667 17.92 17.813333 30.613334 0 12.586667-6.613333 24.32-17.6 30.72-10.88 6.4-24.426667 6.4-35.413333 0.106666L102.506667 465.493333c-11.413333-6.613333-18.24-18.986667-17.706667-32.213333 0.533333-13.226667 8.32-24.96 20.266667-30.613333L807.466667 73.066667c32.426667-15.466667 71.04-10.346667 98.346666 13.12 27.626667 23.04 39.04 60.16 29.226667 94.72l-181.12 649.6c-2.88 10.346667-10.346667 18.773333-20.16 23.04-9.813333 4.16-21.12 3.733333-30.613333-1.386667l-154.56-82.986667-131.306667 175.36c-6.72 8.853333-17.173333 14.08-28.266667 14.186667z m0 0" p-id="4289" fill="#2c2c2c"></path></svg></a><a style="margin-right:5px;" onclick="javascript:pull(`%s`,`%s`);" title="拉取这个远程分支至当前分支"><svg t="1626694363528" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="3318" width="16" height="16"><path d="M549.28494781 696.327485h-74.85380062V127.81286563h74.85380062z m0 0" fill="#2c2c2c" p-id="3319"></path><path d="M902.96915844 913.02923937a8.23391812 8.23391812 0 0 0 7.48537969-8.98245562V120.327485a8.23391812 8.23391812 0 0 0-7.48537969-8.60818688H120.37266687a8.23391812 8.23391812 0 0 0-7.85964843 8.60818688v783.71929875a8.60818688 8.60818688 0 0 0 7.85964844 8.98245563H902.96915844m0 78.59649187H120.37266687A83.08771969 83.08771969 0 0 1 42.15044469 904.04678375V120.327485A82.71345 82.71345 0 0 1 120.37266687 32H902.96915844a82.71345 82.71345 0 0 1 77.84795344 87.20467875v784.842105A83.08771969 83.08771969 0 0 1 902.96915844 991.62573125z m0 0" fill="#2c2c2c" p-id="3320"></path><path d="M497.26155594 880.84210531a18.33918094 18.33918094 0 0 0 15.34502906 8.98245563 18.71345063 18.71345063 0 0 0 15.34503-8.98245563l174.03508687-280.70175469a22.83040969 22.83040969 0 0 0 1e-8-21.33333281 18.33918094 18.33918094 0 0 0-16.46783625-11.22807H338.19722844a18.33918094 18.33918094 0 0 0-16.46783625 11.22807 23.95321594 23.95321594 0 0 0 0 21.33333281z m0 0" fill="#2c2c2c" p-id="3321"></path></svg></a><a onclick="javascript:remove_remote(`%s`);" title="删除此远程分支"><svg t="1626677535162" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2609" width="16" height="16"><path d="M617.9 793.5c-19.2 0-34.7-15.5-34.7-34.7V376.9c0-19.2 15.5-34.7 34.7-34.7s34.7 15.5 34.7 34.7v381.8c0.1 19.3-15.5 34.8-34.7 34.8z m-208.2 0c-19.2 0-34.7-15.5-34.7-34.7V376.9c0-19.2 15.5-34.7 34.7-34.7s34.7 15.5 34.7 34.7v381.8c0 19.3-15.5 34.8-34.7 34.8z m555.4-590.1H791.5V134c0-57.4-46.3-104.1-103.3-104.1h-348c-57.4 0-104.1 46.7-104.1 104.1v69.4H62.6c-19.2 0-34.7 15.5-34.7 34.7s15.5 34.7 34.7 34.7h902.5c19.2 0 34.7-15.5 34.7-34.7s-15.6-34.7-34.7-34.7zM305.5 134c0-19.1 15.6-34.7 34.7-34.7h347.9c19 0 33.9 15.2 33.9 34.7v69.4H305.5V134z m451.4 867.8h-486c-57.4 0-104.1-46.7-104.1-104.1V376.4c0-19.2 15.6-34.7 34.7-34.7 19.2 0 34.7 15.6 34.7 34.7v521.2c0 19.2 15.6 34.7 34.7 34.7h486c19.2 0 34.7-15.6 34.7-34.7V377.8c0-19.2 15.5-34.7 34.7-34.7s34.7 15.6 34.7 34.7v519.8c0.1 57.4-46.7 104.2-104.1 104.2z" p-id="2610" fill="#2c2c2c"></path></svg></a></div></li>' % (
            remote, remote, str(git_repo.active_branch), remote, str(git_repo.active_branch), remote)
        if not git_remotes:
            git_remotes = '<li class="list-group-item">没有远程分支。</li>'
        git_content = open(os.path.join(mydir, "./html/git.html"), encoding="UTF-8").read().replace("{git_branches}",
                                                                                                    git_branches).replace(
            "{git_remotes}", git_remotes)
        response = make_response(git_content)
        response.status = 200
        response.headers["Content-Type"] = "text/html;charset=utf-8"
        return response

    @app.route("/seeicon",methods=["GET"])
    def seeicon_handler():
        icon_by_type=""
        icon_by_suffix=""
        for i in svg_by_type.keys():
            icon_by_type+='<li class="list-group-item">%s%s</li>'%(svg_by_type[i],i)
        for i in svg_by_suffix.keys():
            icon_by_suffix+='<li class="list-group-item">%s%s</li>'%(svg_by_suffix[i],i)
        response=make_response(open(os.path.join(mydir,"./html/seeicon.html"),encoding="UTF-8").read().replace("{icon_by_type}",icon_by_type).replace("{icon_by_suffix}",icon_by_suffix))
        response.status=200
        response.headers["Content-Type"] = "text/html;charset=utf-8"
        return response

    # ------------------------------DO POST------------------------------
    @app.route("/rg", methods=["POST"])
    def rg_handler():
        if request.args.get("token") == token:
            response = make_response(json.dumps({"msg": "OK"}))
            response.headers["Content-type"] = "text/json"
            response.status = 200
            response.set_cookie("token", token)
            return response
        else:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response

    @app.route("/save", methods=["POST"])  # 保存文件。
    def save_handler():
        if request.cookies.get("token") != token:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        mode = request.args.get("mode", "w")
        path = unquote(request.args.get("path", "")).encode("ISO-8859-1").decode("UTF-8")
        if not os.path.isfile(os.path.join(workdir, path)):
            response = make_response(json.dumps({"msg": "File not found."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        data = unquote(request.get_data().decode())
        with open(os.path.join(workdir, path), mode, encoding="UTF-8") as fobj:
            fobj.write(data)
        response = make_response(json.dumps({"msg": "Success to save the file."}))
        response.headers["Content-type"] = "text/json"
        response.status = 200
        return response

    @app.route("/close", methods=["POST"])
    def close_handler():
        if request.cookies.get("token") != token:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        os._exit(0)

    @app.route("/quit", methods=["POST"])
    def quit_handler():
        if request.cookies.get("token") != token:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        response = make_response()
        response.delete_cookie("token")
        response.status = 200
        return response

    @app.route("/new_file", methods=["POST"])
    def new_file_handler():
        if request.cookies.get("token") != token:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        if not request.args.get("file_name"):
            response = make_response(json.dumps({"msg": "File name params not found."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        path = unquote(request.args.get("path")).encode("ISO-8859-1").decode("utf-8")
        if len(path) > 0:
            if path[0] == '/':
                path = ''.join(list(path)[1:])
        file_name = unquote(request.args.get("file_name"))
        if os.path.exists(os.path.join(path, file_name)):
            response = make_response(json.dumps({"msg": "File exists already."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        open(os.path.join(path, file_name), "w")
        response = make_response(json.dumps({"msg": "OK"}))
        response.headers["Content-type"] = "text/json"
        response.status = 200
        return response

    @app.route("/new_folder", methods=["POST"])
    def new_folder_handler():
        if request.cookies.get("token") != token:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        if not request.args.get("folder_name"):
            response = make_response(json.dumps({"msg": "Folder name params not found."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        path = unquote(request.args.get("path")).encode("ISO-8859-1").decode("utf-8")
        if len(path) > 0:
            if path[0] == '/':
                path = ''.join(list(path)[1:])
        folder_name = unquote(request.args.get("folder_name"))
        if os.path.exists(os.path.join(path, folder_name)):
            response = make_response(json.dumps({"msg": "Folder exists already."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        os.mkdir(os.path.join(path, folder_name))
        response = make_response(json.dumps({"msg": "OK"}))
        response.headers["Content-type"] = "text/json"
        response.status = 200
        return response

    @app.route("/rename", methods=["POST"])
    def rename_handler():
        if request.cookies.get("token") != token:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        if not request.args.get("new_file_name") or not request.args.get("file_name"):
            response = make_response(json.dumps({"msg": "File name or new file name params not found."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        path = unquote(request.args.get("path"))
        if len(path) > 0:
            if path[0] == '/':
                path = ''.join(list(path)[1:])
        file_name = unquote(request.args.get("file_name"))
        new_file_name = unquote(request.args.get("new_file_name"))
        print("./"+os.path.join(path, file_name))
        if not os.path.exists(os.path.join(path, file_name)):
            response = make_response(json.dumps({"msg": "File not found."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        if os.path.exists(os.path.join(path, new_file_name)):
            response = make_response(json.dumps({"msg": "New file exists already."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        os.rename(os.path.join(path, file_name), os.path.join(path, new_file_name))
        response = make_response(json.dumps({"msg": "OK"}))
        response.headers["Content-type"] = "text/json"
        response.status = 200
        return response

    # ------------------------------DO GIT POST------------------------------
    @app.route("/git/checkout", methods=["POST"])
    def checkout_handler():
        if request.cookies.get("token") != token:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        if not ".git" in os.listdir("."):
            response = make_response(json.dumps({"msg": "Git dir not found."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        git = Git(".")
        try:
            git.checkout(request.args.get("branch"))
            response = make_response(json.dumps({"msg": "OK"}))
            response.headers["Content-type"] = "text/json"
            response.status = 200
            return response
        except Exception as ex:
            print(ex)
            response = make_response(json.dumps({"msg": "Check out failed. %s" % str(ex)}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response

    @app.route("/git/new_remote", methods=["POST"])
    def new_remote_handler():
        if request.cookies.get("token") != token:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        if not ".git" in os.listdir("."):
            response = make_response(json.dumps({"msg": "Git dir not found."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        g = Git(".")
        try:
            g.execute("git remote add %s %s" % (request.args.get("name"), request.args.get("url")))
            response = make_response(json.dumps({"msg": "OK"}))
            response.headers["Content-type"] = "text/json"
            response.status = 200
            return response
        except Exception as ex:
            print(ex)
            response = make_response(json.dumps({"msg": "Failed. %s" % str(ex)}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response

    @app.route("/git/remove_remote", methods=["POST"])
    def remove_remote_handler():
        if request.cookies.get("token") != token:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        if not ".git" in os.listdir("."):
            response = make_response(json.dumps({"msg": "Git dir not found."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        g = Git(".")
        try:
            g.execute("git remote remove %s" % request.args.get("name"))
            response = make_response(json.dumps({"msg": "OK"}))
            response.headers["Content-type"] = "text/json"
            response.status = 200
            return response
        except Exception as ex:
            print(ex)
            response = make_response(json.dumps({"msg": "Failed. %s" % str(ex)}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response

    @app.route("/git/new_branch", methods=["POST"])
    def new_branch_handler():
        if request.cookies.get("token") != token:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        if not ".git" in os.listdir("."):
            response = make_response(json.dumps({"msg": "Git dir not found."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        g = Git(".")
        try:
            g.execute("git branch %s" % request.args.get("name"))
            response = make_response(json.dumps({"msg": "OK"}))
            response.headers["Content-type"] = "text/json"
            response.status = 200
            return response
        except Exception as ex:
            print(ex)
            response = make_response(json.dumps({"msg": "Failed. %s" % str(ex)}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response

    @app.route("/git/status", methods=["POST"])
    def status_handler():
        if request.cookies.get("token") != token:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        if not ".git" in os.listdir("."):
            response = make_response(json.dumps({"msg": "Git dir not found."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        g = Git(".")
        try:
            response = make_response(json.dumps({"msg": "OK", "result": quote(g.status())}))
            response.headers["Content-type"] = "text/json"
            response.status = 200
            return response
        except Exception as ex:
            print(ex)
            response = make_response(json.dumps({"msg": "Failed. %s" % str(ex)}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response

    @app.route("/git/stage", methods=["POST"])
    def stage_handler():
        if request.cookies.get("token") != token:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        if not ".git" in os.listdir("."):
            response = make_response(json.dumps({"msg": "Git dir not found."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        g = Git(".")
        try:
            g.execute("git add .")
            response = make_response(json.dumps({"msg": "OK"}))
            response.headers["Content-type"] = "text/json"
            response.status = 200
            return response
        except Exception as ex:
            print(ex)
            response = make_response(json.dumps({"msg": "Failed. %s" % str(ex)}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response

    @app.route("/git/commit", methods=["POST"])
    def commit_handler():
        if request.cookies.get("token") != token:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        if not ".git" in os.listdir("."):
            response = make_response(json.dumps({"msg": "Git dir not found."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        r = Repo(".")
        try:
            r.index.commit(unquote(request.args.get("info")))
            response = make_response(json.dumps({"msg": "OK"}))
            response.headers["Content-type"] = "text/json"
            response.status = 200
            return response
        except Exception as ex:
            print(ex)
            response = make_response(json.dumps({"msg": "Failed. %s" % str(ex)}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response

    @app.route("/git/push", methods=["POST"])
    def push_handler():
        if request.cookies.get("token") != token:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        if not ".git" in os.listdir("."):
            response = make_response(json.dumps({"msg": "Git dir not found."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        r = Repo(".")
        try:
            r.remote(request.args.get("remote")).push(request.args.get("branch"))
            response = make_response(json.dumps({"msg": "OK"}))
            response.headers["Content-type"] = "text/json"
            response.status = 200
            return response
        except Exception as ex:
            print(ex)
            response = make_response(json.dumps({"msg": "Failed. %s" % str(ex)}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response

    @app.route("/git/pull", methods=["POST"])
    def pull_handler():
        if request.cookies.get("token") != token:
            response = make_response(json.dumps({"msg": "The token is not match."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        if not ".git" in os.listdir("."):
            response = make_response(json.dumps({"msg": "Git dir not found."}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response
        r = Repo(".")
        try:
            r.remote(request.args.get("remote")).pull(request.args.get("branch"))
            response = make_response(json.dumps({"msg": "OK"}))
            response.headers["Content-type"] = "text/json"
            response.status = 200
            return response
        except Exception as ex:
            print(ex)
            response = make_response(json.dumps({"msg": "Failed. %s" % str(ex)}))
            response.headers["Content-type"] = "text/json"
            response.status = 403
            return response

    # ------------------------------DO GET AND POST------------------------------
    @app.route("/hello", methods=["GET", "POST"])
    def hello_handler():  # 访问这个路径，获得关于PyCheer的信息。
        return "<h1>PyCheer Server</h1>Version %s<br>Running on %s" % (__version__, workdir), 200, {
            "Content-type": "text/html"}

    app.run(host='0.0.0.0', port=int(params['-p']), debug=False)


# 主程序
def main_function():
    if len(sys.argv) < 2:
        print(show_str)
        quit(0)
    else:
        if sys.argv[1] == "run":
            params = {'-p': "1111", "-b": False, "-n": False}
            abbreviations = {'-p': '--port', '-b': '--browser', '-n': '--nogetip'}
            nindex = 2
            while nindex < len(sys.argv):
                if sys.argv[nindex] == '-p' or sys.argv[nindex] == abbreviations['-p']:
                    nindex += 1
                    params['-p'] = sys.argv[nindex]
                elif sys.argv[nindex] == '-b' or sys.argv[nindex] == abbreviations['-b']:
                    params['-b'] = True
                elif sys.argv[nindex] == '-n' or sys.argv[nindex] == abbreviations['-n']:
                    params['-n'] = True
                else:
                    print('"' + sys.argv[nindex] + '" is not available.')
                nindex += 1
            run(params)
        elif sys.argv[1] == 'version':
            print(__version__)
        elif sys.argv[1] == 'help':
            print(help_str)


if __name__ == "__main__":
    main_function()
