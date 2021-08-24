import hashlib
import os
import time

from cryptography.fernet import Fernet
from notedrive.tables import SqliteTable
from notetool.tool.log import log

local_secret_path = '~/.secret'
logger = log('tool')


def set_secret_path(path):
    global local_secret_path
    local_secret_path = path


def get_file_md5(path, chunk=1024 * 4):
    m = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            data = f.read(chunk)
            if not data:
                break
            m.update(data)

    return m.hexdigest()


class SecretManage(SqliteTable):
    def __init__(self, secret_dir=None, cipher_key=None, *args, **kwargs):
        """
        初始化
        :param secret_dir:数据的保存路径
        :param cipher_key: 加密的秘钥，当需要对数据进行加密解密时，这个字段不能为空
        :param args: 其他参数，父类(SqliteTable)所需要的参数
        :param kwargs:其他参数，父类(SqliteTable)所需要的参数
        """
        secret_dir = secret_dir or local_secret_path
        secret_dir = secret_dir.replace("~", os.environ['HOME'])
        secret_path = '{}/.secret_v2.db'.format(secret_dir)

        super(SecretManage, self).__init__(
            secret_path, table_name='secret', *args, **kwargs)
        self.columns = ['secret_key', 'cate1', 'cate2',
                        'cate3', 'cate4', 'cate5', 'value', 'expire_time']
        self.cipher_key = cipher_key
        self.create()

    def create(self):
        self.execute("""
                        create table if not exists {} (
                            secret_key            varchar(300)   primary key
                           ,cate1                 varchar(150)   DEFAULT ''
                           ,cate2                 varchar(150)   DEFAULT ''
                           ,cate3                 varchar(150)   DEFAULT ''
                           ,cate4                 varchar(150)   DEFAULT ''
                           ,cate5                 varchar(150)   DEFAULT ''                                 
                           ,value                 varchar(1000)  DEFAULT ''
                           ,expire_time           int            DEFAULT 8888888888
                           )
                        """.format(self.table_name))

    def encrypt(self, text):
        """
        加密，我也没测试过，不知道能不能正常使用，纯字母的应该没问题，中文的待商榷
        :param text: 需要加密的文本
        :return: 加密后的文本
        """
        if self.cipher_key is None:
            return text
        cipher = Fernet(bytes(self.cipher_key, encoding="utf8"))
        encrypted_text = cipher.encrypt(text.encode())
        return encrypted_text

    def decrypt(self, encrypted_text):
        """
        解密，我也没测试过，不知道能不能正常使用，纯字母的应该没问题，中文的待商榷
        :param encrypted_text: 需要解密的文本
        :return:解密后的文本
        """
        if self.cipher_key is None:
            return encrypted_text
        cipher = Fernet(bytes(self.cipher_key, encoding="utf8"))
        decrypted_text = cipher.decrypt(encrypted_text)
        return decrypted_text.decode()

    def read(self, cate1, cate2=None, cate3=None, cate4=None, cate5=None, value=None, save=True, secret=False,
             expire_time=None):
        """
        按照分类读取保存的key，如果为空或者已过期，则返回None
        :param cate1: cate1
        :param cate2: cate2
        :param cate3: cate3
        :param cate4: cate4
        :param cate5: cate5
        :param value: 保存的数据
        :param save: 是否需要保存，保存的话，会覆盖当前保存的数据
        :param secret: 是否需要加密，如果加密的话，构造类的时候，cipher_key不能为空，这是加密解密的秘钥
        :param expire_time: 过期时间，unix时间戳，如果小于10000000的话，会当做保存数据的持续时间，加上当前的Unix时间戳作为过期时间
        :return: 保存的数据
        """
        if expire_time is not None and expire_time < 1000000000:
            expire_time += int(time.time())
        if save:
            self.write(value, cate1, cate2, cate3, cate4, cate5, secret=secret, expire_time=expire_time)
        if value is not None:
            return value

        properties = {"cate1": cate1, "cate2": cate2, "cate3": cate3, "cate4": cate4, "cate5": cate5}
        sql = f"select * from table_name where {' and '.join(self._condition2equal(properties))}"
        results = self.select(sql)

        for res in results:
            value, expire_time = res['value'], res['expire_time']
            if secret:
                value = self.decrypt(value)

            if expire_time is None or expire_time == 'None' or int(time.time()) < expire_time:
                return value
        return None

    def write(self, value, cate1, cate2=None, cate3=None, cate4=None, cate5=None, secret=False, expire_time=None):
        """
        对数据进行保存
        :param value: 保存的数据
        :param cate1:cate1
        :param cate2:cate2
        :param cate3:cate3
        :param cate4:cate4
        :param cate5:cate5
        :param secret: 是否需要加密
        :param expire_time:过期时间，默认不过期
        """
        if value is None:
            return
        if expire_time is not None and expire_time < 1000000000:
            expire_time += int(time.time())
        if secret:
            value = self.encrypt(value)
        key = self.get_secret_key(cate1, cate2, cate3, cate4, cate5)
        properties = {
            "secret_key": key,
            "cate1": cate1, "cate2": cate2,
            "cate3": cate3, "cate4": cate4,
            "cate5": cate5, "value": value,
            "expire_time": expire_time
        }

        self.update_or_insert(properties, condition={"secret_key": key, })

    @staticmethod
    def get_secret_key(cate1, cate2=None, cate3=None, cate4=None, cate5=None):
        return "{}-{}-{}-{}-{}".format(cate1, cate2 or '', cate3 or '', cate4 or '', cate5 or '')


def get_fernet(cipher_key=None):
    """
    从本地拿取加密的key
    :param cipher_key:传入的key
    :return:
    """
    secert = SecretManage()
    if cipher_key is not None:
        secert.write(value=cipher_key, cate1='secret', cate2='cipher_key')
    else:
        cipher_key = secert.read(cate1='secret', cate2='cipher_key')
        if cipher_key is None:
            cipher_key = str(Fernet.generate_key(), encoding="utf-8")
            secert.write(value=cipher_key, cate1='secret', cate2='cipher_key')
    return cipher_key


def encrypt(text, cipher_key=None):
    if cipher_key is None:
        cipher_key = get_fernet(cipher_key)
    cipher_key = bytes(cipher_key, encoding="utf8")
    cipher = Fernet(cipher_key)
    encrypted_text = cipher.encrypt(text.encode())

    return encrypted_text


def decrypt(encrypted_text, cipher_key=None):
    if cipher_key is None:
        cipher_key = get_fernet(cipher_key)
    cipher_key = bytes(cipher_key, encoding="utf8")
    cipher = Fernet(cipher_key)
    decrypted_text = cipher.decrypt(encrypted_text)

    return decrypted_text.decode()


def read_secret(cate1, cate2=None, cate3=None, cate4=None, cate5=None, value=None, save=True, secret=False,
                expire_time=None):
    value = SecretManage().read(cate1=cate1, cate2=cate2, cate3=cate3, cate4=cate4, cate5=cate5, value=value, save=save,
                                secret=secret, expire_time=expire_time)
    return value


def write_secret(value, cate1, cate2=None, cate3=None, cate4=None, cate5=None, secret=False, expire_time=None):
    SecretManage().write(value=value, cate1=cate1, cate2=cate2,
                         cate3=cate3, cate4=cate4, cate5=cate5, secret=secret, expire_time=expire_time)
