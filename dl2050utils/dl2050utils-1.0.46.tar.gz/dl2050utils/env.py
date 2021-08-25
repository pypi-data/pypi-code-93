import os
from pathlib import Path
from dotenv import load_dotenv;
import yaml

def find_yml():
    config_path = os.getenv('CONFIG_PATH')
    if config_path is not None:
        p = Path(config_path) / '.Config.yml'
        if p.exists(): return p
    dirs = ['.', '/app', '~']
    for e in dirs:
        p = Path(e) / '.Config.yml'
        if p.exists(): return p
    p = Path('/run/secrets/config.yml')
    if p.exists(): return p
    return None

def Config_load():
    load_dotenv()
    fname = find_yml()
    if fname is None:
        return None, 'Config_load ERROR: Cant find .Config.yml'
    with open(str(fname), 'r') as stream:
        try:
            Config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            return None, f'Config_load ERROR: .Config.yml parsing error (str({exc}))'
    return Config, None

def get_db_url(Config, with_db_name=False):
    if Config is None:
        return None
    if not 'db' in Config:
        return None
    if os.getenv('development') is None:
        if not 'host' in Config['db']:
            return None
        host = Config['db']['host']
    else:
        if not 'host_dev' in Config['db']:
            return None
        host = Config['db']['host_dev']
    if not 'port' in Config['db']:
        port = 3306
    else:
        port = Config['db']['port']
    if not 'name' in Config['db']:
        return None
    if not 'passwd' in Config['db']:
        return None
    passwd = Config['db']['passwd']
    url = f'mysql+pymysql://root:{passwd}@{host}:{port}'
    if with_db_name:
        name = Config['db']['name']
        url = f'{url}/{name}'
    return url

def get_rest_url(Config):
    if Config is None:
        return None
    if not 'rest' in Config:
        return None
    if os.getenv('development') is None:
        if not 'host' in Config['rest']:
            return None
        host = Config['rest']['host']
    else:
        if not 'host_dev' in Config['rest']:
            return None
        host = Config['rest']['host_dev']
    if not 'port' in Config['rest']:
        return None
    port = Config['rest']['port']
    url = f'{host}:{port}'
    return url