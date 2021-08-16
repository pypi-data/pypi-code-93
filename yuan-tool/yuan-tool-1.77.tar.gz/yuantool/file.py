import os
import yaml
import shutil
import ruamel.yaml
import zipfile
import tarfile
import uuid
import logging
import pathlib
from io import BytesIO

logger = logging.getLogger(__name__)


def read_file(file, mode='r', encoding='utf-8'):
    """
    :param file: 文件名
    :param encoding: 编码，默认utf-8
    :param mode: open方式，默认r
    :return:
    """
    with open(file, mode, encoding=encoding) as f:
        return f.read()


def read_binary_file(file, mode='rb'):
    """
    :param file: 文件名
    :param mode: open方式，默认r
    :return:
    """
    with open(file, mode) as f:
        return f.read()


def readline_file(file, encoding='utf-8'):
    """
    :param file: 文件名
    :param encoding: 编码，默认utf-8
    :return:
    """
    with open(file, 'r', encoding=encoding) as f:
        return f.readlines()


def read_object(file, mode='r', encoding='utf-8'):
    """
    返回文件对象
    :param file:
    :param mode:
    :param encoding:
    :return:
    """
    f = open(file, mode, encoding=encoding)
    return f


def read_yaml(config_path, config_name=''):
    """
    config_path:配置文件路径
    config_name:需要读取的配置内容,空则为全读
    """
    if config_path:
        with open(config_path, 'r', encoding="utf-8") as f:
            conf = yaml.safe_load(f.read())  # yaml.load(f.read())
        if not config_name:
            return conf
        elif config_name in conf.keys():
            return conf[config_name.upper()]
        else:
            raise KeyError('未找到对应的配置信息')
    else:
        raise ValueError('请输入正确的配置名称或配置文件路径')


def save_yaml(name, content, mode='w+'):
    try:
        with open(name, mode, encoding='utf-8') as f:
            yaml.safe_dump(content, f, allow_unicode=True)
            return True
    except Exception as e:
        raise IOError('yml文件写入错误-{}'.format(e))


def round_read_yaml(path):
    """
    保留yaml所有注释，锚点的读取
    """
    with open(path, 'r', encoding="utf-8") as f:
        doc = ruamel.yaml.round_trip_load(f)
    return doc


def round_save_yaml(path, doc):
    """
    保留yaml所有注释，锚点的保存
    """
    with open(path, 'w', encoding="utf-8") as f:
        ruamel.yaml.round_trip_dump(doc, f, default_flow_style=False)


def read_file_index(file_path):
    num = readline_file(file_path)
    return int(num)


def save_file_index(file_path, cnt):
    with open(file_path, 'w+', encoding="utf-8") as f:
        f.write(str(cnt))


def move_file(src_file, dst_path) -> bool:
    """移动文件"""
    if not os.path.isfile(src_file):
        print("文件不存在")
        return False
    else:
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        shutil.move(src_file, dst_path)
        print("move %s -> %s" % (src_file, dst_path))
        return True


def rm_package(path):
    """删除文件夹以及其下所有文件"""
    shutil.rmtree(path, ignore_errors=True)
    logger.debug('删除文件夹{}'.format(path))


def rm_package_files(path):
    """删除文件夹下所有文件"""
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            rm_package_files(c_path)
        else:
            os.remove(c_path)


def deflated_zip(target, filename, file_url):
    f = zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED)
    f.write(filename, file_url)
    f.close()


def extract_zip(zip_path, target_path):
    """
    解压zip
    解压成功：返回解压出的文件路径
    解压失败：返回False
    """
    try:
        uuid_str = uuid.uuid4().hex
        f = zipfile.ZipFile(zip_path, 'r')
        f.extractall(path=target_path + '/' + uuid_str)
        # corrector(target_path)
    except Exception as e:
        logger.error(e, exc_info=True)
        return False

    return target_path + '/' + uuid_str


def extract_tar(src_file=None, dst_path='./', file_obj=None, _mode='r:gz'):
    """
    默认解压gzip压缩包
    :param _mode: r:gz r:bz2 r:xz
    :param src_file: 源文件
    :param dst_path: 解压路径
    :param file_obj: 文件对象
    :return:
    """
    if not src_file and not file_obj:
        raise ValueError('Source file and byte data must fill in a')

    if src_file:
        _content = io.read_binary_file(src_file)
    elif file_obj:
        _content = file_obj
    else:
        raise BaseException('Unknown error getting file object')

    _obj = tarfile.open(fileobj=BytesIO(_content), mode=_mode)
    _filenames = _obj.getnames()
    for _file in _filenames:
        _obj.extract(_file, dst_path)


def extract_tar_obj(src_file=None, dst_path='./', file_obj=None, _mode='r:gz'):
    """
    默认解压gzip压缩包
    :param _mode: r:gz r:bz2 r:xz
    :param src_file: 源文件
    :param dst_path: 解压路径
    :param file_obj: 文件对象
    :return:
    """
    if not src_file and not file_obj:
        raise ValueError('Source file and byte data must fill in a')

    if src_file:
        _content = read_binary_file(src_file)
    elif file_obj:
        _content = file_obj
    else:
        raise BaseException('Unknown error getting file object')

    _obj = tarfile.open(fileobj=BytesIO(_content), mode=_mode)
    _filenames = _obj.getnames()
    return _obj, _filenames


def get_filename(file, only_file=True):
    """ 获取文件名 """
    if only_file:
        file = pathlib.Path(file).name
    return file[:file.find('.')]
