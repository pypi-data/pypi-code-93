import matplotlib.pyplot as plt

from stad import _validation


def sweep(distances, sweep, histogram_bins = 20, ax = None):
  """ Draw the optimisation traces using matplotlib

  Plots a histogram of normalised edge distances and the objective,
  correlation curves.

  Parameters
  ----------
  distances : 1D or 2D numpy array or scipy sparse matrix
      This parameter can be three types of distance matrices:
          - a dense distance matrix (0 values on diagonals, symmetrical)
          - a condensed distance matrix (as given by
            scipy.spatial.distance.pdist)
          - a scipy sparse distance matrix (including explicit zeros)
      Missing or infinite values are not allowed. In addition, the distance
      matrix should contain at least two unique values.
  sweep : a STAD sweeper object
      The sweep object used to call sd.stad()
  histogram_bins : int
      The number of bins to use for the histogram
  ax : matplotlib Axes object
      A matplotlib axes to draw to. If None, a new one is created

  Returns
  -------
  The matplotlib Figure object that was drawn to
  """
  distances = _validation.distances(distances)
  if ax is None:
    fig = plt.figure()
    ax = plt.gca()
  else:
    plt.sca(ax)
    fig = plt.gcf()

  ax.hist(distances.data / distances.data.max(), bins = histogram_bins)
  ax.set_xlabel('Normalised distance')
  ax.set_ylabel('Count')

  ax2 = ax.twinx()
  ax2.plot(sweep.distance_trace, sweep.penalty_trace, '.', color = 'C4',
           label = 'penalty')
  ax2.plot(sweep.distance_trace, sweep.ratio_trace, '.', color = 'C3',
           label = 'ratio')
  ax2.plot(sweep.distance_trace, sweep.correlation_trace, '.', color = 'C2',
           label = 'correlation')
  ax2.plot(sweep.distance_trace, sweep.objective_trace, '.', color = 'C1',
           label = 'objective')
  plt.legend()
  ax2.set_ylabel('Correlation')

  plt.xlim([0, 1])
  return fig
