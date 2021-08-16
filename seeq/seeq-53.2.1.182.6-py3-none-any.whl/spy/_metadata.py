import datetime
import json
import re

import pandas as pd
import numpy as np

from seeq.base.seeq_names import *
from seeq.sdk import *
from seeq.sdk.rest import ApiException

from seeq.spy import _common
from seeq.spy import _login

from seeq.spy._errors import *
from seeq.spy._common import Status
from seeq.spy._common import EMPTY_GUID


def push(metadata, workbook_id, datasource_output, archive, errors, status):
    items_api = ItemsApi(_login.client)
    trees_api = TreesApi(_login.client)
    datasources_api = DatasourcesApi(_login.client)

    metadata_df = metadata  # type: pd.DataFrame

    timer = _common.timer_start()

    sync_token = datetime.datetime.utcnow().isoformat()

    status_columns = [
        'Signal',
        'Scalar',
        'Condition',
        'Threshold Metric',
        'Asset',
        'Relationship',
        'Overall',
        'Time'
    ]

    status_dict = dict()
    for status_column in status_columns:
        status_dict[status_column] = 0

    status.df = pd.DataFrame([status_dict], index=['Items pushed'])

    status.update('Pushing metadata to datasource <strong>%s [%s]</strong> scoped to workbook ID '
                  '<strong>%s</strong>' % (
                      datasource_output.name, datasource_output.datasource_id, workbook_id),
                  Status.RUNNING)

    total = len(metadata_df)

    def _print_push_progress():
        status.df['Time'] = _common.timer_elapsed(timer)
        status.update('Pushing metadata to datasource <strong>%s [%s]</strong> scoped to workbook ID '
                      '<strong>%s</strong>' % (
                          datasource_output.name, datasource_output.datasource_id, workbook_id),
                      Status.RUNNING)

    flush_now = False
    cache = dict()
    roots = dict()
    batch_size = 1000
    put_signals_input = PutSignalsInputV1()
    put_signals_input.signals = list()
    put_scalars_input = PutScalarsInputV1()
    put_scalars_input.scalars = list()
    condition_batch_input = ConditionBatchInputV1()
    condition_batch_input.conditions = list()
    threshold_metric_inputs = list()
    asset_batch_input = AssetBatchInputV1()
    asset_batch_input.assets = list()
    tree_batch_input = AssetTreeBatchInputV1()
    tree_batch_input.relationships = list()
    tree_batch_input.parent_host_id = datasource_output.id
    tree_batch_input.child_host_id = datasource_output.id
    last_scalar_datasource = None

    if not metadata_df.index.is_unique:
        raise SPyRuntimeError("The metadata DataFrame's index must be unique. Use metadata.reset_index(drop=True, "
                              "inplace=True) before passing in to spy.push().")

    # Make sure the columns of the dataframe can accept anything we put in them since metadata_df might have specific
    # dtypes.
    push_results_df = metadata_df.copy().astype(object)
    if 'Type' not in push_results_df.columns:
        push_results_df['Type'] = pd.Series(np.nan, dtype='object')

    # Workbooks will get processed outside of this function
    push_results_df = push_results_df[~push_results_df['Type'].isin(['Workbook'])]

    if 'Push Result' in push_results_df:
        push_results_df = push_results_df.drop(columns=['Push Result'])

    while True:
        dependencies_not_found = list()
        at_least_one_item_created = False

        for index, row in push_results_df.iterrows():
            if 'Push Result' in row and not pd.isna(row['Push Result']):
                continue

            status.df['Overall'] += 1

            try:
                flush_now, last_scalar_datasource = \
                    _process_push_row(asset_batch_input, cache, condition_batch_input, status, datasource_output,
                                      flush_now, index, last_scalar_datasource, push_results_df, put_scalars_input,
                                      put_signals_input, roots, row, sync_token, tree_batch_input,
                                      workbook_id, threshold_metric_inputs, errors)

            except SPyDependencyNotFound as e:
                dependencies_not_found.append((index, e))
                continue

            except Exception as e:
                if errors == 'raise':
                    raise

                total -= 1
                push_results_df.at[index, 'Push Result'] = str(e)
                continue

            at_least_one_item_created = True

            if int(status.df['Overall']) % batch_size == 0 or flush_now:
                _print_push_progress()

                _flush(put_signals_input, put_scalars_input, condition_batch_input, threshold_metric_inputs,
                       asset_batch_input, tree_batch_input, push_results_df, errors)

                flush_now = False

        _print_push_progress()

        _flush(put_signals_input, put_scalars_input, condition_batch_input, threshold_metric_inputs,
               asset_batch_input, tree_batch_input, push_results_df, errors)

        if len(dependencies_not_found) == 0:
            break

        if not at_least_one_item_created:
            for not_found_index, not_found_data_id in dependencies_not_found:
                push_results_df.at[not_found_index, 'Push Result'] = 'Could not find dependency %s' % not_found_data_id

            if errors == 'raise':
                raise SPyRuntimeError('Could not find all dependencies -- check "Push Result" column for errors')

            break

    for asset_input in roots.values():
        results = items_api.search_items(filters=['Datasource Class==%s && Datasource ID==%s && Data ID==%s' % (
            datasource_output.datasource_class, datasource_output.datasource_id,
            asset_input.data_id)])  # type: ItemSearchPreviewPaginatedListV1
        if len(results.items) == 0:
            raise SPyRuntimeError('Root item "%s" not found' % asset_input.name)
        item_id_list = ItemIdListInputV1()
        item_id_list.items = [results.items[0].id]
        trees_api.move_nodes_to_root_of_tree(body=item_id_list)

    if archive:
        status.df['Time'] = _common.timer_elapsed(timer)
        status.update('Archiving obsolete items in datasource <strong>%s [%s]</strong>' % (
            datasource_output.name, datasource_output.datasource_id),
            Status.RUNNING)

        datasource_clean_up_input = DatasourceCleanUpInputV1()
        datasource_clean_up_input.sync_token = sync_token
        datasources_api.clean_up(id=datasource_output.id, body=datasource_clean_up_input)

    status.df['Time'] = _common.timer_elapsed(timer)
    status.update('Pushed metadata successfully to datasource <strong>%s [%s]</strong> scoped to workbook ID '
                  '<strong>%s</strong>' % (datasource_output.name,
                                           datasource_output.datasource_id,
                                           workbook_id),
                  Status.SUCCESS)

    return push_results_df


def _process_push_row(asset_batch_input, cache, condition_batch_input, status, datasource_output, flush_now, index,
                      last_scalar_datasource, push_results_df, put_scalars_input, put_signals_input, roots, row,
                      sync_token, tree_batch_input, workbook_id, threshold_metric_inputs, errors):
    d = row.to_dict()

    if _common.present(d, 'Path'):
        d['Path'] = _common.sanitize_path_string(d['Path'])

    if not _common.present(d, 'Name'):
        raise SPyRuntimeError('Metadata must have a "Name" column.')

    if _common.get(d, 'Reference') is True:
        if not _common.present(d, 'ID'):
            raise SPyRuntimeError('"ID" column required when "Reference" column is True')
        _build_reference(d)

    d['Scoped To'] = workbook_id

    if not _common.present(d, 'Type') or not _is_handled_type(d['Type']):
        if not _common.present(d, 'Formula'):
            _common.raise_or_catalog(errors, df=push_results_df, column='Push Result', index=index,
                                     exception_type=SPyRuntimeError,
                                     message='Items with no valid type specified cannot be pushed unless they are '
                                             'calculations. "Formula" column is required for such items.')
        else:
            formula = _common.get(d, 'Formula')
            if _common.present(d, 'Formula Parameters'):
                formula_parameters = _process_formula_parameters(_common.get(d, 'Formula Parameters'),
                                                                 workbook_id,
                                                                 push_results_df)
            else:
                formula_parameters = []

            try:
                formulas_api = FormulasApi(_login.client)
                formula_compile_output = formulas_api.compile_formula(formula=formula, parameters=formula_parameters)
                if formula_compile_output.errors or formula_compile_output.return_type == '':
                    _common.raise_or_catalog(errors, df=push_results_df, column='Push Result', index=index,
                                             exception_type=SPyRuntimeError,
                                             message=f'Formula compilation failed with message: '
                                                     f'{formula_compile_output.status_message}')
                    return flush_now, last_scalar_datasource
                else:
                    d['Type'] = formula_compile_output.return_type
                    push_results_df.at[index, 'Type'] = formula_compile_output.return_type
            except ApiException as e:
                _common.raise_or_catalog(errors, df=push_results_df, column='Push Result', index=index,
                                         e=e)

    if _common.present(push_results_df.loc[index], 'Push Result'):
        return flush_now, last_scalar_datasource

    scoped_data_id = get_scoped_data_id(d, workbook_id)
    if not _common.present(d, 'Datasource Class'):
        d['Datasource Class'] = datasource_output.datasource_class

    if not _common.present(d, 'Datasource ID'):
        d['Datasource ID'] = datasource_output.datasource_id

    if 'Signal' in d['Type']:
        signal_input = SignalInputV1() if _common.present(d, 'ID') else SignalWithIdInputV1()

        dict_to_signal_input(d, signal_input)

        signal_input.formula_parameters = _process_formula_parameters(signal_input.formula_parameters,
                                                                      workbook_id,
                                                                      push_results_df)
        if len(signal_input.formula_parameters) > 0:
            push_results_df.at[index, 'Formula Parameters'] = signal_input.formula_parameters

        if signal_input.formula:
            # There are lots of calculated properties that must be None for Appserver to accept our input
            signal_input.maximum_interpolation = None
            signal_input.interpolation_method = None
            signal_input.key_unit_of_measure = None
            signal_input.value_unit_of_measure = None

        if _common.present(d, 'ID'):
            status.df['Signal'] += 1

            # Unfortunately we can't use the _set_item_properties(d) function like we can for Scalar and Condition
            # because we are not allowed to directly set the Value Unit Of Measure.
            try:
                signals_api = SignalsApi(_login.client)
                try:
                    signal_output = signals_api.put_signal(id=d['ID'], body=signal_input)
                except ApiException as e:
                    if SeeqNames.API.ErrorMessages.attempted_to_set_scope_on_a_globally_scoped_item in str(e):
                        # This handles CRAB-25450 by forcing global scope if we encounter the error.
                        signal_input.scoped_to = None
                        signal_output = signals_api.put_signal(id=d['ID'], body=signal_input)
                    else:
                        raise

                _push_ui_config(signal_input, signal_output)
                push_results_df.at[index, 'Push Result'] = 'Success'
                push_results_df.at[index, 'ID'] = signal_output.id
                push_results_df.at[index, 'Type'] = signal_output.type
            except ApiException as e:
                _common.raise_or_catalog(errors, df=push_results_df, index=index, column='Push Result', e=e)
        else:
            signal_input.datasource_class = d['Datasource Class']
            signal_input.datasource_id = d['Datasource ID']
            signal_input.data_id = scoped_data_id
            signal_input.sync_token = sync_token
            setattr(signal_input, 'dataframe_index', index)
            status.df['Signal'] += _add_no_dupe(put_signals_input.signals, signal_input)

    elif 'Scalar' in d['Type']:
        scalar_input = ScalarInputV1()

        dict_to_scalar_input(d, scalar_input)

        scalar_input.parameters = _process_formula_parameters(scalar_input.parameters, workbook_id, push_results_df)
        if len(scalar_input.parameters) > 0:
            push_results_df.at[index, 'Formula Parameters'] = scalar_input.parameters

        if _common.present(d, 'ID'):
            status.df['Scalar'] += 1
            _set_item_properties(d)
        else:
            put_scalars_input.datasource_class = d['Datasource Class']
            put_scalars_input.datasource_id = d['Datasource ID']
            scalar_input.data_id = scoped_data_id
            scalar_input.sync_token = sync_token
            setattr(scalar_input, 'dataframe_index', index)
            status.df['Scalar'] += _add_no_dupe(put_scalars_input.scalars, scalar_input)

            # Since with scalars we have to put the Datasource Class and Datasource ID on the batch, we have to
            # recognize if it changed and, if so, flush the current batch.
            if last_scalar_datasource is not None and \
                    last_scalar_datasource != (d['Datasource Class'], d['Datasource ID']):
                flush_now = True

            last_scalar_datasource = (d['Datasource Class'], d['Datasource ID'])

    elif 'Condition' in d['Type']:
        condition_input = ConditionInputV1()
        dict_to_condition_input(d, condition_input)

        condition_input.parameters = _process_formula_parameters(condition_input.parameters, workbook_id,
                                                                 push_results_df)
        if len(condition_input.parameters) > 0:
            push_results_df.at[index, 'Formula Parameters'] = condition_input.parameters

        if condition_input.formula is None and condition_input.maximum_duration is None:
            raise SPyRuntimeError('"Maximum Duration" column required for stored conditions')

        if _common.present(d, 'ID'):
            status.df['Condition'] += 1
            _set_item_properties(d)
        else:
            condition_input.datasource_class = d['Datasource Class']
            condition_input.datasource_id = d['Datasource ID']
            condition_input.data_id = scoped_data_id
            condition_input.sync_token = sync_token
            setattr(condition_input, 'dataframe_index', index)
            status.df['Condition'] += _add_no_dupe(condition_batch_input.conditions, condition_input)

    elif d['Type'] == 'Asset':
        asset_input = AssetInputV1()
        dict_to_asset_input(d, asset_input)
        asset_input.data_id = scoped_data_id
        asset_input.sync_token = sync_token
        setattr(asset_input, 'dataframe_index', index)
        status.df['Asset'] += _add_no_dupe(asset_batch_input.assets, asset_input, overwrite=True)
        asset_batch_input.host_id = datasource_output.id

    elif 'Metric' in d['Type']:
        threshold_metric_input = ThresholdMetricInputV1()
        dict_to_threshold_metric_input(d, threshold_metric_input)
        _set_threshold_levels_from_system(threshold_metric_input)
        threshold_metric_input.measured_item = _item_id_from_parameter_value(
            threshold_metric_input.measured_item, workbook_id, push_results_df)
        if threshold_metric_input.bounding_condition:
            threshold_metric_input.bounding_condition = _item_id_from_parameter_value(
                threshold_metric_input.bounding_condition, workbook_id, push_results_df)
        threshold_metric_input.thresholds = _convert_thresholds_dict_to_input(threshold_metric_input.thresholds,
                                                                              workbook_id, push_results_df)

        if _common.present(d, 'Statistic'):
            threshold_metric_input.aggregation_function = _common.statistic_to_aggregation_function(d['Statistic'])
        threshold_metric_input.datasource_class = d['Datasource Class']
        threshold_metric_input.datasource_id = d['Datasource ID']
        threshold_metric_input.data_id = scoped_data_id
        setattr(threshold_metric_input, 'dataframe_index', index)
        status.df['Threshold Metric'] += 1
        threshold_metric_inputs.append(threshold_metric_input)
        push_results_df.at[index, 'Push Result'] = 'Success'

    path = _determine_path(d)
    if path:
        _reify_path(path, workbook_id, datasource_output, scoped_data_id, cache, roots,
                    asset_batch_input, tree_batch_input, sync_token, status)
    return flush_now, last_scalar_datasource


def _push_ui_config(input_object, item):
    if not hasattr(input_object, '_ui_config'):
        return

    items_api = ItemsApi(_login.client)
    items_api.set_property(id=item.id,
                           property_name='UIConfig',
                           body=PropertyInputV1(value=getattr(input_object, '_ui_config')))


def _set_item_properties(d):
    items_api = ItemsApi(_login.client)
    ignored_properties = ['ID', 'Type', 'Formula', 'Formula Parameters', 'Key Unit Of Measure', 'Metadata Properties',
                          'Scoped To']
    props = [
        ScalarPropertyV1(name=_name, value=_value) for _name, _value in d.items()
        if _name not in ignored_properties and (isinstance(_value, list) or not pd.isna(_value))
    ]

    item_output = items_api.set_properties(id=d['ID'], body=props)
    if item_output.scoped_to is not None and 'Scoped To' in d:
        # This handles CRAB-25450 by only attempting to set scope if the item is not already globally scoped
        scoped_to = _common.get(d, 'Scoped To')
        if scoped_to is not None:
            items_api.set_scope(id=d['ID'], workbook_id=scoped_to)
        else:
            items_api.set_scope(id=d['ID'])

    if _common.present(d, 'Formula'):
        items_api.set_formula(id=d['ID'], body=FormulaUpdateInputV1(
            formula=d['Formula'], parameters=d['Formula Parameters']))


def _determine_path(d):
    path = list()
    if _common.present(d, 'Path'):
        path.append(_common.get(d, 'Path'))

    _type = _common.get(d, 'Type')

    if _type != 'Asset' and _common.present(d, 'Asset'):
        path.append(_common.get(d, 'Asset'))

    return _common.path_list_to_string(path)


def get_scoped_data_id(d, workbook_id):
    path = _determine_path(d)

    if not _common.present(d, 'Data ID'):
        if path:
            scoped_data_id = '%s >> %s' % (path, d['Name'])
        else:
            scoped_data_id = d['Name']
    else:
        scoped_data_id = d['Data ID']

    if not _is_scoped_data_id(scoped_data_id):
        if not _common.present(d, 'Type'):
            raise SPyRuntimeError('Type is required for all item definitions')

        guid = workbook_id if workbook_id else EMPTY_GUID

        _type = d['Type'].replace('Stored', '').replace('Calculated', '')

        # Need to scope the Data ID to the workbook so it doesn't collide with other workbooks
        scoped_data_id = '[%s] {%s} %s' % (guid, _type, str(scoped_data_id))

    return scoped_data_id.strip()


def _is_scoped_data_id(data_id):
    return re.match(r'^\[%s] {\w+}.*' % _common.GUID_REGEX, data_id) is not None


def _get_unscoped_data_id(scoped_data_id):
    return re.sub(r'^\[%s] {\w+}\s*' % _common.GUID_REGEX, '', scoped_data_id)


def _cleanse_attr(v):
    if isinstance(v, np.generic):
        # Swagger can't handle NumPy types, so we have to retrieve an underlying Python type
        return v.item()
    else:
        return v


def dict_to_input(d, _input, properties_attr, attr_map):
    lower_case_known_attrs = {k.lower(): k for k in attr_map.keys()}
    for k, v in d.items():
        if k.lower() in lower_case_known_attrs and k not in attr_map:
            raise SPyRuntimeError(f'Incorrect case used for known property: "{k}" should be '
                                  f'"{lower_case_known_attrs[k.lower()]}"')

        if k in attr_map:
            if attr_map[k] is not None:
                v = _common.get(d, k)
                if isinstance(v, list) or not pd.isna(v):
                    setattr(_input, attr_map[k], _cleanse_attr(v))
        elif properties_attr is not None:
            p = ScalarPropertyV1()
            p.name = _common.ensure_unicode(k)

            if p.name in RESERVED_ITEM_PROPERTIES or p.name in RESERVED_SPY_COLUMN_NAMES:
                continue

            uom = None
            if isinstance(v, dict):
                uom = _common.get(v, 'Unit Of Measure')
                v = _common.get(v, 'Value')
            else:
                v = _common.get(d, k)

            if not pd.isna(v):
                if isinstance(v, str) and p.name in ['Cache Enabled', 'Archived', 'Enabled', 'Unsearchable']:
                    # Ensure that these are booleans. Otherwise Seeq Server will silently ignore them.
                    v = (v.lower() == 'true')

                p.value = _cleanse_attr(_common.ensure_unicode(v))

                if uom is not None:
                    p.unit_of_measure = _common.ensure_unicode(uom)
                _properties = getattr(_input, properties_attr)
                if _properties is None:
                    _properties = list()
                _properties.append(p)
                setattr(_input, properties_attr, _properties)

    if _common.present(d, 'UIConfig'):
        ui_config = _common.get(d, 'UIConfig')
        if isinstance(ui_config, dict):
            ui_config = json.dumps(ui_config)
        setattr(_input, '_ui_config', ui_config)


def _set_threshold_levels_from_system(threshold_input):
    # type: (ThresholdMetricInputV1) -> None
    """
    Read the threshold limits from the systems endpoint and update the values in the threshold limits. Allows users
    to set thresholds as those defined in the system endpoint such as 'Lo', 'LoLo', 'Hi', 'HiHi', etc.

    :param threshold_input: A Threshold Metric input with a dict in the thresholds with keys of the priority level and
    values of the threshold. Keys are either a numeric value of the threshold, or strings contained in the
    systems/configuration. Values are either scalars or metadata dataframes. If a key is a string that maps to a number
    that is already used in the limits, a RuntimeError will be raised.
    :return: The threshold input with a limits dict with the string values replaced with numbers.
    """

    if not isinstance(threshold_input.thresholds, dict):
        return

    system_api = SystemApi(_login.client)

    # get the priority names and their corresponding levels
    system_settings = system_api.get_server_status()  # type: ServerStatusOutputV1
    priority_levels = {p.name: p.level for p in system_settings.priorities}

    # noinspection PyTypeChecker
    thresholds = threshold_input.thresholds  # type: dict
    updated_threshold_limits = dict()

    def get_numeric_threshold(threshold):
        # Returns an int representing a threshold priority level
        if isinstance(threshold, int):
            return threshold
        elif isinstance(threshold, str):
            threshold = threshold.split('#')[0].strip()
            if threshold in priority_levels:
                return priority_levels[threshold]
            else:
                try:
                    return int(threshold)
                except ValueError:
                    raise SPyRuntimeError(f'The threshold {threshold} could not be converted to an integer for metric '
                                          f'{threshold_input.name}')
        else:
            raise SPyRuntimeError(f'The threshold {threshold} is of invalid type {type(threshold)}')

    def get_color_code(threshold):
        # Extracts and returns the color code from a threshold if it exists
        if isinstance(threshold, str):
            parts = threshold.split('#')
            if len(parts) == 2:
                code = parts[1].strip()
                if not re.match(r'^[0-9a-fA-F]{6}$', code):
                    raise SPyRuntimeError(f'"#{code}" is not a valid color hex code')
                return code.lower()
            elif len(parts) > 2:
                raise SPyRuntimeError(f'Threshold "{k}" contains unknown formatting')
        return None

    for k, v in thresholds.items():
        numeric = get_numeric_threshold(k)
        color_code = get_color_code(k)

        if numeric in [get_numeric_threshold(threshold) for threshold in updated_threshold_limits]:
            raise SPyRuntimeError(
                f'Threshold "{k}" maps to a duplicate threshold value for metric {threshold_input.name}')

        updated_threshold = '#'.join([str(numeric), color_code]) if color_code is not None else str(numeric)
        updated_threshold_limits[updated_threshold] = v

    threshold_input.thresholds = updated_threshold_limits


def dict_to_datasource_input(d, datasource_input):
    dict_to_input(d, datasource_input, None, {
        'Name': 'name',
        'Description': 'description',
        'Datasource Name': 'name',
        'Datasource Class': 'datasource_class',
        'Datasource ID': 'datasource_id'
    })


def dict_to_asset_input(d, asset_input):
    dict_to_input(d, asset_input, 'properties', {
        'Type': None,
        'Name': 'name',
        'Description': 'description',
        'Datasource Class': 'datasource_class',
        'Datasource ID': 'datasource_id',
        'Data ID': 'data_id',
        'Scoped To': 'scoped_to'
    })


def dict_to_signal_input(d, signal_input):
    dict_to_input(d, signal_input, 'additional_properties', {
        'Type': None,
        'Cache ID': None,
        'Name': 'name',
        'Description': 'description',
        'Datasource Class': 'datasource_class',
        'Datasource ID': 'datasource_id',
        'Data ID': 'data_id',
        'Data Version Check': 'data_version_check',
        'Formula': 'formula',
        'Formula Parameters': 'formula_parameters',
        'Interpolation Method': 'interpolation_method',
        'Maximum Interpolation': 'maximum_interpolation',
        'Scoped To': 'scoped_to',
        'Key Unit Of Measure': 'key_unit_of_measure',
        'Value Unit Of Measure': 'value_unit_of_measure',
        'Number Format': 'number_format'
    })


def dict_to_scalar_input(d, scalar_input):
    dict_to_input(d, scalar_input, 'properties', {
        'Type': None,
        'Name': 'name',
        'Description': 'description',
        'Datasource Class': 'datasource_class',
        'Datasource ID': 'datasource_id',
        'Data ID': 'data_id',
        'Data Version Check': 'data_version_check',
        'Formula': 'formula',
        'Formula Parameters': 'parameters',
        'Scoped To': 'scoped_to',
        'Number Format': 'number_format'
    })


def dict_to_condition_input(d, signal_input):
    dict_to_input(d, signal_input, 'properties', {
        'Type': None,
        'Cache ID': None,
        'Name': 'name',
        'Description': 'description',
        'Datasource Class': 'datasource_class',
        'Datasource ID': 'datasource_id',
        'Data ID': 'data_id',
        'Data Version Check': 'data_version_check',
        'Formula': 'formula',
        'Formula Parameters': 'parameters',
        'Maximum Duration': 'maximum_duration',
        'Scoped To': 'scoped_to'
    })


def dict_to_capsule(d, capsule):
    dict_to_input(d, capsule, 'properties', {
        'Capsule Start': None,
        'Capsule End': None
    })


def dict_to_threshold_metric_input(d, metric_input):
    dict_to_input(d, metric_input, 'additional_properties', {
        'Type': None,
        'Name': 'name',
        'Duration': 'duration',
        'Bounding Condition Maximum Duration': 'bounding_condition_maximum_duration',
        'Period': 'period',
        'Thresholds': 'thresholds',
        'Measured Item': 'measured_item',
        'Number Format': 'number_format',
        'Bounding Condition': 'bounding_condition',
        'Metric Neutral Color': 'neutral_color',
        'Scoped To': 'scoped_to',
        'Aggregation Function': 'aggregation_function'
    })


def _handle_reference_uom(definition, key):
    if not _common.present(definition, key):
        return

    unit = definition[key]
    if _login.is_valid_unit(unit):
        if unit != 'string':
            definition['Formula'] += f".setUnits('{unit}')"
        else:
            definition['Formula'] += f".toString()"
    else:
        # This is the canonical place for unrecognized units
        definition[f'Source {key}'] = unit

    del definition[key]


def _build_reference_signal(definition):
    definition['Type'] = 'CalculatedSignal'
    definition['Formula'] = '$signal'

    if _common.present(definition, 'Interpolation Method'):
        definition['Formula'] += f".to{definition['Interpolation Method']}()"
        del definition['Interpolation Method']

    _handle_reference_uom(definition, 'Value Unit Of Measure')

    definition['Formula Parameters'] = 'signal=%s' % definition['ID']
    definition['Cache Enabled'] = False

    for key in ['ID', 'Datasource Class', 'Datasource ID', 'Data ID']:
        if _common.present(definition, key) and not _common.present(definition, 'Referenced ' + key):
            definition['Referenced ' + key] = definition[key]
            del definition[key]


def _build_reference_condition(definition):
    definition['Type'] = 'CalculatedCondition'
    definition['Formula'] = '$condition'
    definition['Formula Parameters'] = 'condition=%s' % definition['ID']
    definition['Cache Enabled'] = False

    for key in ['ID', 'Datasource Class', 'Datasource ID', 'Data ID', 'Unit Of Measure', 'Maximum Duration']:
        if _common.present(definition, key) and not _common.present(definition, 'Referenced ' + key):
            definition['Referenced ' + key] = definition[key]
            del definition[key]


def _build_reference_scalar(definition):
    definition['Type'] = 'CalculatedScalar'
    definition['Formula'] = '$scalar'
    definition['Formula Parameters'] = 'scalar=%s' % definition['ID']
    definition['Cache Enabled'] = False

    _handle_reference_uom(definition, 'Unit Of Measure')

    for key in ['ID', 'Datasource Class', 'Datasource ID', 'Data ID']:
        if _common.present(definition, key) and not _common.present(definition, 'Referenced ' + key):
            definition['Referenced ' + key] = definition[key]
            del definition[key]


def _build_reference(definition):
    {
        'StoredSignal': _build_reference_signal,
        'CalculatedSignal': _build_reference_signal,
        'StoredCondition': _build_reference_condition,
        'CalculatedCondition': _build_reference_condition,
        'CalculatedScalar': _build_reference_scalar
    }[definition['Type']](definition)


def _process_formula_parameters(parameters, workbook_id, push_results_df):
    if parameters is None:
        return list()

    if isinstance(parameters, str):
        parameters = [parameters]

    if isinstance(parameters, dict):
        pairs = parameters.items()

    elif isinstance(parameters, list):
        pairs = []
        for param_entry in parameters:
            if not isinstance(param_entry, str):
                raise SPyValueError(f'Formula Parameter entry {param_entry} has invalid type. Must be string.')
            try:
                k, v = param_entry.split('=')
                pairs.append((k, v))
            except ValueError:
                raise SPyValueError(
                    f'Formula Parameter entry "{param_entry}" not recognized. Must be "var=ID" or "var=Path".')

    else:
        raise SPyValueError(f'Formula Parameters have invalid type {type(parameters)}. Valid types are str, list, '
                            f'and dict.')

    processed_parameters = list()
    for k, v in pairs:
        # Strip off leading dollar-sign if it's there
        parameter_name = re.sub(r'^\$', '', k)
        try:
            parameter_id = _item_id_from_parameter_value(v, workbook_id, push_results_df)
        except (ValueError, TypeError) as e:
            raise SPyRuntimeError(f'Error processing {parameter_name}: {e}')
        processed_parameters.append('%s=%s' % (parameter_name, parameter_id))

    processed_parameters.sort(key=lambda param: param.split('=')[0])
    return processed_parameters


def _item_id_from_parameter_value(dict_value, workbook_id, push_results_df):
    if isinstance(dict_value, pd.DataFrame):
        if len(dict_value) == 0:
            raise SPyValueError('The parameter had an empty dataframe')
        if len(dict_value) > 1:
            raise SPyValueError('The parameter had multiple entries in the dataframe')
        dict_value = dict_value.iloc[0]

    if isinstance(dict_value, (dict, pd.Series)):
        if _common.present(dict_value, 'ID') and not _common.get(dict_value, 'Reference', default=False):
            return dict_value['ID']
        else:
            try:
                scoped_data_id = get_scoped_data_id(dict_value, workbook_id)
            except RuntimeError:
                # This can happen if the dependency didn't get pushed and therefore doesn't have a proper Type
                raise SPyDependencyNotFound(f'Item {dict_value} was never pushed (error code 1)')
            if 'Data ID' in push_results_df:
                pushed_row_i_need = push_results_df[push_results_df['Data ID'] == scoped_data_id]
                if not pushed_row_i_need.empty and _common.present(pushed_row_i_need.iloc[0], 'ID'):
                    return pushed_row_i_need.iloc[0]['ID']
                else:
                    raise SPyDependencyNotFound(f'Item {scoped_data_id} was never pushed (error code 2)')
            else:
                raise SPyDependencyNotFound(f'Item {scoped_data_id} was never pushed (error code 3)')

    elif isinstance(dict_value, str):
        if _common.is_guid(dict_value):
            return dict_value
        # Now treat string like a path
        path = _common.sanitize_path_string(dict_value)
        if 'Data ID' in push_results_df:
            # We query Data ID as opposed to Path/Name to ensure that workbook scope
            # is correct and that the dependency has already been pushed
            wb_index = push_results_df['Data ID'].str.startswith('[%s' % workbook_id if workbook_id else EMPTY_GUID,
                                                                 na=False)
            path_index = push_results_df['Data ID'].str.endswith(path, na=False)
            pushed_row_i_need = push_results_df[wb_index & path_index]
            if not pushed_row_i_need.empty and _common.present(pushed_row_i_need.iloc[0], 'ID'):
                return pushed_row_i_need.iloc[0]['ID']
            else:
                raise SPyDependencyNotFound(f'Item "{path}" was never pushed (error code 4)')
        else:
            raise SPyDependencyNotFound(f'Item "{path}" was never pushed (error code 3)')

    elif dict_value is None:
        raise SPyTypeError('A formula parameter is None, which is not allowed. Check your logic for assigning formula '
                           'parameters and, if you\'re using spy.assets.build(), look for optional Requirements that '
                           'are were not found.')
    else:
        raise SPyTypeError(f'Formula parameter type "{type(dict_value)}" not allowed. Must be DataFrame, Series, '
                           f'dict or ID string')


def _set_push_result_string(dfi, iuo, errors, push_results_df, items_api):
    result_string = 'Success'
    if isinstance(iuo, ItemUpdateOutputV1):
        if iuo.error_message is not None:
            if errors == 'raise':
                raise SPyRuntimeError('Error pushing "%s": %s' % (iuo.data_id, iuo.error_message))
            result_string = iuo.error_message
        else:
            push_results_df.at[dfi, 'Datasource Class'] = iuo.datasource_class
            push_results_df.at[dfi, 'Datasource ID'] = iuo.datasource_id
            push_results_df.at[dfi, 'Data ID'] = iuo.data_id
            push_results_df.at[dfi, 'ID'] = iuo.item.id
            push_results_df.at[dfi, 'Type'] = iuo.item.type
    elif isinstance(iuo, ThresholdMetricOutputV1):
        _item_output = items_api.get_item_and_all_properties(id=iuo.id)  # type: ItemOutputV1
        _item_properties = {p.name: p.value for p in _item_output.properties}
        push_results_df.at[dfi, 'Datasource Class'] = _item_properties['Datasource Class']
        push_results_df.at[dfi, 'Datasource ID'] = _item_properties['Datasource ID']
        push_results_df.at[dfi, 'Data ID'] = _item_properties['Data ID']
        push_results_df.at[dfi, 'ID'] = iuo.id
        push_results_df.at[dfi, 'Type'] = iuo.type
    else:
        raise SPyTypeError('Unrecognized output type from API: %s' % type(iuo))

    push_results_df.at[dfi, 'Push Result'] = result_string


def _process_batch_output(item_inputs, item_updates, errors, push_results_df, items_api):
    repost = False
    for i in range(0, len(item_inputs)):
        item_input = item_inputs[i]
        item_update_output = item_updates[i]  # type: ItemUpdateOutputV1

        if item_update_output.error_message and \
                SeeqNames.API.ErrorMessages.attempted_to_set_scope_on_a_globally_scoped_item in \
                item_update_output.error_message:
            # This handles CRAB-25450. Metadata that was posted prior to that bugfix may have a non-fixable
            # global-scope applied, so rather than error out, just repost with global-scope. This effectively
            # preserves status quo for those users.
            setattr(item_input, 'scoped_to', None)
            repost = True
            continue

        if not isinstance(item_input, AssetInputV1):
            _push_ui_config(item_input, item_update_output.item)

        if hasattr(item_input, 'dataframe_index'):
            _set_push_result_string(item_input.dataframe_index, item_update_output, errors, push_results_df, items_api)

    return repost


def _post_batch(post_function, item_inputs, errors, push_results_df, items_api):
    item_batch_output = post_function()
    repost = _process_batch_output(item_inputs, item_batch_output.item_updates, errors, push_results_df, items_api)
    if repost:
        # This means we're supposed to repost the batch because _process_batch_output() has modified the scoped_to
        # property on some items to overcome CRAB-25450. See test_metadata.test_crab_25450().
        item_batch_output = post_function()
        _process_batch_output(item_inputs, item_batch_output.item_updates, errors, push_results_df, items_api)


def _flush(put_signals_input, put_scalars_input, condition_batch_input, threshold_metric_inputs, asset_batch_input,
           tree_batch_input, push_results_df, errors):
    items_api = ItemsApi(_login.client)
    signals_api = SignalsApi(_login.client)
    scalars_api = ScalarsApi(_login.client)
    conditions_api = ConditionsApi(_login.client)
    assets_api = AssetsApi(_login.client)
    trees_api = TreesApi(_login.client)
    metrics_api = MetricsApi(_login.client)

    if len(put_signals_input.signals) > 0:
        _post_batch(lambda: signals_api.put_signals(body=put_signals_input), put_signals_input.signals, errors,
                    push_results_df, items_api)
        put_signals_input.signals = list()

    if len(put_scalars_input.scalars) > 0:
        _post_batch(lambda: scalars_api.put_scalars(body=put_scalars_input), put_scalars_input.scalars, errors,
                    push_results_df, items_api)
        put_scalars_input.scalars = list()

    if len(condition_batch_input.conditions) > 0:
        _post_batch(lambda: conditions_api.put_conditions(body=condition_batch_input), condition_batch_input.conditions,
                    errors, push_results_df, items_api)
        condition_batch_input.conditions = list()

    if len(threshold_metric_inputs) > 0:
        for tm in threshold_metric_inputs:
            # Check if the metric already exists
            metric_search = items_api.search_items(
                filters=['Datasource Class == {} && Datasource ID == {} && Data ID == {}'.format(tm.datasource_class,
                                                                                                 tm.datasource_id,
                                                                                                 tm.data_id),
                         '@includeUnsearchable'])
            if metric_search.total_results > 1:
                raise SPyRuntimeError('More than one metric had the data triplet {}, {}, {}'.format(tm.datasource_class,
                                                                                                    tm.datasource_id,
                                                                                                    tm.data_id))
            if metric_search.total_results == 1:
                tm_output = metrics_api.get_metric(id=metric_search.items[0].id)
                if tm_output.scoped_to is None and tm.scoped_to is not None:
                    # This handles CRAB-25450
                    tm.scoped_to = None

                tm_push_output = metrics_api.put_threshold_metric(id=metric_search.items[0].id,
                                                                  body=tm)
            else:
                tm_push_output = metrics_api.create_threshold_metric(body=tm)
                _add_data_properties(tm_push_output, tm.datasource_class, tm.datasource_id, tm.data_id)
            _set_push_result_string(tm.dataframe_index, tm_push_output, errors, push_results_df, items_api)

        threshold_metric_inputs.clear()

    if len(asset_batch_input.assets) > 0:
        _post_batch(lambda: assets_api.batch_create_assets(body=asset_batch_input), asset_batch_input.assets,
                    errors, push_results_df, items_api)
        asset_batch_input.assets = list()

    if len(tree_batch_input.relationships) > 0:
        trees_api.batch_move_nodes_to_parents(body=tree_batch_input)  # type: ItemBatchOutputV1
        tree_batch_input.relationships = list()


def _add_data_properties(item, datasource_class, datasource_id, data_id):
    """
    Add a property with a Data ID for items that do not take a data id in their input

    :param item: The output of item creation containing the item's seeq ID
    :param datasource_class: The datasource class to apply to the item
    :param datasource_id: The datasource id to apply to the item
    :param data_id: The data id to add to the item
    :return:
    """
    items_api = ItemsApi(_login.client)
    properties_input = [
        ScalarPropertyV1(unit_of_measure='string', name='Datasource Class', value=datasource_class),
        ScalarPropertyV1(unit_of_measure='string', name='Datasource ID', value=datasource_id),
        ScalarPropertyV1(unit_of_measure='string', name='Data ID', value=data_id)
    ]
    items_api.set_properties(id=item.id, body=properties_input)


def _convert_thresholds_dict_to_input(thresholds_dict, workbook_id, push_results_df):
    """
    Convert a dictionary with keys threshold levels and values of either scalars or metadata to a list of strings
    with level=value/ID of the threshold.

    :param thresholds_dict: A dictionary with keys of threshold levels and values of either number of metadata
    dataframes
    :return:  A list of strings 'level=value' or 'level=ID'
    """

    thresholds_list = list()
    if thresholds_dict:
        for k, v in thresholds_dict.items():
            if isinstance(v, pd.DataFrame) or isinstance(v, dict):
                thresholds_list.append(
                    '{}={}'.format(k, _item_id_from_parameter_value(v, workbook_id, push_results_df)))
            else:
                thresholds_list.append('{}={}'.format(k, v))
    return thresholds_list


def _add_no_dupe(lst, obj, attr='data_id', overwrite=False):
    for i in range(0, len(lst)):
        o = lst[i]
        if hasattr(o, attr):
            if getattr(o, attr) == getattr(obj, attr):
                if overwrite:
                    lst[i] = obj
                return 0

    lst.append(obj)
    return 1


def _is_handled_type(type_value):
    try:
        return 'Signal' in type_value \
               or 'Scalar' in type_value \
               or 'Condition' in type_value \
               or 'Metric' in type_value \
               or type_value == 'Asset'
    except TypeError:
        return False


def _reify_path(path, workbook_id, datasource_output, scoped_data_id, cache, roots, asset_batch_input,
                tree_batch_input, sync_token, status):
    path_items = _common.path_string_to_list(path)

    root_data_id = get_scoped_data_id({
        'Name': '',
        'Type': 'Asset'
    }, workbook_id)

    path_so_far = list()

    parent_data_id = root_data_id
    child_data_id = root_data_id
    for path_item in path_items:
        if len(path_item) == 0:
            raise SPyValueError('Path contains blank / zero-length segments: "%s"' % path)

        asset_input = AssetInputV1()
        asset_input.name = path_item
        asset_input.scoped_to = workbook_id
        asset_input.host_id = datasource_output.id
        asset_input.sync_token = sync_token

        tree_input = AssetTreeSingleInputV1()
        tree_input.parent_data_id = parent_data_id

        path_so_far.append(path_item)

        child_data_id = get_scoped_data_id({
            'Name': path_so_far[-1],
            'Path': _common.path_list_to_string(path_so_far[0:-1]),
            'Type': 'Asset'
        }, workbook_id)

        asset_input.data_id = child_data_id
        tree_input.child_data_id = child_data_id

        if asset_input.data_id not in cache:
            if tree_input.parent_data_id != root_data_id:
                status.df['Relationship'] += 1
                tree_batch_input.relationships.append(tree_input)
            else:
                roots[asset_input.data_id] = asset_input

            status.df['Asset'] += _add_no_dupe(asset_batch_input.assets, asset_input)

            cache[asset_input.data_id] = True

        parent_data_id = child_data_id

    tree_input = AssetTreeSingleInputV1()
    tree_input.parent_data_id = child_data_id
    tree_input.child_data_id = scoped_data_id
    status.df['Relationship'] += _add_no_dupe(tree_batch_input.relationships, tree_input, 'child_data_id')


def create_datasource(datasource=None):
    items_api = ItemsApi(_login.client)
    datasources_api = DatasourcesApi(_login.client)
    users_api = UsersApi(_login.client)

    datasource_input = _common.get_data_lab_datasource_input()
    if datasource is not None:
        if not isinstance(datasource, (str, dict)):
            raise SPyValueError('"datasource" parameter must be str or dict')

        if isinstance(datasource, str):
            datasource_input.name = datasource
            datasource_input.datasource_id = datasource_input.name
        else:
            if 'Datasource Name' not in datasource:
                raise SPyValueError(
                    '"Datasource Name" required for datasource. This is the specific data set being pushed. '
                    'For example, "Permian Basin Well Data"')

            if 'Datasource Class' in datasource:
                raise SPyValueError(
                    '"Datasource Class" cannot be specified for datasource. It will always be '
                    f'"{_common.DEFAULT_DATASOURCE_CLASS}".')

            dict_to_datasource_input(datasource, datasource_input)

        if datasource_input.datasource_id == _common.DEFAULT_DATASOURCE_ID:
            datasource_input.datasource_id = datasource_input.name

    datasource_output_list = datasources_api.get_datasources(datasource_class=datasource_input.datasource_class,
                                                             datasource_id=datasource_input.datasource_id,
                                                             limit=2)  # type: DatasourceOutputListV1

    if len(datasource_output_list.datasources) > 1:
        raise SPyRuntimeError(f'Multiple datasources found with class {datasource_input.datasource_class} '
                              f'and ID {datasource_input.datasource_id}')

    if len(datasource_output_list.datasources) == 1:
        return datasource_output_list.datasources[0]

    datasource_output = datasources_api.create_datasource(body=datasource_input)  # type: DatasourceOutputV1

    # Due to CRAB-23806, we have to immediately call get_datasource to get the right set of additional properties
    datasource_output = datasources_api.get_datasource(id=datasource_output.id)

    # We need to add Everyone with Manage permissions so that all users can push asset trees
    identity_preview_list = users_api.autocomplete_users_and_groups(query='Everyone')  # type: IdentityPreviewListV1
    everyone_user_group_id = None
    for identity_preview in identity_preview_list.items:  # type: IdentityPreviewV1
        if identity_preview.type == 'UserGroup' and \
                identity_preview.name == 'Everyone' and \
                identity_preview.datasource.name == 'Seeq' and \
                identity_preview.is_enabled:
            everyone_user_group_id = identity_preview.id
            break

    if everyone_user_group_id:
        items_api.add_access_control_entry(id=datasource_output.id, body=AceInputV1(
            identity_id=everyone_user_group_id,
            permissions=PermissionsV1(manage=True, read=True, write=True)
        ))

    return datasource_output


RESERVED_SPY_COLUMN_NAMES = [
    'Push Result', 'Push Count', 'Push Time',
    'Pull Result', 'Pull Count', 'Pull Time',
    'Build Path', 'Build Asset', 'Build Template', 'Build Result',
    'ID', 'Path', 'Asset', 'Object', 'Asset Object'
]

# This must be kept in sync with RESERVED_ITEM_PROPERTIES in StoredItemOutput.java
RESERVED_ITEM_PROPERTIES = [
    'GUID', 'Datasource Class', 'Datasource ID', 'Data ID', 'Name', 'Description',
    'Interpolation Method', 'Maximum Duration', 'Maximum Interpolation',
    'Source Maximum Interpolation', 'Override Maximum Interpolation', 'Key Unit Of Measure',
    'Value Unit Of Measure', 'Unit Of Measure', 'Number Format', 'Source Number Format',
    'Formula', 'FormulaParameters', 'UIConfig', 'Data Version Check', 'Sync Token',
    'Permissions From Datasource', 'Source Security String', 'Security String', 'Cache ID', 'Cached By Service'
]
