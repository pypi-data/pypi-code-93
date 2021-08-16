import os
import pytest
import pytz
import re
import random

import pandas as pd
import numpy as np

from seeq import spy
from seeq.sdk import *
from seeq.sdk.rest import ApiException

from seeq.spy.tests import test_common
from seeq.spy import _login
from seeq.spy import _common


def setup_module():
    test_common.login()


def _pull_workbook(_id, include_inventory=True):
    return spy.workbooks.pull(pd.DataFrame([{
        'ID': _common.sanitize_guid(_id),
        'Type': 'Workbook',
        'Workbook Type': 'Analysis'
    }]), include_inventory=include_inventory)[0]


@pytest.mark.system
def test_push_to_workbook():
    folder_name = f'test_push_to_workbook_{_common.new_placeholder_guid()}'

    spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'test_push_to_workbook'
    }]), workbook=f'{folder_name} >> test_push_to_workbook >> My Workbook!', worksheet='My Worksheet!')

    search_df = spy.workbooks.search({'Path': f'{folder_name} >> test_push_to_workbook'})

    assert len(search_df) == 1
    assert search_df.iloc[0]['Name'] == 'My Workbook!'

    workbooks = spy.workbooks.pull(search_df, include_inventory=False)

    assert len(workbooks) == 1
    workbook = workbooks[0]
    assert workbook['Name'] == 'My Workbook!'
    assert len(workbook.worksheets) == 1
    assert workbook.worksheets[0].name == 'My Worksheet!'
    assert workbook.path == f'{folder_name} >> test_push_to_workbook'

    # Push again, but this time using the workbook's ID
    spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'test_push_to_workbook2'
    }]), workbook=workbook.id, worksheet='My Worksheet!')

    # CRAB-22062 ensure workbook path remains unchanged when workbook is pushed
    workbook_id = workbook.id
    workbook = _pull_workbook(workbook_id, include_inventory=False)
    assert workbook.path == f'{folder_name} >> test_push_to_workbook'

    non_admin_username = _login.user.username

    workbook_in_root_name = f'Workbook in Root {_common.new_placeholder_guid()}'

    # Now push to a workbook in the root of My Items
    spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'test_push_to_workbook3'
    }]), workbook=workbook_in_root_name, worksheet='My Root Worksheet!')

    workbook_in_root_search_df = spy.workbooks.search({'Name': workbook_in_root_name})

    workbook_in_root = _pull_workbook(workbook_in_root_search_df.iloc[0]['ID'], include_inventory=False)

    assert workbook_in_root.path == ''

    spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'test_push_to_workbook4'
    }]), workbook=workbook_in_root.id, worksheet='My Root Worksheet!')

    assert workbook_in_root.path == ''

    try:
        # Now login as admin
        test_common.login(admin=True)

        workbook = _pull_workbook(workbook_id, include_inventory=False)

        # It will now appear under the admin-only "Users" folder, since the admin is not the owner
        assert workbook.path == \
            f'{spy.workbooks.USERS} >> {non_admin_username} >> {folder_name} >> test_push_to_workbook'

        # Now try to push it using the ID, which handles the case where it's in the USERS folder but has some
        # intermediate ancestors
        spy.push(pd.DataFrame(), workbook=workbook.id)

        workbook_in_root = _pull_workbook(workbook_in_root_search_df.iloc[0]['ID'], include_inventory=False)

        # Now try to push this one using the ID, which handles the case where it's in the USERS folder
        spy.push(pd.DataFrame(), workbook=workbook_in_root.id)

        workbook_in_root = _pull_workbook(workbook_in_root_search_df.iloc[0]['ID'], include_inventory=False)

        assert workbook_in_root.path == f'{spy.workbooks.USERS} >> {non_admin_username}'

        # Now share the workbook so it would appear under Shared on the Home Screen
        items_api = ItemsApi(_login.client)
        everyone_group = test_common.get_group('Everyone')
        items_api.add_access_control_entry(
            id=workbook_id,
            body=AceInputV1(identity_id=everyone_group.id,
                            permissions=PermissionsV1(read=True)))

        workbook = _pull_workbook(workbook_id, include_inventory=False)

        # Now it will be under the admin's Shared folder
        assert workbook.path == f'{spy.workbooks.SHARED} >> {folder_name} >> test_push_to_workbook'

        with pytest.raises(RuntimeError, match=spy.workbooks.SHARED):
            spy.workbooks.push(workbook, path=spy.workbooks.SHARED, use_full_path=True)

        with pytest.raises(RuntimeError, match=spy.workbooks.ALL):
            spy.workbooks.push(workbook, path=spy.workbooks.ALL, use_full_path=True)

        with pytest.raises(RuntimeError, match=spy.workbooks.USERS):
            spy.workbooks.push(workbook, path=spy.workbooks.USERS, use_full_path=True)

        spy.workbooks.push(workbook, path=spy.workbooks.CORPORATE, use_full_path=True)

        workbook = _pull_workbook(workbook_id, include_inventory=False)

        # Now it will be under the Corporate folder
        assert workbook.path == f'{spy.workbooks.CORPORATE} >> {folder_name} >> test_push_to_workbook'

    finally:
        test_common.login(admin=False)


# CRAB-22132: Push to Workbook without specifying worksheet
@pytest.mark.system
def test_push_to_workbook_data_worksheet_none():
    # Test Scenario: Push data to new workbook, Worksheet=None
    workbook_name = f'My Workbook_{_common.new_placeholder_guid()}'

    numeric_data_df = pd.DataFrame()
    numeric_data_df['Number'] = pd.Series([
        1,
        2
    ], index=[
        pd.to_datetime('2019-01-01T00:00:00Z'),
        pd.to_datetime('2019-01-02T00:00:00Z')
    ])

    spy.push(numeric_data_df, workbook=f'My Folder >> {workbook_name}', worksheet=None)

    search_df = spy.workbooks.search({'Path': 'My Folder', 'Name': workbook_name})
    assert len(search_df) == 1
    assert search_df.iloc[0]['Name'] == workbook_name

    workbooks = spy.workbooks.pull(search_df, include_inventory=False)
    assert len(workbooks) == 1
    workbook = workbooks[0]
    assert len(workbook.worksheets) == 1
    assert workbook.worksheets[0].name == _common.DEFAULT_WORKSHEET_NAME

    # There should be no display items because Worksheet=None prevents any updates to trendview
    assert len(workbook.worksheets[0].display_items) == 0

    # Test Scenario: Push data to existing workbook, Worksheet=None
    # Start by populating trendview with display items so just use same data as above to create a display item
    spy.push(numeric_data_df, workbook=f'My Folder >> {workbook_name}')
    workbook = _pull_workbook(workbook.id, include_inventory=False)
    assert len(workbook.worksheets) == 1

    # There should be one display items because Worksheet=None was removed
    assert len(workbook.worksheets[0].display_items) == 1

    # Now create another signal
    numeric_data_df = pd.DataFrame()
    numeric_data_df['New Number'] = pd.Series([
        3,
        4
    ], index=[
        pd.to_datetime('2019-01-01T00:00:00Z'),
        pd.to_datetime('2019-01-02T00:00:00Z')
    ])

    spy.push(numeric_data_df, workbook=f'My Folder >> {workbook_name}', worksheet=None)

    workbook = _pull_workbook(workbook.id, include_inventory=False)

    assert len(workbook.worksheets) == 1
    assert workbook.worksheets[0].name == _common.DEFAULT_WORKSHEET_NAME

    # There should be one display items because Worksheet=None prevents any updates to trendview
    assert len(workbook.worksheets[0].display_items) == 1


# CRAB-22132: Push to Workbook without specifying worksheet
@pytest.mark.system
def test_push_to_workbook_metadata_worksheet_none():
    # Test Scenario: Push metadata to new workbook, Worksheet=None
    folder_name = f'test_push_to_workbook_{_common.new_placeholder_guid()}'

    spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'test_push_to_workbook'
    }]), workbook=f'{folder_name} >> test_push_to_workbook >> My Workbook!', worksheet=None)

    search_df = spy.workbooks.search({'Path': f'{folder_name} >> test_push_to_workbook'})
    assert len(search_df) == 1
    assert search_df.iloc[0]['Name'] == 'My Workbook!'

    workbooks = spy.workbooks.pull(search_df, include_inventory=False)
    assert len(workbooks) == 1
    workbook = workbooks[0]
    assert workbook['Name'] == 'My Workbook!'
    assert len(workbook.worksheets) == 1
    assert workbook.path == f'{folder_name} >> test_push_to_workbook'
    assert workbook.worksheets[0].name == _common.DEFAULT_WORKSHEET_NAME

    # There should be no display items because Worksheet=None prevents any updates to trendview
    assert len(workbook.worksheets[0].display_items) == 0

    # Test Scenario: Push metadata to existing workbook, Worksheet=None
    # Start by populating trendview with display items so just use same data as above to create a display item
    spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'test_push_to_workbook'
    }]), workbook=f'{folder_name} >> test_push_to_workbook >> My Workbook!')
    workbook = _pull_workbook(workbook.id, include_inventory=False)
    assert len(workbook.worksheets) == 1

    # There should be one display items because Worksheet=None was removed
    assert len(workbook.worksheets[0].display_items) == 1

    spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'new_test_push_to_workbook'
    }]), workbook=f'{folder_name} >> test_push_to_workbook >> My Workbook!', worksheet=None)

    workbook = _pull_workbook(workbook.id, include_inventory=False)

    assert len(workbook.worksheets) == 1
    assert workbook.worksheets[0].name == _common.DEFAULT_WORKSHEET_NAME

    # There should be one display items because Worksheet=None prevents any updates to trendview
    assert len(workbook.worksheets[0].display_items) == 1


@pytest.mark.system
def test_push_to_existing_worksheet():
    workbooks_api = WorkbooksApi(test_common.get_client())
    workbook_input = WorkbookInputV1()
    workbook_input.name = 'test_push_to_existing_worksheet'
    workbook_output = workbooks_api.create_workbook(body=workbook_input)
    worksheet_input = WorksheetInputV1()
    worksheet_input.name = 'auto-created-worksheet'
    worksheet_output = workbooks_api.create_worksheet(workbook_id=workbook_output.id, body=worksheet_input)
    new_annotation = AnnotationInputV1()
    new_annotation.document = ''
    new_annotation.name = 'auto-created-document'
    new_annotation.interests = [{'interestId': worksheet_output.id}]
    annotations_api = AnnotationsApi(_login.client)
    annotations_api.create_annotation(body=new_annotation)

    spy.push(pd.DataFrame({'My Data': [1]}, index=[pd.to_datetime('2019-01-01')]),
             workbook=workbook_output.id, worksheet=worksheet_input.name)

    search_df = spy.workbooks.search({'ID': workbook_output.id})
    workbooks = spy.workbooks.pull(search_df)
    assert len(workbooks) == 1
    workbook = workbooks[0]
    assert workbook.id == workbook_output.id
    assert len(workbook.worksheets) == 1
    worksheet = workbook.worksheets[0]
    assert worksheet.id == worksheet_output.id
    assert worksheet.name == worksheet_output.name


@pytest.mark.system
def test_current_worksteps_crab_21217():
    # Create a workbook with five signals in the details pane
    workbook_name = 'test_current_worksteps_CRAB_21217'
    worksheet_name = '1'
    signals = map(lambda i: {'Name': f'Signal {i}', 'Type': 'Signal'}, range(1, 6))
    spy.push(metadata=pd.DataFrame(signals),
             workbook=workbook_name, worksheet=worksheet_name)
    workbook_id = spy.workbooks.search({'Name': workbook_name})['ID'][0]
    workbook = _pull_workbook(workbook_id)
    worksheet_id = workbook.worksheets[0].id
    workstep_id = workbook.worksheets[0].current_workstep().id

    # Add a journal entry with a link to the current workstep containing five signals
    annotations_api = AnnotationsApi(test_common.get_client())
    annotation_id = annotations_api.get_annotations(annotates=[worksheet_id]).items[0].id
    document = f'''
        <p><a href="/links?type=workstep&workbook={workbook_id}&worksheet={worksheet_id}&workstep={workstep_id}">
        Workstep Link
        </a></p>
    '''
    annotation = AnnotationInputV1()
    annotation.document = document
    annotation.name = 'journal_entry_with_workstep_link'
    annotation.interests = [{'interestId': worksheet_id}]
    annotations_api.update_annotation(id=annotation_id, body=annotation)

    # Push another workstep that clears the details pane
    workstep_input = WorkstepInputV1()
    workstep_input.data = _common.DEFAULT_WORKBOOK_STATE
    workbooks_api = WorkbooksApi(test_common.get_client())
    workbooks_api.create_workstep(workbook_id=workbook_id,
                                  worksheet_id=worksheet_id,
                                  body=workstep_input)

    # Now push a single signal into the details pane
    only_signal_name = 'Only Signal'
    spy.push(metadata=pd.DataFrame([{'Name': only_signal_name, 'Type': 'Signal'}]),
             workbook=workbook_name, worksheet=worksheet_name)

    # Pull the workbook and verify the details pane contains only one signal
    workbook = _pull_workbook(workbook_id)
    details_items = workbook.worksheets[0].current_workstep().data['state']['stores']['sqTrendSeriesStore']['items']
    assert len(details_items) == 1
    assert details_items[0]['name'] == only_signal_name


@pytest.mark.system
def test_push_signal():
    numeric_data_df = pd.DataFrame()
    string_data_df = pd.DataFrame()

    numeric_data_df['Numeric'] = pd.Series([
        1,
        'invalid',
        3,
        None
    ], index=[
        pd.to_datetime('2019-01-01'),
        pd.to_datetime('2019-01-02'),
        pd.to_datetime('2019-01-03'),
        pd.to_datetime('2019-01-04')
    ])

    string_data_df['String'] = pd.Series([
        'ON',
        'OFF',
        None,
        np.nan,
        np.nan
    ], index=[
        pd.to_datetime('2019-01-01'),
        pd.to_datetime('2019-01-02'),
        pd.to_datetime('2019-01-03'),
        pd.to_datetime('2019-01-04'),
        pd.to_datetime('2019-01-05')  # This timestamp won't show up in the pull
    ])

    with pytest.raises(
            RuntimeError,
            match=re.escape('Column "Numeric" was detected as numeric-valued, but string '
                            'value at (2019-01-02 00:00:00, invalid)')):
        spy.push(numeric_data_df)

    with pytest.raises(
            RuntimeError,
            match=re.escape('Column "String" was detected as string-valued, but numeric '
                            'value at (2019-01-03 00:00:00, None)')):
        spy.push(string_data_df)

    data_df = numeric_data_df.combine_first(string_data_df)

    push_df = spy.push(data_df, type_mismatches='invalid')

    search_df = spy.search(push_df)

    assert search_df[search_df['Name'] == 'Numeric'].iloc[0]['Value Unit Of Measure'] == ''
    assert search_df[search_df['Name'] == 'String'].iloc[0]['Value Unit Of Measure'] == 'string'

    pull_df = spy.pull(push_df, start='2019-01-01T00:00:00Z', end='2019-01-05T00:00:00Z', grid=None)

    assert len(pull_df) == 4

    assert pull_df.at[pd.to_datetime('2019-01-01'), 'Numeric'] == 1
    assert pd.isna(pull_df.at[pd.to_datetime('2019-01-02'), 'Numeric'])
    assert pull_df.at[pd.to_datetime('2019-01-03'), 'Numeric'] == 3
    assert pd.isna(pull_df.at[pd.to_datetime('2019-01-04'), 'Numeric'])

    assert pull_df.at[pd.to_datetime('2019-01-01'), 'String'] == 'ON'
    assert pull_df.at[pd.to_datetime('2019-01-02'), 'String'] == 'OFF'
    assert pd.isna(pull_df.at[pd.to_datetime('2019-01-03'), 'String'])
    assert pd.isna(pull_df.at[pd.to_datetime('2019-01-04'), 'String'])

    with pytest.raises(ValueError,
                       match=re.escape('invalid_values_as cannot be None (because Pandas treats it the same as NaN)')):
        spy.pull(push_df, start='2019-01-01T00:00:00Z', end='2019-01-05T00:00:00Z', grid=None, invalid_values_as=None)

    pull_df = spy.pull(push_df, start='2019-01-01T00:00:00Z', end='2019-01-05T00:00:00Z', grid=None,
                       invalid_values_as='INVALID')

    assert pull_df.at[pd.to_datetime('2019-01-01'), 'Numeric'] == 1
    assert pull_df.at[pd.to_datetime('2019-01-02'), 'Numeric'] == 'INVALID'
    assert pull_df.at[pd.to_datetime('2019-01-03'), 'Numeric'] == 3
    assert pull_df.at[pd.to_datetime('2019-01-04'), 'Numeric'] == 'INVALID'

    assert pull_df.at[pd.to_datetime('2019-01-01'), 'String'] == 'ON'
    assert pull_df.at[pd.to_datetime('2019-01-02'), 'String'] == 'OFF'
    assert pull_df.at[pd.to_datetime('2019-01-03'), 'String'] == 'INVALID'
    assert pd.isna(pull_df.at[pd.to_datetime('2019-01-04'), 'String'])

    pull_df = spy.pull(push_df, start='2019-01-01T00:00:00Z', end='2019-01-05T00:00:00Z', grid=None,
                       invalid_values_as=-999)

    assert pull_df.at[pd.to_datetime('2019-01-01'), 'Numeric'] == 1
    assert pull_df.at[pd.to_datetime('2019-01-02'), 'Numeric'] == -999
    assert pull_df.at[pd.to_datetime('2019-01-03'), 'Numeric'] == 3
    assert pull_df.at[pd.to_datetime('2019-01-04'), 'Numeric'] == -999

    assert pull_df.at[pd.to_datetime('2019-01-01'), 'String'] == 'ON'
    assert pull_df.at[pd.to_datetime('2019-01-02'), 'String'] == 'OFF'
    assert pull_df.at[pd.to_datetime('2019-01-03'), 'String'] == -999
    assert pd.isna(pull_df.at[pd.to_datetime('2019-01-04'), 'String'])


@pytest.mark.disabled
def test_crab_19638():
    datasources_api = DatasourcesApi(_login.client)
    signals_api = SignalsApi(_login.client)

    datasource_1_input = DatasourceInputV1()
    datasource_1_input.name = 'datasource_name_1'
    datasource_1_input.datasource_class = 'datasource_class'
    datasource_1_input.datasource_id = 'datasource_id_1'
    datasource_1_input.stored_in_seeq = True
    datasource_1_output = datasources_api.create_datasource(body=datasource_1_input)  # type: DatasourceOutputV1

    datasource_2_input = DatasourceInputV1()
    datasource_2_input.name = 'datasource_name_2'
    datasource_2_input.datasource_class = 'datasource_class'
    datasource_2_input.datasource_id = 'datasource_id_2'
    datasource_2_input.stored_in_seeq = True
    datasource_2_output = datasources_api.create_datasource(body=datasource_2_input)  # type: DatasourceOutputV1

    signal_1_input = SignalInputV1()
    signal_1_input.name = 'bad_signal'
    signal_1_output = signals_api.put_signal_by_data_id(datasource_class=datasource_1_output.datasource_class,
                                                        datasource_id=datasource_1_output.datasource_id,
                                                        data_id='bad_signal',
                                                        body=signal_1_input)  # type: SignalOutputV1

    put_samples_1_input = PutSamplesInputV1()
    put_samples_1_input.samples = [
        SampleInputV1(key='2020-04-05T00:00:00Z', value=1)
    ]
    signals_api.put_samples(id=signal_1_output.id,
                            body=put_samples_1_input)  # type: PutSamplesOutputV1

    get_samples_1_output = signals_api.get_samples(id=signal_1_output.id,
                                                   start='2020-04-04T00:00:00Z',
                                                   end='2020-04-07T00:00:00Z')  # type: GetSamplesOutputV1

    assert len(get_samples_1_output.samples) == 1
    assert get_samples_1_output.samples[0].key == '2020-04-05T00:00:00Z'
    assert get_samples_1_output.samples[0].value == 1

    signal_2_input = SignalInputV1()
    signal_2_input.name = 'bad_signal'
    signal_2_output = signals_api.put_signal_by_data_id(datasource_class=datasource_2_output.datasource_class,
                                                        datasource_id=datasource_2_output.datasource_id,
                                                        data_id='bad_signal',
                                                        body=signal_2_input)  # type: SignalOutputV1

    put_samples_2_input = PutSamplesInputV1()
    put_samples_2_input.samples = [
        SampleInputV1(key='2020-04-06T00:00:00Z', value=2)
    ]
    signals_api.put_samples(id=signal_2_output.id,
                            body=put_samples_2_input)  # type: PutSamplesOutputV1

    get_samples_2_output = signals_api.get_samples(id=signal_2_output.id,
                                                   start='2020-04-04T00:00:00Z',
                                                   end='2020-04-07T00:00:00Z')  # type: GetSamplesOutputV1

    # Because of CRAB-19638, this assertion will fail because samples has size 2
    assert len(get_samples_2_output.samples) == 1
    assert get_samples_2_output.samples[0].key == '2020-04-06T00:00:00Z'
    assert get_samples_2_output.samples[0].value == 2


@pytest.mark.system
def test_push_to_existing_signal():
    # First create a signal that ends up in the "default" Datasource (which currently is PostgresDatums)
    signal_input = SignalInputV1()
    signal_input.name = 'test_push_to_existing_signal'
    signal_input.interpolation_method = 'linear'

    signals_api = SignalsApi(test_common.get_client())
    signal_output = signals_api.create_signal(body=signal_input)  # type: SignalOutputV1

    search_df = spy.search({
        'ID': signal_output.id
    })

    data_df = pd.DataFrame()

    data_df[signal_output.id] = pd.Series([
        1,
        2
    ], index=[
        pd.to_datetime('2019-01-01T00:00:00Z'),
        pd.to_datetime('2019-01-02T00:00:00Z')
    ])

    # Now we push data to the signal we created at the beginning. We do not want a new signal to be created.
    push_df = spy.push(data=data_df)
    assert push_df.at[signal_output.id, 'Push Count'] == 2

    pull_df = spy.pull(search_df, start='2019-01-01T00:00:00Z', end='2020-01-01T00:00:00Z', grid=None, header='ID')

    assert len(pull_df) == 2
    assert pull_df.equals(data_df)


@pytest.mark.system
def test_push_to_non_standard_datasource():
    data_1_df = pd.DataFrame()

    # Once CRAB-19638 is fixed, change this to test_push_to_non_standard_datasource
    data_1_df['test_push_to_non_standard_datasource_1'] = pd.Series([
        1,
    ], index=[
        pd.to_datetime('2019-01-01T00:00:00Z')
    ])

    push_1_df = spy.push(data_1_df, datasource='non_standard_datasource_1')

    data_2_df = pd.DataFrame()

    # Once CRAB-19638 is fixed, change this to test_push_to_non_standard_datasource
    data_2_df['test_push_to_non_standard_datasource_2'] = pd.Series([
        2,
    ], index=[
        pd.to_datetime('2019-01-02T00:00:00Z')
    ])

    push_2_df = spy.push(data_2_df, datasource='non_standard_datasource_2')

    assert len(push_1_df) > 0
    assert len(push_2_df) > 0

    pull_df = spy.pull(push_1_df, start='2019-01-01T00:00:00Z', end='2019-01-02T00:00:00Z', grid=None)
    assert len(pull_df) == 1
    assert pull_df['test_push_to_non_standard_datasource_1'][pd.to_datetime('2019-01-01T00:00:00Z')] == 1

    pull_df = spy.pull(push_2_df, start='2019-01-01T00:00:00Z', end='2019-01-02T00:00:00Z', grid=None)
    assert len(pull_df) == 1
    assert pull_df['test_push_to_non_standard_datasource_2'][pd.to_datetime('2019-01-02T00:00:00Z')] == 2


@pytest.mark.system
def test_push_from_csv():
    csv_file = pd.read_csv(
        os.path.join(os.path.dirname(__file__), '..', 'docs', 'Documentation', 'csv_import_example.csv'),
        parse_dates=['TIME(unitless)'],
        index_col='TIME(unitless)')

    spy.options.push_page_size = 5000
    spy.options.max_concurrent_requests = 2

    fewer_signals = csv_file.iloc[:, :-4]

    push_results = spy.push(data=fewer_signals)

    assert all([x == 'Success' for x in push_results.status.df['Result'].tolist()])

    start = pd.to_datetime('2018-07-25T23:31:01.0000000-06:00')
    end = pd.to_datetime('2018-07-25T23:31:07.0000000-06:00')
    expected_df = fewer_signals.loc[start:end]

    pull_df = spy.pull(push_results, start=start, end=end, grid=None, tz_convert=pytz.FixedOffset(-360))
    pull_df.index.name = 'TIME(unitless)'

    assert pull_df.equals(expected_df)


@pytest.mark.system
def test_bad_calculation():
    with pytest.raises(RuntimeError):
        spy.push(metadata=pd.DataFrame([{
            'Type': 'Signal',
            'Name': 'Bad Calc',
            'Formula': 'hey(nothing)'
        }]))


@pytest.mark.system
def test_push_calculated_signal():
    area_a_signals = spy.search({
        'Path': 'Example >> Cooling Tower 1 >> Area A'
    })

    push_df = spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'Dew Point',
        # From https://iridl.ldeo.columbia.edu/dochelp/QA/Basic/dewpoint.html
        'Formula': "$T - ((100 - $RH.setUnits(''))/5)",
        'Formula Parameters': {
            '$T': area_a_signals[area_a_signals['Name'] == 'Temperature'],
            '$RH': area_a_signals[area_a_signals['Name'] == 'Relative Humidity']
        }
    }]))

    assert len(push_df) == 1
    dew_point_calc = push_df.iloc[0]
    assert 'ID' in dew_point_calc

    assert dew_point_calc['Datasource Class'] == _common.DEFAULT_DATASOURCE_CLASS
    assert dew_point_calc['Datasource ID'] == _common.DEFAULT_DATASOURCE_ID

    # Make sure Everyone got Manage permissions on the datasource
    items_api = ItemsApi(test_common.get_client())
    acl_output = items_api.get_access_control(id=dew_point_calc['ID'])  # type: AclOutputV1
    everyone_entries = [ace for ace in acl_output.entries if ace.identity.name == 'Everyone']

    assert len(everyone_entries) == 1
    assert everyone_entries[0].permissions.manage
    assert everyone_entries[0].permissions.read
    assert everyone_entries[0].permissions.write


@pytest.mark.system
def test_push_calculated_signal_without_specifying_type():
    area_a_signals = spy.search({
        'Path': 'Example >> Cooling Tower 1 >> Area A'
    })

    push_df = spy.push(metadata=pd.DataFrame([{
        'Type': '',
        'Name': 'Dew Point',
        # From https://iridl.ldeo.columbia.edu/dochelp/QA/Basic/dewpoint.html
        'Formula': "$T - ((100 - $RH.setUnits(''))/5)",
        'Formula Parameters': {
            '$T': area_a_signals[area_a_signals['Name'] == 'Temperature'],
            '$RH': area_a_signals[area_a_signals['Name'] == 'Relative Humidity']
        }
    }]))

    assert len(push_df) == 1
    dew_point_calc = push_df.iloc[0]
    assert 'ID' in dew_point_calc

    assert dew_point_calc['Datasource Class'] == _common.DEFAULT_DATASOURCE_CLASS
    assert dew_point_calc['Datasource ID'] == _common.DEFAULT_DATASOURCE_ID

    # Make sure Everyone got Manage permissions on the datasource
    items_api = ItemsApi(test_common.get_client())
    acl_output = items_api.get_access_control(id=dew_point_calc['ID'])  # type: AclOutputV1
    everyone_entries = [ace for ace in acl_output.entries if ace.identity.name == 'Everyone']

    assert len(everyone_entries) == 1
    assert everyone_entries[0].permissions.manage
    assert everyone_entries[0].permissions.read
    assert everyone_entries[0].permissions.write


@pytest.mark.system
def test_push_calculation_with_dependencies_in_metadata():
    metadata = [{
        'Name': 'Calc 1',
        'Formula': 'sinusoid()',
        'Path': 'Calc Parent'
    }, {
        'Name': 'Calc 2',
        'Formula': 'sinusoid()',
        'Path': 'Calc Parent'
    }]
    for i in range(3, 10):
        metadata.append({
            'Name': 'Calc %s' % i,
            'Formula': '$a + $b',
            'Path': 'Calc Parent',
            'Formula Parameters': {
                'a': 'Calc Parent >> Calc %s' % random.randrange(1, i),
                'b': 'Calc Parent >> Calc %s' % random.randrange(1, i)
            }
        })
    # Shuffle so that the dependencies are out of order
    random.shuffle(metadata)
    metadata = pd.DataFrame(metadata)

    push_df = spy.push(metadata=metadata, workbook='Test Calculation Metadata Dependencies')
    assert (push_df['Push Result'] == 'Success').all()


@pytest.mark.system
def test_push_scalar():
    metadata = pd.DataFrame([{
        'Type': 'Scalar',
        'Name': 'Negative Number',
        'Formula': np.int64(-12)
    }])

    push_df = spy.push(metadata=metadata)

    search_df = spy.search(push_df, all_properties=True)
    assert search_df.iloc[0]['Formula'] == '-12'

    pull_df = spy.pull(push_df)
    assert pull_df.iloc[0]['Negative Number'] == -12


@pytest.mark.system
def test_edit_existing_calculated_items():
    signals_api = SignalsApi(_login.client)
    conditions_api = ConditionsApi(_login.client)
    scalars_api = ScalarsApi(_login.client)

    area_a_signals = spy.search({
        'Path': 'Example >> Cooling Tower 1 >> Area A'
    })

    formula_parameters = [
        'RH=%s' % area_a_signals[area_a_signals['Name'] == 'Relative Humidity'].iloc[0]['ID'],
        'T=%s' % area_a_signals[area_a_signals['Name'] == 'Temperature'].iloc[0]['ID']
    ]

    # Create a signal, condition and scalar that we will later edit

    signal_input = SignalInputV1()
    signal_input.name = 'test_alter_existing_items Signal'
    signal_input.formula = "$T - ((100 - $RH.setUnits(''))/5)"
    signal_input.formula_parameters = formula_parameters
    signal_output = signals_api.create_signal(body=signal_input)  # type: SignalOutputV1

    condition_input = ConditionInputV1()
    condition_input.name = 'test_alter_existing_items Condition'
    condition_input.formula = "$T.valueSearch(isLessThan(80)).union($RH.valueSearch(isLessThan(40)))"
    condition_input.parameters = formula_parameters
    condition_output = conditions_api.create_condition(body=condition_input)  # type: ConditionOutputV1

    scalar_input = ScalarInputV1()
    scalar_input.name = 'test_alter_existing_items Scalar'
    scalar_input.formula = "$T.average(capsule('2016-12-18')) + $RH.average(capsule('2016-12-18'))"
    scalar_input.parameters = formula_parameters
    scalar_output = scalars_api.create_calculated_scalar(body=scalar_input)  # type: CalculatedItemOutputV1

    created_items = spy.search(pd.DataFrame([{'ID': signal_output.id},
                                             {'ID': condition_output.id},
                                             {'ID': scalar_output.id}]),
                               all_properties=True)

    assert created_items.iloc[0]['Formula'] == "$T - ((100 - $RH.setUnits(''))/5)"
    assert sorted(created_items.iloc[0]['Formula Parameters']) == formula_parameters
    assert created_items.iloc[1]['Formula'] == "$T.valueSearch(isLessThan(80)).union($RH.valueSearch(isLessThan(40)))"
    assert sorted(created_items.iloc[1]['Formula Parameters']) == formula_parameters
    assert created_items.iloc[2]['Formula'] == "$T.average(capsule('2016-12-18')) + $RH.average(capsule('2016-12-18'))"
    assert sorted(created_items.iloc[2]['Formula Parameters']) == formula_parameters

    # Edit them by just changing values in the DataFrame, then push

    created_items.at[0, 'Formula'] = '$T + 100'
    created_items.at[1, 'Formula'] = 'weekends()'
    created_items.at[2, 'Formula'] = '10kW'

    push_df = spy.push(metadata=created_items, workbook=None)

    assert push_df.iloc[0]['ID'] == signal_output.id
    assert push_df.iloc[1]['ID'] == condition_output.id
    assert push_df.iloc[2]['ID'] == scalar_output.id

    pushed_signal = spy.search(pd.DataFrame([{'ID': signal_output.id},
                                             {'ID': condition_output.id},
                                             {'ID': scalar_output.id}]),
                               all_properties=True)

    assert pushed_signal.iloc[0]['Formula'] == '$T + 100'
    assert pushed_signal.iloc[0]['Formula Parameters'] == [formula_parameters[1]]
    assert pushed_signal.iloc[1]['Formula'] == 'weekends()'
    assert pushed_signal.iloc[1]['Formula Parameters'] == []
    assert pushed_signal.iloc[2]['Formula'] == '10kW'
    assert pushed_signal.iloc[2]['Formula Parameters'] == []


@pytest.mark.system
def test_push_signal_with_metadata():
    witsml_folder = os.path.dirname(__file__)
    witsml_file = '011_02_0.csv'
    witsml_df = pd.read_csv(os.path.join(witsml_folder, witsml_file))
    timestamp_column = witsml_df.columns[0]
    witsml_df = pd.read_csv(os.path.join(witsml_folder, witsml_file), parse_dates=[timestamp_column])
    witsml_df = witsml_df.drop(list(witsml_df.filter(regex='.*Unnamed.*')), axis=1)
    witsml_df = witsml_df.dropna(axis=1, how='all')
    witsml_df = witsml_df.set_index(timestamp_column)

    metadata = pd.DataFrame({'Header': witsml_df.columns.values})
    metadata['Type'] = 'Signal'
    metadata['Tag'] = metadata['Header'].str.extract(r'(.*)\(')
    metadata['Value Unit Of Measure'] = metadata['Header'].str.extract(r'\((.*)\)')
    metadata['File'] = witsml_file
    metadata['Well Number'] = metadata['File'].str.extract(r'(\d+)_\d+_\d+\.csv')
    metadata['Wellbore ID'] = metadata['File'].str.extract(r'\d+_(\d+)_\d+\.csv')

    metadata = metadata.set_index('Header')

    # Without a Name column, we expect the push metadata to fail
    with pytest.raises(RuntimeError):
        spy.push(data=witsml_df, metadata=metadata)

    metadata['Name'] = "Well_" + metadata['Well Number'] + "_" + "Wellbore_" + \
                       metadata['Wellbore ID'] + "_" + metadata['Tag']

    push_results_df = spy.push(data=witsml_df, metadata=metadata, workbook=None)

    search_results_df = spy.search(push_results_df.iloc[0], workbook=None)

    assert len(search_results_df) == 1
    assert search_results_df.iloc[0]['Name'] == metadata.iloc[0]['Name']
    assert 'Push Result' not in search_results_df
    assert 'Push Count' not in search_results_df
    assert 'Push Time' not in search_results_df

    pull_results_df = spy.pull(search_results_df,
                               start='2016-07-25T15:00:00.000-07:00',
                               end='2019-07-25T17:00:00.000-07:00',
                               grid=None)

    assert len(pull_results_df) == 999

    # noinspection PyUnresolvedReferences
    assert (witsml_df.index == pull_results_df.index).all()

    witsml_list = witsml_df['BITDEP(ft)'].tolist()
    pull_list = pull_results_df['Well_011_Wellbore_02_BITDEP'].tolist()
    assert witsml_list == pull_list


@pytest.mark.system
def test_push_capsules():
    capsule_data = pd.DataFrame([{
        'Capsule Start': pd.to_datetime('2019-01-10T09:00:00.000Z'),
        'Capsule End': pd.to_datetime('2019-01-10T17:00:00.000Z'),
        'Operator On Duty': 'Mark'
    }, {
        'Capsule Start': pd.to_datetime('2019-01-11T09:00:00.000Z'),
        'Capsule End': pd.to_datetime('2019-01-11T17:00:00.000Z'),
        'Operator On Duty': 'Hedwig'
    }])

    try:
        spy.push(data=capsule_data,
                 metadata=pd.DataFrame([{
                     'Name': 'Operator Shifts',
                     'Type': 'Condition'
                 }]))

        assert False, 'Without a Maximum Duration, we expect the push to fail'

    except RuntimeError as e:
        assert 'Maximum Duration' in str(e)

    push_result = spy.push(data=capsule_data,
                           metadata=pd.DataFrame([{
                               'Name': 'Operator Shifts',
                               'Type': 'Condition',
                               'Maximum Duration': '2d'
                           }]))

    assert len(push_result) == 1
    assert push_result.iloc[0]['Name'] == 'Operator Shifts'
    assert push_result.iloc[0]['Push Count'] == 2

    pull_result = spy.pull(push_result, start='2019-01-01T09:00:00.000Z', end='2019-02-01T09:00:00.000Z')

    assert len(pull_result) == 2
    assert pull_result.iloc[0]['Condition'] == 'Operator Shifts'
    assert pull_result.iloc[0]['Capsule Start'] == pd.to_datetime('2019-01-10T09:00:00.000Z')
    assert pull_result.iloc[0]['Capsule End'] == pd.to_datetime('2019-01-10T17:00:00.000Z')
    assert pull_result.iloc[0]['Operator On Duty'] == 'Mark'
    assert pull_result.iloc[1]['Condition'] == 'Operator Shifts'
    assert pull_result.iloc[1]['Capsule Start'] == pd.to_datetime('2019-01-11T09:00:00.000Z')
    assert pull_result.iloc[1]['Capsule End'] == pd.to_datetime('2019-01-11T17:00:00.000Z')
    assert pull_result.iloc[1]['Operator On Duty'] == 'Hedwig'


@pytest.mark.system
def test_push_threshold_metric_metadata():
    signals_for_testing = spy.search({
        'Path': 'Example >> Cooling Tower 1 >> Area A'
    })

    # test an expected successful push
    test_dict = {'Type': 'Threshold Metric',
                 'Name': 'push test threshold metric',
                 'Measured Item': signals_for_testing[signals_for_testing['Name'] == 'Temperature']['ID'].iloc[0],
                 'Thresholds': [{'Lo': signals_for_testing[signals_for_testing['Name'] == 'Wet Bulb']['ID'].iloc[0],
                                 '3': 90}]
                 }
    test_metadata = pd.DataFrame(test_dict)

    push_output = spy.push(metadata=test_metadata)

    metrics_api = MetricsApi(spy._login.client)
    confirm_push_output = metrics_api.get_metric(id=push_output['ID'].iloc[0])
    assert confirm_push_output.measured_item.id == test_metadata['Measured Item'].iloc[0]
    tp = [t.priority.level for t in confirm_push_output.thresholds]
    assert confirm_push_output.thresholds[tp.index(-1)].item.id == test_metadata['Thresholds'].iloc[0]['Lo']
    assert confirm_push_output.thresholds[tp.index(3)].value.value == 90

    # Test using metric string levels not defined on the system
    test_metadata['Thresholds'].iloc[0]['9'] = 100
    try:
        spy.push(metadata=test_metadata)
        assert False
    except ApiException as e:
        assert e.status == 400

    # Test using metric string levels that map to multiple values at the same level
    test_metadata.at[0, 'Thresholds'] = {
        'Lo': signals_for_testing[signals_for_testing['Name'] == 'Wet Bulb']['ID'].iloc[0],
        '-1': 90}

    with pytest.raises(RuntimeError):
        spy.push(metadata=test_metadata)

    # Test specifying threshold colors
    test_metadata.at[0, 'Thresholds'] = {
        'Lo#Ff0000': signals_for_testing[signals_for_testing['Name'] == 'Wet Bulb']['ID'].iloc[0],
        '3#00fF00': 90
    }

    push_output = spy.push(metadata=test_metadata)
    confirm_push_output = metrics_api.get_metric(id=push_output['ID'].iloc[0])
    tp = [t.priority.level for t in confirm_push_output.thresholds]
    assert confirm_push_output.thresholds[tp.index(-1)].priority.color == '#ff0000'
    assert confirm_push_output.thresholds[tp.index(3)].priority.color == '#00ff00'

    # Test bad color code
    test_metadata.at[0, 'Thresholds'] = {
        'Lo#gg0000': signals_for_testing[signals_for_testing['Name'] == 'Wet Bulb']['ID'].iloc[0],
        '3#00ff00': 90
    }

    with pytest.raises(RuntimeError):
        spy.push(metadata=test_metadata)

    # Test converting a measured item defined by a dataframe
    temperature_index = signals_for_testing[signals_for_testing['Name'] == 'Temperature'].index.to_list()[0]
    test_dict = [{'Type': 'Threshold Metric',
                  'Name': 'push test threshold metric',
                  'Measured Item': signals_for_testing.iloc[temperature_index].to_dict(),
                  'Thresholds': {'Lo': signals_for_testing[signals_for_testing['Name'] == 'Wet Bulb']['ID'].iloc[0],
                                 '3': 90}}]
    test_metadata = pd.DataFrame(test_dict)

    push_output = spy.push(metadata=test_metadata)
    confirm_push_output = metrics_api.get_metric(id=push_output.at[0, 'ID'])
    assert confirm_push_output.measured_item.name == 'Temperature'

    # Test a threshold defined by a dataframe
    wetbulb_index = signals_for_testing[signals_for_testing['Name'] == 'Wet Bulb'].index.to_list()[0]
    test_dict = [{'Type': 'Threshold Metric',
                  'Name': 'push test threshold metric',
                  'Measured Item': signals_for_testing[signals_for_testing['Name'] == 'Temperature']['ID'].iloc[0],
                  'Thresholds': {'Lo': signals_for_testing.iloc[wetbulb_index].to_dict(),
                                 '3': 90}}]
    test_metadata = pd.DataFrame(test_dict)

    push_output = spy.push(metadata=test_metadata)
    confirm_push_output = metrics_api.get_metric(id=push_output.at[0, 'ID'])
    threshold_items = [t.item.name for t in confirm_push_output.thresholds]
    assert 'Wet Bulb' in threshold_items

    # Test pushing a threshold metric with a percentile
    test_dict = [{'Type': 'Threshold Metric',
                  'Name': 'push test threshold metric',
                  'Measured Item': signals_for_testing.iloc[temperature_index].to_dict(),
                  'Statistic': 'Percentile(50)'}]
    test_metadata = pd.DataFrame(test_dict)

    push_output = spy.push(metadata=test_metadata)
    confirm_push_output = metrics_api.get_metric(id=push_output.at[0, 'ID'])
    assert confirm_push_output.aggregation_function == 'percentile(50)'

    # Test pushing a threshold metric with a rate
    test_dict = [{'Type': 'Threshold Metric',
                  'Name': 'push test threshold metric',
                  'Measured Item': signals_for_testing.iloc[temperature_index].to_dict(),
                  'Statistic': 'Rate("min")'}]
    test_metadata = pd.DataFrame(test_dict)

    push_output = spy.push(metadata=test_metadata)
    confirm_push_output = metrics_api.get_metric(id=push_output.at[0, 'ID'])
    assert confirm_push_output.aggregation_function == 'rate("min")'

    # Test pushing a threshold metric with a total duration
    test_condition = pd.DataFrame([
        {'Type': 'Condition',
         'Name': 'Test condition for threshold metrics',
         'Formula': '$a>80',
         'Formula Parameters': {'a': signals_for_testing.iloc[temperature_index].to_dict()}}
    ])
    test_condition_push_result = spy.push(metadata=test_condition)
    test_dict = [{'Type': 'Threshold Metric',
                  'Name': 'push test threshold metric',
                  'Measured Item': test_condition_push_result.iloc[0].to_dict(),
                  'Measured Item Maximum Duration': '40h',
                  'Statistic': 'Total Duration("min")'}]
    test_metadata = pd.DataFrame(test_dict)

    push_output = spy.push(metadata=test_metadata)
    confirm_push_output = metrics_api.get_metric(id=push_output.at[0, 'ID'])
    assert confirm_push_output.aggregation_function == 'totalDuration("min")'


@pytest.mark.system
def test_push_signal_metadata_with_bad_case_on_uom_property():
    # Written to address https://www.seeq.org/index.php?/forums/topic/672-handling-of-invalid-units

    date_index = pd.date_range('01/14/2020 01:00:00', periods=115, freq='h')

    samples = np.arange(0, 115)
    data = pd.DataFrame(data=samples, index=date_index, columns=['Testdataset2'])

    metadata = {
        'Name': 'Testsignal 5',
        'Type': 'Signal',
        'Maximum Interpolation': '1h',
        'Value Unit of Measure': '1/Min',
        'Interpolation Method': 'Step'
    }

    with pytest.raises(RuntimeError, match='Incorrect case'):
        spy.push(data, metadata=pd.DataFrame([metadata], index=['Testdataset2']), workbook=None)

    del metadata['Value Unit of Measure']
    metadata['Value Unit Of Measure'] = '1/Min'

    spy.push(data, metadata=pd.DataFrame([metadata], index=['Testdataset2']), workbook=None)


@pytest.mark.system
def test_push_archived_item():
    search_df = spy.search({
        'Name': 'Area A_Temperature'
    })

    spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'An Archived Thing',
        'Formula': '$a',
        'Formula Parameters': {
            '$a': search_df.iloc[0]['ID']
        },
        'UIConfig': {'blah': 'blah'},
        'Archived': False
    }]))

    search_df = spy.search({
        'Name': 'An Archived Thing'
    })
    assert len(search_df) == 1

    search_df['Archived'] = True
    with pytest.raises(ApiException):
        # This will fail because we aren't pushing a complete definition
        spy.push(metadata=search_df)

    search_df = spy.search({
        'Name': 'An Archived Thing'
    }, all_properties=True)
    assert len(search_df) == 1

    # Note that we handle both boolean and string in the Archived field
    search_df['Archived'] = 'true'
    spy.push(metadata=search_df)

    empty_df = spy.search({
        'Name': 'An Archived Thing'
    })
    assert len(empty_df) == 0

    search_df['Archived'] = False
    spy.push(metadata=search_df)

    not_empty_df = spy.search({
        'Name': 'An Archived Thing'
    })
    assert len(not_empty_df) == 1


# Disabled because of CRAB-19041
@pytest.mark.disabled
def test_push_archived_item_in_tree():
    spy.push(metadata=pd.DataFrame([{
        'Path': 'test_push_archived_item_in_tree',
        'Asset': 'The Asset',
        'Name': 'The Thing',
        'Type': 'Signal',
        'Archived': True
    }]))

    search_df = spy.search({
        'Path': 'test_push_archived_item_in_tree'
    }, include_archived=False)

    assert len(search_df) == 1
    assert search_df.iloc[0]['Type'] == 'Asset'
    # No signal was found, only the asset -- that's good.

    search_df = spy.search({
        'Path': 'test_push_archived_item_in_tree'
    }, include_archived=True)

    # This currently fails due to CRAB-19041. The spy.search() call just above will have the @includeUnsearchable flag,
    # but for some reason "The Thing" is not returned. HOWEVER, if you push it with Archived as False, then push it
    # again with Archived as True, it gets returned properly from that point forward.
    assert len(search_df) > 1


@pytest.mark.system
def test_push_reference():
    search_df = spy.search({'Name': 'Area A_Temperature'})
    area_a_temp = search_df.squeeze()
    push_df = pd.DataFrame([
        {
            'Type': area_a_temp['Type'],
            'ID': area_a_temp['ID'],
            'Name': 'Coldness Conductivity',
            'Asset': 'Winter',
            'Path': 'Seasons',
            # _metadata._build_reference_signal will set the units to what's in the DataFrame
            'Value Unit Of Measure': 'µS/cm',
            'Reference': True
        },
        {
            'Type': area_a_temp['Type'],
            'ID': area_a_temp['ID'],
            'Name': 'Susceptance',
            'Asset': 'Winter',
            'Path': 'Seasons',
            # µS/cm is specifically stated as supported, but µS by itself is not specifically stated -- it is implied
            'Value Unit Of Measure': 'µS',
            'Reference': True
        },
        {
            'Type': area_a_temp['Type'],
            'ID': area_a_temp['ID'],
            'Name': 'Volume of Coldness',
            'Asset': 'Winter',
            'Path': 'Seasons',
            'Value Unit Of Measure': 'cm³·°F',
            'Reference': True
        },
        {
            'Type': area_a_temp['Type'],
            'ID': area_a_temp['ID'],
            'Name': 'Cold Barrels',
            'Asset': 'Winter',
            'Path': 'Seasons',
            'Value Unit Of Measure': 'bbl/mol',
            'Reference': True
        }
    ])

    push_results_df = spy.push(metadata=push_df)

    search_push_results_df = spy.search(push_results_df)

    assert len(search_push_results_df) == 4

    coldness_conductivity = search_push_results_df[search_push_results_df['Name'] == 'Coldness Conductivity'].squeeze()
    assert coldness_conductivity['Value Unit Of Measure'] == 'µS/cm'
    assert coldness_conductivity['Referenced ID'] == area_a_temp['ID']
    assert coldness_conductivity['ID'] != area_a_temp['ID']

    susceptance = search_push_results_df[search_push_results_df['Name'] == 'Susceptance'].squeeze()
    assert susceptance['Value Unit Of Measure'] == 'µS'
    assert susceptance['Referenced ID'] == area_a_temp['ID']
    assert susceptance['ID'] != area_a_temp['ID']

    volume_of_coldness = search_push_results_df[search_push_results_df['Name'] == 'Volume of Coldness'].squeeze()
    assert volume_of_coldness['Value Unit Of Measure'] == 'cm³·°F'
    assert volume_of_coldness['Referenced ID'] == area_a_temp['ID']
    assert volume_of_coldness['ID'] != area_a_temp['ID']

    cold_barrels = search_push_results_df[search_push_results_df['Name'] == 'Cold Barrels'].squeeze()
    assert cold_barrels['Value Unit Of Measure'] == 'bbl/mol'
    assert cold_barrels['Referenced ID'] == area_a_temp['ID']
    assert cold_barrels['ID'] != area_a_temp['ID']


@pytest.mark.system
def test_crab_21092():
    workbook = 'Test Time Zones'
    worksheet = 'timezones'
    data_df = pd.DataFrame()
    data_df['String'] = pd.Series([
        1.,
        2.,
        1.4,
        1.6,
        1.8
    ], index=[
        pd.Timestamp('2019-01-01 00:00', tz='US/Central'),
        pd.Timestamp('2019-01-01 00:00', tz='US/Central'),
        pd.Timestamp('2019-01-01 00:00', tz='US/Central'),
        pd.Timestamp('2019-01-01 00:00', tz='US/Central'),
        pd.Timestamp('2019-01-01 00:00', tz='US/Central')  # This timestamp won't show up in the pull
    ])

    spy.push(data_df, workbook=workbook, worksheet=worksheet)
    workbooks_df = spy.workbooks.search({
        'Name': workbook
    })
    workbooks = spy.workbooks.pull(workbooks_df, include_inventory=False, quiet=True)
    worksheet_start = workbooks[0].worksheets[0].display_range['Start'].value
    assert worksheet_start == data_df.index[0].value


@pytest.mark.system
def test_push_spaces_in_path_separator():
    signal_name = 'test_crab_20614_1'

    spy.push(metadata=pd.DataFrame([{
        'Type': 'StoredSignal',
        'Name': signal_name,
        'Path': "A>>B >>C"
    }]))
    spy.push(metadata=pd.DataFrame([{
        'Type': 'StoredSignal',
        'Name': signal_name,
        'Path': "A >> B >> C"
    }]))
    spy.push(metadata=pd.DataFrame([{
        'Type': 'StoredSignal',
        'Name': signal_name,
        'Path': " A>> B>>C "
    }]))

    pushed_results = spy.search({'Name': signal_name})
    assert len(pushed_results) == 1


@pytest.mark.system
def test_push_dataframe_nan_column():
    workbook = 'Test NaN Signal'
    worksheet = 'nan worksheet'

    data_df = pd.DataFrame()
    df_index = pd.date_range('2020-01-01', periods=5, freq='s')
    data_df['Normal Signal'] = pd.Series(np.arange(5.0), index=df_index)
    data_df['NaN Signal Numerical'] = pd.Series(np.full(5, np.nan), index=df_index)
    data_df['NaN Signal String'] = pd.Series(np.full(5, np.nan), index=df_index)

    # Test that pushing NaN-only columns without units of measure fails with correct error message
    push_results_df = spy.push(data_df, workbook=workbook, worksheet=worksheet, errors='catalog')
    assert 'contains no data and no value' \
           ' unit of measure was provided' in push_results_df.loc['NaN Signal Numerical', 'Push Result']
    assert 'contains no data and no value' \
           ' unit of measure was provided' in push_results_df.loc['NaN Signal String', 'Push Result']

    metadata_df = push_results_df.copy()
    metadata_df['Value Unit Of Measure'] = ['seconds', 'kg', 'string']
    metadata_df['Type'] = 'Signal'
    metadata_df.drop(columns=['ID'], inplace=True)

    # Test that pushing NaN-only columns with units of measure succeeds
    push_results_df = spy.push(data_df, metadata=metadata_df, workbook=workbook, worksheet=worksheet)
    assert (push_results_df['Push Result'] == 'Success').all()
    assert (push_results_df['Push Count'] == [5, 0, 0]).all()

    # Test pushing only NaNs to a pre-existing signal
    data_df['Normal Signal'] = np.nan
    # Test pushing numerical data to a signal created by a NaN-only spy.push() call
    data_df.loc['2020-01-01 00:00:00', 'NaN Signal Numerical'] = 3.14
    # Test pushing string data to a signal created by a NaN-only spy.push() call
    data_df.loc['2020-01-01 00:00:00', 'NaN Signal String'] = 'foo'

    new_push_results_df = spy.push(data_df, metadata=metadata_df, workbook=workbook, worksheet=worksheet)
    assert (new_push_results_df['Push Result'] == 'Success').all()
    assert (new_push_results_df['Push Count'] == [0, 1, 1]).all()


@pytest.mark.system
def test_push_src_max_interp():
    push_df = spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'test_src_max_interp',
        'Source Maximum Interpolation': '2min'
    }]), workbook='test_push_src_max_interp_wb', worksheet='test_push_src_max_interp_ws')
    assert (push_df['Push Result'] == 'Success').all()


@pytest.mark.performance
def test_push_performance():
    # This test is not currently publishing anything to "sq perf", but my hope is that eventually we have a set of
    # these SPy performance tests that are monitored for performance regressions. For now it's just a convenient
    # way to look at push performance.
    sample_count = 200000
    data_df = pd.DataFrame(np.random.randint(0, 100, size=(sample_count, 4)), columns=list('ABCD'))
    timestamps = pd.date_range(start='2020-01-01', end='2020-06-01', periods=sample_count)
    data_df.index = timestamps

    push_df = spy.push(data_df)
    status_df = push_df.status.df
    print(status_df[['Count', 'Time']])
