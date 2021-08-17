#-*- coding: utf-8 -*-

import time
import hashlib
import base64
import json
# from qcloud_cos import CosConfig
# from qcloud_cos import CosS3Client
# from random import choice
import requests


class Qa(object):
    URL = "http://openapi.xfyun.cn/v2/aiui"
    AUE = "raw"
    AUTH_ID = "559f3654871292b240a4eac4b445ce4d"
    URL = "http://openapi.xfyun.cn/v2/aiui"
    AUE = "raw"
    DATA_TYPE = "text" # 明确处理类型 text文本/audio音频
    SAMPLE_RATE = "16000"
    SCENE = "main" # 情景值
    RESULT_LEVEL = "complete"
    LAT = "23.16" # 纬度
    LNG = "113.23" # 经度
    #个性化参数，需转义
    PERS_PARAM = "{\\\"auth_id\\\":\\\"2894c985bf8b1111c6728db79d3479ae\\\"}"
    FILE_PATH = "test.py.txt" # 如需要从文本中读取,填写文本文件地址,每行为一个输入

    def __init__(self):
        # secret_id = "AKIDqTt43ryimaDbkrOgFZgYBj2EBsKdbcFf"
        # secret_key = "Qef6IGAyaHqFRaaN1QVTHvOceU8ZvCE4"
        # region = 'ap-hongkong'
        # token = None
        # scheme = 'https'
        # prefix = "kdxfsdk/license/qa"
        # bucket = "lmxia-1253647560"
        #
        # config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
        # client = CosS3Client(config)
        # response = client.list_objects(Bucket=bucket, Prefix=prefix)
        # objs = [obj for obj in response['Contents'] if str(obj.get("Size", '0')) != '0']
        # iat_item = choice(objs)
        # license_key = iat_item.get("Key", "kdxfsdk/license/qa/lmxia.config")
        # spec_obj = client.get_object(
        #     Bucket=bucket,
        #     Key=license_key,
        # )
        # fp = spec_obj['Body'].get_raw_stream().read()
        # license_obj = json.loads(fp)
        # self.APP_ID = license_obj.get("APPID")
        # self.API_KEY = license_obj.get("APIKey")
        self.APP_ID = "5cc5623f"
        self.API_KEY = "7e82cb5de9a79bd50be1a925995c7d37"

    def buildHeader(self):
        curTime = str(int(time.time()))
        param = "{\"result_level\":\""+self.RESULT_LEVEL+"\",\"auth_id\":\""+self.AUTH_ID+"\",\"data_type\":\""+self.DATA_TYPE+"\",\"sample_rate\":\""+self.SAMPLE_RATE+"\",\"scene\":\""+self.SCENE+"\",\"lat\":\""+self.LAT+"\",\"lng\":\""+self.LNG+"\"}"
        paramBase64 = base64.b64encode(param.encode('utf-8'))

        m2 = hashlib.md5()
        m2.update((self.API_KEY + curTime + str(paramBase64, 'utf-8')).encode('utf-8'))
        checkSum = m2.hexdigest()

        # 在 Http Request Header 中配置以下参数用于授权认证
        header = {
            'X-CurTime': curTime,
            'X-Param': paramBase64,
            'X-Appid': self.APP_ID,
            'X-CheckSum': checkSum,
        }
        return header

    def readFile(self, filePath):
        binfile = open(filePath, 'rb')
        data = binfile.read()
        print('data in file:', data)
        return data

    def request2aiui(self, text):
        bintext = str.encode(text)
        r = requests.post(self.URL, headers=self.buildHeader(), data=bintext)
        content = r.content
        json_resp = json.loads(content.decode('utf-8'))
        code = json_resp['code']
        if code == '0':
            return json_resp['data'][0]['intent']['answer'].get('text')
        else:
            raise Exception(json_resp)


if __name__ == "__main__":
    try:
        test_text = u'今天的天气怎么样'
        qa = Qa()
        resp = qa.request2aiui(test_text)
        print(resp)
    except Exception as e:
        print(e.args)
