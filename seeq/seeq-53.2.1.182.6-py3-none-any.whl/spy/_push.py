import types

from typing import Optional

import pandas as pd
import numpy as np

from seeq.sdk import *
from seeq import spy

from seeq.spy import _common
from seeq.spy import _config
from seeq.spy import _login
from seeq.spy import _metadata

from seeq.spy._common import Status
from seeq.spy._errors import *


def push(data=None, *, metadata=None, workbook=_common.DEFAULT_WORKBOOK_PATH,
         worksheet=_common.DEFAULT_WORKSHEET_NAME, datasource=None, archive=False, type_mismatches='raise',
         errors='raise', quiet=False, status=None):
    """
    Imports metadata and/or data into Seeq Server, possibly scoped to a
    workbook and/or datasource.

    The 'data' and 'metadata' arguments work together. Signal and condition
    data cannot be mixed together in a single call to spy.push().

    Successive calls to 'push()' with the same 'metadata' but different 'data'
    will update the items (rather than overwrite them); however, pushing a new
    sample with the same timestamp as a previous one will overwrite the old
    one.

    Metadata can be pushed without accompanying data. This is common after
    having invoked the spy.assets.build() function. In such a case, the
    'metadata' DataFrame can contain signals, conditions, scalars or assets.

    Parameters
    ----------
    data : pandas.DataFrame, optional
        A DataFrame that contains the signal or condition data to be pushed.
        If 'metadata' is also supplied, it will have specific formatting
        requirements depending on the type of data being pushed.

        For signals, 'data' must have a pandas.Timestamp-based index with a
        column for each signal. To push to an existing signal, set the column
        name to the Seeq ID of the item to be pushed. An exception will be
        raised if the item does not exist.

        For conditions, 'data' must have an integer index and two
        pandas.Timestamp columns named 'Capsule Start' and 'Capsule End'.

    metadata : pandas.DataFrame, optional
        A DataFrame that contains the metadata for signals, conditions,
        scalars, metrics, or assets. If 'metadata' is supplied, in conjunction
        with a 'data' DataFrame, it has specific requirements depending on the
        kind of data supplied.

        For signals, the 'metadata' index (i.e., each row's index value) must
        match the column names of the 'data' DataFrame. For example, if you
        would like to push data where the name of each column is the Name of
        the item, then you might do set_index('Name', inplace=True, drop=False)
        on your metadata DataFrame to make the index match the data DataFrame's
        column names.

        For conditions and metrics, the 'metadata' DataFrame must have only
        one row with metadata.

        Metadata for each object type includes:

        Type Key:   Si = Signal, Sc = Scalar, C = Condition,
                    A = Asset, M = Metric

        ===================== ==================================== ============
        Metadata Term         Definition                           Types
        ===================== ==================================== ============
        Name                  Name of the signal                   Si,Sc,C,A,M
        Description           Description of the signal            Si,Sc,C,A
        Maximum Interpolation Maximum interpolation between        Si
                              samples
        Value Unit Of Measure Unit of measure for the signal       Si
        Formula               Formula for a calculated item        Si,Sc,C
        Formula Parameters    Parameters for a formula             Si,Sc,C
        Interpolation Method  Interpolation method between points  Si
                              Options are Linear, Step, PILinear
        Maximum Duration      Maximum expected duration for a      C
                              capsule
        Number Format         Formatting string ECMA-376           Si,Sc,M
        Path                  Asset tree path where the item's     Si,Sc,C,A
                              parent asset resides
        Measured Item         The ID of the signal or condition    M
        Statistic             Aggregate formula function to        M
                              compute on the measured item
        Duration              Duration to calculate a moving       M
                              aggregation for a continuous process
        Period                Period to sample for a               M
                              continuous process
        Thresholds            List of priority thresholds mapped
                              to a scalar formula/value or an ID   M
                              of a signal, condition or scalar
        Bounding Condition    The ID of a condition to aggregate   M
                              for a batch process
        Bounding Condition    Duration for aggregation for a       M
        Maximum Duration      bounding condition without a maximum
                              duration
        Asset                 Parent asset name. Parent asset      Si,Sc,C,A,M
                              must be in the tree at the
                              specified path, or listed in
                              'metadata' for creation.
        ===================== ==================================== ============

    workbook : {str, None}, default 'Data Lab >> Data Lab Analysis'
        The path to a workbook (in the form of 'Folder >> Path >> Workbook
        Name') or an ID that all pushed items will be 'scoped to'. Items scoped
        to a certain workbook will not be visible/searchable using the data
        panel in other workbooks. If None, items can also be 'globally scoped',
        meaning that they will be visible/searchable in all workbooks. Global
        scoping should be used judiciously to prevent search results becoming
        cluttered in all workbooks. The ID for a workbook is visible in the URL
        of Seeq Workbench, directly after the "workbook/" part. You can also
        push to the Corporate folder by using the following pattern:
        f'{spy.workbooks.CORPORATE} >> MySubfolder >> MyWorkbook'

    worksheet : {str, None}, default 'From Data Lab'
        The name of a worksheet within the workbook to create/update that will
        render the data that has been pushed so that you can see it in Seeq
        easily. If None, no worksheet will be added or changed.

    datasource : str, optional
        The name of the datasource within which to contain all the
        pushed items. By default, all pushed items will be contained in a "Seeq
        Data Lab" datasource. Do not create new datasources unless you really
        want to and you have permission from your administrator.

    archive : bool, default False
        If 'True', archives any items in the datasource that previously existed
        but were not part of this push call. This can only be used if you also
        specify a 'datasource' argument.

    type_mismatches : {'raise', 'drop', 'invalid'}, default 'raise'
        If 'raise' (default), any mismatches between the type of the data and
        its metadata will cause an exception. For example, if string data is
        found in a numeric time series, an error will be raised. If 'drop' is
        specified, such data will be ignored while pushing. If 'invalid' is
        specified, such data will be replaced with an INVALID sample, which
        will interrupt interpolation in calculations and displays.

    errors : {'raise', 'catalog'}, default 'raise'
        If 'raise', any errors encountered will cause an exception. If
        'catalog', errors will be added to a 'Result' column in the status.df
        DataFrame.

    quiet : bool, default False
        If True, suppresses progress output. Note that when status is
        provided, the quiet setting of the Status object that is passed
        in takes precedent.

    status : spy.Status, optional
        If specified, the supplied Status object will be updated as the command
        progresses. It gets filled in with the same information you would see
        in Jupyter in the blue/green/red table below your code while the
        command is executed. The table itself is accessible as a DataFrame via
        the status.df property.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the metadata for the items pushed, along with any
        errors and statistics about the operation.

        Additionally, the following properties are stored in the
        output DataFrame:

        =================== ===================================================
        Property            Description
        =================== ===================================================
        func                A str value of 'spy.push'
        kwargs              A dict with the values of the input parameters
                            passed to spy.push to get the output DataFrame
        status              A spy.Status object with the status of the
                            spy.push call
        =================== ===================================================
    """
    input_args = _common.validate_argument_types([
        (data, 'data', pd.DataFrame),
        (metadata, 'metadata', pd.DataFrame),
        (workbook, 'workbook', str),
        (worksheet, 'worksheet', str),
        (datasource, 'datasource', str),
        (archive, 'archive', bool),
        (type_mismatches, 'type_mismatches', str),
        (errors, 'errors', str),
        (quiet, 'quiet', bool),
        (status, 'status', _common.Status)
    ])

    status = Status.validate(status, quiet)
    _login.validate_login(status)

    _common.validate_errors_arg(errors)

    if type_mismatches not in ['drop', 'raise', 'invalid']:
        raise SPyValueError("'type_mismatches' must be either 'drop', 'raise' or 'invalid'")

    if archive and datasource is None:
        raise SPyValueError('"datasource" must be supplied when "archive" is true')

    item_type = 'Signal'
    if data is not None:
        if 'Capsule Start' in data.columns or 'Capsule End' in data.columns:
            item_type = 'Condition'

    datasource_output = _metadata.create_datasource(datasource)

    primary_workbook = None
    primary_worksheet = None
    workbook_id = None
    folder_id = None
    if workbook is not None:
        if worksheet is not None and not isinstance(worksheet, str):
            raise SPyValueError('When workbook is supplied, worksheet must also be supplied as a string')

        if _common.is_guid(workbook):
            primary_workbooks = spy.workbooks.pull(pd.DataFrame([{
                'ID': _common.sanitize_guid(workbook),
                'Type': 'Workbook',
                'Workbook Type': 'Analysis'
            }]), include_inventory=False, status=status.create_inner('Pull Workbook', quiet=True))

            if len(primary_workbooks) == 0:
                raise SPyRuntimeError(f'Workbook with ID "{_common.sanitize_guid(workbook)}" not found')

            primary_workbook = primary_workbooks[0]
        else:
            search_query, workbook_name = create_analysis_search_query(workbook)
            search_df = spy.workbooks.search(search_query, quiet=True)
            if len(search_df) == 0:
                primary_workbook = spy.workbooks.Analysis({'Name': workbook_name})
                primary_workbook.worksheet(worksheet if worksheet else _common.DEFAULT_WORKSHEET_NAME)
                spy.workbooks.push(primary_workbook, path=_common.get(search_query, 'Path'), include_inventory=False,
                                   datasource=datasource, status=status.create_inner('Create Workbook', quiet=True))
            else:
                primary_workbook = spy.workbooks.pull(search_df, include_inventory=False,
                                                      status=status.create_inner('Pull Workbook', quiet=True))[0]

        workbook_id = primary_workbook.id
        if len(primary_workbook['Ancestors']) > 0:
            folder_id = primary_workbook['Ancestors'][-1]

    push_result_df = pd.DataFrame()
    if metadata is not None:
        push_result_df = _metadata.push(metadata, workbook_id, datasource_output, archive, errors,
                                        status.create_inner('Push Metadata'))

    sample_stats = types.SimpleNamespace(earliest_sample_in_ms=None, latest_sample_in_ms=None)

    def _on_success(_row_index, _job_result):
        _earliest_sample_in_ms, _latest_sample_in_ms, item_id = _job_result
        if None not in [sample_stats.earliest_sample_in_ms, _earliest_sample_in_ms]:
            sample_stats.earliest_sample_in_ms = min(_earliest_sample_in_ms, sample_stats.earliest_sample_in_ms)
        elif sample_stats.earliest_sample_in_ms is None and _earliest_sample_in_ms is not None:
            sample_stats.earliest_sample_in_ms = _earliest_sample_in_ms

        if None not in [sample_stats.latest_sample_in_ms, _latest_sample_in_ms]:
            sample_stats.latest_sample_in_ms = max(_latest_sample_in_ms, sample_stats.latest_sample_in_ms)
        elif sample_stats.latest_sample_in_ms is None and _latest_sample_in_ms is not None:
            sample_stats.latest_sample_in_ms = _latest_sample_in_ms

        if item_id is None:
            # This can happen if the column has only nan values. In that case, we don't know whether
            # it's a string or numeric signal and we couldn't create the signal item.
            # Check to see if it was created by push_metadata.
            if 'ID' in signal_metadata:
                item_id = signal_metadata['ID']

            # CRAB-19586: Cannot convert string to float error
            # Since the ID column has only nan values, ensure ID column is dtype object
            push_result_df['ID'] = push_result_df['ID'].astype(object)

        push_result_df.at[_row_index, 'ID'] = item_id
        push_result_df.at[_row_index, 'Type'] = \
            'StoredSignal' if item_type == 'Signal' else 'StoredCondition'

    if data is not None:
        def _put_item_defaults(d):
            if 'Datasource Class' not in d:
                d['Datasource Class'] = datasource_output.datasource_class

            if 'Datasource ID' not in d:
                d['Datasource ID'] = datasource_output.datasource_id

            if 'Type' not in d:
                d['Type'] = item_type

            if 'Data ID' not in d:
                d['Data ID'] = _metadata.get_scoped_data_id(d, workbook_id)

        status_columns = list()
        if 'ID' in push_result_df:
            status_columns.append('ID')
        if 'Path' in push_result_df:
            status_columns.append('Path')
        if 'Asset' in push_result_df:
            status_columns.append('Asset')
        if 'Name' in push_result_df:
            status_columns.append('Name')

        status.df = push_result_df[status_columns].copy()
        status.df['Count'] = 0
        status.df['Time'] = 0
        status.df['Result'] = 'Pushing'
        status_columns.extend(['Count', 'Time', 'Result'])

        push_result_df['Push Count'] = np.int64(0)
        push_result_df['Push Time'] = 0
        push_result_df['Push Result'] = ''

        status.update(
            f'Pushing data to datasource <strong>{datasource_output.name} ['
            f'{datasource_output.datasource_id}]</strong> scoped to workbook ID '
            f'<strong>{workbook_id}</strong>',
            Status.RUNNING)

        if item_type == 'Signal':
            for column in data:
                try:
                    status_index = column

                    # For performance reasons, this variable will be supplied to _push_signal() if we had to
                    # retrieve the signal as part of this function
                    signal_output: Optional[SignalOutputV1] = None

                    if status_index in push_result_df.index:
                        # push_result_df will be filled in by _metadata.push() if a metadata DataFrame was
                        # supplied, so grab the metadata out of there for the signal
                        signal_metadata = push_result_df.loc[status_index].to_dict()

                    elif _common.is_guid(status_index):
                        # If an ID is supplied as the column name, then we are pushing to an existing signal and
                        # we need to query that signal for a few pieces of metadata.
                        signals_api = SignalsApi(_login.client)
                        signal_output = signals_api.get_signal(id=status_index)
                        signal_metadata = {
                            # This is the metadata needed to process the samples appropriately in _push_signal()
                            'Name': signal_output.name,
                            'Type': signal_output.type,
                            'Value Unit Of Measure': signal_output.value_unit_of_measure
                        }

                    else:
                        # Metadata has not been supplied and the column name is not an ID, so just create a
                        # "blank" row in the status DataFrame.
                        ad_hoc_status_df = pd.DataFrame({'Count': 0, 'Time': 0, 'Result': 'Pushing'},
                                                        index=[status_index])
                        status.df = status.df.append(ad_hoc_status_df, sort=True)
                        status.update()
                        signal_metadata = dict()

                    if not _common.present(signal_metadata, 'Name'):
                        if '>>' in column:
                            raise SPyRuntimeError(
                                'Paths in column name not currently supported. Supply a metadata argument if you '
                                'would like to put signal(s) directly in an asset tree.')

                        signal_metadata['Name'] = column

                    if not signal_output:
                        # Plant the "default" metadata so that the item will be placed in the specified
                        # datasource and its Data ID will be managed by SPy
                        _put_item_defaults(signal_metadata)

                    push_result_df.at[status_index, 'Name'] = signal_metadata['Name']

                    status.add_job(status_index,
                                   (_push_signal, column, signal_metadata, data, signal_output,
                                    type_mismatches, status_index, status),
                                   _on_success)

                except Exception as e:
                    _common.raise_or_catalog(errors, status=status, df=push_result_df, index=column,
                                             column='Push Result', e=e)

        elif item_type == 'Condition':
            # noinspection PyBroadException
            try:
                if metadata is None or len(metadata) != 1:
                    raise SPyRuntimeError('Condition requires "metadata" input of DataFrame with single row')

                condition_metadata = metadata.iloc[0].to_dict()

                if 'Name' not in condition_metadata or 'Maximum Duration' not in condition_metadata:
                    raise SPyRuntimeError('Condition metadata requires "Name" and "Maximum Duration" columns')

                if 'Capsule Start' not in data or 'Capsule End' not in data:
                    raise SPyRuntimeError('Condition data requires "Capsule Start" and "Capsule End" columns')

                _put_item_defaults(condition_metadata)

                push_result_df.at[0, 'Name'] = condition_metadata['Name']

                status.add_job(0,
                               (_push_condition, condition_metadata, data, 0, status),
                               _on_success)

            except BaseException as e:
                _common.raise_or_catalog(errors, status=status, df=push_result_df, index=0,
                                         column='Push Result', e=e)

        status.execute_jobs(errors)

        for status_index, status_row in status.df.iterrows():
            push_result_df.at[
                status_index, 'Push Result'] = status.df.at[status_index, 'Result']
            push_result_df.at[status_index, 'Push Count'] = status.df.at[status_index, 'Count']
            push_result_df.at[status_index, 'Push Time'] = status.df.at[status_index, 'Time']

    workbooks_to_push = list()
    if metadata is not None and 'Type' in metadata.columns:
        workbook_rows = metadata[metadata['Type'] == 'Workbook']
        for _, workbook_row in workbook_rows.iterrows():
            workbook_object = workbook_row['Object']  # type: spy.workbooks.Workbook
            if workbook_object.name is None:
                workbook_object.name = primary_workbook.name if primary_workbook else _common.DEFAULT_WORKBOOK_NAME
            if isinstance(workbook_object, spy.workbooks.Analysis) and \
               workbook_object.name == primary_workbook.name if primary_workbook else _common.DEFAULT_WORKBOOK_NAME:
                primary_workbook = workbook_object

            for worksheet_object in workbook_object.worksheets:
                if worksheet_object.name is None:
                    worksheet_object.name = worksheet if worksheet else _common.DEFAULT_WORKSHEET_NAME

            workbooks_to_push.append(workbook_object)

    if primary_workbook and len([w for w in workbooks_to_push if isinstance(w, spy.workbooks.Analysis)]) == 0:
        workbooks_to_push.append(primary_workbook)
        if worksheet is not None:
            primary_worksheet = primary_workbook.worksheet(worksheet)
            _auto_populate_worksheet(sample_stats.earliest_sample_in_ms, sample_stats.latest_sample_in_ms,
                                     push_result_df,
                                     primary_worksheet)
        else:
            # User does not want to render any changes in trendview so do not update display_items, just get worksheet
            primary_worksheet = primary_workbook.worksheets[0]
    elif primary_workbook:
        # User is creating worksheets through metadata
        # Get the primary worksheet so we can build up a correct link url
        primary_worksheet = _get_primary_worksheet(primary_workbook, folder_id)

    if metadata is not None and len(metadata) > 0 and 'Asset Object' in metadata.columns:
        for _, _row in metadata.iterrows():
            asset_object = _row['Asset Object']
            if not pd.isna(asset_object):
                asset_object.context.push_df = push_result_df

    # Here we cover the case where an admin is pushing data to a single workbook that they don't own. In R51,
    # there's a proper user folder in the path that can be used as the folder_id. In R50 there is no such user folder,
    # so the folder_id will end up being __All__ or __Shared__, which is not viable to use as a parent folder. But in
    # the case where we're pushing to only the primary workbook, then we don't need to supply the folder_id because the
    # workbook is not being moved and we're not adding other sibling workbooks (and therefore we don't need to know
    # the actual folder that the workbook is in).
    if folder_id in spy.workbooks.SYNTHETIC_FOLDERS and \
            len(workbooks_to_push) == 1 and \
            workbooks_to_push[0] == primary_workbook:
        folder_id = None

    if worksheet is not None:
        workbook_push_df = _push_workbooks(push_result_df, folder_id, workbooks_to_push, datasource, status)

    if primary_workbook:
        if worksheet is not None:
            primary = workbook_push_df[workbook_push_df['ID'] == primary_workbook.id].iloc[0]
            primary_id = primary['Pushed Workbook ID']
            primary_link_url = primary['URL']
        else:
            primary_id = workbook_id
            primary_link_url = '%s/%sworkbook/%s/worksheet/%s' % (
                _config.get_seeq_url(),
                (folder_id + '/') if folder_id is not None else '',
                primary_id,
                primary_worksheet.id
            )
        scope_string = 'and scoped to workbook ID <strong>%s</strong><br>Click the following link to see what ' \
                       'you pushed in Seeq:<br><a href="%s" target="_new">%s</a>' % (primary_id,
                                                                                     primary_link_url,
                                                                                     primary_link_url)
    else:
        scope_string = 'and globally scoped.'

    status.update(
        'Pushed successfully to datasource <strong>%s [Datasource ID: %s]</strong> %s' % (
            datasource_output.name, datasource_output.datasource_id, scope_string),
        Status.SUCCESS)

    push_df_properties = dict(
        func='spy.push',
        kwargs=input_args,
        status=status)

    _common.add_properties_to_df(push_result_df, **push_df_properties)

    return push_result_df


def _get_primary_worksheet(workbook, folder_id):
    workbooks_api = WorkbooksApi(_login.client)
    workbook_id = spy.workbooks.Workbook.find_by_name(workbook.name, workbook.definition['Workbook Type'], folder_id).id

    if workbook_id is not None:
        worksheet_output_list = workbooks_api.get_worksheets(workbook_id=workbook_id, is_archived=False, offset=0,
                                                             limit=1)
        if worksheet_output_list and worksheet_output_list.worksheets[0] is not None:
            return worksheet_output_list.worksheets[0]
        else:
            raise SPyRuntimeError(f'No worksheet found for workbook: {workbook.name}')
    else:
        raise SPyRuntimeError(f'Could not find a workbook in folder with ID: {folder_id}')


def _auto_populate_worksheet(earliest_sample_in_ms, latest_sample_in_ms, push_result_df, worksheet_object):
    display_items = pd.DataFrame()

    if 'Type' in push_result_df:
        display_items = push_result_df[push_result_df['Type'].isin(['StoredSignal', 'CalculatedSignal',
                                                                    'StoredCondition', 'CalculatedCondition',
                                                                    'CalculatedScalar', 'Chart',
                                                                    'ThresholdMetric'])]

    worksheet_object.display_items = display_items.head(10)
    if earliest_sample_in_ms is not None and latest_sample_in_ms is not None:
        _range = {
            'Start': pd.Timestamp(int(earliest_sample_in_ms) * 1000000, tz='UTC'),
            'End': pd.Timestamp(int(latest_sample_in_ms) * 1000000, tz='UTC')
        }
        worksheet_object.display_range = _range
        worksheet_object.investigate_range = _range


def create_analysis_search_query(workbook):
    workbook_spec_parts = _common.path_string_to_list(workbook)
    search_query = dict()
    if len(workbook_spec_parts) > 1:
        search_query['Path'] = _common.path_list_to_string(workbook_spec_parts[0:-1])
        workbook_name = workbook_spec_parts[-1]
    else:
        workbook_name = workbook_spec_parts[0]
    search_query['Name'] = '/^%s$/' % workbook_name
    search_query['Workbook Type'] = 'Analysis'
    return search_query, workbook_name


def _push_signal(column, signal_metadata, data, signal_output, type_mismatches, status_index,
                 status: Status):
    signals_api = SignalsApi(_login.client)
    signal_input = SignalInputV1()
    _metadata.dict_to_signal_input(signal_metadata, signal_input)
    put_samples_input = PutSamplesInputV1()
    put_samples_input.samples = list()
    count = 0
    is_string = None
    # noinspection PyTypeChecker
    timer = _common.timer_start()
    earliest_sample_in_ms = None
    latest_sample_in_ms = None

    def _put_signal(_signal_metadata, _signal_input):
        return signals_api.put_signal_by_data_id(datasource_class=_signal_metadata['Datasource Class'],
                                                 datasource_id=_signal_metadata['Datasource ID'],
                                                 data_id=_signal_metadata['Data ID'],
                                                 body=_signal_input)  # type: SignalOutputV1

    # Performance notes: It was found that pulling out the column as a pd.Series and then using series.iteritems()
    #                    instead of doing data.iterrows() was 5x-6x faster
    series = data[column]  # type: pd.Series
    for index, sample_value in series.iteritems():
        if pd.isna(sample_value) and sample_value is not None:
            continue

        # noinspection PyUnresolvedReferences
        if not isinstance(index, pd.Timestamp):
            raise SPyRuntimeError('data index must only be pd.Timestamp objects, but %s found instead' %
                                  type(index))

        if is_string is None:
            if _common.present(signal_metadata, 'Value Unit Of Measure'):
                is_string = (signal_metadata['Value Unit Of Measure'].lower() == 'string')
            else:
                is_string = isinstance(sample_value, str)

            if is_string:
                signal_input.value_unit_of_measure = 'string'

        if is_string != isinstance(sample_value, str):
            # noinspection PyBroadException
            try:
                if is_string:
                    if sample_value is not None:
                        sample_value = str(sample_value)
                else:
                    if data[column].dtype.name == 'int64':
                        sample_value = int(sample_value)
                    else:
                        sample_value = float(sample_value)
            except BaseException:
                # Couldn't convert it, fall through to the next conditional
                pass

        if is_string != isinstance(sample_value, str):
            if type_mismatches == 'drop':
                continue
            elif type_mismatches == 'raise':
                raise SPyRuntimeError('Column "%s" was detected as %s, but %s value at (%s, %s) found. Supply '
                                      'type_mismatches parameter as "drop" to ignore the sample entirely or '
                                      '"invalid" to insert an INVALID sample in its place.' %
                                      (column, 'string-valued' if is_string else 'numeric-valued',
                                       'numeric' if is_string else 'string',
                                       index, sample_value))
            else:
                sample_value = None

        if isinstance(sample_value, np.number):
            sample_value = sample_value.item()

        if not signal_output:
            signal_output = _put_signal(signal_metadata, signal_input)

        sample_input = SampleInputV1()
        key_in_ms = index.value / 1000000
        earliest_sample_in_ms = min(key_in_ms,
                                    earliest_sample_in_ms) if earliest_sample_in_ms is not None else key_in_ms
        latest_sample_in_ms = max(key_in_ms, latest_sample_in_ms) if latest_sample_in_ms is not None else key_in_ms

        sample_input.key = index.value
        sample_input.value = sample_value
        put_samples_input.samples.append(sample_input)

        if len(put_samples_input.samples) >= _config.options.push_page_size:
            signals_api.put_samples(id=signal_output.id,
                                    body=put_samples_input)
            count += len(put_samples_input.samples)
            status.send_update(status_index, {
                'Result': f'Pushed to {index}',
                'Count': count,
                'Time': _common.timer_elapsed(timer)
            })

            put_samples_input.samples = list()

    if not signal_output:
        if signal_input.value_unit_of_measure is None:
            raise SPyRuntimeError(f'Column "{column}" contains no data and no value unit of measure was provided. '
                                  f'Drop column from dataframe and try again or supply a unit of measure for '
                                  f'"{column}" using the metadata parameter.')
        signal_output = _put_signal(signal_metadata, signal_input)

    if len(put_samples_input.samples) > 0:
        signals_api.put_samples(id=signal_output.id,
                                body=put_samples_input)
        count += len(put_samples_input.samples)

    status.send_update(status_index, {
        'Result': 'Success',
        'Count': count,
        'Time': _common.timer_elapsed(timer)
    })

    return earliest_sample_in_ms, latest_sample_in_ms, signal_output.id if signal_output is not None else None


def _push_condition(condition_metadata, data, status_index, status: Status):
    conditions_api = ConditionsApi(_login.client)
    condition_batch_input = ConditionBatchInputV1()
    condition_input = ConditionInputV1()
    _metadata.dict_to_condition_input(condition_metadata, condition_input)
    condition_batch_input.conditions = [condition_input]
    condition_input.datasource_class = condition_metadata['Datasource Class']
    condition_input.datasource_id = condition_metadata['Datasource ID']
    items_batch_output = conditions_api.put_conditions(body=condition_batch_input)  # type: ItemBatchOutputV1
    item_update_output = items_batch_output.item_updates[0]  # type: ItemUpdateOutputV1
    capsules_input = CapsulesInputV1()
    capsules_input.capsules = list()
    capsules_input.key_unit_of_measure = 'ns'
    count = 0
    timer = _common.timer_start()
    earliest_sample_in_ms = None
    latest_sample_in_ms = None
    for index, row in data.iterrows():
        capsule = CapsuleV1()
        _dict_to_capsule(row.to_dict(), capsule)
        capsule.start = row['Capsule Start'].value
        capsule.end = row['Capsule End'].value
        capsules_input.capsules.append(capsule)
        # noinspection PyTypeChecker
        key_in_ms = capsule.start / 1000000
        earliest_sample_in_ms = min(key_in_ms,
                                    earliest_sample_in_ms) if earliest_sample_in_ms is not None else key_in_ms
        # noinspection PyTypeChecker
        key_in_ms = capsule.end / 1000000
        latest_sample_in_ms = max(key_in_ms, latest_sample_in_ms) if latest_sample_in_ms is not None else key_in_ms

        if len(capsules_input.capsules) > _config.options.push_page_size:
            conditions_api.add_capsules(id=item_update_output.item.id, body=capsules_input)
            count += len(capsules_input.capsules)
            status.send_update(status_index, {
                'Result': f'Pushed to {index}',
                'Count': count,
                'Time': _common.timer_elapsed(timer)
            })
            capsules_input.capsules = list()

    if len(capsules_input.capsules) > 0:
        conditions_api.add_capsules(id=item_update_output.item.id, body=capsules_input)
        count += len(capsules_input.capsules)

    status.send_update(status_index, {
        'Result': 'Success',
        'Count': count,
        'Time': _common.timer_elapsed(timer)
    })

    return earliest_sample_in_ms, latest_sample_in_ms, item_update_output.item.id


def _dict_to_capsule(d, capsule):
    _metadata.dict_to_input(d, capsule, 'properties', {
        'Capsule Start': None,
        'Capsule End': None
    })


def _push_workbooks(push_result_df, folder_id, workbooks, datasource, status: _common.Status):
    for workbook in workbooks:  # type: spy.workbooks.Analysis
        if not isinstance(workbook, spy.workbooks.Analysis):
            continue

        for worksheet in workbook.worksheets:  # type: spy.workbooks.AnalysisWorksheet
            for workstep in worksheet.worksteps.values():  # type: spy.workbooks.AnalysisWorkstep
                display_items = workstep.display_items

                # CRAB-19586: Cannot convert string to float error
                # 'ID' field is sometimes assigned float dtype in display_items dataframe but cannot duplicate this
                # This should be resolved in a fix done in workbooks/_workstep.py that cast the display_items df
                # as object type but since cannot duplicate the issue, let's patch here too
                display_items['ID'] = display_items['ID'].astype(object)

                for index, display_item in display_items.iterrows():
                    if not _common.present(display_item, 'ID') or _common.get(display_item, 'Reference', False):
                        pushed_item = get_from_push_df(display_item, push_result_df)
                        display_items.at[index, 'ID'] = pushed_item['ID']

                workstep.display_items = display_items

    return spy.workbooks.push(workbooks, path=folder_id, refresh=False, include_inventory=False, datasource=datasource,
                              status=status.create_inner('Push Workbooks'))


def get_from_push_df(display_item, push_result_df):
    item_path = _common.get(display_item, 'Path')
    item_asset = _common.get(display_item, 'Asset')
    item_name = _common.get(display_item, 'Name')
    clause = (push_result_df['Asset'] == item_asset) & (push_result_df['Name'] == item_name)
    if item_path:
        clause &= (push_result_df['Path'] == item_path)
    pushed_item = push_result_df[clause]
    if len(pushed_item) == 0:
        raise SPyRuntimeError('Could not find ID for workstep with display item where\n'
                              'Path = "%s"\nAsset = "%s"\nName = "%s"' %
                              (item_path, item_asset, item_name))
    if len(pushed_item) > 1:
        raise SPyRuntimeError('Multiple IDs for workstep with display item where\n'
                              'Path = "%s"\nAsset = "%s"\nName = "%s"\n%s' %
                              (item_path, item_asset, item_name, pushed_item))
    return pushed_item.iloc[0]
