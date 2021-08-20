""" Основные и вспомогательные команды для взаимодействия с приложением через командную строку.

Вспомогательные команды и опции:
    python -m rcore --help
        - показать описание активной команды.
    python -m rcore ..tree [ shortName y/n] [ description y/n] [ expectedType y/n] [ default y/n]
        - показать дерово команд и под-команд от активной команды.

Эти команды можно использовать на любом уровне вложености.
То есть:
    python -m rcore --help - покажет информацию о всех доступных командах первой линии.
    python -m rcore ..tree --help - покажет информацию о команде ..tree.
    python -m rcore ..first ..second --help - покажет информацию о команде ..second, которая являктся под-коммандой ..second.

Основные команды:
    python -m rcore - информаци о rcore.
    python -m rcore ..CLI - информаци о CLI.

"""

from . import cliengine
from .cliengine import CLIOutput, Command, ConsoleOutput, Option
from .rtype import Validator


""" Блок с вспомогательными CLI командами """


def _auxiliary_help(CLIout: CLIOutput):
    """ Вспомогательная опция. При указании выводит описание, список опций и подкоманд у активной команды. """

    ConsoleOutput(CLIout.stages).help(CLIout.this_command)


def _auxiliary_tree(CLIout: CLIOutput):
    """ Вспомогательная команда. При вызове выводит дерево всех опций и подкоманды у активной команды. """

    assert CLIout.next_command is not None  # mypy...

    ConsoleOutput(CLIout.stages).tree(
        CLIout.this_command,
        cliengine.ArgumentPrintOptions(
            name=True,
            shortName=CLIout.next_command.req['shortName'],
            description=CLIout.next_command.req['description'],
            expectedType=CLIout.next_command.req['expectedType'],
            default=CLIout.next_command.req['default']
        )
    )


option = cliengine.AuxiliaryOption(
    ('help', 'h'), 'Опции и подкоманды у активной команды', Validator(bool, [], False), _auxiliary_help
)
cliengine.AuxiliaryOptionList.append(option)


command = cliengine.AuxiliaryCommand(('tree', 'tr'), 'Дерево всех команд и их опций у активной команды', _auxiliary_tree)
command.append(
    Option('shortName', 'Показать короткое имя', Validator(bool, [], False)),
    Option('description', 'Показать подсказку', Validator(bool, [], False)),
    Option('expectedType', 'Показать тип принимаемого значения', Validator(bool, [], False)),
    Option('default', 'Показать значение поумолчанию', Validator(bool, [], False))
)
cliengine.AuxiliaryCommandList.append(command)

for command in cliengine.AuxiliaryCommandList:
    cliengine.AuxiliaryArgumentsNames[Command] += list(command.names())

for option in cliengine.AuxiliaryOptionList:
    cliengine.AuxiliaryArgumentsNames[Option] += list(option.names())


""" Блок с основными CLI командами """


def _entrypoint(CLIout: CLIOutput):
    """ Точка входа в CLI """

    CLIout.next()


def _cli_info(CLIout: CLIOutput):
    """ Вывод информации о CLI """

    if any(CLIout.req.values()):
        CLIout.help()

    if CLIout.req['version']:
        print('CLI version - ' + '.'.join(map(str, cliengine.version)))


entrypoint_command = Command('entrypoint', 'Entry point for interacting with the CLI', _entrypoint)


def init_cli():
    """ Инициализация CLI. Создание дерева команд """

    entrypoint_command.append(
        Option('version', 'Версия', Validator(bool, [], False))
    )

    cli_info_command = Command(('CLI', 'cli'), 'Информация о CLI', _cli_info)
    cli_info_command.append(
        Option('version', 'Версия', Validator(bool, [], False))
    )
    entrypoint_command.append(cli_info_command)


def start():
    """ Запуск CLI

    Нужно для построения дерева CLI без изменения обьекта для надстроек.

    """

    init_cli()
    CLIout = entrypoint_command.handler()
    CLIout.start()
