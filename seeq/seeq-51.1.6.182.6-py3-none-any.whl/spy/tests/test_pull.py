import pytest
import pytz
import datetime
import tempfile
from pathlib import Path

import pandas as pd
import numpy as np

from seeq import spy
from seeq.sdk import *
from seeq.sdk.rest import ApiException

from seeq.spy.tests import test_common
from seeq.spy.assets.tests import test_assets_system

from seeq.spy._common import Status
from seeq.spy import _config


def setup_module():
    test_common.login()


def teardown_module():
    _config.options.pull_page_size = 1000000


@pytest.mark.system
def test_pull_signal_with_grid():
    search_results = spy.search({
        "Path": "Example >> Cooling Tower 1 >> Area A"
    })

    search_results = search_results.loc[
        search_results['Name'].isin(['Compressor Power', 'Compressor Stage'])]

    # Make sure paging works properly
    _config.options.pull_page_size = 10000

    df = spy.pull(search_results, start='2019-01-01', end='2019-03-07', grid='5min', header='Name',
                  tz_convert='US/Central')

    # We assert an exact value here to draw attention to any changes. The only reason this number should change is if
    # the Example Data changes in some way or there is a (possibly unexpected) change to SPy.
    assert len(df) == 18721

    # Note that the canonical timezone for US/Central appears to be CST
    assert df.index[0].tzname() == 'CST'

    assert isinstance(df.iloc[0]['Compressor Power'], np.float64)
    assert isinstance(df.iloc[0]['Compressor Stage'], str)


@pytest.mark.system
def test_pull_signal_with_auto_grid():
    # 1) when the search_results don't collect the estimated sample period and spy.pull is issued with grid='auto'
    search_results = spy.search({
        "Path": "Example >> Cooling Tower 1 >> Area A"
    })

    search_results = search_results.loc[
        search_results['Name'].isin(['Compressor Power', 'Compressor Stage'])]

    df = spy.pull(search_results, start='2019-01-01T00:00:00.000Z', end='2019-03-07T00:00:00.000Z', grid='auto',
                  header='Name', tz_convert='US/Central')

    assert pd.infer_freq(df.index) == '2T'

    # We assert an exact value here to draw attention to any changes. The only reason this number should change is if
    # the Example Data changes in some way or there is a (possibly unexpected) change to SPy.
    assert len(df) == 46801

    # Note that the canonical timezone for US/Central appears to be CST
    assert df.index[0].tzname() == 'CST'
    assert isinstance(df.iloc[0]['Compressor Power'], np.float64)
    assert isinstance(df.iloc[0]['Compressor Stage'], str)

    # 2) when the search_results has the estimated sample period and spy.pull is issued with grid='auto'
    search_results = spy.search({
        'Name': 'Area ?_*',
        'Datasource Name': 'Example Data'
    }, estimate_sample_period=dict(Start='2018-01-01T01:00:00.000Z', End='2018-01-01T02:00:00.000Z'))
    search_results = search_results.loc[search_results['Name'].isin(['Area H_Compressor Power', 'Area Z_Optimizer',
                                                                     'Area Z_Wet Bulb', 'Area I_Compressor Stage',
                                                                     'Area F_Compressor Power'])]

    df = spy.pull(search_results, start='2018-01-01T01:00:00.000Z', end='2018-01-01T02:00:00.000Z', grid='auto',
                  header='Name', tz_convert='US/Central')
    assert len(df) == 59
    assert pd.infer_freq(df.index) == '61S'


@pytest.mark.system
def test_pull_signal_no_grid():
    # This test ensures that time series with non-matching timestamps are returned
    # in a DataFrame with index entries properly interleaved and NaNs where one
    # series has a value and one doesn't.

    data1_df = spy.push(pd.DataFrame({'test_pull_signal_no_grid_1': [1, 2, 3]},
                                     index=[
                                         pd.to_datetime('2019-01-01T00:00:00.000Z'),
                                         pd.to_datetime('2019-01-01T01:00:00.000Z'),
                                         pd.to_datetime('2019-01-01T02:00:00.000Z'),
    ]))

    data2_df = spy.push(pd.DataFrame({'test_pull_signal_no_grid_2': [10, 20, 30]},
                                     index=[
                                         pd.to_datetime('2019-01-01T00:10:00.000Z'),
                                         pd.to_datetime('2019-01-01T01:10:00.000Z'),
                                         pd.to_datetime('2019-01-01T02:10:00.000Z'),
    ]))

    data3_df = spy.push(pd.DataFrame({'test_pull_signal_no_grid_3': [100, 200, 300]},
                                     index=[
                                         pd.to_datetime('2019-01-01T00:20:00.000Z'),
                                         pd.to_datetime('2019-01-01T01:20:00.000Z'),
                                         pd.to_datetime('2019-01-01T02:20:00.000Z'),
    ]))

    all_df = data1_df.append(data2_df).append(data3_df)

    pull_df = spy.pull(all_df, start='2018-12-01T00:00:00Z', end='2019-12-01T00:00:00Z', grid=None)

    expected_df = pd.DataFrame({
        'test_pull_signal_no_grid_1': [1, np.nan, np.nan, 2, np.nan, np.nan, 3, np.nan, np.nan],
        'test_pull_signal_no_grid_2': [np.nan, 10, np.nan, np.nan, 20, np.nan, np.nan, 30, np.nan],
        'test_pull_signal_no_grid_3': [np.nan, np.nan, 100, np.nan, np.nan, 200, np.nan, np.nan, 300]
    }, index=[
        pd.to_datetime('2019-01-01T00:00:00.000Z'),
        pd.to_datetime('2019-01-01T00:10:00.000Z'),
        pd.to_datetime('2019-01-01T00:20:00.000Z'),
        pd.to_datetime('2019-01-01T01:00:00.000Z'),
        pd.to_datetime('2019-01-01T01:10:00.000Z'),
        pd.to_datetime('2019-01-01T01:20:00.000Z'),
        pd.to_datetime('2019-01-01T02:00:00.000Z'),
        pd.to_datetime('2019-01-01T02:10:00.000Z'),
        pd.to_datetime('2019-01-01T02:20:00.000Z')
    ])

    assert pull_df.equals(expected_df)


@pytest.mark.system
def test_pull_empty_results():
    no_data_signal_df = spy.push(metadata=pd.DataFrame([{
        'Name': 'No Data Signal',
        'Type': 'Signal'
    }]))

    no_data_condition_df = spy.push(metadata=pd.DataFrame([{
        'Name': 'No Data Condition',
        'Maximum Duration': '1d',
        'Type': 'Condition'
    }]))

    area_a_df = spy.search({'Name': 'Area A_Temperature'})

    combo1_df = no_data_signal_df.append([no_data_condition_df, area_a_df], sort=True).reset_index(drop=True)
    combo2_df = area_a_df.append([no_data_signal_df, no_data_condition_df], sort=True).reset_index(drop=True)
    combo3_df = no_data_condition_df.append([no_data_signal_df, area_a_df], sort=True).reset_index(drop=True)

    pull_df = spy.pull(no_data_signal_df, start='2019-01-01T00:00:00.000Z', end='2019-01-01T01:00:00.000Z', grid=None)
    assert len(pull_df) == 0

    pull_df = spy.pull(combo1_df, start='2019-01-01T00:00:00.000Z', end='2019-01-01T01:00:00.000Z', grid=None)
    assert len(pull_df) > 0
    assert pull_df.columns.tolist() == ['No Data Signal', 'No Data Condition', 'Area A_Temperature']

    pull_df = spy.pull(combo2_df, start='2019-01-01T00:00:00.000Z', end='2019-01-01T01:00:00.000Z', grid=None)
    assert len(pull_df) > 0
    assert pull_df.columns.tolist() == ['Area A_Temperature', 'No Data Signal', 'No Data Condition']

    pull_df = spy.pull(combo3_df, start='2019-01-01T00:00:00.000Z', end='2019-01-01T01:00:00.000Z', grid=None)
    assert len(pull_df) > 0
    assert pull_df.columns.tolist() == ['No Data Condition', 'No Data Signal', 'Area A_Temperature']

    pull_df = spy.pull(no_data_signal_df, start='2019-01-01T00:00:00.000Z', end='2019-01-01T01:00:00.000Z')

    assert len(pull_df) == 5
    assert len(pull_df.drop_duplicates()) == 1
    assert np.isnan(pull_df.drop_duplicates().iloc[0]['No Data Signal'])


@pytest.mark.system
def test_pull_across_assets():
    search_results = spy.search({
        "Path": "Example >> Cooling Tower 2",
        "Name": "Temperature"
    })

    with pytest.raises(RuntimeError):
        # This will throw an error because header='Name' results in non-unique headers
        spy.pull(search_results, start='2019-01-01', end='2019-01-02', grid='5min', header='Name')

    with pytest.raises(ValueError):
        # This will throw an error because there's not column named 'Stuff'
        spy.pull(search_results, start='2019-01-01', end='2019-01-02', grid='5min', tz_convert='US/Central',
                 group_by='Stuff')

    # Pull data twice-- once by pulling Area D Temperature directly, then again by pulling all Cooling Tower 2
    # Temperature signals with a group_by argument
    pull_df1 = spy.pull(search_results[search_results['Asset'] == 'Area D'], start='2019-01-01', end='2019-01-02',
                        grid='5min', tz_convert='US/Central', header='Name')

    pull_df2 = spy.pull(search_results, start='2019-01-01', end='2019-01-02', grid='5min', tz_convert='US/Central',
                        header='Name', group_by=['Path', 'Asset'])

    # Now select only Area D from the second pull, using MultiIndex manipulation
    assert len(pull_df2.columns) == 1
    assert pull_df2.columns[0] == 'Temperature'
    subset = pull_df2.xs('Area D', level='Asset').droplevel('Path')

    # They should be equal!
    assert pull_df1.equals(subset)


@pytest.mark.system
def test_group_by_with_scalars_and_conditions():
    test_assets_system.build_and_push_hvac_tree()

    search_results = spy.search({
        "Path": "My HVAC Units >> Facility #1 >> Area A",
    }).append(spy.search({
        "Path": "My HVAC Units >> Facility #1 >> Area B",
    })).reset_index(drop=True)

    search_results = search_results[search_results['Type'] != 'Asset']

    pull_df = spy.pull(search_results, start='2019-01-01', end='2019-01-02', grid='5min', tz_convert='US/Central',
                       header='Name', group_by=['Path', 'Asset'])

    # Make sure the Equipment ID string scalar is correct for the individual assets
    area_a_df = pull_df.query("Asset == 'Area A'")
    unique_equipment_id = area_a_df['Equipment ID'].drop_duplicates()
    assert len(unique_equipment_id) == 1
    assert unique_equipment_id.iloc[0] == 'Area A'

    area_b_df = pull_df.query("Asset == 'Area B'")
    unique_equipment_id = area_b_df['Equipment ID'].drop_duplicates()
    assert len(unique_equipment_id) == 1
    assert unique_equipment_id.iloc[0] == 'Area B'

    # The Too Hot condition for Area A and Area B should be different, if we did our bookkeeping correctly.
    too_hot_a = area_a_df['Too Hot'].reset_index(['Path', 'Asset'], drop=True)
    too_hot_b = area_b_df['Too Hot'].reset_index(['Path', 'Asset'], drop=True)
    assert not too_hot_a.equals(too_hot_b)


@pytest.mark.system
def test_bad_timezone():
    with pytest.raises(ValueError):
        spy.pull(pd.DataFrame(), tz_convert='CDT')


@pytest.mark.system
def test_omit_dates():
    search_results = spy.search({
        "Name": "Area A_Temperature"
    })

    margin_in_seconds = 5 * 60

    df = spy.pull(search_results, grid=None)
    assert 25 <= len(df) <= 35
    expected_start = pytz.utc.localize(datetime.datetime.utcnow()) - pd.Timedelta(hours=1)
    expected_end = pytz.utc.localize(datetime.datetime.utcnow())
    assert abs(pd.Timedelta(df.index[0].tz_convert('UTC') - expected_start).total_seconds()) < margin_in_seconds
    assert abs(pd.Timedelta(df.index[-1].tz_convert('UTC') - expected_end).total_seconds()) < margin_in_seconds

    # Note that this will be interpreted as relative to the local timezone
    start = datetime.datetime.now() - pd.Timedelta(hours=2)
    df = spy.pull(search_results, start=start, grid=None)

    assert 50 <= len(df) <= 70
    expected_start = pytz.utc.localize(datetime.datetime.utcnow() - pd.Timedelta(hours=2))
    assert abs(pd.Timedelta(df.index[0].tz_convert('UTC') - expected_start).total_seconds()) < margin_in_seconds
    assert abs(pd.Timedelta(df.index[-1].tz_convert('UTC') - expected_end).total_seconds()) < margin_in_seconds

    # Now add a timezone and make sure we handle that properly

    # noinspection PyTypeChecker
    start = datetime.datetime.now(tz=pytz.timezone('US/Pacific')) - pd.Timedelta(hours=1)
    df = spy.pull(search_results, start=start, grid=None)

    assert 25 <= len(df) <= 35
    expected_start = pd.to_datetime(start)
    assert abs(pd.Timedelta(
        df.index[0].tz_convert('UTC') - expected_start.tz_convert('UTC')).total_seconds()) < margin_in_seconds
    assert abs(pd.Timedelta(
        df.index[-1].tz_convert('UTC') - expected_end).total_seconds()) < margin_in_seconds


@pytest.mark.system
def test_bounding_values():
    metadata_df = pd.DataFrame([{
        'Name': 'test_bounding_values',
        'Type': 'Signal',
        'Interpolation Method': 'step'
    }], index=['test_bounding_values'])

    data_df = pd.DataFrame({'test_bounding_values': [1, 2, 3]},
                           index=[
                               pd.to_datetime('2019-01-01T00:00:00.000Z'),
                               pd.to_datetime('2019-01-01T00:01:00.000Z'),
                               pd.to_datetime('2019-01-01T00:02:00.000Z'),
    ])

    push_df = spy.push(data=data_df, metadata=metadata_df)

    pull_df = spy.pull(push_df, start=pd.to_datetime('2019-01-01T00:01:00.000Z'),
                       end=pd.to_datetime('2019-01-01T00:02:00.000Z'), grid=None)

    expected_df = pd.DataFrame({
        'test_bounding_values': [2, 3]
    }, index=[
        pd.to_datetime('2019-01-01T00:01:00.000Z'),
        pd.to_datetime('2019-01-01T00:02:00.000Z')
    ])

    assert pull_df.equals(expected_df)

    pull_df = spy.pull(push_df, start=pd.to_datetime('2019-01-01T00:00:50.000Z'),
                       end=pd.to_datetime('2019-01-01T00:01:50.000Z'), grid=None)

    expected_df = pd.DataFrame({
        'test_bounding_values': [2]
    }, index=[
        pd.to_datetime('2019-01-01T00:01:00.000Z')
    ])

    assert pull_df.equals(expected_df)

    pull_df = spy.pull(push_df, start=pd.to_datetime('2019-01-01T00:00:50.000Z'),
                       end=pd.to_datetime('2019-01-01T00:01:50.000Z'), grid=None, bounding_values=True)

    expected_df = pd.DataFrame({
        'test_bounding_values': [1, 2, 3]
    }, index=[
        pd.to_datetime('2019-01-01T00:00:00.000Z'),
        pd.to_datetime('2019-01-01T00:01:00.000Z'),
        pd.to_datetime('2019-01-01T00:02:00.000Z')
    ])

    assert pull_df.equals(expected_df)


@pytest.mark.system
def test_pull_condition_as_capsules():
    search_results = spy.search({
        'Name': 'Area A_Temperature'
    })

    push_df = spy.push(metadata=pd.DataFrame([{
        'Type': 'Condition',
        'Name': 'Hot',
        'Formula': '$a.validValues().valueSearch(isGreaterThan(80)).setProperty("My Prop", 1)',
        'Formula Parameters': {
            '$a': search_results.iloc[0]
        }
    }]))

    # Make sure paging works properly
    _config.options.pull_page_size = 100

    # Some capsules
    pull_df = spy.pull(push_df.iloc[0], start='2019-01-01T00:00:00.000Z', end='2019-06-01T00:00:00.000Z')
    assert 'Condition' in pull_df
    assert 'Capsule Start' in pull_df
    assert 'Capsule End' in pull_df
    assert 'Capsule Is Uncertain' in pull_df
    assert 200 <= len(pull_df) <= 230

    assert 'My Prop' in pull_df
    only_my_prop = pull_df.drop_duplicates('My Prop')
    assert len(only_my_prop) == 1
    assert only_my_prop.loc[0]['My Prop'] == 1

    # No matching extra properties
    pull_df = spy.pull(push_df.iloc[0], start='2019-01-01T00:00:00.000Z', end='2019-01-03T00:00:00.000Z',
                       capsule_properties=['Does not match anything'])

    assert 'My Prop' not in pull_df

    # No capsules
    pull_df = spy.pull(push_df.iloc[0], start='2019-01-02T10:00:00.000Z', end='2019-01-02T11:00:00.000Z')
    assert len(pull_df) == 0

    # With signal aggregates
    area_a_temperature_count = search_results.iloc[0].copy()
    area_a_temperature_count['Statistic'] = 'Count'
    area_a_temperature_max = search_results.iloc[0].copy()
    area_a_temperature_max['Statistic'] = 'Maximum'
    area_a_temperature_rate = search_results.iloc[0].copy()
    area_a_temperature_rate['Statistic'] = 'Rate'
    with_signals_df = push_df.append(
        [area_a_temperature_count, area_a_temperature_max, area_a_temperature_rate]).reset_index(drop=True)
    pull_df = spy.pull(with_signals_df, start='2019-01-01T00:00:00.000Z', end='2019-06-01T00:00:00.000Z',
                       shape='capsules', capsule_properties=['My Prop'])
    assert 200 <= len(pull_df) <= 230
    assert 'My Prop' in pull_df
    assert 'Area A_Temperature (Count)' in pull_df
    assert 'Area A_Temperature (Maximum)' in pull_df


@pytest.mark.system
def test_pull_bad_id():
    # Error
    bad_df = pd.DataFrame([{
        'ID': 'BAD!',
        'Type': 'Signal'
    }])

    pull_df = spy.pull(bad_df, start='2019-01-02T10:00:00.000Z', end='2019-01-02T11:00:00.000Z', errors='catalog')
    assert len(pull_df) == 0
    assert len(pull_df.status.df) == 1

    status = Status()
    pull_df = spy.pull(bad_df,
                       start='2019-01-02T10:00:00.000Z', end='2019-01-02T11:00:00.000Z',
                       errors='catalog', status=status)

    assert len(pull_df) == 0
    assert len(status.df) == 1


@pytest.mark.system
def test_pull_condition_as_signal():
    search_results = spy.search({
        'Name': 'Area A_Temperature'
    })

    push_result = spy.push(metadata=pd.DataFrame([{
        'Type': 'Condition',
        'Name': 'Hot',
        'Formula': '$a.validValues().valueSearch(isGreaterThan(80))',
        'Formula Parameters': {
            '$a': search_results.iloc[0]
        }
    }]))

    pull_result = spy.pull(push_result, start='2019-01-01T00:00:00.000Z', end='2019-01-02T00:00:00.000Z',
                           shape='samples')

    assert len(pull_result) == 97
    assert len(pull_result['Hot'].drop_duplicates()) == 2
    assert pull_result.loc[pd.to_datetime('2019-01-01T00:00:00.000Z')]['Hot'] == 1
    assert pull_result.loc[pd.to_datetime('2019-01-01T12:45:00.000Z')]['Hot'] == 1
    assert pull_result.loc[pd.to_datetime('2019-01-01T13:00:00.000Z')]['Hot'] == 0
    assert pull_result.loc[pd.to_datetime('2019-01-01T19:30:00.000Z')]['Hot'] == 0
    assert pull_result.loc[pd.to_datetime('2019-01-01T19:45:00.000Z')]['Hot'] == 1
    assert pull_result.loc[pd.to_datetime('2019-01-01T20:00:00.000Z')]['Hot'] == 0
    assert pull_result.loc[pd.to_datetime('2019-01-01T20:15:00.000Z')]['Hot'] == 1
    assert pull_result.loc[pd.to_datetime('2019-01-01T22:00:00.000Z')]['Hot'] == 1
    assert pull_result.loc[pd.to_datetime('2019-01-02T00:00:00.000Z')]['Hot'] == 0

    pull_df = search_results.append(push_result, ignore_index=True, sort=True)

    pull_result = spy.pull(pull_df, start='2019-01-01T00:00:00.000Z', end='2019-02-01T00:00:00.000Z',
                           shape='samples')

    for ts, row in pull_result.iterrows():
        if row['Area A_Temperature'] > 80:
            assert row['Hot'] == 1
        else:
            assert row['Hot'] == 0


@pytest.mark.system
def test_pull_condition_as_signal_with_no_grid():
    search_results = spy.search({
        'Name': 'Area A_Temperature'
    })

    push_result = spy.push(metadata=pd.DataFrame([{
        'Type': 'Condition',
        'Name': 'Hot',
        'Formula': '$a.validValues().valueSearch(isGreaterThan(80))',
        'Formula Parameters': {
            '$a': search_results.iloc[0]
        }
    }]))

    with pytest.raises(RuntimeError,
                       match="Pull cannot include conditions when no signals are present with shape='samples' "
                             "and grid=None"):
        spy.pull(push_result, start='2019-01-01T00:00:00.000Z', end='2019-01-02T00:00:00.000Z', grid=None,
                 shape='samples')

    with pytest.raises(RuntimeError,
                       match="Pull cannot include conditions when no signals are present with shape='samples' "
                             "and grid='auto'"):
        spy.pull(push_result, start='2019-01-01T00:00:00.000Z', end='2019-01-02T00:00:00.000Z', grid='auto',
                 shape='samples')


@pytest.mark.system
def test_pull_swapped_condition():
    search_results = spy.search({
        'Name': 'Temperature',
        'Path': 'Example >> Cooling Tower 1 >> Area A'
    })

    push_result = spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'Temperature Minus 5',
        'Formula': '$a - 5',
        'Formula Parameters': {
            '$a': search_results.iloc[0]
        }
    }]))

    push_result = spy.push(metadata=pd.DataFrame([{
        'Type': 'Condition',
        'Name': 'Cold',
        'Formula': '$a.validValues().valueSearch(isLessThan(80))',
        'Formula Parameters': {
            '$a': push_result.iloc[0]
        }
    }]))

    pull_df = spy.search({
        'Type': 'Asset',
        'Path': 'Example >> Cooling Tower 2'
    })

    # There will be an error related to trying to swap in Area F
    with pytest.raises(ApiException):
        spy.pull(pull_df, start='2019-01-01T00:00:00.000Z', end='2019-06-01T00:00:00.000Z',
                 calculation=push_result)

    status = Status()
    pull_df1 = spy.pull(pull_df, start='2019-01-01T00:00:00.000Z', end='2019-06-01T00:00:00.000Z',
                        calculation=push_result, shape='capsules', errors='catalog', status=status)

    assert len(pull_df1) > 800

    conditions = pull_df1['Condition'].drop_duplicates().tolist()

    assert len(conditions) == 2
    assert 'Example >> Cooling Tower 2 >> Area D' in conditions
    assert 'Example >> Cooling Tower 2 >> Area E' in conditions

    errors_df = status.df[status.df['Result'] != 'Success']

    assert len(errors_df) == 1
    assert 'unable to swap out Area A and swap in Area F' in errors_df.iloc[0]['Result']

    pull_df1 = spy.pull(pull_df, start='2019-01-01T00:00:00.000Z', end='2019-06-01T00:00:00.000Z',
                        calculation=push_result, shape='samples', errors='catalog', status=status)

    assert 'Example >> Cooling Tower 2 >> Area D' in pull_df1.columns
    assert 'Example >> Cooling Tower 2 >> Area E' in pull_df1.columns
    assert len(pull_df1['Example >> Cooling Tower 2 >> Area D'].drop_duplicates().tolist()) == 2
    assert len(pull_df1['Example >> Cooling Tower 2 >> Area E'].drop_duplicates().tolist()) == 2

    pull_df2 = spy.pull(pull_df, start='2019-01-01T00:00:00.000Z', end='2019-06-01T00:00:00.000Z',
                        calculation=push_result, shape='samples', errors='catalog', status=status,
                        group_by=['Path', 'Asset'], header='Name')

    assert 'Area D' in pull_df2.columns
    assert 'Area E' in pull_df2.columns
    assert len(pull_df2['Area D'].drop_duplicates().tolist()) == 2
    assert len(pull_df2['Area E'].drop_duplicates().tolist()) == 2

    # Now select only Area D
    pull_df1 = pull_df1[['Example >> Cooling Tower 2 >> Area D']]
    pull_df2 = pull_df2['Area D']
    subset = pull_df2.droplevel('Path').droplevel('Asset')

    # They should be equal!
    assert pull_df1['Example >> Cooling Tower 2 >> Area D'].equals(subset)


@pytest.mark.system
def test_seeq_server_error():
    datasources_api = DatasourcesApi(test_common.get_client())
    signals_api = SignalsApi(test_common.get_client())

    datasource_input = DatasourceInputV1()
    datasource_input.name = 'SPy Tests'
    datasource_input.description = 'Signals, conditions and scalars from Seeq Data Lab.'
    datasource_input.datasource_class = 'SPy Tests'
    datasource_input.datasource_id = 'SPy Tests'
    datasource_input.stored_in_seeq = False
    datasource_input.additional_properties = [ScalarPropertyV1(name='Expect Duplicates During Indexing', value=True)]
    datasource_output = datasources_api.create_datasource(body=datasource_input)  # type: DatasourceOutputV1

    signals_api.put_signal_by_data_id(datasource_class=datasource_output.datasource_class,
                                      datasource_id=datasource_output.datasource_id,
                                      data_id='A Signal With No Home',
                                      body=SignalInputV1(name='A Signal With No Home'))

    search_results = spy.search({
        'Name': 'A Signal With No Home'
    })

    # noinspection PyBroadException
    try:
        spy.pull(search_results, start='2019-01-01', end='2019-03-07')
    except BaseException as e:
        assert 'The target datasource is disconnected or no longer exists' in str(e)

    status = Status()
    spy.pull(search_results, start='2019-01-01', end='2019-03-07', errors='catalog', status=status)

    assert len(status.df) == 1
    assert 'The target datasource is disconnected or no longer exists' in status.df.iloc[0]['Result']


@pytest.mark.system
def test_pull_scalar_only():
    compressor_power_limit = spy.push(metadata=pd.DataFrame([{
        'Name': 'Compressor Power Limit',
        'Type': 'Scalar',
        'Formula': '50kW'
    }]), errors='raise')

    pull_df = spy.pull(compressor_power_limit)

    assert len(pull_df) == 1
    assert pull_df.at[0, 'Compressor Power Limit'] == 50

    invalid_scalar = spy.push(metadata=pd.DataFrame([{
        'Name': 'Invalid Scalar',
        'Type': 'Scalar',
        'Formula': 'SCALAR.INVALID'
    }]), errors='raise')

    pull_df = spy.pull(invalid_scalar)

    assert len(pull_df) == 1
    assert pd.isna(pull_df.at[0, 'Invalid Scalar'])

    pull_df = spy.pull(invalid_scalar, invalid_values_as='INVALID')

    assert pull_df.at[0, 'Invalid Scalar'] == 'INVALID'

    pull_df = spy.pull(invalid_scalar, invalid_values_as=-999)

    assert pull_df.at[0, 'Invalid Scalar'] == -999


@pytest.mark.system
def test_pull_grid_auto_fail():
    search_results = spy.search({
        'Name': 'Area ?_*',
        'Datasource Name': 'Example Data'
    }, estimate_sample_period=dict(Start='01/01/2018 1:00AM', End='01/01/2018 2:00AM'))
    search_results = search_results.loc[search_results['Name'].isin(['Area G_Optimizer', 'Area H_Optimizer',
                                                                     'Area I_Optimizer', 'Area J_Optimizer',
                                                                     'Area F_Compressor Power'])]
    with pytest.raises(RuntimeError, match="Could not determine sample period for any of the signals "):
        spy.pull(search_results, start='01/01/2018 1:00AM', end='01/01/2018 2:00AM', grid='auto')


@pytest.mark.system
def test_pull_from_url():
    workbook = test_common.create_worksheet_for_url_tests()
    pull_results = spy.pull(workbook.url)
    assert len(pull_results.columns) == 3
    assert set(pull_results.columns) == {'Temperature Minus 5', 'Cold', 'Constant'}
    assert len(pd.unique(pull_results['Constant'])) == 1
    assert len(pd.unique(pull_results['Cold'])) == 2

    pull_results = spy.pull(workbook.url, start='2020-01-01T00:00Z', end='2020-01-01T17:00Z')
    assert len(pull_results.columns) == 3
    assert pull_results.index[0] == pd.Timestamp('2020-01-01T00:00Z')
    assert pull_results.index[-1] == pd.Timestamp('2020-01-01T17:00Z')


@pytest.mark.system
def test_pull_input_params_property():
    search_results = spy.search({
        "Path": "Example >> Cooling Tower 1"
    }, all_properties=True)

    search_results = search_results.loc[
        search_results['Name'].isin(['Wet Bulb'])].iloc[:3]

    df = spy.pull(search_results, start=None, end=None, grid='auto')

    with tempfile.TemporaryDirectory() as dir_path:
        df.to_pickle(Path(dir_path, 'pull.pickle'))
        df = pd.read_pickle(Path(dir_path, 'pull.pickle'))

        # test kwargs
        assert df.kwargs['items'].equals(search_results)
        assert df.kwargs['start'] is None
        assert df.kwargs['end'] is None
        assert df.kwargs['grid'] == 'auto'
        assert df.kwargs['header'] == '__auto__'
        assert df.kwargs['group_by'] is None
        assert df.kwargs['shape'] == 'auto'
        assert df.kwargs['capsule_properties'] is None
        assert df.kwargs['tz_convert'] is None
        assert df.kwargs['calculation'] is None
        assert not df.kwargs['bounding_values']
        assert np.isnan(df.kwargs['invalid_values_as'])
        assert df.kwargs['errors'] == 'raise'
        assert not df.kwargs['quiet']
        assert df.kwargs['status'] is None
        assert df.kwargs['capsules_as'] is None

        # test effective values
        assert isinstance(df.query_df, pd.DataFrame)
        assert isinstance(df.start, pd.Timestamp)
        assert isinstance(df.end, pd.Timestamp)
        assert df.grid == '120000ms'
        assert df.tz_convert == df.start.tz
        assert df.status.df['Result'].all() == 'Success'
        assert df.func == 'spy.pull'

    workbook = test_common.create_worksheet_for_url_tests()
    pull_results = spy.pull(workbook.url, grid='auto')
    with tempfile.TemporaryDirectory() as dir_path:
        pull_results.to_pickle(Path(dir_path, 'pull.pickle'))
        pull_results = pd.read_pickle(Path(dir_path, 'pull.pickle'))

        # test kwargs
        assert pull_results.kwargs['items'] == workbook.url  # this is a string
        assert pull_results.kwargs['start'] is None
        assert pull_results.kwargs['end'] is None
        assert pull_results.kwargs['grid'] == 'auto'

        # test effective values
        assert isinstance(df.query_df, pd.DataFrame)
        assert isinstance(df.start, pd.Timestamp)
        assert isinstance(df.end, pd.Timestamp)
        assert pull_results.grid == '120000ms'
        assert pull_results.func == 'spy.pull'


@pytest.mark.system
def test_pull_enums():
    # Here we simulate PI enums
    data_df = spy.push(pd.DataFrame({'test_pull_enums': ['ENUM{{0|VALUE1}}', None, 'ENUM{{2|VALUE3}}']},
                                    index=[
                                        pd.to_datetime('2019-01-01T00:00:00.000Z'),
                                        pd.to_datetime('2019-01-01T01:00:00.000Z'),
                                        pd.to_datetime('2019-01-01T02:00:00.000Z'),
    ]),
        type_mismatches='invalid')

    pull_initial_df = spy.pull(data_df, start='2019-01-01T00:00:00.000Z', end='2019-01-01T02:00:00.000Z', grid=None,
                               enums_as=None)
    expected_initial_df = pd.DataFrame({
        'test_pull_enums': ['ENUM{{0|VALUE1}}', np.nan, 'ENUM{{2|VALUE3}}'],
    }, index=[
        pd.to_datetime('2019-01-01T00:00:00.000Z'),
        pd.to_datetime('2019-01-01T01:00:00.000Z'),
        pd.to_datetime('2019-01-01T02:00:00.000Z'),
    ])
    assert pull_initial_df.equals(expected_initial_df)

    pull_numeric_df = spy.pull(data_df, start='2019-01-01T00:00:00.000Z', end='2019-01-01T02:00:00.000Z', grid=None,
                               enums_as='numeric')
    expected_numeric_df = pd.DataFrame({
        'test_pull_enums': [0, np.nan, 2],
    }, index=[
        pd.to_datetime('2019-01-01T00:00:00.000Z'),
        pd.to_datetime('2019-01-01T01:00:00.000Z'),
        pd.to_datetime('2019-01-01T02:00:00.000Z'),
    ])
    assert pull_numeric_df.equals(expected_numeric_df)

    pull_string_df = spy.pull(data_df, start='2019-01-01T00:00:00.000Z', end='2019-01-01T02:00:00.000Z', grid=None,
                              enums_as='string')
    expected_string_df = pd.DataFrame({
        'test_pull_enums': ['VALUE1', np.nan, 'VALUE3'],
    }, index=[
        pd.to_datetime('2019-01-01T00:00:00.000Z'),
        pd.to_datetime('2019-01-01T01:00:00.000Z'),
        pd.to_datetime('2019-01-01T02:00:00.000Z'),
    ])
    assert pull_string_df.equals(expected_string_df)

    pull_tuple_df = spy.pull(data_df, start='2019-01-01T00:00:00.000Z', end='2019-01-01T02:00:00.000Z', grid=None,
                             enums_as='tuple')
    expected_tuple_df = pd.DataFrame({
        'test_pull_enums': [(0, 'VALUE1'), np.nan, (2, 'VALUE3')],
    }, index=[
        pd.to_datetime('2019-01-01T00:00:00.000Z'),
        pd.to_datetime('2019-01-01T01:00:00.000Z'),
        pd.to_datetime('2019-01-01T02:00:00.000Z'),
    ])
    assert pull_tuple_df.equals(expected_tuple_df)
