import logging

# 加载handler name列表
dynamic_handler_names = []

data_dict = {}


def get_dict(np) -> dict:
    data_dict[np] = data_dict.get(np, {})
    return data_dict[np]


# 应用配置项
class Config:
    def __init__(self, **kwargs):
        self.server_port = 8910
        # 数据服务地址
        self.data_server_host = "localhost"
        self.data_server_port = 8902

        self.data_server_url = f"http://{self.data_server_host}:{self.data_server_port}"
        self.data_server_token = None
        # 校验token
        self.check_auth = False

        # redis缓存
        self.use_local_cache = True
        self.redis_ip = "localhost"
        self.redis_port = "6379"

        # es
        self.es_ip = "localhost"
        self.es_port = 9200
        self.es_user = "elastic"
        self.es_password = "elastic"

        # 打印sql
        self.echo_sql = True

        # 日志输出级别
        self.log_level = logging.INFO
        self.log_file = False

        # 用户表
        self.user_table = 'sys_user_info'

        # 数据库连接
        # mysql
        self.mysql_ip = "localhost"
        self.mysql_port = 3306
        self.mysql_user = "root"
        self.mysql_password = "123456"
        self.mysql_database = "admin"

        # postgis
        self.postgis_ip = "localhost"
        self.postgis_port = "5432"
        self.postgis_user = "postgis"
        self.postgis_password = "123456"
        self.postgis_db = "postgis"

        # mongo
        self.mongo_ip = "localhost"
        self.mongo_port = 27017
        self.mongo_user = "root"
        self.mongo_password = ""
        self.mongo_database = ""

        # 白名单：免登录访问方法
        self.white_list = []
        # 免权限验证ip列表
        self.white_ip_list = []

        # RSA加密
        self.rsa = False

        # 项目路径
        self.project_path = __file__
        self.project_name = ""

        self.static_path = ""
        self.template_path = ""
        self.log_path = ""
        self.handler_path = ""
        self.temp_path = ""
        self.sql_path = ""
        self.convert_path = ""
        self.dataset_path = ""
        self.db = ""
        self.doc_path = ""
        self.cookie_secret = "cookie_secret"
        self.jwt_password = "hello_world"
        self.doc_auth = "root"
        self.leeway = 0  # token 有效期
        self.handler_warning = 0

        self.headers = None
        if kwargs:
            self.update(**kwargs)

    def update(self, **kwargs):
        self.__dict__.update(kwargs)
        if self.handler_path == "" and self.handler_warning == 0:
            logging.warning("当前项目缺少Handler路径，将不能完成Handler的自动导入！")
            self.handler_warning += 1

    def keys(self):
        return self.__dict__.keys()


config = Config()
