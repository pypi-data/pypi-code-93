from .__rsa__ import keyGen, encrypt, decrypt
import uuid
import json
import time


class DB:
    @staticmethod
    def dump_platforms(data, path="./"):
        with open(f"{path}file_platforms.json", "w") as f:
            # print("\t", data)
            json.dump(data, f, ensure_ascii=False)

    @staticmethod
    def dump_users(data, path="./"):
        with open(f"{path}file_user.json", "w") as f:
            json.dump(data, f, ensure_ascii=False)

    @staticmethod
    def load_platforms(path="./"):
        try:
            with open(f"{path}file_platforms.json", "r") as f:
                return json.load(f)
        except Exception as e:
            return {}

    @staticmethod
    def load_users(path="./"):
        try:
            with open(f"{path}file_user.json", "r") as f:
                return json.load(f)
        except Exception as e:
            return {}


class DecryptITF:
    @staticmethod
    def decrypt(*args, **kwargs):
        return decrypt(*args, **kwargs)


class SimpleMemberSystem:
    def __init__(self, db_file_path="./", uuid_core="9b542d3a-c4d6-45ea-9408-783dca9e5f2b"):
        self.db_file_path = db_file_path
        self.local_db_label_and_rsa_keys = DB.load_platforms()
        self.local_db_account_and_uuid = DB.load_users()
        self.salt_func = uuid.uuid5
        self.salt_func_namespace = uuid.UUID(uuid_core)

    def signup_platform(self, label=None):
        label = str(uuid.uuid4()) if label is None else label
        encode_key, decode_key = keyGen()
        encode_key, decode_key = [int(i) for i in encode_key], [int(i) for i in decode_key]

        self.__set_db_label_and_rsa_key__(label, encode_key, decode_key)
        return decode_key, label

    def signup_user(self, account, pws):
        account, pws = self.__hash_login_info__(account, pws)
        self.__set_db_account_and_uuid__(account, pws)

    def login_user(self, label, account, pws):
        account, pws = self.__hash_login_info__(account, pws)
        return self.__get_db_account_and_uuid__(label, account, pws)

    def update_user(self, account, pws, **kwargs):
        account, pws = self.__hash_login_info__(account, pws)
        self.__set_db_user_info__(account=account, pws=pws, **kwargs)

    def delete_user(self, account, pws):
        account, pws = self.__hash_login_info__(account, pws)
        self.__del_db_account_and_uuid(account=account, pws=pws)

    ##
    def __hash_login_info__(self, account, pws):
        return str(self.salt_func(self.salt_func_namespace, account)), str(
            self.salt_func(self.salt_func_namespace, pws))

    def __set_db_label_and_rsa_key__(self, label, encode_key, decode_key):
        if label in self.local_db_label_and_rsa_keys:
            raise RuntimeError(f"the label is exist.: {label}")
        self.local_db_label_and_rsa_keys[label] = {
            "encode_key": encode_key,
            "decode_key": decode_key
        }

        #
        DB.dump_platforms(self.local_db_label_and_rsa_keys, self.db_file_path)

    def __get_db_label_and_rsa_key__(self, label):
        return self.local_db_label_and_rsa_keys[label].copy() if label in self.local_db_label_and_rsa_keys else None

    def __set_db_account_and_uuid__(self, account, pws):
        # print(f"local_db_account_and_uuid: {self.local_db_account_and_uuid.keys()}")
        # print(f"account: {account}")
        if account in self.local_db_account_and_uuid:
            raise RuntimeError(f"the account is exist.: {account}")
        self.local_db_account_and_uuid[account] = {
            "pws": pws,
            "uuid": str(uuid.uuid4())
        }

        #
        DB.dump_users(self.local_db_account_and_uuid, self.db_file_path)

    def __set_db_user_info__(self, account, pws, **kwargs):
        source_info = self.__get_db_account_and_uuid__(label=None, account=account, pws=pws, encode=False)
        source_info.update(kwargs)
        self.local_db_account_and_uuid[account] = source_info

        #
        DB.dump_users(self.local_db_account_and_uuid, self.db_file_path)

    def __set_db_account_info__(self, account, pws):
        self.local_db_account_and_uuid[account] = {
            "pws": pws,
            "uuid": str(uuid.uuid4())
        }

    def __get_db_account_and_uuid__(self, label, account, pws, encode=True):
        if account not in self.local_db_account_and_uuid:
            raise RuntimeError(f"the account is not exist.: {account}")
        user = (self.local_db_account_and_uuid[account]).copy() if account in self.local_db_account_and_uuid and \
                                                                   self.local_db_account_and_uuid[account][
                                                                       'pws'] == pws else None

        #
        if encode:
            rsa_key = self.__get_db_label_and_rsa_key__(label)
            if rsa_key is None:
                raise RuntimeError(f"the label is not exist.: {label}")
            del user['pws']
            return encrypt(rsa_key['encode_key'], json.dumps(user))
        else:
            return user

    def __del_db_account_and_uuid(self, account, pws):
        if account not in self.local_db_account_and_uuid:
            raise RuntimeError(f"the account is not exist.: {account}")
        user = (self.local_db_account_and_uuid[account]).copy() if account in self.local_db_account_and_uuid and \
                                                                   self.local_db_account_and_uuid[account][
                                                                       'pws'] == pws else None
        if user is None:
            raise RuntimeError(f"the pws is not error.: {account}")

        del self.local_db_account_and_uuid[account]
        #
        DB.dump_users(self.local_db_account_and_uuid, self.db_file_path)

# # 啟動系統
# itf = SimpleMemberSystem()
#
# # 註冊平台
# decode_key, label = itf.signup_platform()
#
# # 註冊會員
# account = "root"
# pws = "root"
# try:
#     itf.signup_user(account, pws)
# except RuntimeError as e:
#     pass
#
# for idx in range(3):
#     if idx > 0:
#         data = {
#             "var1": idx,
#             "var2": idx,
#             "var3": idx,
#         }
#         print("\t", idx, data)
#         itf.update_user(account, pws, **data)
#
#     # 會員登入
#     encode_text = itf.login_user(label, "root", "root")
#     print(f"會員登入： encode_text:{encode_text}")
#
#     # 解析會員資料
#     decode_text = DecryptITF.decrypt(decode_key, encode_text)
#     print(f"解析會員資料： decode_text:{decode_text}")
