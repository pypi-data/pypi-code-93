""" Contains controlling logic for the tfr permutation tests
"""

from collections import OrderedDict

import numpy as np
import matplotlib.pyplot as plt
import mne

from meggie.utilities.plotting import color_cycle
from meggie.utilities.channels import get_channels_by_type
from meggie.utilities.units import get_power_unit
from meggie_statistics.utilities.stats import prepare_data_for_permutation
from meggie_statistics.utilities.stats import permutation_analysis
from meggie_statistics.utilities.stats import report_permutation_results
from meggie_statistics.utilities.stats import plot_permutation_results


def run_permutation_test(experiment, window, selected_name, groups, time_limits,
                         frequency_limits, location_limits, threshold,
                         significance, n_permutations, design):
    """ Runs permutation test computation and reports the results.
    """
    if location_limits[0] == "ch_name" and frequency_limits is not None and time_limits is not None:
        raise Exception("Cannot run permutation tests with all location, frequency and time limits")

    tfr_item = experiment.active_subject.tfr[selected_name]
    conditions = list(tfr_item.content.keys())
    groups = OrderedDict(sorted(groups.items()))
    times = tfr_item.times
    freqs = tfr_item.freqs

    chs_by_type = get_channels_by_type(tfr_item.info)
    if location_limits[0] == 'ch_type':
        ch_type = location_limits[1]
    else:
        ch_type = [key for key, vals in chs_by_type.items() if location_limits[1] in vals][0]

    info, data, adjacency = prepare_data_for_permutation(
        experiment, design, groups, 'tfr', selected_name,
        location_limits, time_limits, frequency_limits,
        data_format=('locations', 'freqs', 'times'),
        do_meanwhile=window.update_ui)

    results = permutation_analysis(data, design, conditions, groups, threshold, adjacency, n_permutations,
                                   do_meanwhile=window.update_ui)

    report_permutation_results(results, design, selected_name, significance,
                               location_limits=location_limits,
                               time_limits=time_limits,
                               frequency_limits=frequency_limits)

    if design == 'within-subjects':
        title_template = 'Cluster {0} for group {1} (p {2})'
    else:
        title_template = 'Cluster {0} for condition {1} (p {2})'

    def time_fun(cluster_idx, cluster, pvalue, res_key):
        fig, ax = plt.subplots()
        if design == 'within-subjects':
            colors = color_cycle(len(conditions))
            for cond_idx, condition in enumerate(conditions):
                Y = np.mean(data[res_key][cond_idx], axis=0)
                Y = np.mean(Y[np.unique(cluster[0])], axis=0)
                Y = np.mean(Y[:, np.unique(cluster[-1])], axis=1)
                ax.plot(times, Y, label=condition, color=colors[cond_idx])
        else:
            colors = color_cycle(len(groups))
            for group_idx, (group_key, group) in enumerate(groups.items()):
                Y = np.mean(data[res_key][group_idx], axis=0)
                Y = np.mean(Y[np.unique(cluster[0])], axis=0)
                Y = np.mean(Y[:, np.unique(cluster[-1])], axis=1)
                ax.plot(times, Y, label=condition, color=colors[group_idx])

        fig.suptitle(title_template.format(cluster_idx+1, res_key, pvalue))
        fig.canvas.set_window_title('Cluster time course')

        ax.legend()
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Power ({})'.format(
            get_power_unit(ch_type, log=False)))

        ax.axhline(0, color='black')
        ax.axvline(0, color='black')

        tmin = np.min(times[cluster[1]])
        tmax = np.max(times[cluster[1]])
        ax.axvspan(tmin, tmax, alpha=0.5, color='blue')

    def frequency_fun(cluster_idx, cluster, pvalue, res_key):
        fig, ax = plt.subplots()
        if design == 'within-subjects':
            colors = color_cycle(len(conditions))
            for cond_idx, condition in enumerate(conditions):
                Y = np.mean(data[res_key][cond_idx], axis=0)
                Y = np.mean(Y[:, np.unique(cluster[1]), :], axis=1)
                Y = np.mean(Y[:, np.unique(cluster[-1])], axis=1)
                ax.plot(freqs, Y, label=condition, color=colors[cond_idx])
        else:
            colors = color_cycle(len(groups))
            for group_idx, (group_key, group) in enumerate(groups.items()):
                Y = np.mean(data[res_key][group_idx], axis=0)
                Y = np.mean(Y[:, np.unique(cluster[1]), :], axis=1)
                Y = np.mean(Y[:, np.unique(cluster[-1])], axis=1)
                ax.plot(freqs, Y, label=condition, color=colors[group_idx])

        fig.suptitle(title_template.format(cluster_idx+1, res_key, pvalue))
        fig.canvas.set_window_title('Cluster spectrum')

        ax.legend()
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Power ({})'.format
            (get_power_unit(ch_type, log=False)))
        fmin = np.min(freqs[cluster[0]])
        fmax = np.max(freqs[cluster[0]])
        ax.axvspan(fmin, fmax, alpha=0.5, color='blue')

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
                             frequency_limits=frequency_limits,
                             time_limits=time_limits,
                             location_fun=location_fun,
                             frequency_fun=frequency_fun,
                             time_fun=time_fun)


