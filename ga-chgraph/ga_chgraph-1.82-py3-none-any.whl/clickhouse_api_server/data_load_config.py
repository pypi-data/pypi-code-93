import os
import sys
import ujson
from CKClient import get_client
from graph_op import CHGraph
from db_op import DBoperator
import psycopg2
import Longger_design

'''

graph_dir = "./config/tcpflow_flow.cfg.json"

#graph = CHGraph(graph_dir, client)

'''
logger = Longger_design.get_logger()


def load_config():
    print("服务所有配置开始加载")
    curPath = os.path.abspath(os.path.dirname(__file__))
    rootPath = os.path.split(curPath)
    sys.path.append(rootPath[0])
    sys.path.append(rootPath[0] + "/" + rootPath[1])

    clickhouse_config_dir = rootPath[0] + "/" + rootPath[1] + "/config/" + "graph_config.json"

    with open(clickhouse_config_dir, 'r') as f:
        clickhouse_config = ujson.load(f)

    clickhouse_ip = os.getenv("HOST_DAISY") if os.getenv("HOST_DAISY") else clickhouse_config["ip"]
    clickhouse_port = os.getenv("PORT_DAISY") if os.getenv("PORT_DAISY") else clickhouse_config["port"]
    clickhouse_user = os.getenv("USERNAME_DAISY") if os.getenv("USERNAME_DAISY") else clickhouse_config["user"]
    clickhouse_pwd = os.getenv("PASSWORD_DAISY") if os.getenv("PASSWORD_DAISY") else clickhouse_config["password"]

    db_ip = os.getenv("DB_HOST") if os.getenv("DB_HOST") else clickhouse_config["dbip"]
    db_port = os.getenv("DB_PORT") if os.getenv("DB_PORT") else clickhouse_config["dbport"]
    db_user = os.getenv("DB_USERNAME_PREFIX_GA_SERVER") if os.getenv("DB_USERNAME_PREFIX_GA_SERVER") else \
    clickhouse_config["dbuser"]
    db_pwd = os.getenv("DB_PASSWORD_PREFIX_GA_SERVER") if os.getenv("DB_PASSWORD_PREFIX_GA_SERVER") else\
        clickhouse_config["dbpassword"]
    db_table = os.getenv("DB_NAME_PREFIX_GA_SERVER") if os.getenv("DB_NAME_PREFIX_GA_SERVER") else clickhouse_config[
        "dbtable"]
    db_ssl_mode = os.getenv("DB_SSL_MODE") if os.getenv("DB_SSL_MODE") else clickhouse_config["sslMode"]


    # host = '10.202.255.93', port = '9090', user = 'default', password = 'root'
    print(clickhouse_ip, clickhouse_port, clickhouse_user, clickhouse_pwd)
    logger.info("clickhouse_ip is: " + clickhouse_ip)
    # graphClient = Client(host=clickhouse_ip, port=clickhouse_port, user=clickhouse_user, password=clickhouse_pwd)
    clickhouse_connect = {"ip": clickhouse_ip, "port": clickhouse_port, "user": clickhouse_user, "password": clickhouse_pwd}

    graphClient = get_client(clickhouse_connect)
    # res = graphClient.execute('show databases')  # 显示所有的数据库
    # print("show databases:", res)
    graph = CHGraph(graphClient)
    if db_pwd:
        url = 'postgresql://' + db_user + ':' + db_pwd + '@' + db_ip + ':' + db_port + '/' + db_table + '?sslmode=require'
    else:
        url = 'postgresql://' + db_user + '@' + db_ip + ':' + db_port + '/' + db_table + '?sslmode=disable'
    # url = 'postgresql://' + db_user + '@' + db_ip + ':' + db_port + '/' + db_table + '?sslmode=disable'
    # conn = psycopg2.connect(url)
    db = DBoperator(url)
    print("服务所有配置加载结束")
    config_params = {
        "graph": graph,
        "db": db,
        "graphClient": graphClient,
        "clickhouse_connect": clickhouse_connect
    }
    # config_params = {
    #
    # }
    return config_params
