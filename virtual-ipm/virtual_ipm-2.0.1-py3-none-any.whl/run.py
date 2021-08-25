#!/usr/bin/env python

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

import argparse
import logging
import pprint
import sys
from unittest.mock import Mock

from anna import load_from_file
import pyhocon

import virtual_ipm
from virtual_ipm.control.threading import SimulationThread
from virtual_ipm.simulation.setup import SimulationParameters
from virtual_ipm.simulation.output import BasicRecorder
import virtual_ipm.log as log
import virtual_ipm.timings as timings


parser = argparse.ArgumentParser()

parser.add_argument(
    'config',
    help='File path pointing to a configuration file.'
)
parser.add_argument(
    '--version',
    action='version',
    version=virtual_ipm.__version__
)
parser.add_argument(
    '--quiet-console',
    action='store_true',
    help='Use this switch to suppress all console output.'
)
parser.add_argument(
    '--console-log-level',
    choices=('debug', 'info', 'warning', 'error', 'critical'),
    nargs='?',
    const='info',
    default='info',
    type=str,
    help='Set the logging level to one of the levels available in the Python logging library.'
)
parser.add_argument(
    '--log-to-file',
    help='In addition to the console log entries will be stored in the specified file.'
)
parser.add_argument(
    '--file-log-level',
    choices=('debug', 'info', 'warning', 'error', 'critical'),
    nargs='?',
    const='debug',
    default='debug',
    type=str,
    help='The level for file logging can be set independently from the console.'
)
parser.add_argument(
    '--timing-stats-to-file',
    help='The timing (performance) statistics will be written to the specified file.'
)
parser.add_argument(
    '--number-of-particles',
    type=int,
    help='Modify the number of particles used for the simulation',
)
parser.add_argument(
    '--number-of-timesteps',
    type=int,
    help='Modify the number of time steps used for the simulation (the simulation time and time delta remain the same '
         'however)',
)
parser.add_argument(
    '--dryrun',
    action='store_true',
    help='Use this argument to run the given configuration with reduced particle and time step numbers in order to '
         'check whether everything works as expected.',
)

DRYRUN_NUMBER_OF_PARTICLES = 10
DRYRUN_NUMBER_OF_TIMESTEPS = 10


# noinspection PyProtectedMember
def main():
    args = parser.parse_args()

    if not args.quiet_console:
        log.to_console(level=getattr(logging, args.console_log_level.upper()))

    if args.log_to_file:
        log.to_file(args.log_to_file, level=getattr(logging, args.file_log_level.upper()))

    if args.dryrun:
        SimulationParameters._number_of_particles = DRYRUN_NUMBER_OF_PARTICLES
        SimulationParameters._time_range = TimeRangeMock(SimulationParameters._time_range,
                                                         number_of_time_steps=DRYRUN_NUMBER_OF_TIMESTEPS)
        BasicRecorder.UNDETECTED_COUNT_MAX_LOG = float('nan')  # All (in)equality comparisons with NaN will return False.
    if args.number_of_particles:
        SimulationParameters._number_of_particles = args.number_of_particles
    if args.number_of_timesteps:
        SimulationParameters._time_range = TimeRangeMock(SimulationParameters._time_range,
                                                         number_of_time_steps=args.number_of_timesteps)

    def create_configuration_from_args():
        # Default filename for the setup configuration.
        boot_file = 'boot.conf'

        setup_config = pyhocon.ConfigFactory.from_dict({
            name: getattr(args, name)
            for name in filter(
                lambda name: getattr(args, name) is not None,
                ['config']
            )
        })

        try:
            # Specifiers have precedence over parameters stored in the boot file.
            setup_config = setup_config.with_fallback(pyhocon.ConfigFactory.parse_file(boot_file))
        except IOError:
            log.root_logger.debug('Setup configuration file "%s" not found.', boot_file)

        return load_from_file(setup_config['config'])

    thread = SimulationThread()
    thread.setup(create_configuration_from_args())
    thread.prepare()
    thread.run()

    log.root_logger.debug('----- Timing Statistics -----')
    log.root_logger.debug('CPU time:')
    log.root_logger.debug(pprint.pformat(dict(timings.cpu_time_per_component)))
    log.root_logger.debug('Percentages:')
    log.root_logger.debug(pprint.pformat(timings.compute_formatted_percentages()))

    if args.timing_stats_to_file:
        timings.dump_statistics_to_file(args.timing_stats_to_file)

    return 0


class TimeRangeMock(Mock):
    def __init__(self, parameter, *, simulation_time=None, time_delta=None, number_of_time_steps=None):
        super().__init__(spec=parameter.__class__)
        self.__parameter = parameter
        self.__simulation_time = simulation_time
        self.__time_delta = time_delta
        self.__number_of_time_steps = number_of_time_steps

    def __getattr__(self, name):
        return getattr(self.__parameter, name)

    def load_from_configuration(self, *args):
        t, dt, n = self.__parameter.load_from_configuration(*args)
        return (
            self.__simulation_time or t,
            self.__time_delta or dt,
            self.__number_of_time_steps or n,
        )


if __name__ == '__main__':
    sys.exit(main())
