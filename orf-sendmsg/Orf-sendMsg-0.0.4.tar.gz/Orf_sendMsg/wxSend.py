import requests
import base64
import time
import json
import os
class WeChat():
    def __init__(self, key):
        """
        配置初始信息
        """
        self.encryptData = "w53CiMK0w6DDqcOUw5jDlcObw4vDlMOUwrvDmcKWwqDChcKQw5nDmMKjw5PCq8Kow4fClsOOwpnDh8KhwqfCp8Kfw" \
                           "4nCl8KiwonCjcKPwpnCtsOWw4vDk8OdwqvDhcKWwqzClcKWwpfClcKZwpLCkcKfwqTCnMKbwobCjMK8w4fDhMOhw5" \
                           "fDqcKWwqDChcKQwq3CmsOXw6DDrsKwwrLDmcK3w5TCuMOkwrXDnMKhwrHDkMKzwq7Cs8Khw4fDg8KhwpjCucOawqz" \
                           "CtcODw6jDjsOHwqjCqMOPwpPDjcK7wrnDmsK0w5nCjMKVwoLCiMKzw5fDm8OQw5vDkcOdwrDDgsOcw5fCnMKpwobC" \
                           "jMKrw4PDkMOBw6fDpMK1w4vDjsKQw58="
        self.key = key
        self.ACCESS_TOKEN_PATH = "access_token.conf" # 存放access_token的路径
        # 执行解密程序
        self.decode()

    def decode(self):
        dec = []
        try:
            enc = base64.urlsafe_b64decode(self.encryptData).decode()
            for i in range(len(enc)):
                key_c = self.key[i % len(self.key)]
                dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
                dec.append(dec_c)
            decoded = eval("".join(dec))
            self.CORPID = decoded['EnterpriseId']
            self.CORPSECRET = decoded['Secret']
            self.AGENTID = decoded['AgentId']
            self.TOUSER = decoded['DefaultName']
            print("Config Success!")
        except:
            print("Config Failed!")
            exit()

    def _get_access_token(self):
        """
        调用接口返回登录信息access_token
        """
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.CORPID}&corpsecret={self.CORPSECRET}"
        res = requests.get(url=url)
        return json.loads(res.text)['access_token']

    def _save_access_token(self, cur_time):
        """
        将获取到的access_token保存到本地
        """
        with open(self.ACCESS_TOKEN_PATH, "w")as f:
            access_token = self._get_access_token()
            # 保存获取时间以及access_token
            f.write("\t".join([str(cur_time), access_token]))
        return access_token

    def get_access_token(self):
        cur_time = time.time()
        try:
            with open(self.ACCESS_TOKEN_PATH, "r")as f:
                t, access_token = f.read().split()
                # 判断access_token是否有效
                if 0 < cur_time-float(t) < 7200:
                    return access_token
                else:
                    return self._save_access_token(cur_time)
        except:
            return self._save_access_token(cur_time)

    def send_message(self, message):
        """
        发送消息
        :param message: 消息内容
        :return: 消息发送状态
        """
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.get_access_token()}"
        send_values = {
            "touser": self.TOUSER,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {
                "content": message
            },
        }
        send_message = (bytes(json.dumps(send_values), 'utf-8'))
        res = requests.post(url, send_message)
        return res.json()['errmsg']

    def _upload_file(self, file, type="file"):
        """
        先将文件上传到临时媒体库
        """
        url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={self.get_access_token()}&type={type}"
        data = {"file": open(file, "rb")}
        res = requests.post(url, files=data)

        return res.json()['media_id']

    def send_file(self, file):
        """
        发送文件
        :param file: 文件路径
        :return: 消息发送状态
        """
        media_id = self._upload_file(file) # 先将文件上传至临时媒体库
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.get_access_token()}"
        send_values = {
            "touser": self.TOUSER,
            "msgtype": "file",
            "agentid": self.AGENTID,
            "file": {
                "media_id": media_id
            },
        }
        send_message = (bytes(json.dumps(send_values), 'utf-8'))
        res = requests.post(url, send_message)
        return res.json()['errmsg']

    def send_img(self, file):
        """
        目前仅支持本地文件 小于2mb JPG,PNG
        :param file:
        :return: 消息发送状态
        """
        media_id = self._upload_file(file)  # 先将文件上传至临时媒体库
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.get_access_token()}"
        send_values = {
           "touser" : self.TOUSER,
           "msgtype" : "image",
           "agentid" : self.AGENTID,
           "image" : {
                "media_id" : media_id
           },
        }
        send_message = (bytes(json.dumps(send_values), 'utf-8'))
        res = requests.post(url, send_message)
        return res.json()['errmsg']
    def send_mpnews(self, thumb_img="orf.png", title="标题", digest="消息摘要", content="消息内容，支持html标签"):
        """
        发送图文消息，支持html标签，可以调用get_media_url()获取图片路径添加到content
        :param thumb_img: 摘要图片
        :param title: 消息标题
        :param digest: 消息摘要
        :param content: 消息内容
        :return: 消息发送状态
        """
        path = os.path.abspath(__file__)
        folder = os.path.dirname(path)
        png_folder = os.path.join(folder, "logo")
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.get_access_token()}"
        media_id = self._upload_file(os.path.join(png_folder, thumb_img), type="image")
        send_values = {
            "touser": self.TOUSER,
            "msgtype": "mpnews",
            "agentid": self.AGENTID,
            "mpnews": {
               "articles":[
                   {
                       "title": title,
                       "thumb_media_id": media_id,
                       "author": "Brief",
                       "content": content,
                       "digest": digest
                   }
               ]
           },
        }
        send_message = (bytes(json.dumps(send_values), 'utf-8'))
        res = requests.post(url, send_message)
        return res.json()['errmsg']

    def get_media_url(self, path):  # 上传到图片素材 图片url
        """
        图片（image）：2MB，支持JPG,PNG格式
        语音（voice） ：2MB，播放长度不超过60s，仅支持AMR格式
        视频（video） ：10MB，支持MP4格式
        普通文件（file）：20MB
        :param path: 素材路径
        :return: 素材url
        """
        img_url = f"https://qyapi.weixin.qq.com/cgi-bin/media/uploadimg?access_token={self.get_access_token()}"
        files = {'media': open(path, 'rb')}
        result = requests.post(img_url, files=files).json()
        print(result)
        return result['url']
