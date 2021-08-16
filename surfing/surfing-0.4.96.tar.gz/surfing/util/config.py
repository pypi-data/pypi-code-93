
import os
import json
import platform
from typing import Dict

from .singleton import Singleton

DEFAULT_CONFIG_PATH = '/shared/surfing/etc/config.json'
# DEFAULT_CONFIG_PATH = '/Users/puyuantech/Downloads/robo-advisor/rpm/etc/config_local.json'

DEFAULT_LOG_DIR = '/shared/surfing/log/'
DEFAULT_TMP_DIR = '/shared/surfing/tmp/'


class SysSettings(object):

    def __init__(self, sys_json):
        self.log_dir = sys_json.get('log_dir', DEFAULT_LOG_DIR)
        self.tmp_dir = sys_json.get('tmp_dir', DEFAULT_TMP_DIR)

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
    
    def __str__(self):
        return f'log_dir: {self.log_dir}\ntmp_dir: {self.tmp_dir}'

class DbSettings(object):
    '''
    Parse database connection settings in config file
    '''
    def __init__(self, db_json, db_name=None, default_settings=None):
        self.host = db_json.get('host', '' if not default_settings else default_settings.host)
        self.port = db_json.get('port', 0 if not default_settings else default_settings.port)
        self.username = db_json.get('username', '' if not default_settings else default_settings.username)
        self.password = db_json.get('password', '' if not default_settings else default_settings.password)
        self.db_name = db_name

    def to_conn_str(self):
        return 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
            self.username, self.password, self.host, self.port, self.db_name
        )

    def __str__(self):
        return 'mysql+pymysql://{}:********@{}:{}/{}'.format(
            self.username, self.host, self.port, self.db_name
        )

class CassandraSettings(object):

    def __init__(self, conf_json):
        self.hosts = conf_json.get('hosts', '')
        self.port = conf_json.get('port', '')
        self.username = conf_json.get('username', '')
        self.password = conf_json.get('password', '')
        self.default_key_space = conf_json.get('default_key_space', None)

    def to_dict(self):
        return {
            "hosts": self.hosts,
            "port": self.port,
            "username": self.username,
            "password": self.password,
        }

    def __str__(self):
        return 'hosts:{} ** port:{} ** username:{}** password:{}'.format(
            self.hosts, self.port, self.username, self.password,
        )


class AWSSettings:
    """
    Parse aws settings in config file
    """

    _DEFAULT_JSON: Dict[str, str] = {
        'region_name': 'cn-northwest-1',
        'aws_access_key_id': '',
        'aws_secret_access_key': '',
        'etl_tool_bucket_name': '',
    }

    def __init__(self, aws_json):
        self.region_name: str = aws_json.get('region_name')
        self.aws_access_key_id: str = aws_json.get('aws_access_key_id')
        self.aws_secret_access_key: str = aws_json.get('aws_secret_access_key')
        self.etl_tool_bucket_name: str = aws_json.get('etl_tool_bucket_name')

    @classmethod
    def get_default_config(cls):
        return AWSSettings(cls._DEFAULT_JSON)

    def __str__(self):
        return f'region_name: {self.region_name}, aws_access_key_id: {self.aws_access_key_id}, etl_tool_bucket_name: {self.etl_tool_bucket_name}'


class SurfingConfigurator(metaclass=Singleton):

    def __init__(self, config_path=DEFAULT_CONFIG_PATH):
        with open(config_path) as f:
            self.config = json.load(f)

    def get_sys_settings(self):
        assert 'sys' in self.config, 'could not find sys in config'
        settings = SysSettings(self.config['sys'])
        return settings

    def get_db_settings(self, db_name=None):
        assert 'db' in self.config, 'could not find db in config'
        db_config = self.config['db']
        default_settings = None if db_name == '_default' else self.get_db_settings('_default')
        db_settings = DbSettings(db_config.get(db_name, {}), db_name, default_settings)
        return db_settings

    def get_license_settings(self, key=None):
        assert 'license' in self.config, 'could not find license section in config'
        settings = self.config['license']
        assert key in settings, f'could not find {key} section in license config'
        return settings[key]

    def get_wechat_webhook_settings(self, key=None):
        key_map = {
            'wechat_webhook': 'SURFING_WECHAT_WEBHOOK',
            'wechat_webhook_err_msg': 'SURFING_WECHAT_ERR_MSG_WEBHOOK',
            'wechat_webhook_data_check': 'WECHAT_WEBHOOK_DATA_CHECK',
        }
        try:
            settings = os.environ[key_map[key]]
        except KeyError:
            # assert key in self.config, f'could not find {key} section in env and config'
            settings = self.config[key] if key in self.config else None
        return settings

    def get_cassandra_setting(self):
        assert 'surfing_cassandra' in self.config, 'could not find surfing_cassandra section in config'
        return CassandraSettings(self.config['surfing_cassandra'])

    def get_aws_settings(self):
        assert 'surfing_aws' in self.config, 'could not find surfing_aws section in config'
        return AWSSettings(self.config['surfing_aws'])
