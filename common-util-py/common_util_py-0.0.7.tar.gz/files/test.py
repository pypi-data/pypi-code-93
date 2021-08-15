import json_file

try:
    json_file.update('foo.json', 'key', 'value')

    print(json_file.get_all('foo.json'))

    print(json_file.get_value('foo.json', 'key'))
    print(json_file.get_value('foo.json', 'key1'))

    json_file.create_json_file('new.json', 'test.json')
except Exception as e:
    raise RuntimeError('unable to read or write file {}'.format('foo.json')) from e

