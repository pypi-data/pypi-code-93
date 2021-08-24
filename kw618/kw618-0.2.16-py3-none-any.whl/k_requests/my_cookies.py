import time
import redis
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# 导入常用的固定路径(多平台通用)
from kw618._file_path import *
# 本脚本依赖很多 utils_requests的函数和模块, 直接用*  (注意要避免循环导入问题)
from kw618.k_requests.utils_requests import *

req = myRequest().req



class PriceSysCookies():
    name = "price_sys_cookies"

    # def __init__(self, user_name="lvzc1", user_passwd="Lzc15168201914*"):
    def __init__(self, user_name="yangjj4", user_passwd="Yangjiajing131#"):
        self.userEmail = user_name
        self.password = user_passwd
        # password = "OnHKU3EzPweR9sxjC42mXw=="
        # password = "OnHKU3EzPwcih0Hr+9bF5g=="
        self.encrypted_password = self.get_encrypted_password()

    def get_encrypted_password(self):
        "获取js加密后的用户密码"
        js_full_path = f"{FILE_PATH_FOR_KW618}/k_requests/js/encryption_4_price_system.js"
        encrypted_password = exec_js_function(js_full_path, "encryptByDES", self.password, "#z@i!r*o%o&m^")
        return encrypted_password


    def get_user_info(self):
        "获取登录后返回的用户信息: 包括名字/部门/职位/电话"
        url = "http://price.ziroom.com/backend/user/getAllInformation"
        data = {
            "userEmail" : self.userEmail,
            "password" : self.encrypted_password,
        }
        res_str = req(url=url, data=data, req_method="post")
        res_dic = json.loads(res_str)
        return res_dic


    def get_cookies(self):
        login_url = "http://price.ziroom.com/backend/user/login"

        password_urlencode = parse.quote(self.encrypted_password) # 进行url 编码
        data = "userEmail={}&password={}".format(self.userEmail, password_urlencode)
        other_headers = {
            "Connection":"keep-alive",
            "content-type":"application/x-www-form-urlencoded; charset=UTF-8;",
        }
        res_txt = req(login_url, req_method="post",
                        data=data, other_headers=other_headers)
        res_json = json.loads(res_txt, strict=False)
        cookies_dict = res_json # 说明是dict类型的cookies
        return cookies_dict



    def get_target_cookie(self):
        cookies_dict = self.get_cookies()
        TOKEN = cookies_dict.get("data", {}).get("accessToken","618")
        print("\n-------------------\n获取到最新的token：{0}\n\n".format(TOKEN))

        if TOKEN:
            return TOKEN
        else:
            return "error"

# token = PriceSysCookies(user_name="zhangh47", user_passwd="Wsxokn@04").get_target_cookie()
# token = PriceSysCookies(user_name="lvzc1", user_passwd="Lzc15168201914!").get_target_cookie()
# print(token)
# sys.exit()




#
# class PriceSysCookiesByS():
#     "千年不用的, 暂时注释, 需要时候再开启"
#     "ByS: 指用Selenium来进行爬取(与requests库的逻辑不一样)"
#     name = "price_sys_cookies_by_selenium"
#
#     def get_cookies(self):
#         try:
#             # browser = webdriver.PhantomJS()
#             browser = webdriver.Chrome()
#
#             browser.get("http://price.ziroom.com/auth.html")
#             username_input = browser.find_element_by_css_selector("#userAccount")
#             username_input.send_keys("lvzc1")
#
#             password_input = browser.find_element_by_css_selector("#password")
#             password_input.send_keys("Lzc15168201914!")
#
#             login_btn = browser.find_element_by_css_selector("#div-login > div > div:nth-child(4) > div > button")
#             login_btn.send_keys(Keys.ENTER)
#
#             wait = WebDriverWait(browser, 50)
#             wait.until(EC.presence_of_element_located((By.CLASS_NAME, "slimScrollDiv")))
#
#             # print(browser.current_url)
#             # 浏览器对象get_cookies()后,获取到的是lst类型,包含的每个dict都包含"name,value,domain,path"等
#             # browser_cookies_lst 为非标准的cookies形式
#             browser_cookies_lst = browser.get_cookies()
#             print(browser_cookies_lst)
#         finally:
#             print("done")
#             browser.close()
#         ## 输出返回的是 "非标准的"cookies
#         return browser_cookies_lst
#
#
#     def get_target_cookie(self):
#         browser_cookies_lst = self.get_cookies()
#         for cookie_dict in browser_cookies_lst:
#             if cookie_dict.get("name", 0) == "accessToken":
#                 TOKEN = cookie_dict.get("value")
#         print("\n-------------------\n获取到最新的token：{0}\n\n".format(TOKEN))
#         if TOKEN:
#             return TOKEN
#         else:
#             return "error"
#
#
#     # browser = webdriver.PhantomJS()
#     # 生成驱动对象是挺耗时的，所以如果要循环获得多个cookies时，不要马上close，等所有都获取完后，再关闭驱动对象！
#
#     # 打开多个浏览器,循环获取cookies  (基本上用不到这个函数...)
#     def browser_loop(self, times):
#         for i in range(times):
#             cookies = get_cookies()
#         return cookies





class NoahSysCookies_v2():

    def __init__(self, user_name, user_passwd):
        self.user_name = user_name
        self.user_passwd = user_passwd
        # self.user_name = "lvzc1"
        # self.user_passwd = "Lzc15168201914*"
        js_full_path = f"{FILE_PATH_FOR_KW618}/k_requests/js/encryption_4_ziroom_intranet.js"
        self.encrypted_password = exec_js_function(js_full_path, "encodeAes", self.user_passwd)
        # self.ziroom_userName = "lvzc1"
        # self.ziroom_token = "9c0b15d0758030f5f64d419eac77fd47"
        self.req_obj = myRequest()
        self.req = self.req_obj.req


    def get_jsessionid(self):
        url = "http://cas.ziroom.com/CAS/login"
        res_obj = self.req(url, is_obj=True, use_session=True)
        res_selector = Selector(text=res_obj.text)
        # 能够实现把cookiejar对象转化为字典
        ### 获取JSESSIONID
        cookies = requests.utils.dict_from_cookiejar(res_obj.cookies)
        print(cookies)
        jsessionid = cookies.get("JSESSIONID", "")
        self.jsessionid = jsessionid
        self.lt = res_selector.xpath('//*[@id="loginForm"]/input[1]/@value').extract_first()
        self.execution = res_selector.xpath('//*[@id="loginForm"]/input[2]/@value').extract_first()
        self._eventId = res_selector.xpath('//*[@id="loginForm"]/input[3]/@value').extract_first()
        return jsessionid


    def get_castgc(self, authCode=""):
        if "jsessionid" not in dir(self):
            self.get_jsessionid()
        jsessionid = self.jsessionid
        url = "http://cas.ziroom.com/CAS/login;jsessionid={}".format(jsessionid)
        other_headers = {
            "Cookie":"JSESSIONID={jsessionid}".format(jsessionid=jsessionid),
            "Content-Length": "148",
            "Cache-Control": "max-age=0",
            "Origin": "http://cas.ziroom.com",
            "Upgrade-Insecure-Requests": "1",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Referer": "http://cas.ziroom.com/CAS/login",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6",
            "Connection": "keep-alive"
            }
        data = "username={}&password={}&authCode={}&lt={}&execution={}&_eventId={}"
        username = self.user_name
        # password = "Vhydw+8N3+dcg5DxFvuwWg==" # 这部分的加密，已经可以用线程的js代码自动加密生成！！（已破解）
        password = parse.quote(self.encrypted_password)
        if not authCode:
            authCode = input("请手动输入动态密码:\n")
        lt = self.lt
        execution = self.execution
        _eventId = self._eventId
        data = data.format(username, password, authCode, lt, execution, _eventId)

        res_obj = self.req(url=url, other_headers=other_headers, data=data, is_obj=True, req_method="post", use_session=True)
        cookies = requests.utils.dict_from_cookiejar(res_obj.cookies)
        print(cookies)
        castgc = cookies.get("CASTGC", "")
        self.castgc = castgc
        return castgc


    def get_new_jsessionid(self):
        url = "http://z.ziroom.com/"
        res_obj = self.req(url=url, is_obj=True, use_session=True)
        cookies = requests.utils.dict_from_cookiejar(res_obj.cookies)
        new_jsessionid = cookies.get("JSESSIONID")
        print("new_jsessionid:", new_jsessionid)
        self.new_jsessionid = new_jsessionid
        return new_jsessionid


    def req_security_index(self):
        url = "http://z.ziroom.com/security/security!index.action"
        other_headers = {"Cookie":"JSESSIONID={}".format(self.new_jsessionid)}

        res_obj = self.req(url=url, is_obj=True, other_headers=other_headers, allow_redirects=False, use_session=True)
        location_l1 = res_obj.headers.get("location", "")
        self.location_l1 = location_l1

        # 2. 开始下一个跳转
        other_headers = {"Cookie":"JSESSIONID={};CASTGC={}".format(self.jsessionid, self.castgc)}
        res_obj = self.req(url=location_l1, is_obj=True, other_headers=other_headers, allow_redirects=False, use_session=True)
        location_l2 = res_obj.headers.get("location", "")
        self.location_l2 = location_l2
        ticket = re.findall(r"ticket=(.*?com)", location_l2)
        ticket = ticket[0] if len(ticket) else ""
        self.ticket = ticket

        # 3. 开始下一个跳转  (使用ticket访问security！index.action)
        other_headers = {
            "Cookie":"JSESSIONID={}".format(self.new_jsessionid),
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "http://z.ziroom.com/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6",
            "Connection": "keep-alive",
        }
        url_l2 = "http://z.ziroom.com/security/security!index.action?ticket={}".format(self.ticket)
        res_obj = self.req(url=url_l2, is_obj=True, other_headers=other_headers, allow_redirects=False, use_session=True)
        location_l3 = res_obj.headers.get("location", "")
        self.location_l3 = location_l3  # 正常来说，这个location又变成了最初的 security!index.action


        # 4. 开始下一个跳转
        other_headers = {"Cookie":"JSESSIONID={}".format(self.new_jsessionid)}
        res_obj = self.req(url=location_l3, is_obj=True, other_headers=other_headers, allow_redirects=False, use_session=True)
        location_l4 = res_obj.headers.get("location", "")
        self.location_l4 = location_l4

        ##  获取其中的ziroom_token
        cookies = requests.utils.dict_from_cookiejar(res_obj.cookies)
        print(cookies)
        ziroom_token = cookies.get("ziroom_token")
        ziroom_userName = cookies.get("ziroom_userName")
        self.ziroom_token = ziroom_token
        self.ziroom_userName = ziroom_userName
        return ziroom_token



    def get_noah_session(self):
        url = "http://noah.ziroom.com/main?sys=inv"
        self.ziroom_userName = self.user_name
        self.ziroom_token = self.ziroom_token
        other_headers = {
            "Cookie":"ziroom_userName={ziroom_userName};ziroom_token={ziroom_token}".format(
            ziroom_userName=self.ziroom_userName, ziroom_token=self.ziroom_token
            )
        }


        res_obj = self.req(url=url, is_obj=True, other_headers=other_headers, allow_redirects=False, use_session=True)
        cookies = requests.utils.dict_from_cookiejar(res_obj.cookies)
        noah_session = cookies.get("SESSION", "")
        print("noah_session:{}".format(noah_session))
        self.noah_session = noah_session
        location_l1 = res_obj.headers.get("location", "")
        self.location_l1 = location_l1

        # 2. 开始下一个跳转
        other_headers = {"Cookie":"JSESSIONID={};CASTGC={};ziroom_userName={};ziroom_token".format(
                            self.jsessionid, self.castgc, self.ziroom_userName, self.ziroom_token)
                        }
        res_obj = self.req(url=location_l1, is_obj=True, other_headers=other_headers, allow_redirects=False, use_session=True)
        location_l2 = res_obj.headers.get("location", "")
        self.location_l2 = location_l2
        noah_ticket = re.findall(r"ticket=(.*?com)", location_l2)
        noah_ticket = noah_ticket[0] if len(noah_ticket) else ""
        self.noah_ticket = noah_ticket

        # 3. 开始下一个跳转  (使用ticket访问noah.ziroom.com)
        other_headers = {
            "Cookie":"ziroom_userName={};ziroom_token={};SESSION={}".format(
                self.ziroom_userName, self.ziroom_token, self.noah_session),
        }
        url_l2 = "http://noah.ziroom.com/main?sys=inv&ticket={}".format(self.noah_ticket)
        res_obj = self.req(url=url_l2, is_obj=True, other_headers=other_headers, allow_redirects=False, use_session=True)
        location_l3 = res_obj.headers.get("location", "")
        self.location_l3 = location_l3  # 正常来说，这个location又变成了最初的 http://noah.ziroom.com/main?sys=inv


        # 4. 开始下一个跳转
        ### other_headers 沿用上面的headers
        res_obj = self.req(url=location_l3, is_obj=True, other_headers=other_headers, allow_redirects=False, use_session=True)
        location_l4 = res_obj.headers.get("location", "")
        cookies = requests.utils.dict_from_cookiejar(res_obj.cookies)
        noah_id = cookies.get("noah_id")
        self.noah_id = noah_id

        return noah_session


    # 主要的获取流程
    def run(self, authCode=""):
        # 0. 先获取redis的连接对象
        r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

        if not authCode:
            authCode = input("请您输入内网验证码：")
        self.get_castgc(authCode=authCode)
        self.get_new_jsessionid()
        self.req_security_index()
        noah_session = self.get_noah_session()
        r.set("noah_session", noah_session)
        # 设置30分钟过期时间
        r.expire("noah_session", 1800)
        return noah_session
# o = NoahSysCookies_v2()
# o.run(authCode="222590")
# sys.exit()


#
# class NoahSysCookies():
#     "上面已经有第二个版本的实现了, 弃之, 待删"
#
#     def __init__(self):
#         self.ziroom_userName = "lvzc1"
#         self.ziroom_token = "9c0b15d0758030f5f64d419eac77fd47"
#
#     def get_jsessionid(self):
#         url = "http://cas.ziroom.com/CAS/login"
#         res_obj = req(url, is_obj=True)
#         res_selector = Selector(text=res_obj.text)
#         # 能够实现把cookiejar对象转化为字典
#         ### 获取JSESSIONID
#         cookies = requests.utils.dict_from_cookiejar(res_obj.cookies)
#         print(cookies)
#         jsessionid = cookies.get("JSESSIONID", "")
#         self.jsessionid = jsessionid
#         self.lt = res_selector.xpath('//*[@id="loginForm"]/input[1]/@value').extract_first()
#         self.execution = res_selector.xpath('//*[@id="loginForm"]/input[2]/@value').extract_first()
#         self._eventId = res_selector.xpath('//*[@id="loginForm"]/input[3]/@value').extract_first()
#         return jsessionid
#
#
#     def get_castgc(self, authCode=""):
#         if "jsessionid" not in dir(self):
#             self.get_jsessionid()
#         jsessionid = self.jsessionid
#         url = "http://cas.ziroom.com/CAS/login"
#         other_headers = {
#             "Cookie":"JSESSIONID={jsessionid}".format(jsessionid=jsessionid),
#             "Content-Length": "148",
#             "Cache-Control": "max-age=0",
#             "Origin": "http://cas.ziroom.com",
#             "Upgrade-Insecure-Requests": "1",
#             "Content-Type": "application/x-www-form-urlencoded",
#             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
#             "Referer": "http://cas.ziroom.com/CAS/login",
#             "Accept-Encoding": "gzip, deflate",
#             "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6",
#             "Connection": "keep-alive"
#             }
#         data = "username={}&password={}&authCode={}&lt={}&execution={}&_eventId={}"
#         username = "lvzc1"
#         password = "Vhydw+8N3+dcg5DxFvuwWg==" # 这部分的加密，已经可以用线程的js代码自动加密生成！！（已破解）
#         password = parse.quote(password)
#         if not authCode:
#             authCode = input("请手动输入动态密码:\n")
#         lt = self.lt
#         execution = self.execution
#         _eventId = self._eventId
#         data = data.format(username, password, authCode, lt, execution, _eventId)
#
#         res_obj = req(url=url, other_headers=other_headers, data=data, is_obj=True, req_method="post")
#         cookies = requests.utils.dict_from_cookiejar(res_obj.cookies)
#         print(cookies)
#         castgc = cookies.get("CASTGC", "")
#         self.castgc = castgc
#         return castgc
#
#
#
#     def get_unverified_session(self):
#         url = "http://noah.ziroom.com/main?sys=inv"
#         # self.ziroom_userName = "lvzc1"
#         # self.ziroom_token = "9b8199276caa50c1528a1d53d170e0b1"
#         other_headers = {
#             "Cookie":"ziroom_userName={ziroom_userName};ziroom_token={ziroom_token}".format(
#             ziroom_userName=self.ziroom_userName, ziroom_token=self.ziroom_token
#             )
#         }
#         res_obj = req(url=url, is_obj=True, other_headers=other_headers, allow_redirects=False)
#         cookies = requests.utils.dict_from_cookiejar(res_obj.cookies)
#         unverified_session = cookies.get("SESSION", "")
#         print("unverified_session:{}".format(unverified_session))
#         self.unverified_session = unverified_session
#
#         # 上面的allow_redirects参数设为False后，下面需要手动跳转到location的地址
#         location_l1 = res_obj.headers.get("location", "")
#         self.location_l1 = location_l1
#         print(location_l1)
#         return unverified_session
#
#
#
#
#     # 实际上就是获取那个location_l2即可！！（ticket是locaiton中的一个参数）
#     def get_ticket(self, authCode=""):
#         if "castgc" not in dir(self):
#             self.get_castgc(authCode=authCode)
#         if "unverified_session" not in dir(self):
#             self.get_unverified_session()
#         url = self.location_l1
#         other_headers = {
#             "Cookie":"JSESSIONID={jsessionid};CASTGC={castgc};ziroom_userName={ziroom_userName};ziroom_token={ziroom_token}".format(
#             jsessionid=self.jsessionid, castgc=self.castgc, ziroom_userName=self.ziroom_userName, ziroom_token=self.ziroom_token
#             )
#         }
#         res_obj = req(url=url, is_obj=True, other_headers=other_headers, allow_redirects=False)
#         cookies = requests.utils.dict_from_cookiejar(res_obj.cookies)
#         # 上面的allow_redirects参数设为False后，下面需要手动跳转到location_l2的地址
#         location_l2 = res_obj.headers.get("location", "")
#         print(location_l2)
#         ticket = re.findall(r"ticket=(.*?com)", location_l2)
#         ticket = ticket[0] if len(ticket) else ""
#         # print(ticket)
#         self.location_l2 = location_l2
#         self.ticket = ticket
#         return ticket
#
#
#     def get_verified_session(self, authCode=""):
#         if "location_l2" not in dir(self):
#             self.get_ticket(authCode=authCode)
#         if "unverified_session" not in dir(self):
#             self.get_unverified_session()
#         location_l2 = self.location_l2
#         url = location_l2
#         other_headers = {
#             "Cookie":"SESSION={session};ziroom_userName={ziroom_userName};ziroom_token={ziroom_token}".format(
#             session=self.unverified_session, ziroom_userName=self.ziroom_userName, ziroom_token=self.ziroom_token
#             )
#         }
#         res_obj = req(url, is_obj=True, allow_redirects=False, other_headers=other_headers)
#         # cookies = requests.utils.dict_from_cookiejar(res_obj.cookies)
#         # verified_session = cookies.get("SESSION")
#         # self.verified_session = verified_session
#
#         verified_session = self.unverified_session
#         print("SESSION:{}".format(verified_session))
#         return verified_session








def main():

    # cookies_1 = PriceSysCookiesByS().get_target_cookie()
    # print("cookies_1:\n{0}\n\n".format(cookies_1))

    cookies_2 = PriceSysCookies().get_target_cookie()
    print("cookies_2:\n{0}\n\n".format(cookies_2))



if __name__ == '__main__':
    print("start!")
    main()
    print("end!")
