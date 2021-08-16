from api.model.FdInputWrapper import FdInputWrapper
from api.model.AlgorithmFdInputWrapper import AlgorithmFdInputWrapper
from factdatasource import FactDatasourceProxyService
from api.exceptions import IllegalArgumentException
from api.model.FactDatasource import FactDatasourceTypeEnum


class FdInputPipe:
    """
    输入包装
    """
    __source_fd_codes = None

    def __init__(self, source_fd_codes):
        self.__source_fd_codes = source_fd_codes

    def list_source_fd_codes(self):
        """
        列出所有与之关联的来源FD的code
        :return:
        """
        return self.__source_fd_codes

    def get_fd(self, fd_code):
        """
        返回一个Fd的输入代理对象
        :param fd_code:
        :return: FdInputWrapper对象
        """
        fd = FactDatasourceProxyService.fd_client_proxy().fd(fd_code)
        if fd is None:
            raise IllegalArgumentException(f"无法查询到FD:{fd_code}的数据")
        if fd.type == FactDatasourceTypeEnum.ALGORITHM:
            return AlgorithmFdInputWrapper(fd_code, None)
        else:
            return FdInputWrapper(fd_code)
