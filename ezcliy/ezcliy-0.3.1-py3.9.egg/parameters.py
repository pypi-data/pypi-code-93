import re
import uuid


class Parameter:
    """
    Abstract class for creating parameters for cli invoke
    """

    value: str = None
    """Value of parameter"""
    description: str = None
    """Description of param"""

    lock: bool = False

    def pass_args(self, user_args: list[str]) -> list[str]:
        """
        This method gathers all args, and removes processed args.

        :param user_args: list of args to process
        :return: processed list of args, usally smaller then input
        """
        ...

    def __str__(self):
        return str(self.value)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __bool__(self):
        return bool(self.value)


class Flag(Parameter):
    """Simple boolean switch (examples: -v or --verbose)"""

    value: bool = False

    def __init__(self, *aliases: str):
        """

        :param aliases: must contains dash or dashes
        """
        self.aliases = aliases

    def pass_args(self, user_args: list[str]) -> list[str]:
        if self.lock:
            return user_args
        shrinked_args = [arg for arg in user_args if arg not in self.aliases]
        # noinspection PyTypeChecker
        self.value = len(shrinked_args) != len(user_args)
        self.lock = True
        return shrinked_args

    def __repr__(self):
        return f'<Flag {" ".join(self.aliases)} has value {self.value} ({self.lock=}))>'


class KeyVal(Parameter):
    """Pass values for invcation (examples: -c=90 or --count=90)"""

    values: list[str] = []

    def __init__(self, keyname: str, default=None):
        """

        :param keyname: must contains dash or dashes
        """
        self.key = keyname
        if default is not None:
            self.values = [default]

    @property
    def value(self):
        try:
            return self.values[0]
        except IndexError:
            return None

    def pass_args(self, user_args: list[str]) -> list[str]:
        if self.lock:
            return user_args  # Todo add lock decorator
        regex_rule = r'{}[=|\ ]\"?([^-][\w.,]*)\"?'.format(self.key)
        regex_match = re.findall(regex_rule, ' '.join(user_args))

        if not regex_match:
            return user_args

        self.values = list(regex_match)

        # Remove acquired values
        remove_tag = str(uuid.uuid4()) * 2  # Provides true uniqueness
        h = user_args.copy()
        for i, arg in enumerate(h.copy()):
            if arg == self.key:
                h[i] = remove_tag
                continue
            h[i] = re.sub(regex_rule, remove_tag, arg)
        for i, arg in enumerate(h.copy()):
            if i > 0:
                if arg in self.values and h[i - 1] == remove_tag:
                    h[i] = remove_tag
        h = [k for k in h if k != remove_tag]
        self.lock = True
        return h

    def __repr__(self):
        return f'<Value of {self.key} has value {self.value} ({self.lock=})>'
