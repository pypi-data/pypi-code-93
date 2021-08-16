import pytest
import uuid
import tempfile
from pathlib import Path

import pandas as pd

from seeq import spy
from seeq.sdk import *
from seeq.sdk.rest import ApiException

from seeq.spy.workbooks import Topic, Analysis

from seeq.spy.tests import test_common

from seeq.spy import _config


def setup_module():
    test_common.login()


@pytest.mark.system
def test_simple_search():
    search_results = spy.search({
        'Name': 'Area A_Temper'
    })

    assert len(search_results) == 1
    assert 'Estimated Sample Period' not in search_results

    search_results = spy.search(pd.DataFrame([{
        'Name': 'Area A_Temper'
    }]))

    # Nothing will be returned because we use a equal-to comparison when a DataFrame is passed in
    assert len(search_results) == 0

    search_results = spy.search(pd.DataFrame([{
        'Name': 'Area A_Temperature'
    }]))

    assert len(search_results) == 1

    search_results = spy.search(pd.DataFrame([{
        'Name': 'Area A_Temperature'
    }]), all_properties=True)

    assert len(search_results) == 1
    assert 'Maximum Interpolation' in search_results.iloc[0]


@pytest.mark.system
def test_search_without_pushed_workbook():
    # This test ensures that spy.search() returns consistent results with and without a pushed default workbook.
    # In older versions, if a default workbook had not been pushed, spy.search() would return results from ANY
    # workbook.

    # Make sure there is only one thing that contains 'Area B_Rel'. It will be the (global) stored signal from the
    # example data.
    search_results = spy.search({
        'Name': 'Area B_Rel'
    })
    assert len(search_results) == 1

    # Push a new workbook so that we can push a new signal that is scoped to it
    workbook = Analysis('test_signal_in_another_workbook')
    worksheet = workbook.worksheet('auto-created-worksheet')
    spy.workbooks.push(workbook)

    spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'Area B_Rel',
        'Formula': 'sinusoid()'
    }]), workbook=workbook.id, worksheet=worksheet.name)

    search_results = spy.search({
        'Name': 'Area B_Rel'
    })

    # We should still only have one result, since the workbook that we pushed to should be excluded
    assert len(search_results) == 1

    # Push should create the default workbook (if it didn't exist)
    spy.push()

    search_results = spy.search({
        'Name': 'Area B_Rel'
    })

    # We should still have the 1 result (the global stored signal), but this time the scope of the search is global +
    # default workbook
    assert len(search_results) == 1

    # Now push a signal to the default workbook.
    push_df = spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'Area B_Rel',
        'Formula': 'sinusoid()'
    }]))

    search_results = spy.search({
        'Name': 'Area B_Rel'
    })

    # We should now have two results since we pushed a signal to the default workbook
    assert len(search_results) == 2

    # Rename the pushed signal so that this test can be run multiple times
    items_api = ItemsApi(test_common.get_client())
    items_api.set_property(id=push_df.iloc[0]['ID'], property_name='Name',
                           body=PropertyInputV1(value='test_search_without_pushed_workbook_trash'))


@pytest.mark.system
def test_dataframe_single_row_with_id():
    search_results = spy.search({
        'Name': 'Area A_Temper'
    })

    search_results = spy.search(search_results.iloc[0])

    assert len(search_results) == 1
    assert search_results.iloc[0]['Name'] == 'Area A_Temperature'
    assert search_results.iloc[0]['Data ID'] == '[Tag] Area A_Temperature.sim.ts.csv'


@pytest.mark.system
def test_dataframe_multi_row():
    search_results = spy.search(pd.DataFrame([{
        'Name': 'Area A_Relative Humidity',
        'Datasource Name': 'Example Data'
    }, {
        'Name': 'Area A_Temperature',
        'Datasource Name': 'Example Data'
    }, {
        'Path': 'Example >> Cooling Tower 1 >> Area A',
        'Name': 'Relative Humidity'
    }]))

    assert len(search_results) == 3
    assert len(search_results[search_results['Name'] == 'Area A_Temperature']) == 1
    assert len(search_results[search_results['Name'] == 'Area A_Relative Humidity']) == 1
    assert len(search_results[search_results['Name'] == 'Relative Humidity']) == 1


@pytest.mark.system
def test_dataframe_warnings_and_duplicates():
    search_results = spy.search([{
        'Name': 'Humid',
        'Path': 'Example >> Cooling Tower 1'
    }, {
        'Name': 'Area A_',
        'Datasource Name': 'Example Data'
    }, {
        'Name': 'Area A_',
        'Datasource Name': 'Example Data'
    }])

    # Make sure the duplicates will have been dropped
    assert len(search_results) == 14

    assert len(search_results.status.warnings) == 1
    assert '6 duplicates removed' in search_results.status.warnings.pop()

    search_results.drop(columns=['ID'], inplace=True)

    search_results2 = spy.search(search_results)

    # There will be a warning because 'Value Unit Of Measure' will be part of the DataFrame but it can't be searched on
    assert len(search_results2.status.warnings) == 1
    assert 'are not indexed and will be ignored:\n"Value Unit Of Measure", "Archived"' in \
           search_results2.status.warnings.pop()

    assert len(search_results2) == 14

    unique_ids = search_results2['ID'].drop_duplicates().to_list()
    assert len(unique_ids) == 14


@pytest.mark.system
def test_path_with_datasource():
    search_results = spy.search({
        'Name': 'Area ?_*',
        'Datasource Name': 'Example Data'
    })

    push_df = search_results.copy()
    push_df['Reference'] = True
    push_df['Path'] = 'test_path_with_datasource-tree >> branch-alpha'
    push_df['Asset'] = push_df['Name'].str.extract(r'(Area .)_.*')
    push_df['Name'] = push_df['Name'].str.extract(r'Area ._(.*)')

    spy.push(metadata=push_df, datasource='test_path_with_datasource-name-1')

    push_df['Path'] = 'test_path_with_datasource-tree >> branch-bravo'

    spy.push(metadata=push_df, datasource='test_path_with_datasource-name-2')

    search_results = spy.search({
        'Path': 'test_path_with_datasource-tree',
    }, recursive=False)

    paths = search_results['Path'].drop_duplicates().dropna().tolist()
    assets = search_results['Asset'].drop_duplicates().tolist()
    names = sorted(search_results['Name'].tolist())
    types = search_results['Type'].drop_duplicates().tolist()

    assert len(paths) == 0
    assert assets == ['test_path_with_datasource-tree']
    assert names == ['branch-alpha', 'branch-bravo']
    assert types == ['Asset']

    search_results = spy.search({
        'Path': 'test_path_with_datasource-tree',
    }, recursive=True)

    assert len(search_results) > 100
    types = sorted(search_results['Type'].drop_duplicates().tolist())
    assert types == ['Asset', 'CalculatedSignal']
    assert len(search_results[search_results['Asset'] == 'branch-alpha']) > 0
    assert len(search_results[search_results['Asset'] == 'branch-bravo']) > 0

    search_results = spy.search({
        'Path': 'test_path_with_datasource-tree >> branch-alpha',
    }, recursive=True)

    assert len(search_results[search_results['Asset'] == 'branch-alpha']) > 0
    assert len(search_results[search_results['Asset'] == 'branch-bravo']) == 0

    search_results = spy.search({
        'Path': 'test_path_with_datasource-tree >> branch-*',
    }, recursive=True)

    assert len(search_results[search_results['Asset'] == 'branch-alpha']) > 0
    assert len(search_results[search_results['Asset'] == 'branch-bravo']) > 0

    search_results = spy.search({
        'Path': 'test_path_with_datasource-* >> branch-bravo',
    }, recursive=True)

    assert len(search_results[search_results['Asset'] == 'branch-alpha']) == 0
    assert len(search_results[search_results['Asset'] == 'branch-bravo']) > 0

    search_results = spy.search({
        'Path': 'test_path_with_datasource-* >> branch-bravo',
        'Datasource Name': 'test_path_with_datasource-name-1'
    }, recursive=True)

    assert len(search_results) == 0

    search_results = spy.search({
        'Path': 'test_path_with_datasource-* >> branch-alpha',
        'Datasource Name': 'test_path_with_datasource-name-1'
    }, recursive=True)

    assert len(search_results[search_results['Asset'] == 'branch-alpha']) > 0
    assert len(search_results[search_results['Asset'] == 'branch-bravo']) == 0


@pytest.mark.system
def test_dataframe_bad_datasource():
    with pytest.raises(RuntimeError):
        spy.search(pd.DataFrame([{
            'Name': 'Area A_Temperature',
            'Datasource Name': 'Bad Datasource'
        }]))


@pytest.mark.system
def test_type_search():
    search_results = spy.search({
        'Datasource Class': 'Time Series CSV Files',
        'Type': 'Signal'
    })

    assert 150 < len(search_results) < 230

    datasource_names = set(search_results['Datasource Name'].tolist())
    assert len(datasource_names) == 1
    assert datasource_names.pop() == 'Example Data'

    types = set(search_results['Type'].tolist())
    assert len(types) == 1
    assert types.pop() == 'StoredSignal'

    search_results = spy.search({
        'Datasource Class': 'Time Series CSV Files',
        'Type': 'Condition'
    })

    assert len(search_results) == 0

    search_results = spy.search({
        'Datasource Class': 'Time Series CSV Files',
        'Type': 'Scalar'
    })

    assert len(search_results) == 0

    search_results = spy.search({
        'Datasource Class': 'Time Series CSV Files',
        'Type': 'Asset'
    })

    assert 5 < len(search_results) < 20

    # Multiple types
    search_results = spy.search({
        'Datasource Class': 'Time Series CSV Files',
        'Type': ['Signal', 'Asset']
    })

    assert 160 < len(search_results) < 300
    assert 5 < len(search_results[search_results['Type'] == 'Asset']) < 20
    assert 150 < len(search_results[search_results['Type'].str.contains('Signal')]) < 230


@pytest.mark.system
def test_path_search_recursive():
    search_results = spy.search({
        'Path': 'Non-existent >> Path'
    })

    assert len(search_results) == 0

    search_results = spy.search({
        'Path': 'Example >> Cooling Tower 1'
    })

    assert 40 < len(search_results) < 60

    search_results = spy.search({
        'Path': '*xamp* >> Cooling Tower *',
        'Name': '*Compressor*'
    }, workbook=None)

    names = search_results['Name'].drop_duplicates().tolist()
    assert len(names) == 2
    assert 'Compressor Power' in names
    assert 'Compressor Stage' in names
    paths = search_results['Path'].drop_duplicates().tolist()
    assert len(paths) == 2
    assert 'Example >> Cooling Tower 1' in paths
    assert 'Example >> Cooling Tower 2' in paths

    search_results = spy.search({
        'Path': 'Example >> /Cooling Tower [2]/',
        'Name': '*Compressor*'
    }, workbook=None)

    names = search_results['Name'].drop_duplicates().tolist()
    assert len(names) == 2
    assert 'Compressor Power' in names
    assert 'Compressor Stage' in names
    paths = search_results['Path'].drop_duplicates().tolist()
    assert len(paths) == 1
    assert 'Example >> Cooling Tower 2' in paths


@pytest.mark.system
def test_path_search_non_recursive():
    search_results = spy.search({
        'Path': 'Exampl',
        'Type': 'Asset'
    }, recursive=None)

    assert len(search_results) == 0

    search_results = spy.search({
        'Path': 'Example',
        'Type': 'Asset'
    }, recursive=None)

    assert len(search_results) == 2

    search_results = spy.search({
        'Path': 'Example >> Cooling Tower 1',
        'Name': '/Area [ABC]/'
    }, recursive=False, workbook=None)

    assert len(search_results) == 3
    types = search_results['Type'].drop_duplicates().tolist()
    assert len(types) == 1
    assert types[0] == 'Asset'

    search_results = spy.search({
        'Path': 'Example >> Cooling Tower *',
        'Asset': 'Area A',
        'Name': '*Compressor*'
    }, recursive=False, workbook=None)

    assert len(search_results) == 2
    names = search_results['Name'].tolist()
    assert len(names) == 2
    assert 'Compressor Power' in names
    assert 'Compressor Stage' in names
    paths = search_results['Path'].drop_duplicates().tolist()
    assert len(paths) == 1
    assert paths[0] == 'Example >> Cooling Tower 1'


@pytest.mark.system
def test_path_search_pagination():
    # This tests the 'Path' finding code to make sure we'll find a path even if pagination
    # is required.
    original_page_size = _config.options.search_page_size
    try:
        _config.options.search_page_size = 1
        search_results = spy.search({
            'Path': 'Example >> Cooling Tower 1 >> Area G'
        }, recursive=False, workbook=None)

        assert len(search_results) == 6
    finally:
        _config.options.search_page_size = original_page_size


@pytest.mark.system
def test_path_search_root_only():
    search_results = spy.search(pd.DataFrame({
        'Path': [''],
        'Name': ['Example'],
        'Type': ['Asset']
    }), recursive=False)

    assert len(search_results) == 1
    assert search_results.iloc[0]['Name'] == 'Example'
    assert search_results.iloc[0]['Type'] == 'Asset'
    assert 'Path' not in search_results.columns
    assert 'Asset' not in search_results.columns


@pytest.mark.system
def test_asset_id_search():
    search_results = spy.search({
        'Path': 'Example >> Cooling Tower 1',
        'Type': 'Asset'
    })

    asset_id = search_results[search_results['Name'] == 'Area C'].iloc[0]['ID']

    asset_search = spy.search({'Asset': asset_id})

    assert len(asset_search) > 1
    assert all([a == 'Area C' for a in asset_search['Asset'].tolist()])

    asset_search = spy.search({'Asset': asset_id, 'Name': 'Temperature'})

    assert len(asset_search) == 1
    asset = asset_search.iloc[0]
    assert asset['Asset'] == 'Area C'
    assert asset['Name'] == 'Temperature'


@pytest.mark.system
def test_datasource_name_search():
    with pytest.raises(RuntimeError):
        spy.search({
            'Datasource Name': 'Non-existent'
        })

    search_results = spy.search({
        'Datasource Name': 'Example Data'
    })

    assert 150 < len(search_results) < 245


@pytest.mark.system
def test_search_pagination():
    original_page_size = _config.options.search_page_size
    try:
        _config.options.search_page_size = 2
        search_results = spy.search({
            'Name': 'Area A_*'
        })

        assert len(search_results) == 6

    finally:
        _config.options.search_page_size = original_page_size


@pytest.mark.system
def test_search_bad_workbook():
    with pytest.raises(RuntimeError):
        spy.search({
            'Name': 'Area A_*'
        }, workbook='bad')


@pytest.mark.system
def test_search_workbook_guid():
    # The workbook won't be found, so we'll get an access error
    with pytest.raises(ApiException):
        spy.search({
            'Name': 'Area A_*'
        }, workbook='A0B89103-E95D-4E32-A809-390C1FAE9D2F')


@pytest.mark.system
def test_include_archived():
    search_df = spy.search({'Name': 'Area A_*', 'Datasource ID': 'Example Data'})
    area_a_ids = search_df['ID'].tolist()
    area_a_count = len(area_a_ids)
    items_api = ItemsApi(test_common.get_client())

    def _do_archive(archive):
        for _id in area_a_ids:
            items_api.set_property(id=_id, property_name='Archived', body=PropertyInputV1(value=archive))

    try:
        _do_archive(True)
        search_df = spy.search({'Name': 'Area A_*', 'Datasource ID': 'Example Data'})
        assert len(search_df) == 0
        search_df = spy.search({'Name': 'Area A_*', 'Datasource ID': 'Example Data'}, include_archived=True)
        assert len(search_df) == area_a_count
    finally:
        _do_archive(False)

    with pytest.raises(ValueError):
        spy.search({'Path': 'Example', 'Datasource ID': 'Example Data'}, recursive=False, include_archived=True)


@pytest.mark.system
def test_simple_search_with_estimated_sample_period():
    search_results = spy.search({
        'Name': 'Area A_Temper'
    }, estimate_sample_period=dict(Start=None, End=None))

    assert len(search_results) == 1
    assert 'Estimated Sample Period' in search_results
    assert (search_results['Estimated Sample Period'].map(type) == pd.Timedelta).all()

    search_results = spy.search(
        pd.DataFrame([{
            'Name': 'Area A_Temperature'
        }]),
        estimate_sample_period=dict(Start='2018-01-01T00:00:00.000Z', End='2018-06-01T00:00:00.000Z'))

    assert len(search_results) == 1
    assert 'Estimated Sample Period' in search_results
    assert (search_results['Estimated Sample Period'].map(type) == pd.Timedelta).all()
    assert search_results.at[0, 'Estimated Sample Period'] == pd.to_timedelta(120.0, unit='s')


@pytest.mark.system
def test_dataframe_with_estimated_sample_period():
    search_results = spy.search(pd.DataFrame([{
        'Name': 'Area A_Relative Humidity',
        'Datasource Name': 'Example Data'
    }, {
        'Name': 'Area A_Temperature',
        'Datasource Name': 'Example Data'
    }, {
        'Path': 'Example >> Cooling Tower 1 >> Area A',
        'Name': 'Relative Humidity'
    }]), estimate_sample_period=dict(Start=None, End=None))

    assert len(search_results) == 3
    assert 'Estimated Sample Period' in search_results
    assert (search_results['Estimated Sample Period'].map(type) == pd.Timedelta).all()


@pytest.mark.system
def test_path_with_datasource_and_estimated_sample_period():
    search_results = spy.search({
        'Name': 'Area ?_*',
        'Datasource Name': 'Example Data'
    })

    assert 'Estimated Sample Period' not in search_results
    push_df = search_results.copy()
    push_df['Reference'] = True
    push_df['Path'] = 'test_path_with_datasource-tree >> branch-alpha'
    push_df['Asset'] = push_df['Name'].str.extract(r'(Area .)_.*')
    push_df['Name'] = push_df['Name'].str.extract(r'Area ._(.*)')

    spy.push(metadata=push_df, datasource='test_path_with_datasource-name-1')
    push_df['Path'] = 'test_path_with_datasource-tree >> branch-bravo'
    spy.push(metadata=push_df, datasource='test_path_with_datasource-name-2')

    search_results = spy.search({
        'Path': 'test_path_with_datasource-tree',
    }, recursive=False, estimate_sample_period=dict(Start=None, End=None))

    assert len(search_results) == 2
    assert 'Estimated Sample Period' in search_results
    assert search_results['Type'].values[0] == 'Asset' and pd.isna(search_results.at[0, 'Estimated Sample Period'])


@pytest.mark.system
def test_not_enough_data_for_estimated_sample_period():
    search_results = spy.search({
        'Name': 'Area ?_*',
        'Datasource Name': 'Example Data'
    }, estimate_sample_period=dict(Start='2018-01-01T01:00:00.000Z', End='2018-01-01T02:00:00.000Z'))
    assert 'Estimated Sample Period' in search_results
    area_f_compressor_power = search_results[search_results['Name'] == 'Area F_Compressor Power'].squeeze()
    assert pd.isna(area_f_compressor_power['Estimated Sample Period'])


@pytest.mark.system
def test_estimated_sample_period_incorrect_capitalization():
    with pytest.raises(ValueError, match=r"estimate_sample_period must have 'Start' and 'End' keys but got "
                                         r"dict_keys\(\['start', 'End'\]\)"):
        spy.search({
            'Name': 'Area ?_*',
            'Datasource Name': 'Example Data'
        }, estimate_sample_period=dict(start='2018-01-01T01:00:00.000Z', End='2018-01-01T02:00:00.000Z'))

    with pytest.raises(ValueError, match=r"estimate_sample_period must have 'Start' and 'End' keys but got "
                                         r"dict_keys\(\['Start', 'end'\]\)"):
        spy.search({
            'Name': 'Area ?_*',
            'Datasource Name': 'Example Data'
        }, estimate_sample_period=dict(Start='2018-01-01T01:00:00.000Z', end='2018-01-01T02:00:00.000Z'))


@pytest.mark.system
def test_search_with_url():
    workbook = test_common.create_worksheet_for_url_tests()
    search_results = spy.search(workbook.url)

    assert len(search_results) == 3
    assert search_results[search_results['Name'] == 'Temperature Minus 5']['Type'].values[0] == 'CalculatedSignal'
    assert search_results[search_results['Name'] == 'Cold']['Type'].values[0] == 'CalculatedCondition'
    assert search_results[search_results['Name'] == 'Constant']['Type'].values[0] == 'CalculatedScalar'

    search_results = spy.search(workbook.url, estimate_sample_period=dict(Start='2018-01-01T00:00:00.000Z',
                                                                          End='2018-06-01T00:00:00.000Z'))
    assert 'Estimated Sample Period' in search_results


@pytest.mark.system
def test_search_quiet_flag_with_url():
    workbook = test_common.create_worksheet_for_url_tests()
    warning = "The quiet flag is ignored when a status object is provided. Instead, use the quiet flag of your status " \
              "object by creating a quiet status with spy.Status(quiet=True), or setting status.quiet=True."

    # Test that there is no warning when a status is provided and the quiet flag is not set
    test_status_no_warn = spy.Status()
    _ = spy.search(workbook.url, status=test_status_no_warn)
    assert warning not in test_status_no_warn.warnings

    # Test that there is a warning when both a status is provided and the quiet flag is True
    test_status_warn = spy.Status()
    _ = spy.search(workbook.url, quiet=True, status=test_status_warn)

    assert warning in test_status_warn.warnings


@pytest.mark.system
def test_search_with_url_wrong_url():
    test_common.create_worksheet_for_url_tests()
    # test for invalid URLs
    with pytest.raises(ValueError, match=r"The supplied URL is not a valid Seeq address. Verify that both the "
                                         r"workbook ID and worksheet ID are valid Seeq references"):
        spy.search('http://localhost:34216/workbook/376F44F5-9243-A0CF/worksheet/2B7F2EC3-C484-49C6-9FEB-EDA68B9350B1')

    with pytest.raises(ValueError, match=r"The supplied URL is not a valid Seeq address. Verify that both the "
                                         r"workbook ID and worksheet ID are valid Seeq references"):
        spy.search('http://localhost:34216/workbook/376F44F5-9243-453C-A0CF-F14CB08B76FD/worksheet/2B7F2EC3-C484-49C6')

    workbook_id = str(uuid.uuid1()).upper()
    worksheet_id = str(uuid.uuid1()).upper()
    url = f'http://localhost:34216/workbook/{workbook_id}/worksheet/{worksheet_id}'
    with pytest.raises(RuntimeError, match=f'Could not find workbook with ID "{workbook_id}"'):
        spy.search(url)

    host = spy._config.get_seeq_url()
    workbook_search = spy.workbooks.search({'Name': 'test_items_from_URL'})
    workbook = spy.workbooks.pull(workbook_search, include_referenced_workbooks=False, include_inventory=False)[0]
    with pytest.raises(RuntimeError, match=f'Worksheet with ID "{worksheet_id}" does not exist'):
        spy.search(f'{host}/workbook/{workbook.id}/worksheet/{worksheet_id}')


@pytest.mark.system
def test_search_with_url_archived_workbook_worksheet():
    # Get a workbook/worksheet URL for tests
    test_common.create_worksheet_for_url_tests()
    workbook_search = spy.workbooks.search({'Name': 'test_items_from_URL'})
    workbook = spy.workbooks.pull(workbook_search, include_referenced_workbooks=False, include_inventory=False)[0]
    worksheet = [x for x in workbook.worksheets if x.name == 'search from URL'][0]

    items_api = ItemsApi(test_common.get_client())
    items_api.set_property(id=workbook.id, property_name='Archived', body=PropertyInputV1(value=True))

    # tests for archived workbooks
    with pytest.raises(ValueError, match=f"Workbook '{workbook.id}' is archived. Supply 'include_archive=True' if"
                                         f"you want to retrieve the items of an archived workbook"):
        spy.search(workbook.url)

    search_results = spy.search(workbook.url, include_archived=True)
    assert len(search_results) == 3

    # unarchive it in case we need it for another test
    items_api.set_property(id=workbook.id, property_name='Archived', body=PropertyInputV1(value=False))

    # tests for archived worksheet
    items_api.set_property(id=worksheet.id, property_name='Archived', body=PropertyInputV1(value=True))
    with pytest.raises(ValueError, match=f"Worksheet '{worksheet.id}' is archived. Supply 'include_archive=True' if"
                                         f"you want to retrieve archived items"):
        spy.search(workbook.url)

    # unarchive it in case we need it for another test
    items_api.set_property(id=worksheet.id, property_name='Archived', body=PropertyInputV1(value=False))


@pytest.mark.system
def test_search_of_topic_url():
    host = spy._config.get_seeq_url()
    topic = Topic({'Name': "test_Topic_search_url"})
    document = topic.document('Doc1')
    spy.workbooks.push(topic)

    with pytest.raises(ValueError, match=f'URL must be for a valid Workbench Analysis. '
                                         f'You supplied a URL for a Topic.'):
        spy.search(f'{host}/workbook/{topic.id}/worksheet/{document.id}')


@pytest.mark.system
def test_search_kwargs_and_status_metadata():
    search_results = spy.search({'Name': 'Area A_Temperature'})
    with tempfile.TemporaryDirectory() as dir_path:
        search_results.to_pickle(Path(dir_path, 'search.pkl'))
        search_unpickle = pd.read_pickle(Path(dir_path, 'search.pkl'))
        assert search_unpickle.func == 'spy.search'
        assert search_unpickle.kwargs['query'] == {'Name': 'Area A_Temperature'}
        assert not search_unpickle.kwargs['all_properties']
        assert search_unpickle.kwargs['recursive']
        assert not search_unpickle.kwargs['include_archived']
        assert search_unpickle.kwargs['estimate_sample_period'] is None
        assert isinstance(search_unpickle.status, spy.Status)

        # take a slice of the DataFrame to make sure the metadata is preserved
        search_manipulated = search_unpickle[['ID']]
        assert search_manipulated.kwargs['query'] == {'Name': 'Area A_Temperature'}

    search_results = spy.search({'Name': 'Area A_Temperature'},
                                estimate_sample_period=dict(Start='2018-01-01T01:00:00.000Z',
                                                            End='2018-01-01T02:00:00.000Z'))
    with tempfile.TemporaryDirectory() as dir_path:
        search_results.to_pickle(Path(dir_path, 'search.pkl'))
        search_unpickle = pd.read_pickle(Path(dir_path, 'search.pkl'))
        assert search_unpickle.func == 'spy.search'
        assert search_unpickle.kwargs['estimate_sample_period']['Start'] == '2018-01-01T01:00:00.000Z'
        assert search_unpickle.kwargs['estimate_sample_period']['End'] == '2018-01-01T02:00:00.000Z'

        # create a copy of the search DataFrame and test the metadata is preserved on the copy
        duplicate = search_unpickle.copy()
        assert duplicate.kwargs['estimate_sample_period']['Start'] == '2018-01-01T01:00:00.000Z'
        assert duplicate.kwargs['estimate_sample_period']['End'] == '2018-01-01T02:00:00.000Z'


@pytest.mark.system
def test_ignore_unindexed_properties():
    with pytest.raises(ValueError, match=r'The following properties are not indexed:\n"Bilbo"\nUse any of .*'):
        spy.search({
            'Name': 'Area A_Temperature',
            'Bilbo': 'Baggins'
        }, ignore_unindexed_properties=False)

    search_df = spy.search({
        'Name': 'Area A_Temperature',
        'Bilbo': 'Baggins'
    })

    assert len(search_df.status.warnings) == 1
    assert search_df.status.warnings.pop().startswith(
        'The following properties are not indexed and will be ignored:\n"Bilbo"')


@pytest.mark.system
def test_empty_query():
    # This can happen if the user imports a CSV file full of tag names into a DataFrame but the CSV file doesn't
    # have a header.
    query_df = pd.DataFrame({
        'DC3STEAMSO.INITIAL_VALUE': [
            'DC3STEAMSO.FINAL_VALUE',
            'DC3STEAMSO.MOVE',
            'DC3STEAMSO.BASE_CASE'
        ]})

    with pytest.raises(ValueError, match=r'No recognized properties present in "query" argument.'):
        spy.search(query_df)

    with pytest.raises(ValueError, match=r'No recognized properties present in "query" argument.'):
        spy.search(dict())
