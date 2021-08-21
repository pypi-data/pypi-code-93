import matplotlib.pyplot as plt
import numpy as np


def init_figure(figsize=(8, 5), fontsize=18):
    plt.figure(figsize=figsize)
    plt.rcParams['font.size'] = fontsize


def savefig(filename, bbox_inches='tight', pad_inches=0, **kwargs):
    plt.savefig(
        filename, bbox_inches=bbox_inches, pad_inches=pad_inches, **kwargs
    )


def add_diag_refline(
        x, y, linestyle='--', equal_axis=True, zorder=0, label='x = y',
        **kwargs):
    min_max = [
        min(np.min(x), np.min(y)),
        max(np.max(x), np.max(y))
    ]
    plt.plot(
        min_max, min_max,
        linestyle=linestyle, zorder=zorder, label=label, **kwargs
    )
    if equal_axis:
        plt.gca().set_aspect('equal', 'box')


def add_line_at_zero(horizontal=True, vertical=False, labels=[None, None],
                     color='grey', linestyle='--', linewidth=.8):
    """
    Parameters
    ----------
    labels: list of str e.g. ['y = 0', 'x = 0']
    """
    if horizontal:
        plt.axhline(
            y=0, color=color, linestyle=linestyle, linewidth=linewidth, label=labels[0]
        )
    if vertical:
        plt.axvline(
            x=0, color=color, linestyle=linestyle, linewidth=linewidth, label=labels[1]
        )
        
        
def remove_figure_box_edges(sides=['left', 'right', 'top', 'bottom']):
    for side in sides:
        plt.gca().spines[side].set_visible(False)


def delineated_hist(x, bins, color):
    plt.hist(
        x, bins=bins, histtype='step', ec=color, lw=1.25
    )
    plt.hist(
        x, bins=bins, fc=color, alpha=.1
    )