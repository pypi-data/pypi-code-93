"""
yml文件注册功能
"""
import os

import yaml

REGISTRY_PROPERTIES = dict()
ALGORITHM_PROPERTIES = dict()

def load_registry_properties(file, yaml_name: str):
    yaml = read_yaml_file(file, yaml_name)
    if yaml is None:
        return
    global REGISTRY_PROPERTIES
    REGISTRY_PROPERTIES = yaml["sobeyficus"]["registry"]

def load_algorithm_properties(file, yaml_name: str):
    yaml = read_yaml_file(file, yaml_name)
    if yaml is None:
        return
    global ALGORITHM_PROPERTIES
    ALGORITHM_PROPERTIES = yaml["algorithm"]

def read_yaml_file(file, yaml_name: str, profile: str = 'default'):
    """
    读取文件路径中的yaml文件
    :param yaml_name:
    :return:
    """
    # 获取当前文件路径
    filePath = os.path.dirname(file)

    # 这里采用一层一层的递归上去找是否有yaml_name的文件
    # 获取配置文件的路径
    yamlPath = _find_path(filePath, yaml_name)
    if yamlPath is None:
        # 如果文件不存在,忽略
        return None

    # 加上 ,encoding='utf-8'，处理配置文件中含中文出现乱码的情况。
    with open(yamlPath, 'r', encoding='utf-8') as f:
        cont = f.read()

    # 加载多个对象
    docs = yaml.load_all(cont, Loader=yaml.FullLoader)

    # 如果数量大于1,并且填了profile的.那么就按照profile的做合并. key是 spring.profiles
    result = None
    for doc in docs:
        if result is None:
            result = doc
            continue
        if ("spring" in doc and "profiles" in doc["spring"]) and (
                (isinstance(doc["spring"]["profiles"], list) and profile in doc["spring"]["profiles"]) or (
                profile == doc["spring"]["profiles"])):
            # 找到是相同的,进行合并
            from config import annotation
            annotation.deep_search_and_merge(result, doc)

    # 返回yaml文件对象
    return result


def _find_path(file_path, yaml_name):
    """
    递归查找文件
    :param file_path:
    :param yaml_name:
    :return:
    """
    # 这里window中取出来的路径也可能是 / 分割的，这里简单重写下
    r_path = os.path.join(file_path, yaml_name)
    if os.path.exists(r_path):
        return r_path
    else:
        folder_path = os.path.split(file_path)[0]
        if folder_path == file_path:
            return None
        else:
            return _find_path(folder_path, yaml_name)


def _get_separator():
    """
    判断是windows还是其他的,系统不一样 separtor不一样
    :return:
    """
    import platform
    if 'Windows' in platform.system():
        separator = '\\'
    else:
        separator = '/'
    return separator
