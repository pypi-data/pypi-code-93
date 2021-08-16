from api.model.FdInputWrapper import FdInputWrapper

from libs.utils import get_algo_abs_path
from api.model.FactDatasource import FactDatasource
import os


class AlgorithmFdInputWrapper(FdInputWrapper):
    """
    算法fd输入的一个包装
    """
    sub_path: str = None
    input_stream = None


    def __init__(self, fd_code: str, sub_path):
        super().__init__(fd_code)
        self.sub_path = sub_path

    def path(self):
        fd = self.info()
        if fd is None or not isinstance(fd, FactDatasource):
            return None
        if fd.target:
            # 有target说明是文件不可能有subPath
            return get_algo_abs_path(fd.site, fd.connection, fd.target)
        else:
            if self.sub_path:
                return get_algo_abs_path(fd.site, fd.connection, self.sub_path)
            else:
                return get_algo_abs_path(fd.site, fd.connection, '')

    def exists(self):
        path = self.path()
        if path is None:
            return False
        return os.path.exists(path)

    def open(self):
        # 防止改fd改了路径，每次都新开InputStream
        self.close()
        path = self.path()
        if path is None or not os.path.isfile(path):
            return None
        self.input_stream = open(path, 'rb')
        return self.input_stream

    def close(self):
        if self.input_stream is not None:
            self.input_stream.close()
    """
    获取子文件
    """
    def child(self, sub_path: str):
        fd = self.info()
        if not isinstance(fd, FactDatasource) or fd.target:
            # 说明本身就是文件类型的，没有子文件
            return None
        if self.sub_path:
            absolute_path = get_algo_abs_path(fd.site, fd.connection, self.sub_path)
            if not os.path.isdir(absolute_path):
                # 不是文件夹就没有子文件了
                return None
            else:
                directory = self.sub_path
                if not directory.startswith(os.sep):
                    directory = os.sep + directory
                if not directory.endswith(os.sep):
                    directory = directory + os.sep
                if sub_path.startswith(os.sep):
                    sub_path = sub_path[1:]
                # self.sub_path = directory + sub_path
                #return self
                return AlgorithmFdInputWrapper(self._fact_datasource_code, directory + sub_path)
        else:
            #self.sub_path = sub_path
            #return self
            return AlgorithmFdInputWrapper(self._fact_datasource_code, sub_path)

    """
    返回子文件/文件夹，只返回一层
    """
    def list(self):
        results = []
        abs_path = self.path()
        if abs_path is None:
            return results
        if not os.path.isdir(abs_path):
            # 不是文件夹就没有子文件了
            return results
        else:
            files = os.listdir(abs_path)
            for file in files:
                if file.endswith(os.sep):
                    file = file[:-1]
                directory = ''
                if self.sub_path:
                    directory = self.sub_path
                    if not directory.startswith(os.sep):
                        directory = os.sep + directory
                    if not directory.endswith(os.sep):
                        directory = directory + os.sep
                #self.sub_path = directory + file
                #results.append(self)
                results.append(AlgorithmFdInputWrapper(self._fact_datasource_code, directory + file))
            return results
