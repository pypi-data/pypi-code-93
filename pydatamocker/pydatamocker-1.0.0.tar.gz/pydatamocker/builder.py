from pandas import DataFrame, concat
from .mocker import get_config
from .types.dataset import get_dataset_sample, get_table_sample, DATASET_KEYS
from .types.number import get_sample as num_sample, TYPES as NUMTYPES
from .types.datetime import get_sample as time_sample
from .types.enum import get_sample as choice_sample, get_dependent_sample as dep_choice_sample


class _SampleCache:

    def __init__(self) -> None:
        self.data = {}

    def get_sample(self, mock_table, size: int):
        sample = self.data.get(mock_table.name)
        if sample is None or len(sample) != size:
            sample = mock_table.get_dataframe().sample(n=size, replace=True).reset_index(drop=True)
            self.data[mock_table.name] = sample
        return sample


_sample_cache = _SampleCache()


def get_sample(field_name: str, mock_type: str, size: int, accum_df: DataFrame = None, **props):
    if mock_type in DATASET_KEYS:
        return get_dataset_sample(mock_type, size)
    elif mock_type in NUMTYPES:
        return num_sample(mock_type, size, **props)
    elif mock_type == 'enum':
        controller = props.get('controller')
        if controller is None:
            return choice_sample(size, **props)
        else:
            return dep_choice_sample(accum_df[controller], field_name, **props)
    elif mock_type in { 'date', 'datetime' }:
        return time_sample(mock_type, size, **props)
    elif mock_type == 'table':
        return get_table_sample(props['path'], field_name, size)
    elif mock_type == 'mock_reference':
        return _sample_cache.get_sample(props['mock_table'], size)[field_name]
    else:
        raise ValueError('Unsupported type')


def build_dataframe(fields_describe: dict, size: int) -> DataFrame:
    df = None
    report_progress = get_config('report_progress')
    for field, field_spec in fields_describe['fields'].items():
        report_progress and print('Sampling', field, '...')
        sample = get_sample(field, field_spec['mock_type'], size, df, **field_spec['props'])
        sample.name = sample.name or field
        df = concat([df, sample], axis=1)
    report_progress and print('Done!')
    return df
