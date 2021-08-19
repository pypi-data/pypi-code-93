#    Virtual-IPM is a software for simulating IPMs and other related devices.
#    Copyright (C) 2021  The IPMSim collaboration <https://ipmsim.gitlab.io/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module provides components that are responsible for recording/collecting the output of
a simulation run.
"""

from datetime import datetime
from collections import defaultdict

from anna import Bool, Integer, PhysicalQuantity, Filepath, String, Duplet, Choice, Vector, parametrize
import injector
import numpy as np
import pandas
import rx.subjects
import subprocess

import virtual_ipm.di as di
from virtual_ipm.components import Mutable


class OutputRecorder(Mutable):
    """
    Base class for components that are responsible for recording the output of a simulation.
    Output recorders serve as an information sink for particle data in a sense that they are
    responsible for extracting this information and propagating it to external resources.
    Output recorders are only responsible for collecting particle data. Other data or information
    from a simulation run should be obtained by different means (such as dedicated scripts that
    evaluate the corresponding methods of relevant models, to obtain beam field maps for example).

    Two kinds of information about particle data are considered:

      * Event-based information, such as initial and final parameters of particles which are
        identified by the corresponding status changes.
      * Continuous information which must be queried periodically. This is necessary for
        the generation of trajectories for example.

    For retrieving event-based information the :method:`~OutputRecorder.status_update` method
    should be overridden. The output recorder will be subscribed to the
    :method:`ParticleSupervisor.status_update` stream using this method. For the characteristics
    of a status update object which is passed to this method see :class:`ParticleSupervisor`.

    In order to collect continuous information the :method:`~OutputRecorder.record` method should
    be overridden. This method is invoked subsequent to each iteration of the simulation.
    Particle data can be queried through the particle supervisor instance during this method.

    Output recorders are used as context managers and therefore should implement the
    ``__enter__`` and ``__exit__`` methods appropriately in order to allocate and free
    external resources which serve as external information sinks.
    """

    CONFIG_PATH = 'Simulation/Output/Parameters'
    CONFIG_PATH_TO_IMPLEMENTATION = 'Simulation/Output/Recorder'

    def __init__(self, particle_supervisor, configuration=None):
        """
        Parameters
        ----------
        particle_supervisor : :class:`ParticleSupervisor`
        configuration : :class:`ConfigurationAdaptor` derived class 
        """
        super().__init__(configuration)
        self._particle_supervisor = particle_supervisor
        particle_supervisor.status_updates.subscribe(on_next=self.status_update)

    def __enter__(self):
        """
        Part of the output recorder's context manager interface. Should be overridden
        in order to allocate external resources.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Part of the output recorder's context manager interface. Should be overridden
        in order to free external resources.
        """
        pass

    def record(self, progress):
        """
        This method is invoked subsequent to each iteration of the simulation.
        It should be overridden in order to collect continuous data which must be queried
        periodically.

        Parameters
        ----------
        progress : :class:`Progress`
            The current simulation progress when this method is invoked.
        """
        pass

    def status_update(self, update):
        """
        This method is invoked whenever a particle's status has changed.
        It should be overridden in order to retrieve event-based information about particles.

        Parameters
        ----------
        update : ParticleSupervisor.StatusUpdate
        """
        pass

Interface = OutputRecorder


@parametrize(
    Filepath(
        'Filename'
    ),
    Bool(
        'SaveInitial',
        default=True,
        info='Save initial positions and momenta of particles.'
    ),
    Bool(
        'SaveFinal',
        default=True,
        info='Save final positions and momenta of particles.'
    ),
    Bool(
        'SaveMomentum',
        default=True,
        info='Save initial and final momenta of particles.'
    ),
    Bool(
        'SaveSimulationStep',
        default=True,
        info='Save initial and final simulation steps of particles.'
    ),
    Bool(
        'SaveId',
        default=True,
        info='Save the UUID of particles.'
    ),
    Bool(
        'SkipInvalidParticles',
        default=False,
        info='Do not save invalid particles.'
    ),
    Bool(
        'SkipTrackedParticles',
        default=True,
        info="Do not save particles which haven't finished tracking."
    )
)
class BasicRecorder(OutputRecorder):
    """
    Records initial and final data of particles. The amount of data to be saved can be configured.
    By default all invalid particles (those who reached the boundary for example) are saved while
    all tracked particles (those who haven't finished tracking) are skipped.
    """

    # Keys are internal to this program, the values are the actual column names in the generated
    # csv file and may therefore change. By introducing this separate dict we can ensure
    # consistency within the program while allowing the flexibility of changing column names that
    # will appear to external components. Those external components can refer to the column names
    # defined here when consuming a generated file.
    possible_column_names = {
        'uuid': 'uuid',
        'initial sim. step': 'initial sim. step',
        'initial x': 'initial x',
        'initial y': 'initial y',
        'initial z': 'initial z',
        'initial px': 'initial px',
        'initial py': 'initial py',
        'initial pz': 'initial pz',
        'final sim. step': 'final sim. step',
        'final x': 'final x',
        'final y': 'final y',
        'final z': 'final z',
        'final px': 'final px',
        'final py': 'final py',
        'final pz': 'final pz',
        'status': 'status',
    }

    possible_column_names_and_conditions = [
        (possible_column_names['uuid'], ('_save_id',)),
        (possible_column_names['initial sim. step'], ('_save_initial', '_save_simulation_step')),
        (possible_column_names['initial x'], ('_save_initial',)),
        (possible_column_names['initial y'], ('_save_initial',)),
        (possible_column_names['initial z'], ('_save_initial',)),
        (possible_column_names['initial px'], ('_save_initial', '_save_momentum')),
        (possible_column_names['initial py'], ('_save_initial', '_save_momentum')),
        (possible_column_names['initial pz'], ('_save_initial', '_save_momentum')),
        (possible_column_names['final sim. step'], ('_save_final', '_save_simulation_step')),
        (possible_column_names['final x'], ('_save_final',)),
        (possible_column_names['final y'], ('_save_final',)),
        (possible_column_names['final z'], ('_save_final',)),
        (possible_column_names['final px'], ('_save_final', '_save_momentum')),
        (possible_column_names['final py'], ('_save_final', '_save_momentum')),
        (possible_column_names['final pz'], ('_save_final', '_save_momentum')),
        (possible_column_names['status'], True),
    ]

    UNDETECTED_COUNT_MAX_LOG = 5

    @injector.inject(
        particle_supervisor=di.components.particle_supervisor,
        configuration=di.components.configuration
    )
    def __init__(self, particle_supervisor, configuration):
        super().__init__(
            particle_supervisor=particle_supervisor,
            configuration=configuration
        )
        self._initial_sim_steps = {}
        self._initial_positions = {}
        self._initial_momenta = {}
        self._final_sim_steps = {}
        self._final_positions = {}
        self._final_momenta = {}
        self._invalid_particles = set()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.log.info('Writing collected output ...')
        self.log.debug('%s', self)
        self._save_as_pandas(self._filename)
        self.log.info('... done.')

    def status_update(self, update):
        super().status_update(update)
        particle = update.particle
        progress = update.progress
        if particle.is_queued:
            self._initial_sim_steps[particle.uuid] = progress.step
            self._initial_positions[particle.uuid] = particle.position.copy()
            self._initial_momenta[particle.uuid] = particle.momentum.copy()
        elif particle.is_detected:
            self._final_sim_steps[particle.uuid] = progress.step
            self._final_positions[particle.uuid] = particle.position.copy()
            self._final_momenta[particle.uuid] = particle.momentum.copy()
        elif particle.is_invalid:
            self._final_sim_steps[particle.uuid] = progress.step
            self._final_positions[particle.uuid] = particle.position.copy()
            self._final_momenta[particle.uuid] = particle.momentum.copy()
            self._invalid_particles.add(particle.uuid)

    def _save_as_numpy(self, filename):
        np.savetxt(
            filename,
            self._generate_particle_data(),
            header=str('# ' + ', '.join(self._generate_header()))
        )

    def _save_as_pandas(self, filename):
        data_frame = self._generate_data_frame(
            self._generate_particle_data()
        )
        data_frame.to_csv(filename)

    def _generate_data_frame(self, data):
        if data.size == 0:
            return pandas.DataFrame(columns=self._generate_header())
        if self._save_id:
            return pandas.DataFrame(
                data=data,
                columns=self._generate_header()
            ).set_index('uuid')
        return pandas.DataFrame(
            data=data,
            columns=self._generate_header()
        )

    def _generate_header(self):
        return self._extract_data_per_column({
            col[0]: col[0] for col in self.possible_column_names_and_conditions
        })

    def _generate_particle_data(self):
        undetected_count = 0

        particle_uuids = set(self._initial_positions)
        if self._skip_invalid_particles:
            particle_uuids -= self._invalid_particles
        if self._skip_tracked_particles:
            particle_uuids -= set(filter(
                lambda x: (
                    self._particle_supervisor.get_particle_by_uuid(x).is_tracked or
                    self._particle_supervisor.get_particle_by_uuid(x).is_queued
                ),
                particle_uuids
            ))

        data = []
        for uuid in particle_uuids:
            particle = self._particle_supervisor.get_particle_by_uuid(uuid)
            if uuid not in self._final_positions:
                if undetected_count < self.UNDETECTED_COUNT_MAX_LOG:
                    self.log.warning(
                        'Encountered undetected particle: %s',
                        particle
                    )
                undetected_count += 1
                final_sim_step = -1
                final_position = particle.position.copy()
                final_momentum = particle.momentum.copy()
            else:
                final_sim_step = self._final_sim_steps[uuid]
                final_position = self._final_positions[uuid]
                final_momentum = self._final_momenta[uuid]

            data.append(
                self._extract_data_per_column({
                    'uuid':              uuid,
                    'initial sim. step': self._initial_sim_steps[uuid],
                    'initial x':         self._initial_positions[uuid][0],
                    'initial y':         self._initial_positions[uuid][1],
                    'initial z':         self._initial_positions[uuid][2],
                    'initial px':        self._initial_momenta[uuid][0],
                    'initial py':        self._initial_momenta[uuid][1],
                    'initial pz':        self._initial_momenta[uuid][2],
                    'final sim. step':   final_sim_step,
                    'final x':           final_position[0],
                    'final y':           final_position[1],
                    'final z':           final_position[2],
                    'final px':          final_momentum[0],
                    'final py':          final_momentum[1],
                    'final pz':          final_momentum[2],
                    'status':            particle.status_as_string
                })
            )

        if undetected_count >= self.UNDETECTED_COUNT_MAX_LOG:
            self.log.warning(
                'Encountered %d undetected particles',
                undetected_count
            )

        return np.array(data, dtype=str)

    def _extract_data_per_column(self, data):
        return list(map(
            lambda x: data[x],
            map(
                lambda x: x[0],
                filter(
                    lambda x: all(map(
                        lambda field_name: getattr(self, field_name),
                        x[1]
                    )) if isinstance(x[1], tuple) else bool(x[1]),
                    self.possible_column_names_and_conditions
                )
            )
        ))


@parametrize(
    Filepath(
        'Filename',
        info='A separate file is created for each particle. Use the substitution pattern '
             '"%(uuid)d" in order to specify where the UUID should appear within the filename. '
             'If no substitution pattern is found the uuid is appended instead.'
    ),
    Vector[Integer](
        'Particles',
        info='The UUIDs of particles which will be saved. During the simulation UUIDs start '
             'at 0 (the first generated particle) and are incremented by 1 for each additionally '
             'generated particle.'
    ),
    Bool(
        'SaveMomentum',
        default=True,
        info='Save the momentum of a particle along with its position for each time step.'
    ),
    Choice(
        String(
            'Format',
            default='pandas-csv'
        )
    ).add_option('numpy')
)
class TrajectoryRecorder(OutputRecorder):
    """
    Records trajectories of the specified particles.
    
    The trajectories are saved in csv files with the following format::
    
        ,step,x,y,z
        
    The column "step" denotes the simulation step at whose beginning the particle was at the
    specified position (specified on the same row).
    """

    @injector.inject(
        particle_supervisor=di.components.particle_supervisor,
        configuration=di.components.configuration
    )
    def __init__(self, particle_supervisor, configuration):
        super().__init__(
            particle_supervisor=particle_supervisor,
            configuration=configuration
        )
        self._trajectories = defaultdict(list)
        self._momenta = defaultdict(list)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.log.info('Writing collected output ...')
        self.log.debug('%s', self)
        for uuid in self._particles:
            self._save_particle_data(uuid)
        self.log.info('... done.')

    def record(self, progress):
        super().record(progress)
        for uuid in self._particles:
            particle = self._particle_supervisor.get_particle_by_uuid(uuid)
            if particle.is_tracked:
                # Save `step + 1` because this indicates the step at whose _beginning_ the particle
                # was at the given position. `record` is called at the _end_ of each step so we
                # need to add 1.
                self._trajectories[uuid].append(
                    [progress.step + 1] + particle.position.tolist()
                )
                if self._save_momentum:
                    self._momenta[uuid].append(particle.momentum.tolist())

    def status_update(self, update):
        super().status_update(update)
        # Need to capture the first value of the trajectory via `status_update` because
        # `record` is called after tracking.
        # The last value will be recorded during the previous step; the value at the end of a step
        # is the same as the value at the beginning of the next step. `record` is called at the
        # end of each step (so in a sense we always save the value of the next step's start).
        particle = update.particle
        progress = update.progress
        if particle.is_tracked:
            self._trajectories[particle.uuid].append(
                [progress.step] + particle.position.tolist()
            )
            if self._save_momentum:
                self._momenta[particle.uuid].append(particle.momentum.tolist())

    def _save_particle_data(self, uuid):
        if '%(uuid)d' in self._filename:
            filename = self._filename % {'uuid': uuid}
        else:
            filename = '{0}.{1}'.format(self._filename, uuid)

        data = np.array(self._trajectories[uuid])
        columns = ['step', 'x', 'y', 'z']

        if self._save_momentum:
            data = np.append(data, self._momenta[uuid], axis=1)
            columns += ['px', 'py', 'pz']

        getattr(self, self.save_as[self._format])(filename, data, columns)

    @staticmethod
    def _save_as_pandas(filename, data, columns):
        if data.size == 0:
            pandas.DataFrame(columns=columns).to_csv(filename)
        else:
            pandas.DataFrame(data=data, columns=columns).to_csv(filename)

    @staticmethod
    def _save_as_numpy(filename, data, columns):
        np.savetxt(filename, data, header=columns)

    # noinspection PyUnresolvedReferences
    save_as = {
        'pandas-csv': _save_as_pandas.__func__.__name__,
        'numpy': _save_as_numpy.__func__.__name__,
    }


@parametrize(
    Vector[Integer](
        'PublishedParticles',
        info='The UUIDs of particles which will be published. During the simulation UUIDs start '
             'at 0 (the first generated particle) and are incremented by 1 for each additionally '
             'generated particle.'
    )
)
class PublishingRecorder(OutputRecorder):
    """
    This output recorder publishes the "live" trajectories of a set of particles which can be
    specified via the `PublishedParticles` parameter. This can be used for example to display
    trajectories of particles in real time.
    """

    @injector.inject(
        particle_supervisor=di.components.particle_supervisor,
        configuration=di.components.configuration
    )
    def __init__(self, particle_supervisor, configuration):
        super().__init__(
            particle_supervisor=particle_supervisor,
            configuration=configuration
        )
        self._position_updates = rx.subjects.Subject()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)

    @property
    def position_updates(self):
        return self._position_updates

    def record(self, progress):
        super().record(progress)
        for uuid in self._published_particles:
            particle = self._particle_supervisor.get_particle_by_uuid(uuid)
            if particle.is_tracked:
                self._position_updates.on_next((uuid, particle.position.tolist()))


@parametrize(
    Filepath('Filename'),
    PhysicalQuantity(
        'BinSize',
        unit='m',
        info='The bin size of the resulting initial and final profile histograms.'
    ),
    Duplet[PhysicalQuantity](
        'HistogramRange',
        unit='m',
        optional=True,
        info='The range of the resulting initial and final histograms. The first element must '
             'indicate the lower boundary. If not specified the minimal and maximal recorded '
             'positions determine the histogram range.'
    )
)
class XMLProfileRecorder(OutputRecorder):
    """
    This output recorder saves the initial and final profile in the common XML format used for
    exchange of data related to beam profile measurements.
    
    References
    ----------
    https://twiki.cern.ch/twiki/pub/IPMSim/Internal_Documents/TransverseBeamProfileMonitors_DataExchangeFormat.pdf
    """

    @injector.inject(
        particle_supervisor=di.components.particle_supervisor,
        configuration=di.components.configuration
    )
    def __init__(self, particle_supervisor, configuration):
        super().__init__(
            particle_supervisor=particle_supervisor,
            configuration=configuration
        )
        self._config = configuration
        self._initial_xs = []
        self._final_xs = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)

        self.log.info('Generating XML configuration ...')
        self.log.debug('%s', self)

        self.generate_xml_config_from_samples(
            self._config,
            self._initial_xs,
            self._final_xs,
            self._bin_size,
            self._histogram_range
        ).dump_to_file(self._filename)

        self.log.info('... done.')

    def status_update(self, update):
        super().status_update(update)
        particle = update.particle
        if particle.is_queued:
            self._initial_xs.append(particle.position[0])
        elif particle.is_detected:
            self._final_xs.append(particle.position[0])

    @classmethod
    def generate_xml_config_from_samples(
            cls, config, initial, final, bin_size, histogram_range=None):
        histogram_initial = cls.generate_histogram(initial, bin_size, histogram_range)
        histogram_final = cls.generate_histogram(final, bin_size, histogram_range)

        initial_config = cls.generate_profile_sub_config(
            config,
            histogram_initial[1],
            histogram_initial[0],
            bin_size
        )
        final_config = cls.generate_profile_sub_config(
            config,
            histogram_final[1],
            histogram_final[0],
            bin_size
        )

        profile_set_config = type(config)()
        profile_set_config.insert_element(
            'ProfileSet/Profile',
            profile_set_config.Element(
                'Profile',
                None,
                {
                    'id': '1',
                    'type': 'initial',
                }
            )
        )
        profile_set_config.insert_config('ProfileSet/Profile', initial_config)
        profile_set_config.insert_element(
            'ProfileSet/Profile',
            profile_set_config.Element(
                'Profile',
                None,
                {
                    'id': '2',
                    'type': 'simulated',
                }
            )
        )
        profile_set_config.insert_config('ProfileSet/Profile[1]', final_config)

        # Apparently XMLAdaptors have a strange formatting when they are loaded from file.
        # input_config = copy.deepcopy(self._config)
        input_config = type(config)()
        input_config.insert_config('', cls.generate_meta_data_config(config))
        input_config.insert_config('', config)
        input_config.insert_config('', profile_set_config)
        return input_config

    @classmethod
    def generate_meta_data_config(cls, config):
        config = type(config)()
        date = cls.supply_date()
        config.insert_element(
            'Meta/Date',
            config.Element(
                'Date',
                date
            )
        )
        name, email = cls.supply_contact_info()
        config.insert_element(
            'Meta/Contact/Name',
            config.Element(
                'Name',
                name
            )
        )
        config.insert_element(
            'Meta/Contact/Email',
            config.Element(
                'Email',
                email
            )
        )
        config.insert_element(
            'Meta/Comment',
            config.Element(
                'Comment',
                'This file was created by %s'
                % '{0}.{1}'.format(__name__, cls.__name__)
            )
        )
        return config

    @staticmethod
    def generate_histogram(samples, bin_size, histogram_range=None):
        if histogram_range is None:
            histogram_range = (np.min(samples), np.max(samples))
        n_bins = int((histogram_range[1] - histogram_range[0]) / bin_size)
        bins, edges = np.histogram(samples, bins=n_bins, range=histogram_range)
        # `edges` denotes the lower edges of bins. Here we compute the bin centers instead.
        centers = edges[:-1] + (edges[1] - edges[0]) / 2.
        return bins, centers

    @staticmethod
    def generate_profile_sub_config(config, positions, bins, bin_size):
        config = type(config)()
        timestamp = datetime.now().strftime(
            '%Y-%m-%dT%H:%M:%S'
        )
        timestamp = str(timestamp)
        config.insert_element(
            'Timestamp',
            config.Element(
                'Timestamp',
                timestamp,
                {'format': 'iso'}
            )
        )
        config.insert_element(
            'Position',
            config.Element(
                'Position',
                '%e*i + %e' % (bin_size, positions[0]),
                {'unit': 'm'}
            )
        )
        config.insert_element(
            'Amplitude',
            config.Element(
                'Amplitude',
                ', '.join(map(
                    lambda x: '%e' % x,
                    bins
                )),
                {'unit': 'arbitrary'}
            )
        )
        return config

    @staticmethod
    def supply_date():
        return datetime.now().strftime('%Y-%m-%d')

    @staticmethod
    def supply_contact_info():
        try:
            name = subprocess.check_output(['git', 'config', 'user.name']).decode('utf-8')
        except (OSError, subprocess.CalledProcessError):
            # `git` either not installed (OSError) or not configured (CalledProcessError).
            name = subprocess.check_output(['whoami']).decode('utf-8')
            email = ''
            # Windows returns "pc-name\user-name" from whoami.
            name = name.split('\\')[-1]
        else:
            email = subprocess.check_output(['git', 'config', 'user.email']).decode('utf-8')
        return name, email
