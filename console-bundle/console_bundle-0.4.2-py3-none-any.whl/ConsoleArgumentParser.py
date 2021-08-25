from argparse import ArgumentParser


class ConsoleArgumentParser(ArgumentParser):

    __command_name = None
    __command_name_usage_message = "usage: console [-h] [-e ENV] command_name"
    __command_name_error_messages = (
        "console: error: the following arguments are required: command_name",
        "CommandRunner.py: error: the following arguments are required: command_name"
    )

    def set_command_name(self, command_name: str):
        self.__command_name = command_name

    def exit(self, status=0, message=None):
        if message is not None:
            stripped_message = message.strip()

            if stripped_message in self.__command_name_error_messages:
                return

        super().exit(status, message)

    def _print_message(self, message, file=None):
        stripped_message = message.strip()

        if stripped_message == self.__command_name_usage_message:
            return

        if self.__command_name:
            replaced_message = message.replace("command_name", self.__command_name)
        else:
            replaced_message = message

        super()._print_message(replaced_message, file)
