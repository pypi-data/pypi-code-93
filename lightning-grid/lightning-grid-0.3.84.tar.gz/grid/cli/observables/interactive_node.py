from __future__ import annotations

import ast
from datetime import datetime, timezone
import typing
from typing import Dict, Optional

import click
from dateutil.parser import parse as date_string_parse
from gql import Client, gql
from rich.progress import BarColumn, Progress, TextColumn

from grid.cli.exceptions import ResourceNotFound
import grid.cli.globals as env
from grid.cli.observables.base import BaseObservable, TASK_CLASS_IGNORE, TASK_CLASS_MAPPING
from grid.cli.utilities import get_abs_time_difference, string_format_timedelta

if typing.TYPE_CHECKING:
    from grid.cli.core import Team


def get_sessions(client: Client, team: Optional['Team'] = None) -> Dict:
    query = gql(
        """
    query GetInteractiveNodes ($teamId: ID){
        getInteractiveNodes(teamId: $teamId) {
            interactiveNodeId
            interactiveNodeName
            clusterId
            createdAt
            jupyterUrl
            status
            desiredState
            config {
                diskSize
                instanceType
            }
            userDetails {
                username
            }
        }
    }
    """
    )
    if team:
        params = {'teamId': team.id}  # noqa
    else:
        params = {'teamId': None}
    result = client.execute(query, variable_values=params)
    if not result['getInteractiveNodes']:
        raise ResourceNotFound
    return result


class InteractiveNode(BaseObservable):
    """
    Base observable for a Grid interactive node.

    Parameters
    ----------
    client: Client
        GQL client
    """
    def __init__(self, client: Client):
        self.client = client

        super().__init__(client=client, spinner_load_type="Interactive Nodes")

    # TODO: This isn't currently used anywhere. It may be useful to also
    #  show pre-run status for tasks related to creating an interactive node.
    #  New changes like teams/collaboration are not implemented for this func
    def _get_task_status(self, interactive_node_id: str):  # pragma: no cover
        """
        Gets task status for a given interactive node.

        Parameters
        ----------
        interactive_node_id: str
            Interactive node ID.
        """
        self.spinner.start()

        query = gql(
            """
        query GetInteractiveTaskStatus ($interactiveNodeId: ID!) {
            getInteractiveTaskStatus(interactiveNodeId: $interactiveNodeId) {
                status
                message
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
        params = {'interactiveNodeId': interactive_node_id}

        try:
            result = self.client.execute(query, variable_values=params)
        except Exception as e:  # skipcq: PYL-W0703
            message = ast.literal_eval(str(e))['message']
            self.spinner.fail("✘")
            raise click.ClickException(message)

        # Gets dependenceis.
        dependencies = result['getRunTaskStatus']['dependencies']

        #  Figure out the status of each task.
        dependency_data = {}
        for task in dependencies:
            if task['taskType'] in TASK_CLASS_IGNORE:
                continue

            dependency_data[task['taskType']] = {
                'status': task['status'],
                'error': task['error'],
                'message': task['message'],
                'status_message': TASK_CLASS_MAPPING[task['taskType']]
            }

        #  Display the status of setting-up the cluster & environment
        #  to the user.
        self.spinner.text = 'Done!'
        self.spinner.ok("✔")

        #  Show message if there's an error in a pre-start task.
        all_status = [s['status'] for s in dependency_data.values()]
        if any(s == 'failed' for s in all_status) and \
                not env.SHOW_PROCESS_STATUS_DETAILS:
            click.echo(
                f'''
        The Interactive Node "{interactive_node_id}" failed to start due to a setup error.
        You can see the errors by running

            grid status {interactive_node_id} --details

            '''
            )

        #  Create progress bar.
        click.echo('\n')
        with Progress(
            TextColumn("[bold blue]{task.description}", justify="left"), BarColumn(bar_width=55),
            "[self.progress.percentage]{task.percentage:>3.1f}%"
        ) as progress_bar:

            #  Render progress bar based on finished tasks.
            task_id = progress_bar.add_task('Creating Interactive Node', start=True, total=len(all_status))

            progress = sum(1 for s in all_status if s == 'finished')
            progress_bar.update(task_id, advance=progress)

        #  If there's an error with creating a cluster, then
        #  print that error to the terminal.
        if env.SHOW_PROCESS_STATUS_DETAILS:
            for key, value in dependency_data.items():
                if value.get('error'):
                    styled_key = click.style(TASK_CLASS_MAPPING[key], fg='red')
                    error = value.get('error')
                    for line in error.splitlines():
                        click.echo(f'[{styled_key}] {line}')
                else:
                    styled_key = click.style(TASK_CLASS_MAPPING[key], fg='green')
                    message = value.get('message')
                    click.echo(f'[{styled_key}] {message} ... ')

    def get(self, is_global: Optional[bool] = False):
        self.spinner.start()
        sessions = []

        # Fetching team's sessions if asked
        if is_global:
            # TODO Refactor this when the we continue the work on SDK
            from grid.cli.core.team import Team
            try:
                teams = Team.get_all()
            except Exception as e:
                teams = []
                self.spinner.fail("✘")
                if env.DEBUG:
                    click.echo(e)

            for team in teams:
                try:
                    team_sessions = get_sessions(self.client, team)
                    sessions.append(team_sessions)
                except ResourceNotFound:
                    # No sessions found
                    pass
                except Exception as e:
                    self.spinner.fail("✘")
                    if env.DEBUG:
                        click.echo(e)
        else:
            # Fetching user session
            try:
                user_session = get_sessions(self.client)
            except ResourceNotFound:
                # No sessions found
                pass
            except Exception as e:
                self.spinner.fail("✘")
                if env.DEBUG:
                    click.echo(e)
            else:
                sessions.append(user_session)

        # Create table with results.
        table_rows = 0
        if is_global:
            table_cols = ['Session', 'Status', 'Created By', 'Instance Type', 'Duration', 'URL']
        else:
            table_cols = ['Session', 'Status', 'Instance Type', 'Duration', 'URL']
        table = BaseObservable.create_table(columns=table_cols)

        for result in sessions:
            for row in result['getInteractiveNodes']:
                url = row['jupyterUrl']

                # Calculate how long the interactive node has been up.
                created_at = date_string_parse(row['createdAt'])
                delta = get_abs_time_difference(datetime.now(timezone.utc), created_at)
                duration_str = string_format_timedelta(delta)

                # Add rows to table. Accounts for a series of transition
                # states.
                if row['status'] == 'finished':
                    status = 'ready'
                elif row['status'] == 'paused' and row['desiredState'] == 'RUNNING':
                    status = 'resuming'
                elif row['status'] != 'paused' and row['desiredState'] == 'PAUSED':
                    status = 'pausing'
                elif row['status'] != 'deleted' and row['desiredState'] == 'DELETED':
                    status = 'deleting'
                else:
                    status = row['status']

                # Replace anything that doesn't have data with
                # a placeholder '-'.
                if is_global:
                    username = row['userDetails']['username'] if row['userDetails'] else None
                    all_rows = [
                        row['interactiveNodeName'], status, username, row['config']['instanceType'], duration_str, url
                    ]
                else:
                    all_rows = [row['interactiveNodeName'], status, row['config']['instanceType'], duration_str, url]
                all_rows = ['-' if not r else r for r in all_rows]
                table.add_row(*all_rows)

                # Adds iterator
                table_rows += 1

        #  Close the spinner.
        self.spinner.stop()

        # If there are no nodes active, add a
        # placeholder row indicating that.
        if not table_rows:
            table.add_row("None Active.", *[" " for i in range(len(table_cols) - 1)])

        # Print table
        self.console.print(table)

    def follow(self, is_global: Optional[bool] = False):  # pragma: no cover
        pass
