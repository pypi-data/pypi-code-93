""" Модуль Интерфейса Командной Строки - CLI

Из этого модуля импортируются основные классы для использования CLI

Все информационные сообщения передаются в виде исключения в функцию-декоратор ex.exception,
где выводятся как обычный текст.

"""

from __future__ import annotations

import sys
import typing
import typing as _T
from copy import copy, deepcopy
from dataclasses import dataclass

from rcore import exception as ex
from rcore import rtype

version = (2, 0)


class CLIOutput(object):
    """ Интерфес связи между разными уровнями обработки команды и хранилище для значений опций.

    Если при инициализации команды вы указали каллбек функцию,
    то при выполнении этой команды в указанную функцию придет объекта данного класса.

    Во всех командах, точнее их функциях, которые не являются конечными точками, должен вызваться метод next() у объекта данного класса.
    При вызове этой функции, будет запущена следующая команда.

    """

    def __str__(self):
        return self.this_command.name

    stages: list = []
    this_command: Command
    next_command: _T.Optional[CLIOutput] = None
    req: dict[str, typing.Any]

    def __init__(self):
        self.stages = []
        self.req = {}

    def help(self):
        """ Вызов подсказки для активной команды """

        ConsoleOutput(self.stages).help(self.this_command)

    def start(self, *args, **kwargs) -> typing.Any:
        """Запуск команды

        Returns:
            typing.Any: Возвращает значение функции хэндлера

        """

        if self.this_command.callback:
            return self.this_command.callback(self, *args, **kwargs)

        else:
            return self.next(*args, **kwargs)

    def next(self, *args, **kwargs) -> typing.Any:
        """Переход на следующий уровень обработки команды

        Returns:
            typing.Any: Возвращает значение функции следующего уровня хэндлера

        """

        if self.next_command is not None:
            return self.next_command.start(*args, **kwargs)
        else:
            self.help()


_CommandCallback = _T.Optional[typing.Callable[[CLIOutput], _T.Optional[_T.Any]]]


class Argument(object):
    """ Атомарная еденица обработчика команды """

    name: str
    needShortName: bool
    shortName: _T.Union[str, bool, None]
    description: _T.Union[str, None]

    def __init__(self, name: _T.Union[str, tuple[str, str]], description: _T.Union[str, None] = None):

        if isinstance(name, tuple):
            self.name = name[0]

            self.shortName = name[1]
            self.needShortName = False

            if name[1] is None:
                self.shortName = None
                self.needShortName = True
        else:
            self.name = name
            self.shortName = None
            self.needShortName = True

        self.description = description

    def names(self) -> tuple[_T.Union[str, bool, None], _T.Union[str, bool, None]]:
        """ Возвращает кортеж имен аргумента.

        Returns:
            tuple[str, str]: кортеж имен.

        """

        return (self.name, self.shortName)


class Option(Argument):
    """ Опция команды

    Args:
        name (str, tuple[str, str]): Имя или связка полного и короткого имени
        description ([type], optional): [description]. Defaults to None.
        expectedType ([type], optional): Тип, к которому будет приводиться полученное значение. Defaults to None.
        default (typing.Any, optional): Значение по умолчанию. Defaults to None.

    """

    validator: _T.Union[rtype.Validator, None]

    def __init__(self, name: _T.Union[str, tuple[str, str]], description: _T.Union[str, None] = None, validator: _T.Union[rtype.Validator, None] = None):
        super().__init__(name, description)
        self.validator = validator


class Command(Argument):
    """ Команда

    Args:
        name (str, tuple[str, str]): Имя или связка полного и короткого имени
        description ([type], optional): [description]. Defaults to None.
        callback ([type], optional): Функция, которую можно будет вызвать через CLIOutput.next(). Defaults to None.

    """

    commands: list[Command]
    options: list[Option]
    callback: _CommandCallback

    def __init__(self,
                 name: _T.Union[str, tuple[str, str]],
                 description: _T.Union[str, None] = None,
                 callback: _CommandCallback = None
                 ):
        super().__init__(name, description)
        self.options = []
        self.commands = []
        self.callback = callback

    def append(self, *arguments: _T.Union[Option, Command]):
        """ Добавление дочерних аргументов (Команд и Опций) к команде """

        for argument in arguments:
            if isinstance(argument, Option):
                self.options.append(argument)
            if isinstance(argument, Command):
                self.commands.append(argument)

    def analyze(self):
        """ Проверка валидности обработчика """

        def __check_name(nameList: list[str], argument: _T.Union[Command, Option]):
            """ Проверка на дублирование имен и коротких имен у аргументов.

            Если короткого имени нет и пользователь не уточнил его отсутствие, то оно будет создано

            Args:
                nameList (list[str]): Список уже использованных имен некого типа аргумента у команды
                argument ([type]): Подаргумент, который надо проверить

            Raises:
                ex.info.CliArgumentError: Имена повторились

            """

            names = [i for i in argument.names() if isinstance(i, str)]
            if argument.needShortName:
                names = [argument.name]

            for name in names:
                if name in nameList:
                    raise ex.info.CliArgumentError(
                        f'Повторение имени аргумента "{name}" у команды {self.name}: {nameList}'
                    )
                nameList.append(name)

            if argument.needShortName:
                shortName = ''
                for char in argument.name:
                    shortName += char
                    if shortName not in nameList:
                        break

                if shortName == '':
                    argument.shortName = False
                else:
                    argument.shortName = shortName
                    nameList.append(argument.shortName)

        nameList = copy(AuxiliaryArgumentsNames[Option])
        for command in self.options:
            __check_name(nameList, command)

        nameList = copy(AuxiliaryArgumentsNames[Command])
        for command in self.commands:
            __check_name(nameList, command)

            command.analyze()

    def __matching_wrapper(self, stages: list[str], commandValue: BrickMaskCommand) -> CLIOutput:
        self.__auxiliary(stages, commandValue)
        return self.__matching(stages, commandValue)

    def __auxiliary(self, stages: list[str], commandValue: BrickMaskCommand):
        """ Проверка вызыва вспомогательных атрибутов

        Args:
            commandValue (BrickMaskCommand): Принятый аргумет

        """

        for subCommandValue in commandValue.commands:
            for command in AuxiliaryCommandList:
                if subCommandValue.name in command.names():
                    assert command.callback is not None  # mypy...

                    self.commands.append(command)
                    command.callback(self.__matching(stages, commandValue))

        for OptionValue in commandValue.options:
            for option in AuxiliaryOptionList:
                if OptionValue.name in option.names():
                    assert option.callback is not None  # mypy...

                    option.callback(self.__matching(stages, commandValue))

    def __matching(self, stages: list[str], commandValue: BrickMaskCommand) -> CLIOutput:
        """ Спопоставление ожидаемых команд с опциями и принятых аргуметов

        Args:
            commandValue (BrickMaskCommand): Дерево принятых аргуметов

        Returns:
            CLIOutput: Интерфейс взаимодействия со всеми уровнями команд

        """

        clioutput = CLIOutput()
        clioutput.stages = stages + [self.name]
        clioutput.this_command = copy(self)

        for comand in self.commands:
            for subCommandValue in commandValue.commands:
                if subCommandValue.name in comand.names():
                    clioutput.next_command = comand.__matching_wrapper(
                        clioutput.stages, subCommandValue
                    )

        valuesCopy = copy(commandValue.values)

        for option in self.options:

            value = None

            for optionValue in commandValue.options:
                if (optionValue.name == option.name) or (optionValue.isShortName and optionValue.name == option.shortName):
                    value = optionValue.value.value

            if value is None:
                if len(valuesCopy) != 0:
                    value = valuesCopy[0].value
                    valuesCopy = valuesCopy[1:]

            if option.validator is not None:
                try:
                    value = option.validator.check(value, True)

                except TypeError:
                    ConsoleOutput(clioutput.stages).error_type(option, value)

                except ValueError:
                    ConsoleOutput(clioutput.stages).error_required(self, option)

            clioutput.req[option.name] = value

        return clioutput

    def handler(self, arguments: _T.Union[list[str], None] = None) -> CLIOutput:
        """ Запуск обработчика.

        Args:
            arguments ([type], optional): Аргуметы из командной строки. Defaults to None.

        """

        if arguments is None:
            arguments = sys.argv[1:]

        self.analyze()

        initCommand = BrickMaskCommand('init')
        initCommand.deconstruct(arguments)

        return self.__matching_wrapper([], initCommand)


class AuxiliaryOption(Option):
    """ Вспомогательная опция. При указании для команды будет выполнена функция """

    callback: _CommandCallback

    def __init__(self, name: tuple[str, str], description: str, validator: rtype.Validator, callback: _CommandCallback):
        super().__init__(name, description, validator)
        self.callback = callback


class AuxiliaryCommand(Command):
    """ Вспомогательная команда. При указании выполнена функция, в которую передастся обьект команды-родителя. """

    def __init__(self, name: tuple[str, str], description: str, callback: typing.Callable):
        super().__init__(name, description, callback)


AuxiliaryOptionList: list[AuxiliaryOption] = []
AuxiliaryCommandList: list[AuxiliaryCommand] = []

AuxiliaryArgumentsNames: dict[_T.Union[type[Command], type[Option]], list] = {
    Command: [], Option: [],
}


@dataclass
class ArgumentPrintOptions(object):
    """ Параметры вывода аргумента """

    tablvl: int = 0
    name: bool = True
    shortName: bool = True
    description: bool = True
    expectedType: bool = False
    default: bool = False


def argument_to_str(argument: _T.Union[Command, Option], printOptions: ArgumentPrintOptions) -> str:
    """ Создание строки, отражающей аргумент.

    Args:
        argument ([type]): Аргумент, который надо представить в виде строки
        printOptions (ArgumentPrintOptions): Параметры полноты информации о аргументе

    Returns:
        str: Информация о аргументе

    """

    string = '    ' * printOptions.tablvl

    if isinstance(argument, Option):
        prefix = '-'
    elif isinstance(argument, Command):
        prefix = '.'

    if argument.name and printOptions.name:
        string += '%-15s' % (prefix * 2 + argument.name)

    if isinstance(argument.shortName, str) and printOptions.shortName:
        string += '%-10s' % (prefix + argument.shortName)

    if argument.description and printOptions.description:
        string += ' [ ' + argument.description + ' ] '

    if isinstance(argument, Option) and argument.validator is not None:
        if len(argument.validator.types) > 0 and printOptions.expectedType:
            string += str(argument.validator.types[0]) + ' '

        if printOptions.default:
            if argument.validator.default is Exception:
                string += '*'
            else:
                string += '(' + str(argument.validator.default) + ')'

    return string + '\n'


@dataclass
class BrickMaskValue(object):
    """ Составляющие командны """

    value: _T.Union[str, bool]


class BrickMaskOption(object):
    """ Составляющие командны """

    name: str
    isShortName: bool = True
    value: BrickMaskValue = BrickMaskValue(True)


class BrickMaskCommand(object):
    """ Составляющие командны """

    name: str
    isShortName: bool = True
    commands: list[BrickMaskCommand]  # Подкоманды
    options: list[BrickMaskOption]  # Опции со значениями
    values: list[BrickMaskValue]  # Значения без опций

    def __init__(self, name: _T.Union[str, None] = None):
        if name is not None:
            self.name = name

        self.commands = []
        self.options = []
        self.values = []

    def deconstruct(self, arguments: list[str]):
        """ Заполнение параметров команды.

        Args:
            arguments (list[str]): Список аргументов относящиеся с этой команде

        """

        lastBrick = None

        for i in range(len(arguments)):
            brick = convert_word(arguments[i])

            if isinstance(brick, BrickMaskCommand):
                brick.deconstruct(arguments[i + 1:])
                self.commands.append(brick)
                break

            elif isinstance(brick, BrickMaskOption):
                self.options.append(brick)

            else:
                if isinstance(lastBrick, BrickMaskOption):
                    lastBrick.value = brick
                    lastBrick = None
                    continue

            if isinstance(lastBrick, BrickMaskValue):
                self.values.append(lastBrick)

            lastBrick = brick

        if isinstance(lastBrick, BrickMaskValue):
            self.values.append(lastBrick)


def convert_word(word: str) -> _T.Union[BrickMaskCommand, BrickMaskOption, BrickMaskValue]:
    """ Определяет роль аргумента из команды запуска.

    Args:
        word (str): аргумент

    Returns:
        [BrickMaskCommand, BrickMaskOption, BrickMaskValue]: Обьект роли со значением

    """

    brick: _T.Union[BrickMaskCommand, BrickMaskOption, BrickMaskValue]

    if len(word) == 0:
        raise ex.errors.CliErrorParseArgument(word)

    if word[0] == '.':
        brick = BrickMaskCommand()
    elif word[0] == '-':
        brick = BrickMaskOption()
    else:
        return BrickMaskValue(word)

    if len(word) == 1:
        raise ex.errors.CliErrorParseArgument(word)

    if word[0] == word[1]:

        if len(word) == 2:
            raise ex.errors.CliErrorParseArgument(word)

        brick.isShortName = False

    brick.name = word[2:]
    if brick.isShortName:
        brick.name = word[1:]

    return brick


class ConsoleOutput(object):
    """ Класс для вывода информации от cli: формирование исключения c текстом """

    outputText: str

    def __init__(self, stages: list[str] = []):
        self.outputText = '\nCLI message.\n'
        if len(stages) > 0:
            self.outputText += 'Active commands: ' + ' -> '.join(stages) + '\n'
        self.outputText += '\n'

    def error_required(self, command: Command, option: Option):
        """ Вывод информации о пропуске обязательной опции

        Args:
            command (Command): Команда, в которой пропущена опция.
            option (Option): Опция, которую пропустили.

        """

        self.outputText += f'Для команды ..{command.name} Вы пропустили обязательную опцию --{option.name} \n\n'
        try:
            self.help(command)
        except ex.info.CliHelpPrint:
            raise ex.info.CliErrorRequired(self.outputText) from None

    def error_type(self, option: Option, badval: typing.Any):
        """ Вывод информации о несоответствии значения и ожидаеого типа у опции

        Args:
            option (Option): Опция, в которй допущена ошибка.
            badval (typing.Any): Полученное невалидное значение.

        """

        assert option.validator is not None # mypy...

        if len(option.validator.enum) > 0:
            self.outputText += f'Для опции --{option.name} Вы указали не входящее в допустимое множество значение.\n'
            self.outputText += f'Need {option.validator.enum}, not "{badval}"'

        else:
            self.outputText += f'Для опции --{option.name} Вы указали неподходящее типом значение.\n'
            self.outputText += f'Need {option.validator.types}, not "{badval}"'

        raise ex.info.CliErrorType(self.outputText)

    def help(self, command: Command):
        """ Вывод подробной информации о опциях и подкомандах

        Args:
            command (Command): Команда, информацию о которой надо получить.

        """

        printOptions = ArgumentPrintOptions()
        printOptions.tablvl = 1

        exceptText = ''

        if len(command.options) > 0:
            exceptText += 'Options:\n'

            for subOption in command.options:
                exceptText += argument_to_str(subOption, printOptions)
            exceptText += '\n'

        if len(command.commands) > 0:
            exceptText += 'Commands:\n'

            for subCommand in command.commands:
                exceptText += argument_to_str(subCommand, printOptions)
            exceptText += '\n'

        if len(command.commands) == 0 and len(command.options) == 0:
            exceptText += 'This command has no Options or Commands.\n\n'

        exceptText += 'Auxiliary Options and Commands:\n'
        for auxOption in AuxiliaryOptionList:
            exceptText += argument_to_str(auxOption, printOptions)
        for auxCommand in AuxiliaryCommandList:
            exceptText += argument_to_str(auxCommand, printOptions)

        self.outputText += exceptText

        raise ex.info.CliHelpPrint(self.outputText)

    def tree(self, command: Command, printOptions: _T.Union[ArgumentPrintOptions, None] = None):
        """ Вывод дерева всех подкоманд и их опций

        Args:
            command (Command): Команда, от которой начать вывод дерева.
            printOptions (ArgumentPrintOptions, optional): Параметры вывода. Defaults to None.

        """

        if printOptions is None:
            printOptions = ArgumentPrintOptions()

        def __inner(command: Command, printOptions: ArgumentPrintOptions):

            text = argument_to_str(command, printOptions)

            printOptions.tablvl += 1

            for subOption in command.options:
                text += argument_to_str(subOption, printOptions)

            for subCommand in command.commands:
                if isinstance(subCommand, AuxiliaryCommand):
                    continue
                text += __inner(subCommand, deepcopy(printOptions))

            return text

        printOptions.tablvl = 0

        outputText = __inner(command, printOptions)
        raise ex.info.CliHelpPrint(self.outputText + outputText)
