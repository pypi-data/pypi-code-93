import pytest
import mock
import os
import pandas as pd
import requests

from seeq import spy
from seeq.spy._errors import SPyValueError
from seeq.spy.jobs import _schedule
from seeq.spy.jobs import _push
from seeq.spy.jobs import _common as _jobs_common
from seeq.spy.tests import test_common
from seeq.spy import _common

seeq_url = 'http://localhost:34216'


def setup_module():
    # assume all the calls return successfully
    _schedule.call_schedule_notebook_api = mock.Mock()
    _schedule.call_unschedule_notebook_api = mock.Mock()
    _schedule.get_notebook_path = mock.Mock(return_value='notebook.ipynb')
    _schedule.make_dirs = mock.Mock(return_value=True)
    _schedule.dump_pickle = mock.Mock(return_value=True)

    mock_get_resp = requests.Response()
    mock_get_resp.json = mock.Mock(return_value={'content': [{'name': 'georgie-girl'}]})
    mock_get_resp.status_code = 200
    _jobs_common.requests_get = mock.Mock(return_value=mock_get_resp)
    mock_post_resp = requests.Response()
    mock_post_resp.json = mock.Mock(return_value={'path': 'ogenicity'})
    _jobs_common.requests_post = mock.Mock(return_value=mock_post_resp)
    mock_patch_resp = requests.Response()
    mock_patch_resp.json = mock.Mock(return_value={'path': 'ological'})
    mock_patch_resp.status_code = 200
    _jobs_common.requests_patch = mock.Mock(return_value=mock_patch_resp)
    _schedule.pickle_df_to_path = mock.Mock()
    put_pickle_resp = mock.Mock()
    put_pickle_resp.status_code = 200
    _jobs_common.requests_put = mock.Mock(return_value=put_pickle_resp)


@pytest.mark.system
def test_schedule_in_datalab():
    setup_run_in_datalab()

    test_jobs_df = pd.DataFrame({'Schedule': ['0 */2 1 * * ? *', '0 0 2 * * ? *', '0 42 03 22 1 ? 2121']})
    test_status = _common.Status()
    schedule_result = _schedule.schedule_df(jobs_df=test_jobs_df, status=test_status)
    assert test_status.message.startswith("Scheduled")
    assert 'notebook.ipynb' in test_status.message
    assert 'notebook.pkl' in test_status.message
    assert len(schedule_result.index) == 3

    # dataframe without the schedule column, but first column containing the schedules
    datalab_notebook_url = f'{seeq_url}/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C865/notebooks/1.ipynb'
    test_jobs_df = pd.DataFrame({'Other Name': ['0 */2 1 * * ? *', '0 0 2 * * ? *']})
    test_status = _common.Status()
    schedule_result = _schedule.schedule_df(jobs_df=test_jobs_df, datalab_notebook_url=datalab_notebook_url,
                                            status=test_status)
    assert test_status.message.startswith("Scheduled")
    assert '1.ipynb' in test_status.message
    assert '1.pkl' in test_status.message
    assert len(schedule_result.index) == 2

    # schedule with a label
    label = 'This is a label!'
    schedule_result = _schedule.schedule_df(jobs_df=test_jobs_df, datalab_notebook_url=datalab_notebook_url,
                                            label=label, status=test_status)
    assert test_status.message.startswith("Scheduled")
    assert '1.ipynb' in test_status.message
    assert f' with label <strong>{label}</strong> ' in test_status.message
    assert f'1.with.label.{label}.pkl' in test_status.message
    assert len(schedule_result.index) == 2

    # dataframe without the schedule column
    test_jobs_df = pd.DataFrame({'Some Name': ['abc'], 'Other Name': ['abc']})
    with pytest.raises(ValueError, match='Could not interpret "abc" as a schedule'):
        _schedule.schedule_df(jobs_df=test_jobs_df, status=test_status)


@pytest.mark.system
def test_schedule_in_executor():
    setup_run_in_executor()

    test_jobs_df = pd.DataFrame({'Schedule': ['0 */5 * * * ?'], 'Param': ['val1']})
    test_status = _common.Status()
    schedule_result = _schedule.schedule_df(jobs_df=test_jobs_df, status=test_status)
    assert test_status.message.startswith("Scheduled")
    assert 'test.ipynb' in test_status.message
    assert 'test.pkl' in test_status.message
    assert len(schedule_result.index) == 1


@pytest.mark.system
def test_schedule_outside_datalab():
    setup_run_outside_datalab()
    spy.logout()

    test_jobs_df = pd.DataFrame({'Schedule': ['0 0 2 * * ? *', '0 42 03 22 1 ? 2121']})
    test_status = _common.Status()
    with pytest.raises(RuntimeError) as err1:
        _schedule.schedule_df(jobs_df=test_jobs_df, status=test_status)
    assert "Not logged in" in str(err1.value)

    test_common.login()

    # no datalab_notebook_url provided
    with pytest.raises(RuntimeError) as err2:
        _schedule.schedule_df(jobs_df=test_jobs_df, status=test_status)
    assert "Provide a Seeq Data Lab Notebook URL" in str(err2.value)

    datalab_notebook_url = f'http://remote.com/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C865/notebooks/1.ipynb'
    schedule_result = _schedule.schedule_df(jobs_df=test_jobs_df, datalab_notebook_url=datalab_notebook_url,
                                            status=test_status)
    assert test_status.message.startswith("Scheduled")
    assert '1.ipynb' in test_status.message
    assert '1.pkl' in test_status.message
    assert len(schedule_result.index) == 2


@pytest.mark.system
def test_unschedule_in_datalab():
    setup_run_in_datalab()

    test_status = _common.Status()
    schedule_result = _schedule.schedule_df(status=test_status)
    assert test_status.message.startswith("Unscheduled")
    assert 'notebook.ipynb' in test_status.message
    pd.testing.assert_frame_equal(schedule_result, pd.DataFrame())

    datalab_notebook_url = f'{seeq_url}/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C865/notebooks/1.ipynb'
    schedule_result = _schedule.schedule_df(datalab_notebook_url=datalab_notebook_url, status=test_status)
    assert test_status.message.startswith("Unscheduled")
    assert '1.ipynb' in test_status.message
    pd.testing.assert_frame_equal(schedule_result, pd.DataFrame())

    label = 'Labeled!'
    schedule_result = _schedule.schedule_df(jobs_df=pd.DataFrame(), label=label, status=test_status)
    assert test_status.message.startswith("Unscheduled")
    assert 'notebook.ipynb' in test_status.message
    assert label in test_status.message
    pd.testing.assert_frame_equal(schedule_result, pd.DataFrame())

    label = '*'
    schedule_result = _schedule.schedule_df(jobs_df=pd.DataFrame(), label=label, status=test_status)
    assert test_status.message.startswith("Unscheduled")
    assert 'notebook.ipynb' in test_status.message
    assert 'for all labels' in test_status.message
    pd.testing.assert_frame_equal(schedule_result, pd.DataFrame())


@pytest.mark.system
def test_unschedule_outside_datalab():
    setup_run_outside_datalab()
    spy.logout()

    test_status = _common.Status()

    with pytest.raises(RuntimeError) as err:
        _schedule.schedule_df(status=test_status)
    assert "Not logged in" in str(err.value)

    test_common.login()

    # should provide a datalab_notebook_url
    with pytest.raises(RuntimeError):
        _schedule.schedule_df(status=test_status)

    datalab_notebook_url = f'http://remote.com/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C865/notebooks/1.ipynb'
    schedule_result = _schedule.schedule_df(datalab_notebook_url=datalab_notebook_url, status=test_status)
    assert test_status.message.startswith("Unscheduled")
    assert '1.ipynb' in test_status.message
    pd.testing.assert_frame_equal(schedule_result, pd.DataFrame())

    schedule_result = _schedule.schedule_df(jobs_df=pd.DataFrame(), datalab_notebook_url=datalab_notebook_url,
                                            status=test_status)
    assert test_status.message.startswith("Unscheduled")
    assert '1.ipynb' in test_status.message
    pd.testing.assert_frame_equal(schedule_result, pd.DataFrame())


@pytest.mark.system
def test_validate_and_get_next_trigger():
    test_common.login()
    validate_result = _schedule.validate_and_get_next_trigger(['0 */5 * * * ? 2069'])
    assert '2069-01-01 00:00:00 UTC' == validate_result['0 */5 * * * ? 2069']

    with pytest.raises(RuntimeError) as err1:
        _schedule.validate_and_get_next_trigger(['0 */5 * * * ? 2001', '0 */5 * * * *'])
    assert "schedules are invalid" in str(err1.value)
    assert "0 */5 * * * ? 2001" in str(err1.value)
    assert "No future trigger" in str(err1.value)

    with pytest.raises(RuntimeError) as err2:
        _schedule.validate_and_get_next_trigger(['* */2 * * * '])
    assert "Unexpected end of expression" in str(err2.value)

    with pytest.raises(RuntimeError) as err3:
        _schedule.validate_and_get_next_trigger(['* abc * * * ? *'])
    assert "Illegal characters for this position" in str(err3.value)


@pytest.mark.system
def test_retrieve_notebook_path_in_datalab():
    setup_run_in_datalab()
    data_lab_url, project_id, file_path = _schedule.retrieve_notebook_path()
    assert project_id == '8A54CD8B-B47A-42DA-B8CC-38AD4204C863'
    assert file_path == 'notebook.ipynb'

    datalab_notebook_url = f'{seeq_url}/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C865/notebooks/1.ipynb'
    data_lab_url, project_id, file_path = _schedule.retrieve_notebook_path(datalab_notebook_url)
    assert project_id == '8A54CD8B-B47A-42DA-B8CC-38AD4204C865'
    assert file_path == '1.ipynb'


@pytest.mark.system
def test_retrieve_notebook_path_in_executor():
    setup_run_in_executor()
    data_lab_url, project_id, file_path = _schedule.retrieve_notebook_path()
    assert project_id == '8A54CD8B-B47A-42DA-B8CC-38AD4204C863'
    assert file_path == 'test.ipynb'

    datalab_notebook_url = f'{seeq_url}/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C866/notebooks/2.ipynb'
    data_lab_url, project_id, file_path = _schedule.retrieve_notebook_path(datalab_notebook_url)
    assert project_id == '8A54CD8B-B47A-42DA-B8CC-38AD4204C866'
    assert file_path == '2.ipynb'


@pytest.mark.unit
def test_retrieve_notebook_path_outside_sdl():
    setup_run_outside_datalab()
    with pytest.raises(RuntimeError) as err:
        _schedule.retrieve_notebook_path()
    assert "Provide a Seeq Data Lab Notebook URL" in str(err.value)

    datalab_notebook_url = f'{seeq_url}/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C867/notebooks/3.ipynb'
    data_lab_url, project_id, file_path = _schedule.retrieve_notebook_path(datalab_notebook_url)
    assert project_id == '8A54CD8B-B47A-42DA-B8CC-38AD4204C867'
    assert file_path == '3.ipynb'


@pytest.mark.unit
def test_verify_not_actually_existing_and_accessible():
    setup_run_outside_datalab()
    datalab_notebook_url = f'http://nonce.com/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C867/notebooks/3.ipynb'
    contents_request_url = f'http://nonce.com/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C867/api/contents/3.ipynb'
    mock_resp = requests.Response()
    mock_resp.status_code = 404
    mock_requests_get = mock.Mock(return_value=mock_resp)
    mock_client = mock.MagicMock()
    mock_client.auth_token = 'some token'
    with mock.patch('seeq.spy.jobs._common.requests_get', mock_requests_get):
        with mock.patch('seeq.spy._login.client', mock_client):
            with pytest.raises(RuntimeError) as err:
                _schedule.verify_existing_and_accessible(datalab_notebook_url)
            assert 'Notebook not found for URL' in str(err.value)
            mock_requests_get.assert_called_once_with(contents_request_url,
                                                      params={'type': 'file', 'content': 0},
                                                      cookies={'sq-auth': 'some token'})


@pytest.mark.unit
def test_parse_data_lab_url_project_id_and_path():
    # incorrect data-lab value
    bad_base_url = 'http://192.168.1.100:34216'
    notebook_url_bad1 = f'{bad_base_url}/data-lab1/8A54CD8B-B47A-42DA-B8CC-38AD4204C862/notebooks/SPy' \
                        f'%20Documentation/SchedulingTest.ipynb'
    with pytest.raises(ValueError) as err1:
        _schedule.parse_data_lab_url_project_id_and_path(notebook_url_bad1)
    assert "not a valid SDL notebook" in str(err1.value)

    # invalid project id
    notebook_url_bad2 = f'{bad_base_url}/data-lab1/A8A54CD8B-B47A-42DA-B8CC-38AD4204C862/notebooks/SPy' \
                        '%20Documentation/SchedulingTest.ipynb'
    with pytest.raises(ValueError) as err2:
        _schedule.parse_data_lab_url_project_id_and_path(notebook_url_bad2)
    assert "not a valid SDL notebook" in str(err2.value)

    # path with whitespace
    notebook_url1 = f'{bad_base_url}/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C862/notebooks/SPy' \
                    '%20Documentation/SchedulingTest.ipynb'
    data_lab_url, project_id, file_path = _schedule.parse_data_lab_url_project_id_and_path(notebook_url1)
    assert project_id == '8A54CD8B-B47A-42DA-B8CC-38AD4204C862'
    assert file_path == 'SPy Documentation/SchedulingTest.ipynb'

    # partial path without whitespace
    mock_get = mock.MagicMock(return_value=f'{bad_base_url}/data-lab')
    with mock.patch('seeq.spy._config.get_data_lab_orchestrator_url', mock_get):
        # mock_config.get_data_lab_orchestrator_url = mock.Mock(return_value=f'{seeq_url}/data-lab')
        notebook_url2 = '/data-lab/8A54CD8B-B47A-42DA-B8CC-38AD4204C862/notebooks/SchedulingTest.ipynb'
        data_lab_url, project_id, file_path = _schedule.parse_data_lab_url_project_id_and_path(notebook_url2)
        assert data_lab_url == 'http://192.168.1.100:34216/data-lab'
        assert project_id == '8A54CD8B-B47A-42DA-B8CC-38AD4204C862'
        assert file_path == 'SchedulingTest.ipynb'


@pytest.mark.parametrize(
    'seconds_val, expected_result',
    [
        pytest.param('86400', ['0', '0', '0', '*/1'], id='days'),
        pytest.param('7200', ['0', '0', '*/2', '*'], id='hours'),
        pytest.param('120', ['0', '*/2', '*', '*'], id='minutes'),
        pytest.param('45', ['*/45', '*', '*', '*'], id='seconds'),
    ]
)
@pytest.mark.unit
def test_convert_seconds(seconds_val, expected_result):
    assert _schedule.convert_seconds(seconds_val) == expected_result


@pytest.mark.unit
def test_get_cron_expression_list():
    jobs_df = pd.DataFrame({'Schedule': ['0 0 0 ? * 3', 'every february at 2pm']})
    assert _schedule.get_cron_expression_list(jobs_df) == [(0, '0 0 0 ? * 3'), (1, '0 0 14 1 2 ?')]

    jobs_df = pd.DataFrame({'Schedule': ["my cat's breath smells like cat food"]})
    with pytest.raises(ValueError):
        assert _schedule.get_cron_expression_list(jobs_df)


@pytest.mark.unit
def test_parse_schedule_df():
    assert _schedule.parse_schedule_string('0 0 0 ? * 3') == '0 0 0 ? * 3'
    assert _schedule.parse_schedule_string('every february at 2pm') == '0 0 14 1 2 ?'

    with pytest.raises(ValueError):
        assert _schedule.parse_schedule_string("my cat's breath smells like cat food")

    with pytest.raises(ValueError):
        assert _schedule.parse_schedule_string("every breath you take")


@pytest.mark.unit
def test_friendly_schedule_to_cron():
    assert _schedule.friendly_schedule_to_quartz_cron('every tuesday') == '0 0 0 ? * 3'
    assert _schedule.friendly_schedule_to_quartz_cron('every february at 2pm') == '0 0 14 1 2 ?'
    assert _schedule.friendly_schedule_to_quartz_cron('every tuesday and friday at 6am') == '0 0 6 ? * 3,6'
    assert _schedule.friendly_schedule_to_quartz_cron('every january and june 1st at 17:00') == '0 0 17 1 1,6 ?'
    assert _schedule.friendly_schedule_to_quartz_cron('every fifth of the month') == '0 0 0 5 */1 ?'
    assert _schedule.friendly_schedule_to_quartz_cron('every five hours') == '0 0 */5 * * ?'
    assert _schedule.friendly_schedule_to_quartz_cron('every six minutes') == '0 */6 * * * ?'
    assert _schedule.friendly_schedule_to_quartz_cron('every thursday at 2:05am') == '0 5 2 ? * 5'
    assert _schedule.friendly_schedule_to_quartz_cron('Every 180 seconds') == '0 */3 * * * ?'

    with pytest.raises(SPyValueError):
        _schedule.friendly_schedule_to_quartz_cron('0 5 2 ? * 5')

    with pytest.raises(SPyValueError):
        _schedule.friendly_schedule_to_quartz_cron('2020-01-01T00:00:00.000Z')

    with pytest.raises(SPyValueError):
        _schedule.friendly_schedule_to_quartz_cron('Every 90 seconds')


@pytest.mark.unit
def test_spread():
    cron = _schedule.friendly_schedule_to_quartz_cron('every february 1')
    assert _schedule.spread_over_period([(i, cron) for i in range(3)], '8h') \
        == [(0, '0 0 0 1 2 ?'), (1, '0 40 2 1 2 ?'), (2, '0 20 5 1 2 ?')]

    cron = _schedule.friendly_schedule_to_quartz_cron('every 2 minutes')
    assert _schedule.spread_over_period([(i, cron) for i in range(4)], '1min') == \
        [(0, '0 */2 * * * ?'), (1, '15 */2 * * * ?'), (2, '30 */2 * * * ?'), (3, '45 */2 * * * ?')]

    cron = _schedule.friendly_schedule_to_quartz_cron('every 5 minutes')
    assert _schedule.spread_over_period([(i, cron) for i in range(4)], '3min') == \
        [(0, '0 0/5 * * * ?'), (1, '45 0/5 * * * ?'), (2, '30 1/5 * * * ?'), (3, '15 2/5 * * * ?')]

    cron = _schedule.friendly_schedule_to_quartz_cron('every 15 minutes')
    assert _schedule.spread_over_period([(i, cron) for i in range(3)], '1h') == \
        [(0, '0 0/15 * * * ?'), (1, '0 20/15 * * * ?'), (2, '0 40/15 * * * ?')]

    cron = _schedule.friendly_schedule_to_quartz_cron('every 6 hours')
    assert _schedule.spread_over_period([(i, cron) for i in ['a', 'b', 'c']], '6h') == \
        [('a', '0 0 0/6 * * ?'), ('b', '0 0 2/6 * * ?'), ('c', '0 0 4/6 * * ?')]


@pytest.mark.unit
def test_get_parameters_without_interactive_index_not_executor_returns_none():
    # assure we are not in executor
    os.environ['SEEQ_SDL_CONTAINER_IS_EXECUTOR'] = 'None'

    test_jobs_df = pd.DataFrame({'Schedule': ['0 */2 1 * * *', '0 0 2 * * *', '0 42 03 22 1 * 2021']})
    test_status = _common.Status()
    test_status.message = 'Blah'
    assert _push.get_parameters(test_jobs_df, None, test_status) is None


@pytest.mark.unit
def test_get_parameters_with_interactive_index():
    # assure we are not in executor
    os.environ['SEEQ_SDL_CONTAINER_IS_EXECUTOR'] = 'None'

    test_status = _common.Status()
    test_status.message = 'Blah'
    test_jobs_df = pd.DataFrame({'Schedule': ['0 */2 1 * * *', '0 0 2 * * *', '0 42 03 22 1 * 2021']})
    pd.testing.assert_series_equal(pd.Series(name=0, data={'Schedule': '0 */2 1 * * *'}), _push.get_parameters(
        test_jobs_df, 0, test_status))
    pd.testing.assert_series_equal(pd.Series(name=2, data={'Schedule': '0 42 03 22 1 * 2021'}), _push.get_parameters(
        test_jobs_df, 2, test_status))
    with pytest.raises(ValueError):
        _push.get_parameters(test_jobs_df, 3, test_status)

    test_jobs_df_with_params = pd.DataFrame({'Param1': ['val1', 'val2'], 'Param2': ['val3', 'val4']})
    pd.testing.assert_series_equal(pd.Series(name=1, data={'Param1': 'val2', 'Param2': 'val4'}), _push.get_parameters(
        test_jobs_df_with_params, 1, test_status))


@pytest.mark.unit
def test_get_parameters_with_interactive_index_in_executor_is_ignored():
    # assure we are in executor
    os.environ['SEEQ_SDL_CONTAINER_IS_EXECUTOR'] = 'true'

    test_status = _common.Status()
    test_status.message = 'Blah'
    test_jobs_df = pd.DataFrame({'Param1': ['val1', 'val2'], 'Param2': ['val3', 'val4']})
    # don't set the true schedule index yet
    with pytest.raises(RuntimeError):
        _push.get_parameters(test_jobs_df, 1, test_status)

    # set the schedule index which will override the interactive_index
    os.environ['SEEQ_SDL_SCHEDULE_INDEX'] = '0'
    pd.testing.assert_series_equal(pd.Series(name=0, data={'Param1': 'val1', 'Param2': 'val3'}), _push.get_parameters(
        test_jobs_df, 1, test_status))


def setup_run_outside_datalab():
    os.environ['SEEQ_SDL_CONTAINER_IS_DATALAB'] = ''
    os.environ['SEEQ_SDL_CONTAINER_IS_EXECUTOR'] = ''
    os.environ['SEEQ_PROJECT_UUID'] = ''
    os.environ['SEEQ_SDL_FILE_PATH'] = ''


def setup_run_in_datalab():
    test_common.login()
    os.environ['SEEQ_SDL_CONTAINER_IS_DATALAB'] = 'true'
    os.environ['SEEQ_SDL_CONTAINER_IS_EXECUTOR'] = ''
    os.environ['SEEQ_PROJECT_UUID'] = '8A54CD8B-B47A-42DA-B8CC-38AD4204C863'
    spy._config.set_seeq_url(seeq_url)
    spy._config.Setting.SEEQ_PROJECT_UUID.set('8A54CD8B-B47A-42DA-B8CC-38AD4204C863')


def setup_run_in_executor():
    test_common.login()
    os.environ['SEEQ_SDL_CONTAINER_IS_DATALAB'] = ''
    os.environ['SEEQ_SDL_CONTAINER_IS_EXECUTOR'] = 'true'
    os.environ['SEEQ_PROJECT_UUID'] = '8A54CD8B-B47A-42DA-B8CC-38AD4204C864'
    os.environ['SEEQ_SDL_FILE_PATH'] = 'test.ipynb'
    os.environ['SEEQ_SDL_LABEL'] = 'run-in-executor-label'
    os.environ['SEEQ_SDL_SCHEDULE_INDEX'] = '0'
    spy._config.set_seeq_url(seeq_url)
    spy._config.Setting.SEEQ_PROJECT_UUID.set('8A54CD8B-B47A-42DA-B8CC-38AD4204C863')
