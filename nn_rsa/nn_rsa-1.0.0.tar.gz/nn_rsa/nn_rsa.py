import rsa
import base64
import os
from rsa import common


class NnRsa:

    def __check_rsa_key(self, key: str, public_tag=True):
        func = rsa.PublicKey.load_pkcs1 if public_tag else rsa.PrivateKey.load_pkcs1
        try:
            obj = func(key.encode())
        except:
            raise Exception("公钥/私钥解析出错！")
        return obj

    def __init__(self, public_key: str = None, private_key: str = None):
        '''加密需要传公钥，解密需要传私钥'''
        self.public_key_obj = self.__check_rsa_key(public_key) if public_key else None
        self.private_key_obj = self.__check_rsa_key(private_key, False) if private_key else None

    def get_max_message_len(self, decrypt=False):
        # 计算加密/解密的最大长度
        # 消息加密/解密的时候消息如果超过最大长度，解密/加密的时候需要一块一块解密/加密

        reserve_size = 0 if decrypt else 11  # 如果是加密的话，有一个预留的长度，是11，如果是解密，就没有预留长度
        rsa_key = self.private_key_obj.n if decrypt else self.public_key_obj.n
        # private_key_obj.n 是私钥的最大消息长度，public_key_obj.n是公钥最大的消息长度
        return common.byte_size(rsa_key) - reserve_size  # 最大长度为消息最大长度 - 预留长度

    def encrypt(self, message: str):
        '''公钥加密，传入需要加密的字符串'''
        if self.public_key_obj == None:
            raise Exception("加密时，公钥不能为空！")
        print("加密前字符串:{}".format(message))
        max_message_len = self.get_max_message_len()  # 获取最大长度
        result_message = bytes()  # rsa加密完的数据是bytes类型的
        while message:  # 消息不为空的时候循环
            _message = message[:max_message_len]  # 从开头取到最大的消息长度
            message = message[max_message_len:]  # 从取完的下标往后取
            result_message += rsa.encrypt(_message.encode(), self.public_key_obj)  # 加密一块，累加到reuslt里面
        b64_msg = base64.b64encode(result_message).decode()  # 加密后的是bytes类型的，不是一个字符串，转成base64的
        print("加密后字符串:{}".format(b64_msg))
        return b64_msg

    def decrypt(self, message: str):
        '''私钥解密，传入加密后的字符串'''
        if self.private_key_obj == None:
            raise Exception("解密时，私钥不能为空！")
        print("解密前的字符串:{}".format(message))
        max_message_len = self.get_max_message_len(True)  # 获取最大长度
        decrypt_message = ""
        try:
            message = base64.b64decode(message)  # 加密之后，字符串是base64过的，base64解密一下
            while message:
                _message = message[:max_message_len]  # 从开头取到最大的消息长度
                message = message[max_message_len:]  # 从取完的下标往后取
                decrypt_message += rsa.decrypt(_message, self.private_key_obj).decode()
                # 加密后的是bytes类型的，不是一个字符串，转成字符串，累加
        except:
            print("解密出错，请检查密文是否有误")
            return False
        print("解密成功，解密后的字符串：{}".format(decrypt_message))
        return decrypt_message

    @staticmethod
    def create_key(size=1024, file_name_prefix: str = None):
        if file_name_prefix:
            public_key_file_name = file_name_prefix + "_public_key.pem"
            private_key_file_name = file_name_prefix + "_private_key.pem"
            if os.path.exists(public_key_file_name) or os.path.exists(private_key_file_name):
                ok = input("公钥/私钥文件已经存在，是否需要覆盖，输入1覆盖，输入其他取消生成:").strip()
                if ok != "1":
                    return

        public_key_obj, private_key_obj = rsa.newkeys(size)
        public_key = public_key_obj.save_pkcs1()
        private_key = private_key_obj.save_pkcs1()

        if file_name_prefix == None:
            print("public_key:\n", public_key.decode())
            print("private_key:\n", private_key.decode())
            return

        with open(public_key_file_name, 'wb') as f1, open(private_key_file_name, 'wb') as f2:
            f1.write(public_key)
            f2.write(private_key)
        print("public_key_file:", public_key_file_name)
        print("private_key:", private_key_file_name)

