# -*- coding:utf-8 -*-
import requests
import time
import hashlib
import base64
# from qcloud_cos import CosConfig
# from qcloud_cos import CosS3Client
# from random import choice
import json
import linecache


class Image(object):
    def __init__(self):
        # secret_id = "AKIDqTt43ryimaDbkrOgFZgYBj2EBsKdbcFf"
        # secret_key = "Qef6IGAyaHqFRaaN1QVTHvOceU8ZvCE4"
        # region = 'ap-hongkong'
        # token = None
        # scheme = 'https'
        # prefix = "kdxfsdk/license/image"
        # bucket = "lmxia-1253647560"
        #
        # config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
        # client = CosS3Client(config)
        # response = client.list_objects(Bucket=bucket, Prefix=prefix)
        # objs = [obj for obj in response['Contents'] if str(obj.get("Size", '0')) != '0']
        # iat_item = choice(objs)
        # license_key = iat_item.get("Key", "kdxfsdk/license/iat/lmxia.config")
        # spec_obj = client.get_object(
        #     Bucket=bucket,
        #     Key=license_key,
        # )
        # fp = spec_obj['Body'].get_raw_stream().read()
        # license_obj = json.loads(fp)
        # self.APPID = license_obj.get("APPID")
        # self.APIKey = license_obj.get("APIKey")
        # self.APISecret = license_obj.get("APISecret")
        self.APPID = "5cc5623f"
        self.APIKey = "317aff16cd10deab8aabf24d251c2d6a"
        # self.APISecret = license_obj.get("APISecret")

    def getHeader(self, image_name, image_url=""):
        curTime = str(int(time.time()))
        param = "{\"image_name\":\"" + image_name + "\",\"image_url\":\"" + image_url + "\"}"
        paramBase64 = base64.b64encode(param.encode('utf-8'))
        tmp = str(paramBase64, 'utf-8')
        m2 = hashlib.md5()
        m2.update((self.APIKey + curTime + tmp).encode('utf-8'))
        checkSum = m2.hexdigest()

        header = {
            'X-CurTime': curTime,
            'X-Param':  paramBase64,
            'X-Appid': self.APPID,
            'X-CheckSum': checkSum,
        }
        return header

    def getBody(self, file_path="tmp.jpg"):
        binfile = open(file_path, 'rb')
        data = binfile.read()
        return data

    def recognise(self, file_path="tmp.jpg"):
        URL = "http://tupapi.xfyun.cn/v1/currency"
        r = requests.post(URL, headers=self.getHeader(file_path), data=self.getBody(file_path))
        json_resp = json.loads(r.content.decode('utf-8'))
        label = json_resp.get('data').get("fileList")[0]['label']
        return linecache.getline("/home/pi/ai_config/code-map", label + 1).split()[2]


if __name__ == "__main__":
    image = Image()
    print(image.recognise())
