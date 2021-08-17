import os
import pickle
import platform

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.WARNING)

DEF_MONGO_ADDR = 'mongodb://localhost:27017'
DEF_WIN_SQLITE3_PATH = 'C:\\_db'
DEF_LINUX_SQLITE3_PATH = '/home/hj3415/Stock/_db'

FILENAME = 'db_setting.pickle'
FULL_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), FILENAME)


def load() -> dict:
    """
    return  {'mongo': 주소..., 'sqlite3': 경로...}
    주소값이 ''이면 데이터베이스를 비활성화하는 것으로 간주한다.
    """
    try:
        with open(FULL_PATH, "rb") as fr:
            p_dict = pickle.load(fr)
            logger.info(p_dict)
            return p_dict
    except (EOFError, FileNotFoundError) as e:
        logger.error(e)
        set_default()
        # 새로 만든 파일을 다시 불러온다.
        with open(FULL_PATH, "rb") as fr:
            p_dict = pickle.load(fr)
            logger.info(p_dict)
            return p_dict


def chg_mongo_addr(addr: str):
    if addr == '' or addr.startswith('mongodb://'):
        p_dict = load()
        before = p_dict['mongo']
        p_dict['mongo'] = addr
        if before != addr:
            print(f'Change mongo setting : {before} -> {addr}')
        with open(FULL_PATH, "wb") as fw:
            pickle.dump(p_dict, fw)
    else:
        raise ValueError(f'Invalid mongo address : {addr}')


def chg_sqlite3_path(path: str):
    p_dict = load()
    before = p_dict['sqlite3']
    p_dict['sqlite3'] = path
    if before != path:
        print(f'Change mongo setting : {before} -> {path}')
    with open(FULL_PATH, "wb") as fw:
        pickle.dump(p_dict, fw)


def set_default():
    pickle_dict = {'mongo': DEF_MONGO_ADDR, 'sqlite3': ''}
    if 'Windows' in platform.platform():
        pickle_dict['sqlite3'] = DEF_WIN_SQLITE3_PATH
    elif 'Linux' in platform.platform():
        pickle_dict['sqlite3'] = DEF_LINUX_SQLITE3_PATH
    else:
        raise
    with open(FULL_PATH, "wb") as fw:
        pickle.dump(pickle_dict, fw)
