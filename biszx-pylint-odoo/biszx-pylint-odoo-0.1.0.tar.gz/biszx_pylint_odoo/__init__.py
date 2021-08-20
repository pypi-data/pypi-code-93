from .checker import FunctionChecker, FieldChecker
from . import messages


def register(linter):
    '''required method to auto register this checker'''
    linter.register_checker(FunctionChecker(linter))
    linter.register_checker(FieldChecker(linter))


def get_all_messages():
    '''Get all messages of this plugin'''
    all_msgs = {}
    all_msgs.update(messages.FUNCTION_CHECKER_MSGS)
    all_msgs.update(messages.FIELD_CHECKER_MSGS)
    return all_msgs


def messages2md():
    all_msgs = get_all_messages()
    md_msgs = 'Code | Description | short name\n--- | --- | ---'
    for msg_code, (title, name_key, _) in sorted(all_msgs.items()):
        md_msgs += f'\n{msg_code} | {title} | {name_key}'
    md_msgs += '\n'
    return md_msgs
