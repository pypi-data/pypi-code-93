from collections.abc import Mapping
from csv import DictReader
import pandas as pd
import json
from Accuinsight.modeler.core.Run.RunInfo.RunInfo import get_current_run
from Accuinsight.modeler.core.LcConst.LcConst import RUN_OBJ_CSV_PATH, RUN_BASE_PATH, RUN_RESULT_PATH, \
    RUN_MODEL_VISUAL_CSV_PATH, RUN_PREFIX_PATH, RUN_MODEL_JSON_PATH
from Accuinsight.modeler.protos.life_cycle_pb2 import LcMetric, LcParam

# get parameter path with run type
# get metric path with run type


def _get_current_run():
    # {'run_name': 'keras',
    #  'json_path': 'model-info-json/keras_nn-1.json',
    #  'csv_path': 'for-visual-csv/keras_nn-history-1.csv'}

    return get_current_run()


def load_keras_parameter():
    run_info_json = _get_current_run()

    run_result_path = run_info_json[RUN_RESULT_PATH]
    base_path = run_result_path[RUN_BASE_PATH]
    prefix_path = run_result_path[RUN_PREFIX_PATH]
    json_path = run_result_path[RUN_MODEL_JSON_PATH]
    param_path = ''.join([base_path, prefix_path, json_path])

    with open(param_path) as json_file:
        param_json_data = json.load(json_file)

    return param_json_data


def _read_csv_with_pandas():
    run_info_json = _get_current_run()
    csv_path = run_info_json[RUN_BASE_PATH] + 'results-keras/' + run_info_json[RUN_OBJ_CSV_PATH]
    # csv_data = pd.read_csv(csv_path,
    #                        sep=';', index_col='epoch')

    return pd.read_csv(csv_path, sep=';', index_col=0, squeeze=True, header=None).to_dict()


def _read_csv_with_csv():
    column_dict = {}

    run_info_json = _get_current_run()

    run_result_path = run_info_json[RUN_RESULT_PATH]
    base_path = run_result_path[RUN_BASE_PATH]
    prefix_path = run_result_path[RUN_PREFIX_PATH]
    csv_path = run_result_path[RUN_MODEL_VISUAL_CSV_PATH]

    csv_path = ''.join([base_path, prefix_path, csv_path])

    with open(csv_path, 'r') as read_csv:
        csv_dict_reader = DictReader(read_csv, delimiter=';')
        column_names = csv_dict_reader.fieldnames

        for row in csv_dict_reader:
            for col_name in column_names:
                column_dict.setdefault(col_name, []).append(row[col_name])

    return column_dict


def load_keras_metric():
    # csv_data = _read_csv_with_pandas()
    column_dict = _read_csv_with_csv()

    result_dict = {'metrics': []}
    for key in column_dict:
        if key != 'epoch':
            result_dict['metrics'].append({'key': key, 'values': column_dict[key], 'timestamp': column_dict['epoch'], 'steps': column_dict['epoch']})

    return result_dict


def parse_keras_metric():
    metric_data = load_keras_metric()
    metrics = metric_data['metrics']

    grpc_metrics = []

    for item in metrics:
        metric = LcMetric(
                key=item['key'],
                values=item['values'],
                timestamp=item['timestamp'],
                steps=item['steps']
            )
        grpc_metrics.append(metric)
    return grpc_metrics


def _parse_optimizer_info(param_data):
    grpc_params = []
    optimizer_info = param_data['optimizer_info']
    if isinstance(optimizer_info, Mapping):
        for k, v in optimizer_info.items():
            optimizer = LcParam(
                key='type_of_optimizer',
                value=str(k)
            )
            grpc_params.append(optimizer)
            if isinstance(v, Mapping):
                for k, v in v.items():
                    param = LcParam(
                        key=k,
                        value=str(v)
                    )
                    grpc_params.append(param)
    return grpc_params


def parse_keras_parameter():
    param_data = load_keras_parameter()

    dummy_data = {
        'model_description': 'keras test',
        'logging_time': '2020-05-06 10:30:50',
        'run_id': '9FCEF776-D830-4353-8961-144491DC03CC',
        'model_type': 'keras_nn',
        'optimizer_info': {
            'RMSprop': {
                'learning_rate': 9.999999747378752e-05,
                'rho': 0.8999999761581421,
                'decay': 0.0,
                'epsilon': 1e-07
            }
        },
        'time_delta': '0:00:14.912202'
    }

    return _parse_optimizer_info(param_data)


def parse_run_result():
    result_dict = {'metrics': None, 'params': None, 'visual': None}

    metric_data = parse_keras_metric()
    parameter_data = parse_keras_parameter()

    result_dict['params'] = parameter_data
    result_dict['metrics'] = metric_data
    return result_dict

