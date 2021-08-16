import base64
import json
import os
import pathlib
import pickle
import re

from datetime import datetime, timedelta
from typing import Optional

import ipykernel

import pytz as tz
import pandas as pd

import cron_descriptor
from recurrent import RecurringEvent

from urllib.parse import unquote

from seeq.sdk import *

from seeq.spy import _common
from seeq.spy import _config
from seeq.spy import _login
from seeq.spy._errors import *
from seeq.spy.jobs import _common as _jobs_common


def schedule(schedule_spec: str, datalab_notebook_url: Optional[str] = None, label: Optional[str] = None,
             user: Optional[str] = None, suspend: bool = False, quiet: bool = False,
             status: Optional[_common.Status] = None):
    """
    Schedules the automatic execution of a Seeq Data Lab notebook.

    The current notebook is scheduled for execution unless datalab_notebook_url
    is supplied. Scheduling can be done on behalf of another user by a user with
    admin privileges.

    Successive calls to 'schedule()' for the same notebook and label but with
    different schedules will replace the previous schedule for the notebook-
    label combination.

    Removing the scheduling is accomplished via unschedule().

    A copy of the jobs DataFrame is automatically stored to a _Job DataFrames
    folder adjacent to the Notebook for which the job is scheduled.

    Parameters
    ----------
    schedule_spec : str
        A string that represents the frequency with which the notebook should
        execute.

        Examples: 'every 15 minutes'
                  'every tuesday and friday at 6am'
                  'every fifth of the month'

        The timezone used for scheduling is the one specified in the logged-in
        user's profile.

        You can also use Quartz Cron syntax. Use the following site to
        construct it:
        https://www.freeformatter.com/cron-expression-generator-quartz.html

    datalab_notebook_url : str, default None
        A datalab notebook URL. If the value is not specified the currently
        running notebook URL is used.

    label : str, default None
        A string used to enable scheduling of the Notebook by different users
        or from different Analysis Pages.  Labels may contain letters, numbers,
        spaces, and the following special characters: !@#$^&-_()[]{}

    user : str, default None
        Determines the user on whose behalf the notebook is executed. If the
        value is not specified the currently logged in user is used. The can be
        specified as username or a user's Seeq ID.

    suspend : bool, default False
        If True, unschedules all jobs for the specified notebook. This is used
        in scenarios where you wish to work with a notebook interactively and
        temporarily "pause" job execution. Remove the argument (or change it
        to False) when you are ready to resume job execution.

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
    pd.DataFrame
        The jobs_df with an appended column containing a description of the
        schedule
    """
    _common.validate_argument_types([
        (schedule_spec, 'schedule_string', str),
    ])

    status = _common.Status.validate(status, quiet)

    try:
        return schedule_df(pd.DataFrame([{'Schedule': schedule_spec}]) if schedule_spec else None,
                           datalab_notebook_url=datalab_notebook_url, label=label, user=user, suspend=suspend,
                           status=status)
    except SchedulePostingError:
        # See _push.push() for why we swallow this error in the executor
        if not _jobs_common.running_in_executor():
            raise


def unschedule(datalab_notebook_url: Optional[str] = None, label: Optional[str] = None,
               quiet: bool = False, status: Optional[_common.Status] = None):
    """
    Unschedules ALL jobs for a particular notebook and label.

    The current notebook is unscheduled unless datalab_notebook_url
    is supplied. Unscheduling can be done on behalf of another user by a user
    with admin privileges.

    Parameters
    ----------
    datalab_notebook_url : str, default None
        A datalab notebook URL. If the value is not specified the currently
        running notebook URL is used.

    label : str, default None
        A string used to enable scheduling of the Notebook by different users
        or from different Analysis Pages.  Labels may contain letters, numbers,
        spaces, and the following special characters:

        !@#$^&-_()[]{}

        A value of '*' will unschedule all jobs across all labels associated
        with the supplied notebook (or the current Notebook, if no
        datalab_notebook_url is supplied).

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
    """
    status = _common.Status.validate(status, quiet)
    schedule_df(jobs_df=None, datalab_notebook_url=datalab_notebook_url, label=label, status=status)


class SchedulePostingError(SPyRuntimeError):
    pass


def schedule_df(jobs_df=None, spread=None, datalab_notebook_url=None, label=None, user=None, suspend=False,
                status=None):
    input_args = _common.validate_argument_types([
        (jobs_df, 'jobs_df', pd.DataFrame),
        (datalab_notebook_url, 'datalab_notebook_url', str),
        (label, 'label', str),
        (user, 'user', str),
        (suspend, 'suspend', bool),
        (status, 'status', _common.Status)
    ])

    if jobs_df is None:
        jobs_df = pd.DataFrame()

    _login.validate_login(status)

    indexed_cron_expressions = get_cron_expression_list(jobs_df) if not suspend else []
    if spread:
        indexed_cron_expressions = spread_over_period(indexed_cron_expressions, spread)
    next_trigger_map = validate_and_get_next_trigger([cron for idx, cron in indexed_cron_expressions])
    datalab_base_url, project_id, file_path = retrieve_notebook_path(datalab_notebook_url)
    # Even though the following verify method immediately calls retrieve_notebook_path again, it is convenient to have
    # the passed URL for the error message, so we don't call it with the resulting tuple.  The verification is done
    # separately so that retrieve_notebook_path can be reused for cases where existence of the URL is not required,
    # and so that an appropriate error message will be provided before attempting the contents API if the URL is bad.
    if datalab_notebook_url:
        verify_existing_and_accessible(datalab_notebook_url)

    try:
        user_identity = _login.find_user(user) if user is not None else None
        if len(indexed_cron_expressions) == 0:
            call_unschedule_notebook_api(project_id, file_path, label)
        else:
            call_schedule_notebook_api(indexed_cron_expressions, project_id, file_path, label, user_identity)
    except BaseException as e:
        status.exception(e)
        raise SchedulePostingError(e)

    with_label_text = f' with label <strong>{label}</strong> ' if label else ' '
    if indexed_cron_expressions:
        status.update(f'Scheduled the notebook <strong>{file_path}</strong>{with_label_text}successfully.\n'
                      f'Current context is <strong>{"JOB" if _jobs_common.running_in_executor() else "INTERACTIVE"}'
                      '</strong>.', _common.Status.SUCCESS)
        pickle_path = pickle_jobs_df(jobs_df, datalab_notebook_url, label)
        if pickle_path:
            status.update(f'{status.message}  The jobs_df was stored to {pickle_path}')
    else:
        unlabeled = " " if label else " unlabeled "
        with_label_text = ' for all labels ' if label == '*' else with_label_text
        status.update(f'Unscheduled all{unlabeled}jobs for notebook <strong>{file_path}'
                      f'</strong>{with_label_text}successfully.', _common.Status.SUCCESS)

    if indexed_cron_expressions:
        cron_expressions = [cron for idx, cron in indexed_cron_expressions]
        schedule_result_df = pd.concat(
            [jobs_df,
             pd.Series(cron_expressions, index=jobs_df.index).rename('Scheduled').map(cron_descriptor.get_description)],
            axis=1
        )
        schedule_result_df = pd.concat(
            [schedule_result_df,
             pd.Series(cron_expressions, index=jobs_df.index).rename('Next Run').map(lambda ce: next_trigger_map[ce])],
            axis=1
        )
    else:
        schedule_result_df = pd.DataFrame()
    schedule_df_properties = dict(
        func='spy.schedule',
        kwargs=input_args,
        status=status)
    _common.add_properties_to_df(schedule_result_df, **schedule_df_properties)

    status.df = schedule_result_df
    status.update()
    return schedule_result_df


def verify_existing_and_accessible(datalab_notebook_url):
    datalab_base_url, project_id, file_path = retrieve_notebook_path(datalab_notebook_url)
    contents_api_url = f'{datalab_base_url}/{project_id}/api/contents'
    params = {'type': 'file', 'content': 0}
    cookies = {"sq-auth": _login.client.auth_token}
    resp = _common.requests_get(f'{contents_api_url}/{file_path}', params=params, cookies=cookies)
    if resp.status_code != 200:
        raise SPyRuntimeError(f'Notebook not found for URL {datalab_notebook_url}.  Verify that the notebook exists '
                              f'and the user account has access to it')


def pickle_jobs_df(jobs_df, datalab_notebook_url=None, label=None):
    data_lab_url, project_id, file_path = retrieve_notebook_path(datalab_notebook_url)
    file_path_path = pathlib.PurePosixPath(file_path)
    path_to_parent = path_or_empty_string(file_path_path.parent)
    with_label_text = f'.with.label.{label}' if label else ''
    jobs_df_pickle = f'{file_path_path.stem}{with_label_text}.pkl'

    jobs_dfs_folder_path = pathlib.PurePosixPath(path_to_parent, _common.JOB_DATAFRAMES_FOLDER_NAME)
    cookies = {'sq-auth': _login.client.auth_token}
    contents_api_url = f'{data_lab_url}/{project_id}/api/contents'

    if not get_or_create_folder(contents_api_url, str(jobs_dfs_folder_path)):
        raise SPyRuntimeError(f'Could not get or create {_common.JOB_DATAFRAMES_FOLDER_NAME} folder')

    put_pickle_path = pathlib.PurePosixPath(jobs_dfs_folder_path, jobs_df_pickle)
    content_encoded = base64.b64encode(pickle.dumps(jobs_df)).decode('utf-8')
    content_model = {
        'format': 'base64',
        'name': jobs_df_pickle,
        'path': str(put_pickle_path),
        'type': 'file',
        'content': content_encoded
    }
    resp = _common.requests_put(f'{data_lab_url}/{project_id}/api/contents/{put_pickle_path}',
                                data=json.dumps(content_model),
                                cookies=cookies)
    if resp.status_code in [200, 201]:
        return put_pickle_path


def get_or_create_folder(contents_api_url: str, folder_path: str):
    cookies = {"sq-auth": _login.client.auth_token}
    folder_path_as_path = pathlib.PurePosixPath(folder_path)
    folder_parent = path_or_empty_string(folder_path_as_path.parent)
    resp = _common.requests_get(f'{contents_api_url}/{folder_parent}', cookies=cookies)
    if folder_path_as_path.name in [item['name'] for item in resp.json()['content']]:
        return True
    else:
        new_folder_post_resp = _common.requests_post(contents_api_url,
                                                     data=json.dumps({'type': 'directory'}),
                                                     cookies=cookies)
        new_folder_path = pathlib.PurePosixPath(new_folder_post_resp.json()['path'])
        rename_folder_resp = _common.requests_patch(f'{contents_api_url}/{new_folder_path}',
                                                    data=json.dumps({'path': folder_path}),
                                                    cookies=cookies)
        return True if rename_folder_resp.status_code == 200 else False


def path_or_empty_string(path):
    return '' if str(path) in ['.', '/'] else str(path)


def pickle_df_to_path(df, path):
    df.to_pickle(path)


def validate_and_get_next_trigger(cron_expression_list):
    jobs_api = JobsApi(_login.client)
    validate_cron_input = ValidateCronListInputV1()
    validate_cron_input.timezone = _login.get_user_timezone()
    validate_cron_input.next_valid_time_after = datetime.now(tz.timezone(_login.get_user_timezone())) \
        .replace(microsecond=0)
    validate_cron_input.schedules = cron_expression_list
    validation_output = jobs_api.validate_cron(body=validate_cron_input)

    invalid_cron_expressions = []
    for cron_validation in validation_output.schedules:
        if cron_validation.error is not None:
            invalid_cron_expressions.append({'string': cron_validation.quartz_cron_expression,
                                             'error': cron_validation.error})
    if invalid_cron_expressions:
        raise SPyRuntimeError('The following schedules are invalid: ' + str(invalid_cron_expressions))
    return dict((s.quartz_cron_expression, s.next_run_time) for s in validation_output.schedules)


def call_schedule_notebook_api(cron_expressions, project_id, file_path, label, user_identity):
    projects_api = ProjectsApi(_login.client)
    schedule_input = ScheduledNotebookInputV1()
    schedule_input.file_path = file_path
    schedule_input.schedules = [ScheduleInputV1(key=idx, cron_schedule=cron) for idx, cron in cron_expressions]
    schedule_input.timezone = _login.get_user_timezone()
    schedule_input.label = label
    if user_identity is not None:
        schedule_input.user_id = user_identity.id

    projects_api.schedule_notebook(id=project_id, body=schedule_input)


def call_unschedule_notebook_api(project_id, file_path, label):
    if label is None:
        ProjectsApi(_login.client).unschedule_notebook(id=project_id, file_path=file_path)
    else:
        ProjectsApi(_login.client).unschedule_notebook(id=project_id, file_path=file_path, label=label)


def retrieve_notebook_path(datalab_notebook_url=None):
    if datalab_notebook_url is None:
        if _jobs_common.running_in_datalab():
            return _config.get_data_lab_orchestrator_url(), _config.get_data_lab_project_id(), \
                get_notebook_path()
        if _jobs_common.running_in_executor():
            return _config.get_data_lab_orchestrator_url(), _config.get_data_lab_project_id(), \
                os.environ['SEEQ_SDL_FILE_PATH']
        else:
            raise SPyRuntimeError('Provide a Seeq Data Lab Notebook URL for scheduling')
    else:
        data_lab_url, project_id, file_path = parse_data_lab_url_project_id_and_path(datalab_notebook_url)
        if not data_lab_url:
            if _jobs_common.running_in_datalab() or _jobs_common.running_in_executor():
                data_lab_url = _config.get_data_lab_orchestrator_url()
            else:
                raise SPyRuntimeError('Path for Seeq Data Lab Notebook URL must include protocol and host if not '
                                      'running in Data Lab')
        return data_lab_url, project_id, file_path


def parse_data_lab_url_project_id_and_path(notebook_url):
    matches = re.search(r'^(.*/data-lab)/([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})/[\w]+/(.*)',
                        notebook_url)
    if not matches:
        raise SPyValueError('URL is not a valid SDL notebook')

    data_lab_url = _config.get_data_lab_orchestrator_url() if matches.group(1) == '/data-lab' else matches.group(1)
    project_id = matches.group(2)
    file_path = unquote(matches.group(3))
    return data_lab_url, project_id, file_path


def get_notebook_path():
    kernel_id = re.search('kernel-(.*).json', ipykernel.connect.get_connection_file()).group(1)
    cookies = {
        'sq-auth': _login.client.auth_token
    }
    url = f'{_config.get_data_lab_project_url()}/api/sessions'
    response = _common.requests_get(url, cookies=cookies)
    for nn in json.loads(response.text):
        if nn['kernel']['id'] == kernel_id:
            return nn['notebook']['path']


def spread_over_period(cron_expressions, over_period):
    over_period_delta = _common.parse_str_time_to_timedelta(over_period)

    if len(cron_expressions) == 0:
        return []

    if over_period_delta.total_seconds() > (60 * 60 * 24):
        raise SPyValueError(f'over_period cannot be more than 24 hours')

    spacing = timedelta(seconds=(over_period_delta.total_seconds() / len(cron_expressions)))
    current_slot = timedelta()
    new_expressions = list()
    for idx, cron_expression in cron_expressions:
        parts = re.split(r'\s+', cron_expression)
        parts[0] = re.sub(r'(.+?)(/.+)?', rf'{int(current_slot.total_seconds() % 60)}\2', parts[0])
        if over_period_delta.total_seconds() > 60:
            parts[1] = re.sub(r'(.+?)(/.+)?', rf'{int((current_slot.total_seconds() / 60) % 60)}\2', parts[1])
        if over_period_delta.total_seconds() > (60 * 60):
            parts[2] = re.sub(r'(.+?)(/.+)?', rf'{int(current_slot.total_seconds() / (60 * 60))}\2', parts[2])
        new_expressions.append((idx, ' '.join(parts)))
        current_slot += spacing

    return new_expressions


def get_cron_expression_list(jobs_df):
    if jobs_df is None or jobs_df.empty:
        return []

    if 'Schedule' not in jobs_df:
        schedule_column = jobs_df.columns[0]
    else:
        schedule_column = 'Schedule'

    return [(idx, parse_schedule_string(row[schedule_column])) for idx, row in jobs_df.iterrows()]


def parse_schedule_string(schedule_string):
    # noinspection PyBroadException
    try:
        # If cron_descriptor can parse it, then it's a valid cron schedule already
        cron_descriptor.get_description(schedule_string)
        return schedule_string
    except BaseException:
        pass

    return friendly_schedule_to_quartz_cron(schedule_string)


def friendly_schedule_to_quartz_cron(schedule_string):
    r = RecurringEvent()
    r.parse(schedule_string)

    rules = r.get_params()
    if len(rules) == 0 or 'freq' not in rules or 'interval' not in rules:
        raise SPyValueError(f'Could not interpret "{schedule_string}" as a schedule')
    days = {'SU': 1, 'MO': 2, 'TU': 3, 'WE': 4, 'TH': 5, 'FR': 6, 'SA': 7}
    if not r.is_recurring:
        raise SPyValueError(f'Could not interpret "{schedule_string}" as a recurring schedule')
    minute = rules.get('byminute', '0')
    hour = rules.get('byhour', '0')
    day_of_month = rules.get('bymonthday', '?')
    month = rules.get('bymonth', '*')
    day_of_week = ','.join([str(days[byday]) for byday in rules['byday'].split(',')]) if 'byday' in rules else '?'

    if day_of_month == '?' and day_of_week == '?':
        day_of_month = '1' if rules['freq'] in ['monthly', 'yearly'] else '*'

    interval = rules['interval']
    if rules['freq'] == 'minutely':
        hour = '*'
        minute = f'*/{interval}'
    elif rules['freq'] == 'hourly':
        hour = f'*/{interval}'
    elif rules['freq'] == 'daily':
        day_of_month += f'/{interval}'
    elif rules['freq'] == 'weekly':
        pass
    elif rules['freq'] == 'monthly':
        month += f'/{interval}'

    cron = f'0 {minute} {hour} {day_of_month} {month} {day_of_week}'

    return cron
