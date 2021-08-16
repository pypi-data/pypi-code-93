import re

ARGS_PATTERN = re.compile("--([a-zA-Z0-9_]+)(?:=(.+))?")


def convert_args_to_dict(args):
    positional = []
    named = {}
    for x in args:
        match = ARGS_PATTERN.match(x)
        if match:
            named[match.group(1)] = match.group(2) or ""
        else:
            positional.append(x)
    escape_spaces = [x if " " not in x else f'"{x}"' for x in positional]
    arg_zero = " ".join(escape_spaces)
    positional = [arg_zero] + positional
    positional_dict = {f"_{i}": value for i, value in enumerate(positional)}
    return {**positional_dict, **named}
