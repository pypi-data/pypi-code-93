""" Contains controlling logic for the evoked permutation tests
"""

from collections import OrderedDict

import mne
import numpy as np
import matplotlib.pyplot as plt

from meggie.utilities.plotting import color_cycle
from meggie.utilities.channels import get_channels_by_type
from meggie_statistics.utilities.stats import prepare_data_for_permutation
from meggie_statistics.utilities.stats import permutation_analysis
from meggie_statistics.utilities.stats import report_permutation_results
from meggie_statistics.utilities.stats import plot_permutation_results

from meggie.utilities.units import get_unit


def run_permutation_test(experiment, window, selected_name, groups, time_limits,
                         frequency_limits, location_limits, threshold,
                         significance, n_permutations, design):
    """ Does permutation test computation and reporting.
    """
    if location_limits[0] == "ch_name" and time_limits is not None:
        raise Exception('Cannot run permutation tests with both location and time limits')

    evoked_item = experiment.active_subject.evoked[selected_name]
    conditions = list(evoked_item.content.keys())
    groups = OrderedDict(sorted(groups.items()))
    times = evoked_item.times

    chs_by_type = get_channels_by_type(evoked_item.info)
    if location_limits[0] == 'ch_type':
        ch_type = location_limits[1]
    else:
        ch_type = [key for key, vals in chs_by_type.items() if location_limits[1] in vals][0]

    info, data, adjacency = prepare_data_for_permutation(
        experiment, design, groups, 'evoked', selected_name,
        location_limits, time_limits, frequency_limits, 
        data_format=('locations', 'times'),
        do_meanwhile=window.update_ui)

    results = permutation_analysis(data, design, conditions, groups, threshold, adjacency, n_permutations,
                                   do_meanwhile=window.update_ui)

    report_permutation_results(results, design, selected_name, significance,
                               location_limits=location_limits,
                               time_limits=time_limits)

    if design == 'within-subjects':
        title_template = 'Cluster {0} for group {1} (p {2})'
    else:
        title_template = 'Cluster {0} for condition {1} (p {2})'

    def time_fun(cluster_idx, cluster, pvalue, res_key):
        """
        """
        fig, ax = plt.subplots()
        if design == 'within-subjects':
            colors = color_cycle(len(conditions))
            for cond_idx, condition in enumerate(conditions):
                evoked = np.mean(data[res_key][cond_idx][:, :, np.unique(cluster[-1])],
                                 axis=(0, -1))
                ax.plot(times, evoked, label=condition, color=colors[cond_idx])
        else:
            colors = color_cycle(len(groups))
            for group_idx, (group_key, group) in enumerate(groups.items()):
                evoked = np.mean(data[res_key][group_idx][:, :, np.unique(cluster[-1])],
                                 axis=(0, -1))
                ax.plot(times, evoked, label=group_key, color=colors[group_idx])

        fig.canvas.set_window_title('Cluster time course')
        fig.suptitle(title_template.format(cluster_idx+1, res_key, pvalue))

        ax.legend()
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude ({})'.format(
            get_unit(ch_type)))

        ax.axhline(0, color='black')
        ax.axvline(0, color='black')

        tmin = np.min(times[cluster[0]])
        tmax = np.max(times[cluster[0]])
        ax.axvspan(tmin, tmax, alpha=0.5, color='blue')

    def location_fun(cluster_idx, cluster, pvalue, res_key):
        map_ = [1 if idx in cluster[-1] else 0 for idx in
                range(len(info['ch_names']))]

        fig, ax = plt.subplots()
        ch_type = location_limits[1]
        mne.viz.plot_topomap(np.array(map_), info, vmin=0, vmax=1,
                             cmap='Reds', axes=ax, ch_type=ch_type, 
                             contours=0)

        fig.suptitle(title_template.format(cluster_idx+1, res_key, pvalue))
        fig.canvas.set_window_title('Cluster topomap')

    plot_permutation_results(results, significance, window,
                             location_limits=location_limits,
                             time_limits=time_limits,
                             location_fun=location_fun,
                             time_fun=time_fun)


