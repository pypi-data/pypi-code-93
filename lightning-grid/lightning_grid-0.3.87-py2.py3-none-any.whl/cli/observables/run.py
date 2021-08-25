from datetime import datetime, timezone
from typing import Dict, Optional

import click
from dateutil.parser import parse as date_string_parse
from gql import Client, gql
from gql.transport.exceptions import TransportQueryError

import grid.cli.globals as env
from grid.cli.observables.base import BaseObservable
from grid.cli.utilities import get_abs_time_difference, string_format_date, string_format_timedelta


def get_runs(client: Client, run_name: Optional[str], team_id: Optional[str] = None) -> Dict:

    params = {'runName': run_name, "teamId": team_id}

    query = gql(
        """
        query (
            $runName: ID, $teamId: ID
        ) {
            getRuns (runName: $runName, teamId: $teamId) {
                name
                createdAt
                experiments {
                    experimentId
                }
                nExperiments
                nFailed
                nCancelled
                nRunning
                nCompleted
                nQueued
                nPending
                projectId
                userDetails {
                    username
                }
            }
        }
        """
    )

    result = client.execute(query, variable_values=params)
    return result['getRuns']


def get_runs_history(client: Client, run_name: Optional[str], team_id: Optional[str] = None) -> Dict:

    params = {'runName': run_name, "teamId": team_id}

    query = gql(
        """
         query (
            $runName: ID, $teamId: ID
        ) {
            getRuns (runName: $runName, teamId: $teamId) {
                name
                createdAt
                experiments {
                    experimentId
                }
                nExperiments
                nFailed
                nCancelled
                nRunning
                nCompleted
                nQueued
                userDetails {
                    username
                }
            }
        }
        """
    )

    result = client.execute(query, variable_values=params)
    return result['getRuns']


class Run(BaseObservable):
    def __init__(self, client: Client, identifier: Optional[str] = []):
        self.client = client

        self.identifier = identifier

        super().__init__(client=client, spinner_load_type="Runs")

    def get(self, is_global: Optional[bool] = False):
        """
        Gets the run status; either for a single run or all runs for
        user.

        Parameters
        ----------
        is_global: Optional[bool], default False
            if True, returns status of experiment(s) of the everyone in the team (TODO)
        """
        runs = []
        self.spinner.start()
        self.spinner.text = 'Getting Run status...'

        run_name = None
        if self.identifier:
            run_name = self.identifier

        try:
            if is_global:
                from grid.cli.core.team import Team
                teams = Team.get_all()
                for team in teams:
                    team_runs = get_runs(self.client, run_name=run_name, team_id=team.id)
                    runs.extend(team_runs)
            else:
                runs = get_runs(self.client, run_name=run_name, team_id=None)
            self.spinner.text = 'Done!'
        except TransportQueryError as e:
            self.spinner.fail("✘")
            self.spinner.stop()
            if env.DEBUG:
                click.echo(str(e))

            raise click.ClickException('Query to Grid failed. Try again in a few minutes.')

        if is_global:
            table_cols = [
                'Run',
                'Project',
                'Status',
                'Created By',
                'Duration',
                'Experiments',
                'Running',
                'Queued',
                'Completed',
                'Failed',
                'Stopped',
            ]
        else:
            table_cols = [
                'Run',
                'Project',
                'Status',
                'Duration',
                'Experiments',
                'Running',
                'Queued',
                'Completed',
                'Failed',
                'Stopped',
            ]

        table = BaseObservable.create_table(columns=table_cols)

        #  Whenever we don't have yet submitted experiments,
        table_rows = 0
        for row in runs:
            status = None

            # we only have 3 statuses for runs
            # running (if something is running)
            is_running = row['nRunning'] is not None and row['nRunning'] > 0

            # We classify queued and pending into queued
            queued = row['nQueued']
            pending = row['nPending']
            n_queued = queued + pending

            # If anything is queued, the the status of the entire
            # run is queued. All other statuses are running in
            # all other conditions.
            if n_queued > 0:
                status = 'queued'

            # If you have anything running (and nothing queued)
            # then, mark the run as running.
            elif is_running:
                status = 'running'

            # If it doesn't match the conditions above, just
            # skip this row and add the row and put it in history.
            else:
                # don't render table because it should be in history
                continue

            #  Change the printed key from `None` to `-` if the
            #  no data exists for those keys.
            keys = ['nExperiments', 'nRunning', 'nQueued', 'nCompleted', 'nFailed', 'nCancelled']
            for key in keys:
                if row[key] is None:
                    row[key] = '-'

            # Calculate the duration column
            created_at = date_string_parse(row['createdAt'])
            delta = get_abs_time_difference(datetime.now(timezone.utc), created_at)
            duration_str = string_format_timedelta(delta)

            if is_global:
                table.add_row(
                    row['name'], row['projectId'], status, row['userDetails']['username'], duration_str,
                    str(row['nExperiments']), str(row['nRunning']), str(n_queued), str(row['nCompleted']),
                    str(row['nFailed']), str(row['nCancelled'])
                )
            else:
                table.add_row(
                    row['name'], row['projectId'], status, duration_str, str(row['nExperiments']), str(row['nRunning']),
                    str(n_queued), str(row['nCompleted']), str(row['nFailed']), str(row['nCancelled'])
                )

            #  Let's count how many rows have been added.
            table_rows += 1

        #  Close the spinner.
        self.spinner.ok("✔")
        self.spinner.stop()

        # If there are no Runs to render, add a
        # placeholder row indicating none are active.
        if table_rows == 0:
            table.add_row("None Active.", *[" " for i in range(len(table_cols) - 1)])

        self.console.print(table)

        #  Print useful message indicating that users can run
        #  grid history.
        history_runs = len(runs) - table_rows
        if history_runs > 0:
            click.echo(f'{history_runs} Run(s) are not active. Use `grid history` ' 'to view your Run history.\n')

        return {'getRuns': runs}

    def get_history(self, is_global: Optional[bool] = False):
        """
        Fetches a complete history of runs. This includes runs that
        are not currently active.

        Parameters
        ----------
        is_global: Optional[bool], default False
            Returns status of session from everyone in the team
        """
        runs = []
        self.spinner.start()
        self.spinner.text = 'Getting Runs ...'

        run_name = None
        if self.identifier:
            run_name = self.identifier[0]

        try:
            if is_global:
                from grid.cli.core.team import Team
                teams = Team.get_all()
                for team in teams:
                    team_runs = get_runs_history(self.client, run_name=run_name, team_id=team.id)
                    runs.extend(team_runs)
            else:
                runs = get_runs_history(self.client, run_name=run_name, team_id=None)
            self.spinner.text = 'Done!'
            self.spinner.ok("✔")
            self.spinner.stop()
        except TransportQueryError as e:
            self.spinner.fail("✘")
            self.spinner.stop()
            if env.DEBUG:
                click.echo(str(e))

            raise click.ClickException('Query to Grid failed. Try again in a few minutes.')

        if is_global:
            table_cols = ['Run', 'Created By', 'Created At', 'Experiments', 'Failed', 'Stopped', 'Completed']
        else:
            table_cols = ['Run', 'Created At', 'Experiments', 'Failed', 'Stopped', 'Completed']
        table = BaseObservable.create_table(columns=table_cols)

        #  Whenever we don't have yet submitted experiments,
        table_rows = runs
        for row in table_rows:
            keys = ['nExperiments', 'nFailed', 'nCancelled', 'nCompleted']
            for key in keys:
                if row[key] is None:
                    row[key] = '-'

            # check if it is running
            is_running = row['nRunning'] is not None and row['nRunning'] > 0

            # check if queued
            is_queued = row['nQueued'] is not None and row['nQueued'] > 0

            # history is everything else
            if is_queued or is_running:
                continue

            created_at = string_format_date(date_string_parse(row['createdAt']))

            if is_global:
                table.add_row(
                    row['name'], row['userDetails']['username'], created_at, str(row['nExperiments']),
                    str(row['nFailed']), str(row['nCancelled']), str(row['nCompleted'])
                )
            else:
                table.add_row(
                    row['name'], created_at, str(row['nExperiments']), str(row['nFailed']), str(row['nCancelled']),
                    str(row['nCompleted'])
                )

        # Add placeholder row if no records are available.
        if not table_rows:
            table.add_row("No History.", *[" " for i in range(len(table_cols) - 1)])

        self.console.print(table)

        return runs

    def follow(self, is_global: Optional[bool] = False):  # pragma: no cover
        pass

    def _get_task_run_dependencies(self, run_name: str):
        """Gets dependency data for a given Run"""
        query = gql(
            """
        query (
            $runName: ID!
        ) {
            getRunTaskStatus (
                runName: $runName
            ) {
                success
                message
                runId
                name
                dependencies {
                    taskId
                    status
                    taskType
                    message
                    error
                }
            }
        }
        """
        )
        params = {'runName': run_name}

        #  Make GraphQL query.
        result = None
        try:
            result = self.client.execute(query, variable_values=params)
            if not result['getRunTaskStatus']['success']:
                raise Exception(result['getRunTaskStatus'])
        except Exception as e:  # skipcq: PYL-W0703
            self.spinner.fail("✘")
            self.spinner.stop()

            raise click.ClickException(f'Could not retrieve task dependencies. Error: {str(e)}')

        if result:
            dependencies = result['getRunTaskStatus']['dependencies']
            return dependencies
        return None
