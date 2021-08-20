import typing
import importlib


def ReadModule(module: str) -> dict:
    np = importlib.import_module(module)
    NewVariables = {}
    for key in [i for i in dir(np) if not i.startswith('__')]:
        NewVariables[key] = getattr(np, key)
    return NewVariables


def __new_value(variables: dict, string: str) -> typing.Any:
    for key in variables:
        locals()[key] = variables[key]
    return eval(string)


def ReadValues(variables: dict, string: str) -> dict:
    """ Преобразовывает строку с синтаксисом как при инициализации словаря python3

    Args:
        variables (dict): Доступные переменные
        string (str): Обрабатываемая строка.

    Returns:
        dict: Словарь полученый при выполнении string компялятором python с учетом переменных variables
    """

    return __new_value(variables, "{"+string+"}")


def ReturnValue(variables: dict, string: str) -> typing.Any:
    """ Преобразоание строку в значение.

    Args:
        variables (dict): Доступные переменные
        ReturnValue (str): Обрабатываемая строка.

    Returns:
        any: Значение полученное при выполнении string компялятором python с учетом переменных variables
    """

    return __new_value(variables, string)
