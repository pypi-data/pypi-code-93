import sys
import argparse
import numpy as np
import pandas as pd

from . import Lens, ThresholdDistance, SweepDistanceLogarithmic, stad
from .export import to_json 


def create_argument_parser():
  """
  Configures argparse for this program.
  """
  parser = argparse.ArgumentParser(
    description = 'pySTAD -- creates a JSON network representation of data.')
  parser.add_argument('distances', metavar = 'dists', type = str,
                      help = 'A .csv file containing a symmetrical, positive '
                             'distance matrix. The first row should contain '
                             'the node labels. There should not be a special '
                             'first column.')
  group = parser.add_mutually_exclusive_group(required = False)
  group.add_argument('-t', '--threshold', dest = 'threshold', type = float,
                     metavar = 'threshold',
                     help = 'A (normalised 0 to 1) distance threshold to '
                            'apply. Edges with distances below the threshold '
                            'are added to the network. Use this option as an '
                            'alternative to --sweep, when the optimal '
                            'threshold is already known. Do *not* specify '
                            'both --sweep and --threshold.')
  group.add_argument('-s', '--sweep', dest = 'sweep', type = float, nargs = 3,
                     default = [0.01, 0.3, 10], metavar = 'sweep',
                     help = 'The (start, stop, num_steps) parameters of a '
                            'logarithmic sweep over the normalised '
                            'edge-distance. Start and stop should satisfy: 0 '
                            '<= start < stop <= 1. Num_steps specifies the '
                            'number of thresholds to evaluate. The network of '
                            'the best observed value threshold is returned. '
                            'When neither `-t` nor `-s` are specified, '
                            '`-s 0.01 0.3 10` is used. Do *not* specify both '
                            '-s and -t.')
  parser.add_argument('-p', '--edge-penalty', dest = 'penalty', type = float,
                      default = 0, metavar = 'penalty',
                      help = 'A value to use as  edge penalty (float). Used '
                             'in a penalty term to reduce the number of edges '
                             'in the optimal network: objective = correlation '
                             '- penalty * added_edges / total_edges')
  parser.add_argument('-r', '--use-ratio', dest = 'ratio',
                      action = 'store_true',
                      help = 'A flag to enable STAD-R variant. Penalizes the '
                             'number of edges more strongly than the edge '
                             'penalty. Designed for left-skewed distance '
                             'distributions.')
  parser.add_argument('-o', '--openmp-threads', dest = 'threads',
                      metavar = 'threads', type = int, default = -1,
                      help = 'The number of threads to use when computing '
                             'shortest-path network distances. By default '
                             'STAD uses a thread per core.')
  parser.add_argument('-b', '--filter_bins', dest = 'bins', type = int,
                      default = 0, metavar = 'bins',
                      help = 'The number of bins to  segment the filter '
                             'dimension into. The lens is disabled when a '
                             'value lower or equal to 0 is used, or when the '
                             'filter values are not present in the node '
                             'attributes')
  parser.add_argument('-c', '--circular_filter', dest = 'circular',
                      action = 'store_true', default = False,
                      help = 'A flag to indicate whether the filter-dimension '
                             'is circular in nature.')
  parser.add_argument('-n', '--node-attributes', dest = 'node_attributes',
                      metavar = 'node-attributes', type = str,
                      help = 'A .csv file containing node attributes. Every '
                             'row should provide information of a single '
                             'node. The node order should be the same as the '
                             'column order of the distance matrix. Three ('
                             'optional) columns are used: `color`, `radius`, '
                             'and `filter`. All columns should contain '
                             'floating-point values. Default values are used '
                             'if a column is not present. The filter is '
                             'disabled when no `filter` column is present.')
  parser.add_argument('-e', '--edge-attributes', dest = 'edge_attributes',
                      metavar = 'edge-attributes', type = str,
                      help = 'A .csv file containing edge attributes. Two '
                             'columns should exist: source and target, '
                             'indicating the source-node and target-node '
                             'index in a condensed distance matrix. '
                             'Two optional columns, color and width, can be '
                             'used to specify additional information (float). '
                             'Default values are used when these columns are not'
                             ' present. Edges not present in the file are '
                             'silently ignored, default values are used.')
  return parser


def read_node_attributes(args):
  """
  Load a csv file of node-attributes.

  Parameters
  ----------
  args :
    The commandline arguments as parsed by argparse.

  Returns
  -------
  A tuple of three 1d numpy arrays containing values for color, radius, and
  filter of nodes.
  A tuple of three times None if no node-attributes were specified.
  """
  node_color = None
  node_radius = None
  node_filter = None

  if args.node_attributes is not None:
    nodes = pd.read_csv(args.node_attributes)
    if 'color' in nodes.columns:
      node_color = nodes['color'].to_numpy()
    if 'radius' in nodes.columns:
      node_radius = nodes['radius'].to_numpy()
    if 'filter' in nodes.columns and args.bins > 0:
      node_filter = nodes['filter'].to_numpy()

  return node_color, node_radius, node_filter


def read_edge_attributes(args):
  """
  Load a csv file of edge-attributes.

  Parameters
  ----------
  args :
    The commandline arguments as parsed by argparse.

  Returns
  -------
  A tuple of three 1d numpy arrays containing values for color, radius, and
  filter of edges.
  A tuple of three times None if no edge-attributes were specified.
  """
  edge_source = None
  edge_target = None
  edge_color = None
  edge_width = None

  if args.edge_attributes is not None:
    edges = pd.read_csv(args.edge_attributes)
    edge_source = edges['source'].to_numpy()
    edge_target = edges['target'].to_numpy()
    if 'color' in edges.columns:
      edge_color = edges['color'].to_numpy()
    if 'width' in edges.columns:
      edge_width = edges['width'].to_numpy()

  return edge_source, edge_target, edge_color, edge_width


def filter_edge_attributes(network, edge_source: np.ndarray,
                           edge_target: np.ndarray, edge_color: np.ndarray,
                           edge_width: np.ndarray):
  """
  Extracts the edge attributes of edges included in the final network.

  Parameters
  ----------
  network : a scipy sparse coo matrix
    The final network.
  edge_source : 1d numpy array
    An array with the index of source nodes in a condensed distance matrix.
  edge_target : 1d numpy array
    An array with the index of target nodes in a condensed distance matrix.
  edge_color : 1d numpy array
    An array with a data-value to map to the color of an edge.
  edge_width : 1d numpy array
    An array with a data-value to map to the width of an edge.

  Returns
  -------
  A tuple with link color and width values, for each link in the network.
  A tuple with two Nones if not edge-attributes were specified.
  """
  # Early return if edge attributes were not specified
  if edge_source is None:
    return None, None
  
  # Extract edge-attributes for the edges in the network
  link_color = np.repeat(0.5, len(network.data))
  link_width = np.repeat(0.2, len(network.data))
  if edge_color is not None or edge_width is not None:
    for idx in range(len(network.data)):
      mask = (edge_source == network.row[idx]) & \
             (edge_target == network.col[idx])
      if mask.any():
        if edge_color is not None:
          link_color[idx] = edge_color[mask]
        else:
          link_width[idx] = edge_width[mask]

  return link_color, link_width


def main():
  """
  Run STAD and print the resulting network as JSON string.
  """
  # Create argument parser
  parser = create_argument_parser()
  args = parser.parse_args()
  
  # Process arguments
  dists = pd.read_csv(args.distances)
  node_label = dists.columns.to_numpy()
  node_color, node_radius, node_filter = read_node_attributes(args)
  edge_source, edge_target, edge_color, edge_width = read_edge_attributes(args)
  lens = Lens(node_filter, n_bins = args.bins, circular = args.circular)
  if args.threshold is not None:
    sweep = ThresholdDistance(args.threshold)
  else:
    sweep = SweepDistanceLogarithmic(args.sweep[0], args.sweep[1],
                                     int(args.sweep[2]))

  # Run STAD and log results
  network, sweep = stad(dists.to_numpy(), lens = lens, sweep = sweep,
                 edge_penalty = args.penalty, use_ratio = args.ratio,
                 num_threads = args.threads)
  print(f'Evaluated {sweep.n_steps:d} networks. The optimal network:',
        file = sys.stderr)
  print(f'   - objective: {sweep.best_objective:.3f}', file = sys.stderr)
  print(f'   - correlation: {sweep.best_correlation:.3f}', file = sys.stderr)
  print(f'   - penalty: {sweep.best_penalty:.3f}', file = sys.stderr)
  print(f'   - ratio: {sweep.best_ratio:.3f}', file = sys.stderr)
  print(f'   - threshold: {sweep.best_distance:.3f}', file = sys.stderr)
  print(f'   - added-edges: {sweep.best_added_edges:d}', file = sys.stderr)

  # Extract network edges information
  link_color, link_width = filter_edge_attributes(network, edge_source,
                                                  edge_target, edge_color,
                                                  edge_width)

  # Print resulting network
  network_str = to_json(network, node_label = node_label,
                        node_color = node_color, node_radius = node_radius,
                        link_color = link_color, link_width = link_width)
  print(network_str)


if __name__ == '__main__': 
  main()
