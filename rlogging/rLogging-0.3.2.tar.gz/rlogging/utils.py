import importlib
import typing as _T


def get_obj(objPath: str) -> _T.Any:
    """ Получение объекта, имея путь до этого объекта

    Args:
        objPath (str): Путь до объекта

    Returns:
        _T.Any: Объект

    """

    moduleName, _, loggerClassName = objPath.rpartition('.')
    module = importlib.import_module(moduleName)
    return getattr(module, loggerClassName)
