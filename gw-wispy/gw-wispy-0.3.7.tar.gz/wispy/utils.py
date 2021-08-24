from tomlkit import parse
from tomlkit import dumps


def recursive_dict_print(d, depth=0, print_fn=print):
    """recursively print dictionary

    Args:
        d ([dictionary]): [description]
        depth (int, optional): [description]. Defaults to 0.
        print_fn ([type], optional): [description]. Defaults to print.
    """

    for k, v in sorted(d.items(), key=lambda x: x[0]):
        if isinstance(v, dict):
            print_fn("\t" * depth + f"{k}:")
            recursive_dict_print(v, depth + 1, print_fn)
        else:
            print_fn("\t" * depth + f"{k}: {v}")


def read_and_parse_toml(toml_file):
    with open(toml_file, "r") as f:
        text = f.read()

    doc = parse(text)
    return doc


def write_string_to_file(string, filename):
    with open(filename, "w") as f:
        f.write(string)