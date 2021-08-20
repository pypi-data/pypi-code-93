import matplotlib.pyplot as plt
import itertools
import pandas as pd
import numpy as np

class Plot:

  def set_axis_style(self, ax, labels):
    ax.xaxis.set_tick_params(direction='out')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks(np.arange(1, len(labels) + 1))
    ax.set_xticklabels(labels)
    ax.set_xlim(0.25, len(labels) + 0.75)

  def plot_top_ranking_probs(self, model_names, algorithm_names, probs, empirical, axs):
    assert(len(model_names) > 0)
    assert(len(model_names) == len(probs))
    assert(len(algorithm_names) == len(axs))
    num_samples, num_algorithms = probs[0].shape

    for i, ax in enumerate(axs):
      if ax != None:
        df = pd.DataFrame(columns=model_names)

        for model_name, sample in zip(model_names, probs):
          df[model_name] = sample[:,i]
        
        ax.violinplot(df.values, showmeans=True)
        ax.axhline(y=empirical[i], linestyle=':', color='black', label='Empirical')
        ax.set_title(algorithm_names[i])
        self.set_axis_style(ax, model_names)

  def plot_better_than_probs(self, model_names, algorithm_names, probs, empirical, axs):
    assert(len(model_names) > 0)
    assert(len(model_names) == len(probs))
    num_samples, num_algorithms, _ = probs[0].shape

    first_row = True
    for model, prob, row in zip(model_names, probs, axs):
      for i, ax in enumerate(row):
        if ax != None:
          idxs = [x for x in range(0, num_algorithms) if x != i]
          names = [algorithm_names[x] for x in idxs]
          x_values = range(1, len(idxs) + 1)
          empirical_values = [empirical[i, vs] for vs in idxs]
          
          ax.scatter(x_values, empirical_values, marker='o', color='black', s=30, zorder=3)
          ax.violinplot(prob[:, i, idxs], showmeans=True)
          ax.set_ylabel(model)
          self.set_axis_style(ax, names)

          if first_row:
            ax.set_title(algorithm_names[i])
      first_row = False

  def plot_top_k_probs(self, model_names, algorithm_names, probs, empirical, axs):
    assert(len(model_names) > 0)
    assert(len(model_names) == len(probs))
    num_samples, num_algorithms, _ = probs[0].shape

    first_row = True
    for model, prob, row in zip(model_names, probs, axs):
      for i, ax in enumerate(row):
        if ax != None:
          idxs = list(range(num_algorithms))
          names = algorithm_names
          x_values = range(1, len(idxs) + 1)
          empirical_values = [empirical[i, vs] for vs in idxs]
          
          ax.violinplot(prob[:, idxs, i], showmeans=True)
          ax.scatter(x_values, empirical_values, marker='o', color='black', s=30, zorder=3)
          ax.set_ylabel(model)
          self.set_axis_style(ax, names)

          if first_row:
            ax.set_title("Top: " + str(i + 1))
      first_row = False
