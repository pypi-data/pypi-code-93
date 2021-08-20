"""
Chain of Command
"""
import enum


class CommandState(enum.Enum):
    UNKNOWN = 0
    ERROR = 1
    FAILURE = 2
    SUCCESS = 3


class Context(dict):
    pass


class ChainException(Exception):
    pass


class ContextException(ChainException):
    pass


class ContextKeyException(ContextException):
    pass


class Command(object):
    FAILURE = False
    SUCCESS = True

    def execute(self, context: Context) -> bool:
        return Command.SUCCESS

    def post_execute(self, context: Context, state: CommandState, error: Exception = None) -> None:
        pass


class Chain(Command):
    def __init__(self):
        self.commands = list()

    def append(self, command: Command) -> None:
        self.commands.append(command)

    def execute(self, context: Context) -> bool:
        success = True
        for command in self.commands:
            success = command.execute(context)
            if not success:
                break

        return success

    def post_execute(self, context: Context, state: CommandState, error: Exception = None) -> None:
        for command in self.commands[::-1]:
            command.post_execute(context, state, error)


class Runner(Chain):
    def execute(self, context: Context) -> bool:
        exception = Exception("No exception")
        state = CommandState.UNKNOWN

        try:
            if super().execute(context):
                state = CommandState.SUCCESS
            else:
                state = CommandState.FAILURE
        except Exception as err:
            exception = err
            state = CommandState.ERROR
        finally:
            super().post_execute(context, state, exception)

        if state == CommandState.ERROR:
            raise exception
        elif state == CommandState.FAILURE:
            return Command.FAILURE
        elif state == CommandState.SUCCESS:
            return Command.SUCCESS
        else:
            # Huh, How did this happen?
            return Command.FAILURE


class Processor(Runner):
    def __init__(self):
        super().__init__()

        self.reporting = Chain()
        self.initialization = Chain()
        self.authentication = Chain()
        self.authorization = Chain()
        self.validating = Chain()
        self.processing = Chain()

        super().append(self.initialization)
        super().append(self.reporting)
        super().append(self.authentication)
        super().append(self.authorization)
        super().append(self.validating)
        super().append(self.processing)

    def append(self, command: Command) -> None:
        raise ChainException("Do not use!")
