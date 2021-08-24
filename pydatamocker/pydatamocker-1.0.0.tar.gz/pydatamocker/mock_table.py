from .util.data import load_data, write_dataframe, load_json, write_json
from .builder import build_dataframe
from .util.collections import dedup_list, list_diff


def _config_column_order(specified, fields_dict):
    if not specified or len(specified) < 1:
        return fields_dict
    spec_dedup = dedup_list(specified)
    order = spec_dedup + list_diff(fields_dict.keys(), spec_dedup)
    return {key: fields_dict[key] for key in order}


class MockTable:

    def __init__(self, name: str, config = None) -> None:
        self.name = name
        self.dataframe = None
        if config:
            self.fields_describe = load_json(config)
        else:
            self.fields_describe = { 'fields': dict() }

    def dump_config(self, path, pretty=True, indent=2):
        write_json(self.fields_describe, path, pretty, indent)

    def add_field(self, name: str, mock_type:str, **props):
        self.fields_describe['fields'][name] = {
            'mock_type': mock_type,
            'props': props
        }
        return self

    def add_fields(self, fields_dict: dict):
        self.fields_describe['fields'].update(fields_dict)
        return self

    def add_table(self, path: str):
        data = load_data(path)
        columns = data.columns
        for col in columns:
            self.fields_describe['fields'][col] = {'mock_type': 'table', 'props': { 'path': path }}
        return self

    def add_lookup(self, mock_table, fields):
        for field in fields:
            self.fields_describe['fields'][field] = {
                'mock_type': 'mock_reference',
                'props': {
                    'mock_table': mock_table
                }
            }
        return self

    def sample(self, size: int):
        self.dataframe = build_dataframe(self.fields_describe, size)
        return self

    def get_dataframe(self):
        return self.dataframe.copy()

    def dump(self, path):
        if not path:
            raise ValueError('Path must be specified')
        write_dataframe(path, self.dataframe)

    def set_column_order(self, order):
        self.fields_describe['fields'] = _config_column_order(order, self.fields_describe['fields'])
        return self

    def col(self, col_s):
        return self.dataframe[col_s]

    def __str__(self):
        return self.dataframe.__str__()

    def __repr__(self):
        return self.dataframe.__repr__()
