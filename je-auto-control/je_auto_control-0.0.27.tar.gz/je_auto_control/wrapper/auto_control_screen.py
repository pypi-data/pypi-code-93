from je_auto_control.utils.je_auto_control_exception import exception_tag
from je_auto_control.utils.je_auto_control_exception.exceptions import AutoControlScreenException
from je_auto_control.wrapper.platform_wrapper import screen


def size():
    try:
        return screen.size()
    except Exception:
        raise AutoControlScreenException(exception_tag.screen_get_size)
