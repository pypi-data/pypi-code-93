"""Utils used in the dbispipeline implementation."""
import configparser
import datetime
from email.mime.text import MIMEText
import inspect
import json
import logging
import os
from os.path import basename
from os.path import join
from os.path import splitext
import pickle
import platform
import smtplib
import tempfile
import traceback
import warnings

import numpy as np

from . import store

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(name)-16s %(message)s',
    level=logging.INFO,
)
LOGGER = logging.getLogger('dbispipeline')

OPTION_BACKUP_DIR = 'backup_dir'
OPTION_DATASET_DIR = 'dataset_dir'

SECTION_DATABASE = 'database'
SECTION_PROJECT = 'project'
SECTION_VARIABLES = 'variables'
SECTION_MAIL = 'mail'

POSTGRES_DEFAULT_PORT = 5432

INI_FILE_NAME = 'dbispipeline.ini'


def load_project_config():
    """Loads the project configuration."""
    config_files = [join('/usr/local/etc', INI_FILE_NAME)]
    user_home = os.getenv('HOME')
    if user_home:
        config_files.append(join(user_home, '.config', INI_FILE_NAME))

    # find a configuration in any parent folder
    parent_directory_configs = []
    directory = os.path.realpath('.')
    while directory != os.path.dirname(directory):
        candidate = join(directory, INI_FILE_NAME)
        if os.path.isfile(candidate):
            parent_directory_configs.append(candidate)
            break
        directory = os.path.dirname(directory)
    # directories 'closer' to the current cwd are preferred
    parent_directory_configs.reverse()

    config_files += parent_directory_configs
    config = configparser.ConfigParser()

    if os.getenv('DBISPIPELINE_ENV') == 'ci':
        # Sets default values if the environment is a ci
        config.read_dict({
            SECTION_DATABASE: {
                'host': 'postgres',
                'port': POSTGRES_DEFAULT_PORT,
                'user': 'runner',
                'password': 'runner_password',
                'database': 'pipelineresults',
            },
        })
        LOGGER.debug('detected CI environment')

    parsed_files = config.read(config_files)
    LOGGER.debug(f'loaded configuration from files: {parsed_files}')

    if not config.has_section(SECTION_DATABASE):
        raise KeyError('no database section found in the configuration')

    # set some default values
    if not config.has_option(SECTION_DATABASE, 'port'):
        config.set(SECTION_DATABASE, 'port', str(POSTGRES_DEFAULT_PORT))

    if not config.has_section(SECTION_PROJECT):
        config.add_section(SECTION_PROJECT)

    if not config.has_option(SECTION_PROJECT, OPTION_DATASET_DIR):
        config.set(SECTION_PROJECT, OPTION_DATASET_DIR, '')

    if os.getenv('DBISPIPELINE_DATASET_DIR'):
        dataset_dir = os.getenv('DBISPIPELINE_DATASET_DIR')
        config.set(SECTION_PROJECT, OPTION_DATASET_DIR, dataset_dir)

    if not config.has_option(SECTION_PROJECT, OPTION_BACKUP_DIR):
        config.set(SECTION_PROJECT, OPTION_BACKUP_DIR, tempfile.gettempdir())

    if os.getenv('DBISPIPELINE_BACKUP_DIR'):
        backup_dir = os.getenv('DBISPIPELINE_BACKUP_DIR')
        config.set(SECTION_PROJECT, OPTION_BACKUP_DIR, backup_dir)

    backup_dir = config[SECTION_PROJECT][OPTION_BACKUP_DIR]
    if not os.path.isdir(backup_dir):
        raise ValueError('the %s backup dir does not exist.' % backup_dir)

    return config


def get_backup_dir():
    """Returns the backup directory."""
    config = load_project_config()
    return config[SECTION_PROJECT][OPTION_BACKUP_DIR]


def load_result_backup(path):
    """
    Loads results from a pickle backup.

    Args:
        path: to the backup file
    """
    with open(path, 'rb') as f:
        return pickle.load(f)


def restore_backup(path, storage_handlers):
    """
    Reads a backup file and handles it with the given handlers.

    Args:
        path: to the backup file.
        storage_handlers: an iterable containing storage handlers
    """
    backup = load_result_backup(path)

    for handler in storage_handlers:
        handler.handle_result(backup)


def store_prediction(model, dataloader, file_name_prefix=None):
    """
    Predicts test data with fitted models.

    This method first tries to call predict() and stores the results into a
    file called <prefix>predict.npy.
    Afterwards, it tries to call predict_proba() and stores that result into
    <prefix>predict_proba.npy.


    Args:
        model: a trained model that should call predict() or predict_proba().
        dataloader: a dataloader that has the load_test() method.
        file_name_prefix: a prefix for the file names. If this prefix does not
            end with an underscore, one will be appended to it.
    """
    if not file_name_prefix:
        file_name_prefix = type(model).__name__

    if store['plan_path']:
        if file_name_prefix[-1] != '_':
            file_name_prefix += '_'
        file_name_prefix += splitext(basename(store['plan_path']))[0]

    if file_name_prefix[-1] != '_':
        file_name_prefix += '_'

    x_test, _ = dataloader.load_test()

    try:
        y_pred = model.predict(x_test)
        np.save(file_name_prefix + 'predict.npy', y_pred)
    except AttributeError:
        LOGGER.warning('Model does not support predict.')

    try:
        y_pred = model.predict_proba(x_test)
        np.save(file_name_prefix + 'predict_proba.npy', y_pred)
    except AttributeError:
        LOGGER.warning('Model does not support predict_proba.')


def notify_success(plan_path,
                   times,
                   result=None,
                   run=None,
                   subject='DBIS Pipeline: successfully finished',
                   loader_config=None):
    """
    Sends an email that new results have been successfully stored.

    Args:
        plan_path: the path to the plan file that has been used
        result: something representing a result that is tried to be included
            in the email. It should be json-dumpable.
        run: the run number. This setting is useful for multiloaders, where
            multiple runs emerge from the same plan.
        subject: email subject
        loader_config: configuration of the dataloader that was used. Useful
            for multiloaders, where multiple runs emerge from the same plan.
    """
    run_string = ''
    if run is not None:
        run_string = f' run #{run}'

    result_string = 'The results are available in the database.'
    if result and isinstance(result, dict) or isinstance(result, str):
        try:
            pretty_printed_json = json.dumps(result, indent=2, sort_keys=True)
            result_string = f'Your results are:\n\n{pretty_printed_json}'
        except Exception:
            LOGGER.warn('could not write result as pretty json string')
            pass
    computer_name = platform.node()
    duration = datetime.timedelta(seconds=int(times['eval'] - times['start']))
    message = f'''\
Hello,
your configuration file {plan_path} running on {computer_name}\
        has finished{run_string}.
The calculation took {duration}.'''

    if loader_config:
        message += f'''
The configuration of the dataloader was:
    {loader_config}'''

    message += '\n' + result_string

    _notify(message, subject)


def notify_error(plan_path,
                 error_stage,
                 error_object,
                 subject='DBIS Pipeline: error',
                 run=None,
                 loader_config=None):
    """
    Sends an email that something has gone wrong during the pipeline execution.

    Args:
        plan_path: the path to the plan file that has been used
        error_stage: string at which point the pipeline failed.
        error_object: additional information that is added in the mail body.
            should be json-dumpable.
        subject: email subject
        run: the run number. This setting is useful for multiloaders, where
            multiple runs emerge from the same plan.
        loader_config: configuration of the dataloader that was used. Useful
            for multiloaders, where multiple runs emerge from the same plan.
    """
    run_string = ''
    if run is not None:
        run_string = f' on run #{run}'
    message = f'''Hello,
unfortunately, your configuration file {plan_path} caused an error on
the pipeline running on {platform.node()} during {error_stage}{run_string}.
'''
    if loader_config:
        message += f'''
The configuration of the dataloader was:
    {loader_config}'''

    if error_object:
        message += f'''
The error message is:
    {traceback.format_tb(error_object.__traceback__)}'''

    _notify(message, subject)


def _notify(message, subject):
    cfg = load_project_config()
    if SECTION_MAIL not in cfg:
        LOGGER.debug(f'missing section [{SECTION_MAIL}]: not sending success '
                     'message: {message}')
        return

    required_fields = ['recipient', 'sender', 'smtp_server']
    for field in required_fields:
        if field not in cfg[SECTION_MAIL]:
            LOGGER.error(f'missing option in mail configuration: {field}')
            return

    # required
    recipient = cfg[SECTION_MAIL]['recipient']
    sender = cfg[SECTION_MAIL]['sender']
    host = cfg[SECTION_MAIL]['smtp_server']

    LOGGER.info(f'sending mail to {recipient}')
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    if cfg[SECTION_MAIL].getboolean('authenticate', fallback=False):

        more_required_fields = ['username', 'password']
        for field in more_required_fields:
            if field not in cfg[SECTION_MAIL]:
                LOGGER.error(f'missing field in mail configuration: {field}')
                return

        # optional
        port = cfg.getint(SECTION_MAIL, 'port', fallback=465)
        s = smtplib.SMTP_SSL(host, port)
    else:
        s = smtplib.SMTP(host)

    s.sendmail(sender, [recipient], msg.as_string())


def write_slurm_job_file(dryrun, force, verbose, restore, mail, plan):
    """
    Writes a slurm job to 'slurmjobs/<timestamp>_<jobname>.job'.

    The arguments passed to this method will be used as the arguments for the
    main method, so see those for detailed information.
    """
    config = load_project_config()
    job_name = config.get('project', 'name', fallback=None)
    job_name += '_' + os.path.splitext(os.path.basename(plan))[0]
    log_directory = config.get('project', 'log_directory', fallback='logs')
    options = [
        '--partition=IFIgpu',
        f'--job-name={job_name}',
        '--account=dbis',
        '--nodes=1',
        '--tasks-per-node=1',
        f'-o {log_directory}/{job_name}-%j.out',
        f'-e {log_directory}/{job_name}-%j.err',
    ]

    if mail is not None:
        email = config.get('slurm', 'email', fallback=None)
        if email:
            options.append('--mail-type=ALL')
            options.append(f'--mail-user={email}')
        else:
            warnings.warn('No email address found in configuration, slurm will'
                          'not send any emails')

    content = '#!/bin/bash -l\n'
    content += '\n'.join(['#SBATCH ' + x for x in options])

    venv_manager = config.get('slurm',
                              'virtual_env_manager',
                              fallback='pipenv')
    content += f'\nsrun {venv_manager} run python -m dbispipeline {plan} '

    if dryrun:
        content += '--dryrun '
    if force:
        content += '--force '
    if restore:
        content += f'--restore {restore} '
    if verbose:
        content += '--verbose '

    if not os.path.isdir('slurmjobs'):
        os.makedirs('slurmjobs')
    timestamp = datetime.datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
    plan_noext = os.path.splitext(os.path.basename(plan))[0]
    job_filename = f'{timestamp}_{job_name}_{plan_noext}.job'
    jobfile = join('slurmjobs', job_filename)
    with open(jobfile, 'w') as o_f:
        o_f.write(content)
        LOGGER.info('slurm job written to %s', jobfile)
    return jobfile


def get_job_id():
    """Returns the assigned job id.

    If run on a supported batch system (currently sge and slurm) this is the
    job id assigend by the batch system and as a fallback it is the process id.

    If DBISPIPELINE_JOB_ID is set. This overrides the other values and the
    respective values is reutrned.
    """
    # set a job id overruling all other job ids
    if os.getenv('DBISPIPELINE_JOB_ID'):
        return int(os.getenv('DBISPIPELINE_JOB_ID'))

    # slurm job id
    if os.getenv('SLURM_JOB_ID'):
        return int(os.getenv('SLURM_JOB_ID'))

    # sge job id
    if os.getenv('JOB_ID'):
        return int(os.getenv('JOB_ID'))

    # fallback job id
    return os.getpid()


def check_serializability(content,
                          nan_replacement=0.0,
                          pos_inf_replacement=0.0,
                          neg_inf_repacement=0.0):
    """
    Returns a copy of a dict object that can be json-serialized.

    For each item pair of the dictionary, if key and value are json
    serializable, the pair is kept as-is. Otherwise, the value of the pair is
    returned as string to enable storing in the database.

    Args:
        content: anything
            The object to be checked
        nan_replacement (float):
            Value to replace np.nan for serialization
    Returns:
        A copy of the results which can be stored in a JSON column in the db,
        or as a pickle for the pickle storage handler
    """
    try:
        _ = json.dumps(content, allow_nan=False)
        return content
    except (ValueError, TypeError):
        if type(content) == list or type(content) == tuple:
            cleaned = [
                check_serializability(x,
                                      nan_replacement=nan_replacement,
                                      pos_inf_replacement=pos_inf_replacement,
                                      neg_inf_repacement=neg_inf_repacement)
                for x in content
            ]
        elif type(content) == dict:
            cleaned = {
                k:
                check_serializability(v,
                                      nan_replacement=nan_replacement,
                                      pos_inf_replacement=pos_inf_replacement,
                                      neg_inf_repacement=neg_inf_repacement)
                for k, v in content.items()
            }
        elif callable(content):
            cleaned = inspect.getsource(content).strip()
        elif type(content) == float and np.isnan(content):
            cleaned = nan_replacement
        elif type(content) == float and np.isposinf(content):
            cleaned = pos_inf_replacement
        elif type(content) == float and np.isneginf(content):
            cleaned = neg_inf_repacement
        elif type(content) == np.ndarray:
            cleaned = content.tolist()
        else:
            try:
                # assume numpy type
                cleaned = content.item()
            except AttributeError as ex:
                raise ValueError(
                    f'Type \'{type(content)}\' is no numpy type.') from ex

        return cleaned
