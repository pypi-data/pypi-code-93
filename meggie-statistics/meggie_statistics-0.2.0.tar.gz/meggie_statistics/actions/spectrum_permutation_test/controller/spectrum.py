""" Contains controlling logic for the spectrum permutation tests.
"""
from collections import OrderedDict

import mne

import numpy as np
import matplotlib.pyplot as plt

import pandas as pd

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
    if location_limits[0] == "ch_name" and frequency_limits is not None:
        raise Exception('Cannot run permutation tests with both location and frequency limits')

    spectrum_item = experiment.active_subject.spectrum[selected_name]
    conditions = list(spectrum_item.content.keys())
    groups = OrderedDict(sorted(groups.items()))
    freqs = spectrum_item.freqs

    chs_by_type = get_channels_by_type(spectrum_item.info)
    if location_limits[0] == 'ch_type':
        ch_type = location_limits[1]
    else:
        ch_type = [key for key, vals in chs_by_type.items() if location_limits[1] in vals][0]

    log_transformed = False

    info, data, adjacency = prepare_data_for_permutation(
        experiment, design, groups, 'spectrum', selected_name,
        location_limits, time_limits, frequency_limits,
        data_format=('locations', 'freqs'),
        do_meanwhile=window.update_ui)

    results = permutation_analysis(data, design, conditions, groups, threshold, adjacency, n_permutations,
                                   do_meanwhile=window.update_ui)

    report_permutation_results(results, design, selected_name, significance,
                               location_limits=location_limits, 
                               frequency_limits=frequency_limits)

    if design == 'within-subjects':
        title_template = 'Cluster {0} for group {1} (p {2})'
    else:
        title_template = 'Cluster {0} for condition {1} (p {2})'

    def frequency_fun(cluster_idx, cluster, pvalue, res_key):
        fig, ax = plt.subplots()
        if design == 'within-subjects':
            colors = color_cycle(len(conditions))
            for cond_idx, condition in enumerate(conditions):
                spectrum = np.mean(data[res_key][cond_idx][:, :, np.unique(cluster[-1])],
                                   axis=(0, -1))
                ax.plot(freqs, spectrum, label=condition, color=colors[cond_idx])

        else:
            colors = color_cycle(len(groups))
            for group_idx, (group_key, group) in enumerate(groups.items()):
                spectrum = np.mean(data[res_key][group_idx][:, :, np.unique(cluster[-1])],
                                   axis=(0, -1))
                ax.plot(freqs, spectrum, label=group_key, color=colors[group_idx])

        fig.suptitle(title_template.format(cluster_idx+1, res_key, pvalue))
        fig.canvas.set_window_title('Cluster spectrum')

        ax.legend()
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Power ({})'.format(
            get_power_unit(ch_type, log_transformed)))
        fmin = np.min(freqs[cluster[0]])
        fmax = np.max(freqs[cluster[0]])
        ax.axvspan(fmin, fmax, alpha=0.5, color='blue')

    def location_fun(cluster_idx, cluster, pvalue, res_key):
        map_ = [1 if idx in cluster[-1] else 0 for idx in 
                range(len(info['ch_names']))]

        fig, ax = plt.subplots()
        mne.viz.plot_topomap(np.array(map_), info, vmin=0, vmax=1,
                             cmap='Reds', axes=ax, ch_type=ch_type,
                             contours=0)

        fig.suptitle(title_template.format(cluster_idx+1, res_key, pvalue))
        fig.canvas.set_window_title('Cluster topomap')

    plot_permutation_results(results, significance, window,
                             location_limits=location_limits, 
                             frequency_limits=frequency_limits, 
                             location_fun=location_fun,
                             frequency_fun=frequency_fun)

