import base64
from collections import defaultdict
from datetime import datetime
from inspect import signature
import json
from pathlib import Path
import shlex
from typing import Collection, Iterable, List, Mapping, Union
import warnings

import yaml

from grid.sdk import env
from grid.sdk._gql.queries import (
    cancel_run,
    estimate_run_cost_mutation,
    experiment_archived_build_logs,
    experiment_live_build_logs,
    get_runs,
)
from grid.sdk.action import (
    _check_run_name_is_valid,
    _generate_default_grid_config,
    _resolve_instance_type_nickname,
    _verify_entrypoint_script_is_valid,
    check_description_isnt_too_long,
    read_config,
    train,
    validate_and_configure_datastore,
)
from grid.sdk.experiments import Experiment
from grid.sdk.user import SDKUser, User
from grid.sdk.utils.name_generator import unique_name


class Run:
    _name: str
    _entrypoint: Union[str, Path]
    _script_args: str
    _description: str
    _strategy: str
    _num_trials: int  # if strategy == random
    _framework: str
    _dependency_file: Union[str, Path]
    _instance_type: str
    _use_spot: bool
    _cpus: int  # if < 1 use max on instance
    _gpus: int  # if < 1 and gpus are on machine, use max on machine
    _memory: int
    _datastore_name: str
    _datastore_version: str
    _datastore_mount_dir: str
    _scratch_size: str
    _scratch_mount_path: str
    _localdir: Union[str, Path]
    _dockerfile: Union[str, Path]
    _config_file: Union[str, Path]
    _cluster: str
    _run_id: str

    _user: SDKUser
    _config_dict: dict
    _experiments: Mapping[str, 'Experiment']
    _created_at: datetime
    _estimated_hourly_cost: Union[float, int]
    _script_command: str

    def __init__(
        self,
        name: str = '',
        entrypoint: Union[str, Path] = '',
        script_args: str = '',
        description: str = None,
        strategy: str = 'grid_search',
        num_trials: int = 0,  # if strategy == random
        framework: str = 'lightning',
        dependency_file: Union[str, Path] = '',
        instance_type: str = 't2.medium',
        use_spot: bool = False,
        cpus: int = 0,  # if < 1 use max on instance
        gpus: int = 0,  # if < 1 and gpus are on machine, use max on machine
        memory: str = '',
        datastore_name: str = '',
        datastore_version: str = '',
        datastore_mount_dir: str = '',
        scratch_size: str = '',
        scratch_mount_path: str = '/tmp/scratch',
        localdir: bool = False,
        dockerfile: Union[str, Path] = '',
        config_file: Union[str, Path] = '',
        cluster: str = '',
        run_id: str = '',  # TODO(rlizzo): don't alias python reserved name
    ):
        """A ``Run`` is a container for a set of computations executed over search space.

        This object can be instantiated with constructor args below in
        order to create/start a new set of computations (``Experiments``)
        which make up the ``Run``.

        Alternatively, an existig ``Run`` ``name`` can be passed in the
        constructor, and the SDK will load all the associated ``Run`` /
        ``Experiment`` details in this structure automatically.

        This class provides properties for access to run attributes
        which can be read at any time, or set before the ``Run``
        objects ``.start()`` method is called.

        Parameters
        ----------
        name
            name of the run. If loading a ``Run`` that already exists,
            this must be provided. If creating a new ``Run`` then setting
            this field is optional (a unique name will be assigned for you).
        entrypoint
            Path to the script which should actually be run.
        script_args
            The hyperparameter search arguments which are being used to
            run the ``entrypoint`` stript.
        description
            Optional human readable description of the ``Run``
        strategy
            one of ``"grid_search"`` or ``"random_search"``. Grid search executes
            all combinations of parameters in the search space, random search
            executes ``num_trials`` selected at random from the search space.
            Note: the ``num_trials`` argument must be set if using the
            ``"random_search"`` strategy.
        num_trials
            when using ``"random_search" strategy``, the number of experiments
            to execute within the possible search space.
        framework
            The machine learning framework to load. Must be one of ``["lightning",
            "pytorch", "tensorflow", "julia"]``. By default, ``"lightning"``
        dependency_file
            Path to a dependency file to use to install runtime requirements.
        instance_type
            name of the compute instance type to use when launching the instance
            computations
        use_spot
            If ``True``, inturuptable instance types will be used to launch the
            experiment computations. This trades the potential of longer
            times to completion for drastically reduced prices.
        cpus
            The number of CPUs to assign to each experiment. Grid reserves one
            CPU core on each node to run our managment layer, so this value
            must be ``<= num_cpus_per_node - 1``
        gpus
            The number of GPUs to assign to each experiment on a node. To optimize
            costs ensure the following is True: ``num_gpus_per_node % gpus = 0``
        memory
            DEPRECATED. Do not use
        datastore_name
            If attaching a datastore to the running experiments, the name of
            the datastore you wish to use.
        datastore_version
            If attaching a datastore to the running experiments, the version
            of the datastore which should be used.
        datastore_mount_dir
            If attaching a datastore to the running experiments, the file
            path where the datastore root path is located.
        scratch_size
            DEPRECATED. Do not use
        scratch_mount_path
            DEPRECATED. Do not use
        localdir
            if True, A non-github compatible source code directory is being
            used to execute this experiment.
        dockerfile
            If passed a path to a Dockerfile in the repository, use this
            Dockerfile to actually launch the experiments.
        config_file
            An optional path to a configuration file in the repo which can
            statically store most of the inputs provided in these arguments.
        cluster
            For bring your own cluster users, the name of the cluster which
            you would like to use to run this experiment
        run_id
            INTERNAL ONLY. Do not use.
        """
        # this is always the currently logged in user account. if this is a run
        # that already exists, then the "user" property of the Run will be overwritten
        # to the user who actual created the run. We use the logged in user to prevent
        # further queries being made from users who may be on our do-not-allow list.
        self._user = SDKUser.from_logged_in_user()
        if self._user.is_blocked:
            raise PermissionError("Your user account has been blocked. Please contact support@grid.ai")

        self._created_at = None
        self._config_dict = None
        self._experiments = None
        self._extimated_hourly_cots = None

        # we use entrypoint argument to determine if this is a new run or now.
        if entrypoint == '':
            # If this is a run that already exists
            if name == '':
                raise ValueError("Must pass a ``name`` argument when accessing an existing run")

            data = get_runs(run_name=name)
            if len(data) != 1:
                raise ValueError(f'more than one run returned in: {data}')
            details = data[0]
            # transform data to config expected in normal user yaml
            # (ie. deserialize JSON & convert camelCase to snake_case)
            details['config']['compute'] = json.loads(details['config']['compute'])
            details['config']['hyper_params'] = json.loads(details['config']['hyperParams'])
            del details['config']['hyperParams']

            # Set any attributes values if they would not be set
            # from arguments provided when starting a new run.

            self._user = User(
                user_id=details['userDetails']['id'],
                username=details['userDetails']['username'],
                first_name=details['userDetails']['firstName'],
                last_name=details['userDetails']['lastName'],
            )
            self._script_command = details['scriptCommand']
            self._created_at = datetime.fromisoformat(details['createdAt'])
            self._config_dict = details['config']
            self._estimated_hourly_cost = details['estimatedHourlyCost']

            exps = {}
            for exp_conf in details['experiments']:
                # noinspection PyProtectedMember
                exp = Experiment._init_via_gql_query(exp_id=exp_conf['experimentId'])
                exps[exp.name] = exp
            self._experiments = exps

            # details from non nested returns
            config_file = None
            entrypoint = details['entrypoint']
            script_args = details['scriptCommand']
            description = details['description']
            run_id = details['runId']

            # from provider sub-key.
            cluster = details['config']['compute']['provider'].get('cluster')

            # from config/hyper_params sub-key.
            strategy = details['config']['hyper_params']['settings']['strategy']
            num_trials = len(details['config']['hyper_params']['params']['n_experiments'])

            # from config/compute/train sub-key
            framework = details['config']['compute']['train'].get('framework')
            dependency_file = details['config']['compute']['train'].get('dependency_file_info', {}).get('path')
            instance_type = details['config']['compute']['train'].get('instance')
            use_spot = details['config']['compute']['train'].get('use_spot')
            cpus = details['config']['compute']['train'].get('cpus')
            gpus = details['config']['compute']['train'].get('gpus')
            memory = details['config']['compute']['train'].get('memory')
            datastore_name = details['config']['compute']['train'].get('datastore_name')
            datastore_version = details['config']['compute']['train'].get('datastore_version')
            datastore_mount_dir = details['config']['compute']['train'].get('datastore_mount_dir')
            localdir = details['config']['compute']['train'].get('localdir')
            dockerfile = details['config']['compute']['train'].get('dockerfile')

            _scratch = details['config']['compute']['train'].get('scratch', {})
            # default for missing scratch key sets the value to an empty list,
            # which does not have a ``get`` parameter. this is handled below.
            if isinstance(_scratch, dict):
                scratch_size = details['config']['compute']['train'].get('scratch', {}).get('size_gb')
                scratch_mount_path = details['config']['compute']['train'].get('scratch', {}).get('mount_path')
            else:
                scratch_size = ''
                scratch_mount_path = '/tmp/scratch'

        self._name = name
        self._entrypoint = entrypoint
        self._script_args = script_args
        self._description = check_description_isnt_too_long(description)
        self._strategy = strategy
        self._num_trials = num_trials
        self._framework = framework
        self._dependency_file = dependency_file
        self._instance_type = _resolve_instance_type_nickname(instance_type)
        self._use_spot = use_spot
        self._cpus = cpus
        self._gpus = gpus
        self._memory = memory
        self._datastore_name = datastore_name
        self._datastore_version = datastore_version
        self._datastore_mount_dir = datastore_mount_dir
        self._scratch_size = scratch_size
        self._scratch_mount_path = scratch_mount_path
        self._localdir = localdir
        self._dockerfile = dockerfile
        self._config_file = config_file
        self._cluster = cluster
        self._run_id = run_id

    # ------------------- User Provided Info -----------------------

    @property
    def name(self) -> str:
        """Name of the Run
        """
        return self._name

    @name.setter
    def name(self, value: str):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'name' after run has been started.")
        self._name = value

    @property
    def entrypoint(self) -> Union[str, Path]:
        """Path to the script which should actually be run.
        """
        return self._entrypoint

    @entrypoint.setter
    def entrypoint(self, value: Union[str, Path]):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'entrypoint' after run has been started.")
        self._entrypoint = value

    @property
    def script_args(self) -> str:
        """Set of entrypoint script arguments which set up the search space to compute over.
        """
        return self._script_args

    @script_args.setter
    def script_args(self, value: str):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'script_args' after run has been started.")
        self._script_args = value

    @property
    def description(self) -> str:
        """Human readable description of the Run's contents
        """
        return self._description

    @description.setter
    def description(self, value: str):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'description' after run has been started.")
        self._description = check_description_isnt_too_long(value)

    @property
    def strategy(self) -> str:
        """Hyperparameter search strategy. Must be one of ``['grid_search', 'random_search']``
        """
        return self._strategy

    @strategy.setter
    def strategy(self, value: str):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'strategy' after run has been started.")
        self._strategy = value

    @property
    def num_trials(self) -> int:
        """How many samples of full search space are used using the ``'random_search'`` strategy.
         """
        return self._num_trials

    @num_trials.setter
    def num_trials(self, value: int):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'trials' after run has been started.")
        self._num_trials = value

    @property
    def framework(self) -> str:
        """The ML framework used. One of ``["lightning", "pytorch", "tensorflow", "julia"]``.
        """
        return self._framework

    @framework.setter
    def framework(self, value: str):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'framework' after run has been started.")
        self._framework = value

    @property
    def dependency_file(self) -> Union[str, Path]:
        """Path to a dependency file to use to install runtime requirements.
        """
        return self._dependency_file

    @dependency_file.setter
    def dependency_file(self, value: Union[str, Path]):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'dependency_file' after run has been started.")
        self._dependency_file = value

    @property
    def instance_type(self) -> str:
        return self._instance_type

    @instance_type.setter
    def instance_type(self, value: str):
        """name of the compute instance type to use when launching the instance computations.
        """
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'instance_type' after run has been started.")
        self._instance_type = _resolve_instance_type_nickname(value)

    @property
    def use_spot(self) -> bool:
        """If ``True``, inturuptable instance types will be used to launch the experiment computations.
        """
        return self._use_spot

    @use_spot.setter
    def use_spot(self, value: bool):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'use_spot' after run has been started.")
        self._use_spot = value

    @property
    def cpus(self) -> int:
        """The number of CPUs to assign to each experiment
        """
        return self._cpus

    @cpus.setter
    def cpus(self, value: int):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'cpus' after run has been started.")
        self._cpus = value

    @property
    def gpus(self) -> int:
        """The number of GPUs to assign to each experiment on a node
        """
        return self._gpus

    @gpus.setter
    def gpus(self, value: int):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'gpus' after run has been started.")
        self._gpus = value

    @property
    def memory(self) -> str:
        """DEPRECATED. Do not use
        """
        return self._memory

    @memory.setter
    def memory(self, value: str):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'memory' after run has been started.")
        self._memory = value

    @property
    def datastore_name(self) -> str:
        """If attaching a datastore to the running experiments, the name of the datastore you wish to use.
        """
        return self._datastore_name

    @datastore_name.setter
    def datastore_name(self, value: str):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'datastore_name' after run has been started.")
        self._datastore_name = value

    @property
    def datastore_version(self) -> str:
        """If attaching a datastore to the running experiments, the version of the datastore which should be used.
        """
        return self._datastore_version

    @datastore_version.setter
    def datastore_version(self, value: str):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'datastore_version' after run has been started.")
        self._datastore_version = value

    @property
    def datastore_mount_dir(self) -> str:
        """If attaching a datastore to the running experiments, the file path where the datastore root path is located.
        """
        return self._datastore_mount_dir

    @datastore_mount_dir.setter
    def datastore_mount_dir(self, value: str):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'datastore_mount_dir' after run has been started.")
        self._datastore_mount_dir = value

    @property
    def scratch_size(self) -> str:
        """DEPRECATED. Do not use
        """
        return self._scratch_size

    @scratch_size.setter
    def scratch_size(self, value: str):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'scratch_size' after run has been started.")
        self._scratch_size = value

    @property
    def scratch_mount_path(self) -> str:
        """DEPRECATED. Do not use
        """
        return self._scratch_mount_path

    @scratch_mount_path.setter
    def scratch_mount_path(self, value: str):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'scratch_mount_path' after run has been started.")
        self._scratch_mount_path = value

    @property
    def localdir(self) -> bool:
        """if True, A non-github compatible source code directory is being used to execute this experiment.
        """
        return self._localdir

    @localdir.setter
    def localdir(self, value: bool):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'localdir' after run has been started.")
        self._localdir = value

    @property
    def dockerfile(self) -> Union[str, Path]:
        """If passed a path to a Dockerfile in the repository, use this Dockerfile to actually launch the experiments.
        """
        return self._dockerfile

    @dockerfile.setter
    def dockerfile(self, value: Union[str, Path]):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'dockerfile' after run has been started.")
        self._dockerfile = value

    @property
    def config_file(self) -> Union[str, Path]:
        """Path to a config file which can set most of the Run options.
        """
        return self._config_file

    @config_file.setter
    def config_file(self, value: Union[str, Path]):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'config_file' after run has been started.")
        self._config_file = value

    @property
    def cluster(self) -> str:
        """Name of the cluster the computations execute on.
        """
        return self._cluster

    @cluster.setter
    def cluster(self, value: str):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'cluster' after run has been started.")
        self._cluster = value

    @property
    def run_id(self) -> str:
        """Id of the run.
        """
        return self._run_id

    @run_id.setter
    def run_id(self, value: str):
        if self._created_at is not None:
            raise PermissionError(f"cannot alter attribute 'id' after run has been started.")
        self._run_id = value

    # ------------ Auto Generated Information --------------------

    @property
    def experiments(self) -> Mapping[str, 'Experiment']:
        """A mapping view of experiment names -> experiment interaction objects.
        """
        if self._created_at is None:
            warnings.warn("No run has been started yet, no experiments to show.")
        return self._experiments

    @property
    def user(self) -> User:
        """An object containing details about the user who created this ``Run``
        """
        return self._user

    @property
    def grid_config(self) -> dict:
        """The grid config of the run (either auto generated or specified explicitly).

        Returns
        -------
        dict
            nested dictionary corresponding to the grid YAML nesting structure

        See Also
        --------
        - Grid yaml config specification:
          https://docs.grid.ai/products/run-run-and-sweep-github-files/yaml-configs/yaml-api
        """
        if self._created_at is None:
            warnings.warn("No run has been started yet, no parsed config dict to show.")
        return self._config_dict

    @property
    def estimated_hourly_cost(self) -> Union[int, float]:
        """Estimated hourly cost of the run.

        Returns
        -------
        Union[int, float]
            Value corresponding to (estimated) cost / hr in US Dollars.
        """
        if hasattr(self, '_estimated_hourly_cost') and (self._estimated_hourly_cost != 0):
            return self._estimated_hourly_cost
        else:
            if self._config_file:
                #  Adds required structure to the base YML file, if that structure isn't there.
                config_dict = read_config(self._config_file)
            else:
                config_dict = {}

            if self._strategy not in ['grid_search', 'random_search']:
                raise ValueError(f"strategy {self._strategy} is not valid.")

            if self._framework not in ['lightning', 'torch', 'tensorflow', 'julia', 'torchelastic']:
                raise ValueError(self._framework)

            _verify_entrypoint_script_is_valid(Path(self._entrypoint))
            script_arguments = shlex.split(self._script_args)

            #  If the user has not passed a grid config file, then generate one with a set of
            #  default options. We'll add a default instance and the user's default credentials.
            if not config_dict:
                _grid_config = _generate_default_grid_config(
                    instance_type=self._instance_type,
                    cluster=self._cluster,
                    use_spot=self._use_spot,
                    grid_strategy=self._strategy,
                    grid_trials=self._num_trials,
                    gpus=self._gpus,
                    memory=self._memory,
                    cpus=self._cpus,
                    datastore_name=self._datastore_name,
                    datastore_version=self._datastore_version,
                    datastore_mount_dir=self._datastore_mount_dir,
                    framework=self._framework,
                    localdir=self._localdir,
                    dockerfile=self._dockerfile,
                    scratch_size=self._scratch_size,
                    scratch_mount_path=self._scratch_mount_path,
                    dependency_file=self._dependency_file
                )
            else:
                _grid_config = config_dict
                _grid_config['compute'].setdefault('train', {})
                _grid_config['compute']['train'].setdefault('localdir', self._localdir)
                _grid_config['compute']['train'].setdefault('dockerfile', self._dockerfile)

            _new_config = validate_and_configure_datastore(grid_config=_grid_config)
            if _new_config is not None:
                _grid_config = _new_config

            # Warn user if they have not specified a cpu or gpu number so cpus will be set to 1
            cpus = _grid_config['compute']['train'].get('cpus')
            gpus = _grid_config['compute']['train'].get('gpus')
            if not cpus and not gpus:
                _grid_config['compute']['train']['cpus'] = 1

            # TODO(rlizzo): Why does this method fail if these two keys are present?
            del _grid_config['compute']['train']['memory']
            del _grid_config['compute']['provider']['cluster']

            encoded_config = base64.b64encode(yaml.dump(_grid_config).encode('ascii')).decode('ascii')
            res = estimate_run_cost_mutation(
                script_args=script_arguments, entrypoint=self._entrypoint, config_encoded=encoded_config
            )
            return res['estimatedHourlyCost']

    @property
    def script_command(self) -> str:
        """Set of entrypoint script arguments which set up the search space to compute over.
        """
        if self._created_at is None:
            warnings.warn("No run has been started yet, no script_command to show.")

        return self._script_command

    @property
    def created_at(self) -> datetime:
        """Datetime inidicating the timestamp at which the experiments in a Run were submitted for execute.
        """
        if self._created_at is None:
            warnings.warn("No run has been started yet, created_at time has not been set.")
        return self._created_at

    def start(self):
        """Start performing the computations described by the configuration of this ``Run`` object.
        """
        if self._created_at is not None:
            raise PermissionError(f"cannot start a run which already exits.")

        _invocation_args = {}
        sig = signature(self.__init__)
        for p_name, param in sig.parameters.items():
            if p_name == ['entrypoint', 'script_args']:
                continue
            if getattr(self, p_name) != param.default:
                _invocation_args[p_name] = getattr(self, p_name)

        if self._config_file:
            #  Adds required structure to the base YML file, if that structure isn't there.
            config_dict = read_config(self._config_file)
        else:
            config_dict = {}

        if self._name:
            name = _check_run_name_is_valid(self._name)
        else:
            name = unique_name()

        if self._strategy not in ['grid_search', 'random_search']:
            raise ValueError(f"strategy {self._strategy} is not valid.")

        check_description_isnt_too_long(self._description)
        self._instance_type = _resolve_instance_type_nickname(self._instance_type)

        if self._framework not in ['lightning', 'torch', 'tensorflow', 'julia', 'torchelastic']:
            raise ValueError(self._framework)

        _verify_entrypoint_script_is_valid(Path(self._entrypoint))
        script_arguments = shlex.split(self._script_args)

        shlex_g_args = ' '.join([
            shlex.quote(f'--{k}') + ' ' + shlex.quote(f'{v}') for k, v in _invocation_args.items()
        ])
        shlex_entrypoint = shlex.quote(f'{self._entrypoint}')
        shlex_script_args = ' '.join([shlex.quote(x) for x in shlex.split(self._script_args)])
        invocation_command = shlex.quote(f'grid run {shlex_g_args} {shlex_entrypoint} {shlex_script_args}')

        # make a fun random name when user does not pass in a name
        name = unique_name() if name is None else name

        #  If the user has not passed a grid config file, then generate one with a set of
        #  default options. We'll add a default instance and the user's default credentials.
        if not config_dict:
            _grid_config = _generate_default_grid_config(
                instance_type=self._instance_type,
                cluster=self._cluster,
                use_spot=self._use_spot,
                grid_strategy=self._strategy,
                grid_trials=self._num_trials,
                gpus=self._gpus,
                memory=self._memory,
                cpus=self._cpus,
                datastore_name=self._datastore_name,
                datastore_version=self._datastore_version,
                datastore_mount_dir=self._datastore_mount_dir,
                framework=self._framework,
                localdir=self._localdir,
                dockerfile=self._dockerfile,
                scratch_size=self._scratch_size,
                scratch_mount_path=self._scratch_mount_path,
                dependency_file=self._dependency_file
            )

        else:
            _grid_config = config_dict
            _grid_config['compute'].setdefault('train', {})
            _grid_config['compute']['train'].setdefault('localdir', self._localdir)
            _grid_config['compute']['train'].setdefault('dockerfile', self._dockerfile)

        validate_and_configure_datastore(grid_config=_grid_config)

        # Warn user if they have not specified a cpu or gpu number so cpus will be set to 1
        cpus = _grid_config['compute']['train'].get('cpus')
        gpus = _grid_config['compute']['train'].get('gpus')
        if not cpus and not gpus:
            _grid_config['compute']['train']['cpus'] = 1

        #  Send to client.
        run_name = train(
            config=_grid_config,
            run_name=name,
            run_description=self._description,
            entrypoint=self._entrypoint,
            script_args=script_arguments,
            invocation_command=invocation_command,
            localdir=self._localdir,
            dependency_file=self._dependency_file
        )

        # set properties after run config from server is successfully returned
        self._config_dict = _grid_config
        self._name = run_name

        self._setup_from_name()

    def _setup_from_name(self):
        if self._created_at is not None:
            raise PermissionError(f"cannot start a run which already exits.")

        data = get_runs(run_name=self._name)
        if len(data) != 1:
            raise ValueError(f'more than one run returned in: {data}')
        data = data[0]

        exps = {}
        for exp_conf in data['experiments']:
            # noinspection PyProtectedMember
            exp = Experiment._init_via_gql_query(exp_id=exp_conf['experimentId'])
            exps[exp.name] = exp

        self._run_id = data['runId']
        self._cluster = data['clusterId']
        self._user = User(
            user_id=data['userDetails']['id'],
            username=data['userDetails']['username'],
            first_name=data['userDetails']['firstName'],
            last_name=data['userDetails']['lastName'],
        )
        self._script_command = data['scriptCommand']
        self._config_dict = data['config']
        self._experiments = exps
        self._description = data['description']
        self._created_at = datetime.fromisoformat(data['createdAt'])
        self._estimated_hourly_cost = data['estimatedHourlyCost']

    def __repr__(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                status = self.status()
            except RuntimeError:
                status = {}
            try:
                script_command = self.script_command
            except AttributeError:
                script_command = ''
            experiments = self.experiments
            if experiments is None:
                experiments = {}

        return (
            f"{self.__class__.__name__}(\n"
            f"    name={self._name},\n"
            f"    description=\"{self._description}\",\n"
            f"    script_command={script_command},\n"
            f"    num_experiments={len(experiments)},\n"
            f"    status={ {k: len(v) for k, v in status.items()} },\n"
            f"    user={self.user.username},\n"
            f"    created_at={self._created_at},\n"
            f"    cluster={self._cluster},\n"
            f")"
        )

    def __contains__(self, item: str) -> bool:
        """Check if an experiment with the provided name exists in the Run.

        Returns
        -------
        bool
            True if the experiment exists, otherwise False.
        """
        return item in self._experiments

    def __len__(self) -> int:
        """Check how many experiments are recorded in the Run.

        Returns
        -------
        int
            Number of experiments recorded in the Run.
        """
        return len(self._experiments)

    def __iter__(self) -> Iterable['Experiment']:
        """Allows for iteration over the run, yielding every Experiment object recorded.
        """
        for exp in self._experiments.values():
            yield exp

    def status(self) -> Mapping[str, Collection[str]]:
        """Requests the status for all Experiments in the run from the grid platform.

        Returns
        -------
        Mapping[str, Collection[str]]
            Mapping of statuses ("QUEUED", "RUNNING", "FAILED", "CANCELLED",
            "COMPLETED") to collection of experiment names which are in
            that particular state.

        TODO(rlizzo): Batch status update to reduce amount of API calls.
        """
        if self._created_at is None:
            raise RuntimeError(f"cannot get status of a run which is has not been started.")

        states = defaultdict(list)
        for exp_name, exp in self.experiments.items():
            status = exp.status()
            states[status.upper()].append(exp_name)
        return states

    def cancel(self) -> List[str]:
        """Requests the grid platform cancels every Experiment in the Run.

        Returns
        -------
        List[str]
            a collection of experiment names if each experiment was successfully
            cancelled or had previously reached a terminal status ("CANCELLED",
            "FAILED", "COMPLETED").
        """
        if self._created_at is None:
            raise RuntimeError(f"cannot a run which has not been started.")

        cancel_run(run_name=self._name)
        return list(self._experiments.keys())

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
        if self._created_at is None:
            raise RuntimeError(f"cannot get build logs from a run which has not been started.")

        any_exp_id = next(iter(self.experiments.values())).id

        statuses = self.status()
        if any([statuses[s] for s in env.STARTED_STATES]):
            logs = experiment_archived_build_logs(exp_id=any_exp_id)
        else:
            logs = experiment_live_build_logs(exp_id=any_exp_id, limit=n_lines)

        for log in logs:
            ts = datetime.fromisoformat(log['timestamp'])
            yield f"[{ts}] [{log['message'].rstrip()}]\n"
