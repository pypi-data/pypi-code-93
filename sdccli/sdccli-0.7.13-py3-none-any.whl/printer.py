import json
from prettytable import PrettyTable, PLAIN_COLUMNS


def print_list(lst, keys):
    t = PrettyTable(keys)
    t.set_style(PLAIN_COLUMNS)
    t.align = 'l'

    for item in lst:
        values = [item[key]
                  if key in item else ""
                  for key in keys]
        t.add_row(values)
    print(t.get_string())


def print_item(item, keys):
    for key in keys:
        if key in item:
            if (item[key] and (isinstance(item[key], list) and isinstance(item[key][0], dict))
                    or isinstance(item[key], dict)):
                print(key + ":")
                for line in json.dumps(item[key], indent=2).split('\n'):
                    print("    " + line)
            else:
                print("{:25} {}".format(key + ":", item[key]))
