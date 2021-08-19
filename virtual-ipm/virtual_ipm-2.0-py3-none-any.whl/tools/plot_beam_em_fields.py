from argparse import ArgumentParser
from pathlib import Path
import sys

from anna import XMLAdaptor
from anna.exceptions import InvalidPathError
import numpy as np
import matplotlib.pyplot as plt
from scipy import constants

from virtual_ipm.simulation.beams.beams import BeamsWrapper
from virtual_ipm.simulation.beams.factory import BeamFactory

parser = ArgumentParser()
parser.add_argument('configuration', type=Path, help='File path to XML configuration file')
parser.add_argument('--beam-id', type=int, default=0, help='If the configuration specifies multiple beams, this '
                                                           'parameter can be used to select between them.')
parser.add_argument('--x', type=float, default=0, help='Determines the space offset in x direction,'
                                                       ' units in [m]')
parser.add_argument('--y', type=float, default=0, help='Determines the space offset in y direction,'
                                                       ' units in [m]')
parser.add_argument('--z', type=float, default=0, help='Determines the space offset in z direction,'
                                                       ' units in [m]')
parser.add_argument('--t', type=float, default=0, help='Determines the time offset, units in [s]')
parser.add_argument('--plot-axis', choices=tuple('xyz'), type=str, default='x', help='Chose which axis to plot'
                                                                                     ' the electric field over')
parser.add_argument('--n', type=int, default=1000, help='Integer number of steps for the plot')
parser.add_argument('--lim', type=float, default=0.015, help='Range of the plot, one argument in units of [m]')


def plot1d(beam, args):
    """Plot the beam electric field along the specified axis."""
    # Declaring variables
    t = args.t
    x = args.x
    y = args.y
    z = args.z
    lim = args.lim
    n = args.n
    num_plot_axis = ord(args.plot_axis) - ord('x') + 1

    # Setup four vector and electric field
    positions_four_vector = np.empty((4, n))
    positions_four_vector[0] = [constants.speed_of_light*t]*n
    positions_four_vector[1] = [x]*n
    positions_four_vector[2] = [y]*n
    positions_four_vector[3] = [z]*n
    positions_four_vector[num_plot_axis] += np.linspace(-lim, lim, num=n)
    progress = Progress(t)
    electric_field = beam.electric_field_at(positions_four_vector, progress)

    # Plot
    cmetre = 1 / 2.54
    fig, ax = plt.subplots(ncols=1, figsize=(22*cmetre, 20*cmetre))
    plt.plot(positions_four_vector[num_plot_axis], electric_field[num_plot_axis-1, :])
    plt.title('Electric field in the lab frame')
    ax.set_xlabel('%s [m]' % args.plot_axis)
    ax.set_ylabel('E%s [V/m]' % args.plot_axis)
    ax.set_xlim(positions_four_vector[num_plot_axis][0], positions_four_vector[num_plot_axis][-1])
    ax.grid(True)
    plt.figure(1)
    plt.show()


def main():
    args = parser.parse_args()
    configuration = XMLAdaptor(filepath=str(args.configuration.resolve()))
    try:
        beam_config = configuration.get_sub_configurations(BeamsWrapper.PATH_TO_BEAMS)[args.beam_id]
    except InvalidPathError:
        print_err('The configuration does not include a beam specification')
    except IndexError:
        print_err(f'The specified --beam-id ({args.beam_id}) '
                  f'exceeds the number of beams specified in the configuration')
    else:
        beam = BeamFactory(None).create(beam_config)
        plot1d(beam, args)
    return 0


def print_err(*args, **kwargs):
    kwargs.setdefault('file', sys.stderr)
    print(*args, **kwargs)


class Progress:
    def __init__(self, time):
        self.time = time


if __name__ == '__main__':
    sys.exit(main())
