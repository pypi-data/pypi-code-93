import time
import json
import redis
from kw618.k_requests.utils_requests import myRequest
from kw618.k_requests.my_cookies import PriceSysCookies

# 导入必要变量
    ## 1. redis
r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
    ## 2. requests
req = myRequest().req


class RobustZiru():
    def __init__(self, user_name="lvzc1", user_passwd="Lzc15168201914*", AccessToken=""):
        """
            坑点:
                1. 使用该类的req方法访问ziru系统时, 第一次不会用到 user_name/user_passwd
                2. 这里的 user_name/user_passwd, 只有在第二次req请求时候才会被用到

        """
        self.user_name = user_name
        self.user_passwd = user_passwd
        self.AccessToken = AccessToken



    def req(self, url, req_method="get", data=None, other_headers={}):
        """
        此函数是在req的基础上做了定制化处理,
        考虑到多种可能的返回值,分流处理,稳定地得到最终需要的数据.

        function:
            - 专门针对自如价格相关系统的 robust_req
            - 情况1: 如果token仍然有效, 直接正常访问
            - 情况2: 当访问失败时(token过期), 会自动重新生成token, 并更新到本地redis缓存中

        更新日期: 2020-07-07
        """
        for retry_time in range(1, 4):
            try:
                # 1.获取token
                # (二者选其一, 一旦token无效, 就使用账号密码重新生成token)
                if self.AccessToken:
                    # token获取方式1: 直接传入
                    # 一定要给一个正确的token  (web上, 最好是直接给我一个能用的/有效的token)
                    token = self.AccessToken
                else:
                    # token获取方式2: 从redis中取出"已存在的token"
                    token = r.get("price_system:AccessToken")
                headers = {
                    "Access-Token":token,
                }
                other_headers.update(headers)
                # 2.发起req
                res_txt = req(url, other_headers=other_headers, req_method=req_method, data=data)
                res_json = json.loads(res_txt, strict=False)
                # 3.如果验证失败，重新获取cookies
                    # 40002:token过期;     40017:无数据权限;
                if res_json.get("code", 0) == "40002" or res_json.get("code", 0) == "40017":
                    print("token验证失败，使用post模拟登陆，获取cookies....")
                    # token获取方式3: 使用账号密码, 重新生成
                    token = PriceSysCookies(user_name=self.user_name, user_passwd=self.user_passwd).get_target_cookie()
                    r.set("price_system:AccessToken", token)
                    r.expire("price_system:AccessToken", 1800)
                    print("\n最新token:{}\n".format(token))
                    other_headers = {
                        "Access-Token":token,
                    }
                    res_txt = req(url, other_headers=other_headers, req_method=req_method, data=data)
                    res_json = json.loads(res_txt, strict=False)
                # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> (以上是关于cookies的验证)

                # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> (以下是关于response的分流处理)
                # 1..如果获取到的code字段=40001,说明 post方法缺少必要参数
                if res_json.get("code", 0) == "40001":
                    return {}, "miss" # post方法缺少必要参数
                # 2.如果获取到的status字段=5,说明发生其他问题,待处理
                elif res_json.get("status", 0) == "5": #此处占坑,作为其他错误response的捕获#
                    return {}, "failure"
                # 3.如果以上错误response都没捕获到,说明response正常,返回该正常的response
                else:
                    return res_json, "success" #"被期望"的正常情况#

            except Exception as e:
                print(e)
                ## 服务器确实只返回这样的数据,可能是被反爬了,也可能是发送给服务器的数据有问题
                ## (大概率是被反爬了:1.ip被封;2.cookies过期;3.headers/query缺失等)
                ## 需要在上面代码块重新调整"返回值的判断逻辑"!!
                print("response 非目标对象, 可能被反爬!")
                print("马上进行第 {} 次req重试\n[睡眠3秒]".format(retry_time))
                time.sleep(3)
                continue
            return {}, "error"



# 待删: 已经用"类"的形式实现了!
# def robust_req_ziru(url, req_method="get", data=None, other_headers={}, AccessToken=""):
#     """
#     此函数是在req的基础上做了定制化处理,
#     考虑到多种可能的返回值,分流处理,稳定地得到最终需要的数据.
#
#     function:
#         - 专门针对自如价格相关系统的 robust_req
#         - 情况1: 如果token仍然有效, 直接正常访问
#         - 情况2: 当访问失败时(token过期), 会自动重新生成token, 并更新到本地redis缓存中
#
#     更新日期: 2020-07-07
#     """
#     for retry_time in range(1, 4):
#         try:
#             # 1.获取token
#             if AccessToken:
#                 # 一定要给一个正确的token
#                 token = AccessToken
#             else:
#                 # 从redis中取出"已存在的token"
#                 token = r.get("price_system:AccessToken")
#             headers = {
#                 "Access-Token":token,
#             }
#             other_headers.update(headers)
#             # 2.发起req
#             res_txt = req(url, other_headers=other_headers, req_method=req_method, data=data)
#             res_json = json.loads(res_txt, strict=False)
#             # 3.如果验证失败，重新获取cookies
#             if res_json.get("code", 0) == "40002":
#                 print("token验证失败，使用post模拟登陆，获取cookies....")
#                 token = PriceSysCookies(user_name=user_name, user_passwd=user_passwd).get_target_cookie()
#                 r.set("price_system:AccessToken", token)
#                 r.expire("price_system:AccessToken", 1800)
#                 print("\n最新token:{}\n".format(token))
#                 other_headers = {
#                     "Access-Token":token,
#                 }
#                 res_txt = req(url, other_headers=other_headers, req_method=req_method, data=data)
#                 res_json = json.loads(res_txt, strict=False)
#             # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> (以上是关于cookies的验证)
#
#             # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> (以下是关于response的分流处理)
#             # 1..如果获取到的code字段=40001,说明 post方法缺少必要参数
#             if res_json.get("code", 0) == "40001":
#                 return {}, "miss" # post方法缺少必要参数
#             # 2.如果获取到的status字段=5,说明发生其他问题,待处理
#             elif res_json.get("status", 0) == "5": #此处占坑,作为其他错误response的捕获#
#                 return {}, "failure"
#             # 3.如果以上错误response都没捕获到,说明response正常,返回该正常的response
#             else:
#                 return res_json, "success" #"被期望"的正常情况#
#
#         except Exception as e:
#             print(e)
#             ## 服务器确实只返回这样的数据,可能是被反爬了,也可能是发送给服务器的数据有问题
#             ## (大概率是被反爬了:1.ip被封;2.cookies过期;3.headers/query缺失等)
#             ## 需要在上面代码块重新调整"返回值的判断逻辑"!!
#             print("response 非目标对象, 可能被反爬!")
#             print("马上进行第 {} 次req重试\n[睡眠3秒]".format(retry_time))
#             time.sleep(3)
#             continue
#         return {}, "error"


def test():
    # 测试: robust_req_ziru() 函数
    url = "http://price.ziroom.com/backend/adjustprice/getApprovalDedail?id=505180037330304"
    res_dict, my_status = robust_req_ziru(url)
    print(res_dict, my_status)







if __name__ == '__main__':
    print("start test!")
    test()
    print("\n\n\neverything is ok!")
