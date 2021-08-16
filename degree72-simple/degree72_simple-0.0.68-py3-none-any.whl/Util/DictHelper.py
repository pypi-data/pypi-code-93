

# to find dict in a dict
def find_dict(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find_dict(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                if isinstance(d, dict):
                    for result in find_dict(key, d):
                        yield result

# to find dict in a dict key = value
def find_dict2(key, val, dictionary):
    for k, v in dictionary.items():
        if k == key and v == val:
            yield dictionary
        elif isinstance(v, dict):
            for result in find_dict2(key, val, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                if isinstance(d, dict):
                    for result in find_dict2(key, val, d):
                        yield result


def extract_dict(dict_input: dict, keys: list):
    dict_output = {}
    for each in keys:
        if isinstance(each, tuple):
            key_input = each[0]
            if '.' in key_input:
                nodes = key_input.split('.')
                temp = dict_input.get(nodes[0])
                for node in nodes[1:]:
                    temp = temp.get(node)
                value = temp
            else:
                value = dict_input.get(key_input)
            key_output = each[1]
        else:
            key_output = each
            value = dict_input.get(each, None)

        dict_output[key_output] = value
    return dict_output


if __name__ == '__main__':
    dict_input = {'a': {'b': {'c': {'d': 'test'}}}}
    extract_dict(dict_input, [('a.b.c.d', 'result')])