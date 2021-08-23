from typing import Tuple, List


def get_log_message(operation, parallel, project) -> str:
    message: str = ''
    message += '[INFO] '
    message += 'Running '
    message += f'the operations "{", ".join(operation)}" ' \
        if isinstance(operation, Tuple) or isinstance(operation, List) else ""
    message += f'{"the operation " + operation} ' \
        if isinstance(operation, str) else ""
    message += f'on projects "{", ".join(project)}" ' \
        if isinstance(project, Tuple) else ""
    message += f'{"on project " + project} ' \
        if isinstance(project, str) else ""
    message += f'{"in parallel" if parallel else "sequentially"}.'

    return message
