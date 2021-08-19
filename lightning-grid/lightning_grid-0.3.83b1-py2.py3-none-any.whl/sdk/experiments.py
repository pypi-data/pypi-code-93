from datetime import datetime
from typing import Any, Dict, Iterable, NamedTuple, Optional

from grid.sdk import env
from grid.sdk._gql.queries import (
    cancel_experiment,
    experiment_archived_build_logs,
    experiment_archived_logs,
    experiment_live_build_logs,
    experiment_live_logs,
    get_experiment_details_gql,
    get_experiment_status_gql,
)
from grid.sdk.user import User


class ExperimentName(NamedTuple):
    name: str
    username: Optional[str]

    @classmethod
    def from_external_format(cls, name: str):
        """User can pass experiments as username:experiment_name to fetch other users experiments.
        """
        username = None
        split = name.split(":")
        if len(split) > 2:
            raise ValueError(f"Error while parsing {name}. Use the format <username>:<experiment-name>")
        elif len(split) == 2:
            username = split[0]
            name = split[1]

        return cls(name=name, username=username)


class Experiment:
    _name: str
    _exp_id: str
    _last_status: str
    _desired_state: str

    _created_at: datetime
    _started_running_at: datetime
    _finished_at: datetime

    _github_id: str
    _commit_sha: str
    _invocation_commands: str
    _parameters: Dict[str, Any]
    _user: User

    def __init__(
        self,
        name: str,
        exp_id: str,
        last_status: str,
        desired_state: str,
        created_at: datetime,
        started_running_at: datetime,
        finished_at: datetime,
        github_id: str,
        commit_sha: str,
        invocation_commands: str,
        parameters: Dict[str, Any],
        user: User,
    ):
        self._exp_id = exp_id
        self._name = name
        self._last_status = last_status
        self._desired_state = desired_state
        self._created_at = created_at
        self._started_running_at = started_running_at
        self._finished_at = finished_at
        self._github_id = github_id
        self._commit_sha = commit_sha
        self._invocation_commands = invocation_commands
        self._parameters = parameters
        self._user = user

    @classmethod
    def _init_via_gql_query(cls, exp_id: str):
        config = get_experiment_details_gql(experiment_id=exp_id)
        _parameters = {}
        for param in config['parameters']:
            name, value = param['name'], param['value']
            if name == value:
                # not a true parameter, just part of the setup.
                continue
            _parameters[name] = value

        return cls(
            exp_id=config['experimentId'],
            name=config['name'],
            user=User(
                user_id=config['userDetails']['id'],
                username=config['userDetails']['username'],
                first_name=config['userDetails']['firstName'],
                last_name=config['userDetails']['lastName'],
            ),
            last_status=config['status'].upper(),
            desired_state=config['desiredState'].upper(),
            github_id=config['githubId'],
            commit_sha=config['commitSha'],
            created_at=datetime.fromisoformat(config['createdAt']),
            started_running_at=datetime.fromisoformat(config['startedRunningAt']),
            finished_at=datetime.fromisoformat(config['finishedAt']),
            invocation_commands=config['invocationCommands'],
            parameters=_parameters
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(, \n"
            f"    name={self.name}, \n"
            f"    status={self.status()}, \n"
            f"    project={self.github_id} @ {self.commit_sha}, \n"
            f"    parameters={self.parameters}, \n"
            f"    invocation_command={self.invocation_commands}, \n"
            f"    user={self.user.username}, \n"
            f"    created_at={self.created_at}, \n"
            f"    started_running_at={self.started_running_at}, \n"
            f"    finished_at={self.finished_at}, \n"
            f")"
        )

    @property
    def id(self) -> str:
        """Id of the experiment
        """
        return self._exp_id

    @property
    def name(self) -> str:
        """The name of this experiment. Typically ``run-name + -expN``.
        """
        return self._name

    def _update_status(self):
        current = get_experiment_status_gql(experiment_id=self.id)
        self._last_status = current['status']
        self._desired_state = current['desiredState']
        self._created_at = datetime.fromisoformat(current['createdAt'])
        self._started_running_at = datetime.fromisoformat(current['startedRunningAt'])
        self._finished_at = datetime.fromisoformat(current['finishedAt'])

    def status(self) -> str:
        """Queries the grid platform to retrieve the current state of this experiment.

        Returns
        -------
        str
            one of "QUEUED", "RUNNING", "CANCELLED", "FAILED", "COMPLETED"
        """
        # perform query once and cache results
        if self._last_status not in env.TERMINAL_STATES:
            self._update_status()

        return self._last_status

    @property
    def created_at(self) -> datetime:
        """Datetime which the experiment was first scheduled to start.
        """
        return self._created_at

    @property
    def started_running_at(self) -> datetime:
        """Datetime when the experiment actually started running.
        """
        if self._last_status not in env.TERMINAL_STATES:
            self._update_status()
        return self._started_running_at

    @property
    def finished_at(self) -> datetime:
        """Datetime when the experiment finished running (either completed, failed, or cancelled).
        """
        if self._last_status not in env.TERMINAL_STATES:
            self._update_status()
        return self._finished_at

    @property
    def invocation_commands(self) -> str:
        """Command which was used to kick off the script's job.
        """
        return self._invocation_commands

    @property
    def parameters(self) -> dict:
        """Dict of hyperparameter names/values which this experiment used
        """
        return self._parameters

    @property
    def user(self) -> User:
        """User who launched this experiment.
        """
        return self._user

    @property
    def github_id(self) -> str:
        """Github project which the code in this experiment runs from.
        """
        return self._github_id

    @property
    def commit_sha(self) -> str:
        """Commit sha which of a git repo which the code runs from.
        """
        return self._commit_sha

    def cancel(self) -> str:
        """Request the grid platform cancels the experiment

        Returns
        -------
        str
            Name of the experiment if it was successfully cancelled or had
            previously reached a terminal status ("CANCELLED", "FAILED", "COMPLETED").
        """
        # do not perform POST if we know that we don't have to
        cancel_experiment(self._exp_id)
        if self._last_status not in env.TERMINAL_STATES:
            self._last_status = "CANCELLED"
        return self.name

    def build_logs(self, n_lines: int = 200) -> Iterable[str]:
        """Request the build logs for this experiment from the grid platform.

        Parameters
        ----------
        n_lines
            Max number of lines to return. By default, 200.

        Yields
        -------
        str
            every return is a single line of the build log output;
            sorted by order of time, oldest log is at index 0,
            latest log is at the end of the list.
        """
        status = self.status()
        if status == 'PENDING':
            return []
        elif status in env.TERMINAL_STATES:
            logs = experiment_archived_build_logs(exp_id=self.id)
        else:
            logs = experiment_live_build_logs(exp_id=self.id, limit=n_lines)

        for log in logs:
            ts = datetime.fromisoformat(log['timestamp'])
            yield f"[{ts}] [{log['message'].rstrip()}]\n"

    def logs(self, n_lines: int = 200) -> Iterable[str]:
        """Request the stdout logs for this experiment from the grid platform.

        Parameters
        ----------
        n_lines
            Max number of lines to return. By default, 200.

        Yields
        -------
        str
            every return is a single line of the build log output;
            sorted by order of time, oldest log is at index 0,
            latest log is at the end of the list.
        """
        status = self.status()
        if status == 'PENDING':
            return []
        elif status in env.TERMINAL_STATES:
            logs = experiment_archived_logs(exp_id=self.id)
        else:
            logs = experiment_live_logs(exp_id=self.id, n_lines=n_lines)

        for log in logs:
            ts = datetime.fromisoformat(log['timestamp'])
            yield f"[{ts}] [{log['message'].rstrip()}]\n"

    # def artifacts(self, p: Union[str, Path]) -> List[str]:
    #     """Download experiment artifacts to the specified directory path.
    #
    #     TODO(rlizzo): This entire workflow should allow for iterating over
    #                   the the available data files that can be downloaded.
    #                   Maybe make this a property and just return an metrics
    #                   object which implements methods of type
    #                   ``collections.abc.MappingView``.
    #
    #     Parameters
    #     ----------
    #     p
    #         Path to a directory in which to store the resulting artifacts.
    #         This path must exist on the host machine and must be writeable by
    #         the PID/user executing this program.
    #
    #     Returns
    #     -------
    #     List[str]
    #         Paths to files which have been written on disk.
    #     """
    #     raise NotImplementedError

    # def metrics(self):
    #     """Download metrics
    #
    #     TODO(rlizzo): This entire workflow should allow for iterating over the
    #                   available metrics. Maybe make this a property and just
    #                   return an metrics object which implements methods of type
    #                   ``collections.abc.MappingView``.
    #     """
    #     raise NotImplementedError
