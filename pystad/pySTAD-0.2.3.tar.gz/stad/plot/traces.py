import matplotlib.pyplot as plt


def traces(sweep):
  """ Draw the optimisation traces using matplotlib

  Plot the objective and correlation traces created during a sweep.

  Parameters
  ----------
  sweep : a STAD sweeper object
      The sweep object used to call sd.stad()

  Returns
  -------
  The matplotlib Figure object that was drawn to
  """  
  fig, axes = plt.subplots(6, 1)
  _plot_trace(sweep.objective_trace, 'C1', 'Objective', axes[0])
  _plot_trace(sweep.correlation_trace, 'C2', 'Correlation', axes[1])
  _plot_trace(sweep.ratio_trace, 'C3', 'Ratio', axes[2])
  _plot_trace(sweep.penalty_trace, 'C4', 'Penalty', axes[3])
  _plot_trace(sweep.distance_trace, 'C5', 'Distance', axes[4])
  _plot_trace(sweep.added_edges_trace, 'C6', 'Added edges', axes[5])
  return fig


def _plot_trace(trace, color, label, ax):
  ax.plot(trace, '.', color=color)
  ax.set_xlabel('Iteration')
  ax.set_ylabel(label)