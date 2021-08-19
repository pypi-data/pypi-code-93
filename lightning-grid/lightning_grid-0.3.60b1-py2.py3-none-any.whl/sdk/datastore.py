from datetime import datetime
import os
from pathlib import Path
import time
from typing import List, Optional, Union
from urllib.parse import urlparse

import click

from grid.sdk._gql.queries import delete_datastore, get_available_datastores, get_user_teams
from grid.sdk.team import Team
from grid.sdk.user import SDKUser, User
from grid.sdk.utils.datastore_uploader import create_datastore_session

DATASTORE_TERMINAL_STATES = ['FAILED', 'SUCCEEDED']


def fail_if_deleted(func):
    """Decorator which raises an exception at access time if the datastore has been deleted.
    """
    def wrapper(self, *args, **kwargs):
        if not self._alive:
            raise RuntimeError('Cannot perform operation on deleted datastore') from None
        return func(self, *args, **kwargs)

    return wrapper


def fail_if_datastore_currently_exists(func):
    """Decorator which raises an exception at access time if the datastore has been uploaded to Grid.
    """
    def wrapper(self, *args, **kwargs):
        if self._currently_exists:
            raise RuntimeError('Property only can be accessed before the datastore is uploaded to Grid.') from None
        return func(self, *args, **kwargs)

    return wrapper


def fail_if_datastore_does_not_exist(func):
    """Decorator which raises an exception at access time if the datastore has not been uploaded to Grid.
    """
    def wrapper(self, *args, **kwargs):
        if not self._currently_exists:
            raise RuntimeError('Property only can be accessed before the datastore is uploaded to Grid.') from None
        return func(self, *args, **kwargs)

    return wrapper


def list_all_available_datastores(include_teams: bool = False) -> List['DataStore']:

    datastores = []
    user_dstores_data = get_available_datastores()
    for dstore_data in user_dstores_data:
        user = User(
            username=dstore_data['userDetails']['username'],
            user_id=dstore_data['userDetails']['id'],
            first_name=dstore_data['userDetails']['firstName'],
            last_name=dstore_data['userDetails']['lastName'],
        )
        dstore = Datastore._from_existing(
            name=dstore_data['name'],
            version=int(dstore_data['version']),
            owner=user,
            team=None,
            size=dstore_data['size'],
            created_at=datetime.fromisoformat(dstore_data['createdAt']),
            snapshot_status=dstore_data['snapshotStatus'],
            datastore_id=dstore_data['id'],
            cluster_id=dstore_data['clusterId'],
        )
        datastores.append(dstore)

    # If ``include_teams`` is set, add datastores registered to the team.

    teams = []
    if include_teams is True:
        teams_data = get_user_teams()
        for team_data in teams_data:
            members = {}
            for member_data in team_data['members']:
                user = User(
                    username=member_data['username'],
                    user_id=member_data['id'],
                    first_name=member_data['firstName'],
                    last_name=member_data['lastName'],
                )
                members[user.username] = user

            team = Team(
                team_id=team_data['id'],
                name=team_data['name'],
                created_at=team_data['createdAt'],
                role=team_data['role'],
                members=members,
            )
            teams.append(team)

    for team in teams:
        team_dstores_data = get_available_datastores(team_id=team.team_id)
        for dstore_data in team_dstores_data:
            user = User(
                user_id=dstore_data['userDetails']['id'],
                username=dstore_data['userDetails']['username'],
                first_name=dstore_data['userDetails']['firstName'],
                last_name=dstore_data['userDetails']['lastName']
            )

            dstore = Datastore._from_existing(
                name=dstore_data['name'],
                version=int(dstore_data['version']),
                owner=user,
                team=team,
                size=dstore_data['size'],
                created_at=datetime.fromisoformat(dstore_data['createdAt']),
                snapshot_status=dstore_data['snapshotStatus'],
                datastore_id=dstore_data['id'],
                cluster_id=dstore_data['clusterId'],
            )
            datastores.append(dstore)

    return datastores


class Datastore:
    _name: str
    _datastore_id: str
    _version: int
    _source: Optional[Union[str, Path]] = None
    _compression: bool
    _snapshot_status: str
    _created_at: datetime
    _owner: User
    _team: Optional[Team]
    _cluster_id: str
    _size: str

    _alive: bool = True
    _currently_exists: bool = False

    def __init__(
        self,
        name: Optional[str] = None,
        source: Optional[os.PathLike] = None,
        version: int = 1,
        compression: Optional[bool] = None,
        owner: Optional[str] = None,
        team: Optional[str] = None,
        cluster_id: Optional[str] = None,
    ):
        """Initialize a new DataStore Object.

        If a DataStore with the given name, version, team and cluster already exists,
        then the object returned will be able to interact with the existing DataStore.

        Alternatively, if the DataStore is going to be created for the first time, then
        the ``source`` and ``compression`` parameters can be used to specify the location
        of the DataStore on disk (or at a remote location). and to optionally compress the
        data before uploading.

        After initializing the datastore object, the data itself can be uploaded by calling
        the ``upload()`` method.

        Parameters
        ----------
        name
            The name of the DataStore.
        version
            The version of the DataStore.
        source
            The location of the DataStore on disk or at a remote location.
        compression
            True if the DataStore should be compressed before uploading. Otherwise False.
        owner
            The username of the owner of the DataStore.
        team
            The name of the team that owns the DataStore.
        cluster_id
            The name of the cluster that the DataStore should be uploaded to.
        """
        if self._currently_exists is True:
            return

        if owner is None:
            _sdk_user = SDKUser.from_logged_in_user()
            owner = User(
                user_id=_sdk_user.user_id,
                username=_sdk_user.username,
                first_name=_sdk_user.first_name,
                last_name=_sdk_user.last_name
            )

        if name is None:
            name = parse_name_from_source(source)

        self._name = name
        self._version = version
        self._source = source
        self._compression = compression
        self._owner = owner
        self._team = team
        self._cluster_id = cluster_id

        self._datastore_id = None
        self._snapshot_status = None
        self._created_at = None
        self._size = None

        for datastore in list_all_available_datastores(True):
            if datastore == self:
                self._name = datastore.name
                self._datastore_id = datastore.datastore_id
                self._version = datastore._version
                self._source = datastore._source
                self._compression = datastore.compression
                self._snapshot_status = datastore.snapshot_status
                self._created_at = datastore.created_at
                self._owner = datastore.owner
                self._team = datastore.team
                self._cluster_id = datastore.cluster_id
                self._size = datastore.size

                self._alive = True
                self._currently_exists = True

    @classmethod
    def _from_existing(
        cls,
        name: str,
        version: int,
        owner: User,
        size: str,
        created_at: datetime,
        snapshot_status: str,
        datastore_id: str,
        cluster_id: str,
        team: Optional[Team] = None,
    ):
        cls._currently_exists = True
        try:
            dstore = cls()
        finally:
            # need to reset value so that other instances can be created in the future.
            cls._currently_exists = False

        dstore._name = name
        dstore._version = version
        dstore._datastore_id = datastore_id
        dstore._size = size
        dstore._created_at = created_at
        dstore._snapshot_status = snapshot_status
        dstore._owner = owner
        dstore._team = team
        dstore._cluster_id = cluster_id

        dstore._source = None
        dstore._compression = None

        dstore._currently_exists = True

        return dstore

    # ------------------ Attributes Only Valid Before Upload ---------------

    @property
    @fail_if_deleted
    def source(self) -> Union[str, Path]:
        return self._source

    @property
    @fail_if_deleted
    def compression(self) -> bool:
        return self._compression

    # ------------------ Attributes Fully Active After Upload ---------------

    @property
    @fail_if_deleted
    def name(self) -> str:
        return self._name

    @property
    @fail_if_deleted
    def version(self) -> int:
        return self._version

    @property
    @fail_if_deleted
    def owner(self) -> User:
        return self._owner

    @property
    @fail_if_deleted
    def team(self) -> Team:
        return self._team

    @property
    @fail_if_deleted
    def created_at(self) -> datetime:
        return self._created_at

    @property
    @fail_if_deleted
    def size(self) -> str:
        return self._size

    @property
    @fail_if_deleted
    def snapshot_status(self) -> str:
        if (self._snapshot_status and
            (self._snapshot_status.upper() not in DATASTORE_TERMINAL_STATES)) or ((self._snapshot_status is None) and
                                                                                  (self._currently_exists is True)):
            self._update_status()
        return self._snapshot_status

    @property
    @fail_if_deleted
    def cluster_id(self) -> str:
        return self._cluster_id

    @property
    @fail_if_deleted
    def datastore_id(self) -> str:
        return self._datastore_id

    # -------------- Dunder Methods ----------------------

    @fail_if_deleted
    def __repr__(self):
        if self._currently_exists:
            res = (
                f"{self.__class__.__name__}(\n"
                f"  name={self.name}, \n"
                f"  version={self.version}, \n"
                f"  size={self.size}, \n"
                f"  created_at={self.created_at}, \n"
                f"  owner={self.owner}, \n"
                f"  team={self.team}, \n"
                f"  cluster_id={self.cluster_id}, \n"
                f"  datastore_id={self.datastore_id}\n"
                f"  )"
            )
        else:
            res = (
                f"{self.__class__.__name__}(\n"
                f"  name={self.name}, \n"
                f"  version={self.version}, \n"
                f"  source={self.source}, \n"
                f"  compression={self.compression} \n"
                f"  owner={self.owner}, \n"
                f"  team={self.team}, \n"
                f"  cluster_id={self.cluster_id}, \n"
                f")"
            )

        return res

    @fail_if_deleted
    def __str__(self):
        return repr(self)

    @fail_if_deleted
    def __eq__(self, other: 'Datastore'):
        # need to handle case where attributes of a DataStore are not `User` or `Team`
        # classes. This is the case before the datastore is uploaded.
        self_team = self._team.team_id if hasattr(self._team, 'team_id') else self._team
        other_team = other._team.team_id if hasattr(other._team, 'team_id') else self._team

        self_owner = self._owner.user_id if hasattr(self._owner, 'user_id') else self._owner
        other_owner = other._owner.user_id if hasattr(other._owner, 'user_id') else other.owner

        return (
            self.__class__.__qualname__ == other.__class__.__qualname__ and self._name == other._name
            and self._version == other._version and self_owner == other_owner and self_team == other_team
        )

    @fail_if_deleted
    def __hash__(self):
        return hash((
            self._name, self._datastore_id, self._version, self._size, self._created_at, self._snapshot_status,
            self._owner, self._team, self._source, self._compression, self._cluster_id, self._alive,
            self._currently_exists
        ))

    # ---------------------  Internal Methods ----------------------

    @fail_if_deleted
    def _update_status(self):
        """Refreshes the``snapshot_status`` attribute by querying the Grid API.
        """
        tid = None if self._team is None else self.team.team_id
        all_dstore_data = get_available_datastores(team_id=tid)

        for dstore_data in all_dstore_data:
            if dstore_data['id'] == self._datastore_id:
                self._snapshot_status = dstore_data['snapshotStatus'] or "unknown"

    # -------------------  Public Facing Methods ----------------------

    @fail_if_deleted
    @fail_if_datastore_does_not_exist
    def delete(self):
        """Deletes the datastore from the grid system
        """
        delete_datastore(name=self.name, version=self.version, cluster=self.cluster_id)
        self._alive = False

    @fail_if_deleted
    @fail_if_datastore_currently_exists
    def upload(self):
        session = create_datastore_session(
            name=self.name,
            source=self.source,
            compression=self.compression,
            cluster=self.cluster_id,
        )
        session.upload()

        # Since we can't query just a single datastore by it's ID (THIS IS INSANE!)
        # we just grab the entire world of datastores and check to see which one
        # has the same attributes as this (as determined by this classes __eq__ method)

        time.sleep(1)  # give the backend time to process the new record.
        for datastore in list_all_available_datastores(include_teams=True):
            if datastore == self:
                self._name = datastore._name
                self._datastore_id = datastore._datastore_id
                self._version = datastore._version
                self._source = datastore._source
                self._compression = datastore._compression
                self._snapshot_status = datastore._snapshot_status
                self._created_at = datastore._created_at
                self._owner = datastore._owner
                self._team = datastore._team
                self._cluster_id = datastore._cluster_id
                self._size = datastore._size

                self._alive = True
                self._currently_exists = True


def parse_name_from_source(ctx, _, name: Optional[str] = None) -> str:
    """Parses datastore name from source if name isn't provided"""
    if name:
        return name

    source = ctx.params['source']
    try:
        parse_result = urlparse(source)
    except ValueError:
        raise click.ClickException("Invalid source for datastore, please input only a local filepath or valid url")

    path = Path(parse_result.path)
    base = path.name.split(".")[0]
    return base.lower().strip()
