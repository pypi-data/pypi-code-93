"""This module is called when executing from a venv mapped cli call."""
import logging
from subprocess import call

import click
import git

import dbispipeline.cli.dataset as dataset
from dbispipeline.core import Core
from dbispipeline.storage_handlers import PostGresOutputHandler
from dbispipeline.storage_handlers import PrintHandler
from dbispipeline.utils import LOGGER
from dbispipeline.utils import restore_backup
from dbispipeline.utils import write_slurm_job_file


@click.command(help='Uses the plan file specified in PLAN to run the dbis '
               'pipeline.')
@click.option('--dryrun', is_flag=True, help='Don\'t store results into DB')
@click.option('--force', is_flag=True, help='Run even if git is dirty')
@click.option('-v', '--verbose', is_flag=True, help='increase logging')
@click.option('--slurm', is_flag=True, help='create slurm file')
@click.option('--slurm-and-run', is_flag=True,
              help='create slurm job file and submit using sbatch')
@click.option('--restore', type=str, help='result file to be restored')
@click.option(
    '--mail',
    type=click.Choice(['none', 'run', 'total']),
    default='none',
    help='Mail notification level. Choose one of [None, \'run\', \'total\''
    ']. If set no None, no mails will be sent. if set to \'run\', one info'
    ' mail will be sent for each run. If set to \'total\', one mail will '
    'be sent after the entire pipeline is complete.')
@click.argument('plan', type=click.Path(exists=True))
def main(dryrun, force, verbose, slurm, slurm_and_run, restore, mail, plan):
    """Entry point that executes the pipeline given a configuration."""
    if verbose:
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.debug('setting logging level to DEBUG')

    if restore:
        restore_backup(restore, [PrintHandler(), PostGresOutputHandler()])
        exit(0)

    if not force:
        try:
            repo = git.Repo(search_parent_directories=True)
            if repo.is_dirty():
                LOGGER.error(
                    'Please commit your changes before you run the pileline.')
                exit(1)
        except git.GitError:
            pass

    if slurm or slurm_and_run:
        job = write_slurm_job_file(dryrun, force, verbose, restore, mail,
                                   plan)
        if slurm_and_run:
            LOGGER.info('starting slurm job: %s', job)
            call(['sbatch', job])
    else:
        Core(plan, dryrun=dryrun, mail=mail).run()


@click.command(help='Links the specified dataset to the data folder.')
@click.option(
    '--dataset-dir',
    '-p',
    default=None,
    type=str,
    help='The path prefix used to find the datasets.',
)
def link(dataset_dir):
    """Links the dataset as specified in data/links.yaml."""
    dataset.link(dataset_dir=dataset_dir)
