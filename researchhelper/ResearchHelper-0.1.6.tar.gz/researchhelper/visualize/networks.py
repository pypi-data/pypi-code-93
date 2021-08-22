"""Visualization unit of network data."""

from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.collections import LineCollection
import matplotlib.animation as animation
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def plot_grid(ax, model, layout, with_labels=False, title=''):
    """Plot grid network.

    Parameters
    ----------
    ax : matplotlib.axis
        Matplotlib axis to plot in.
    model : Mesa.model
        Mesa agent-based model object.
    layout : nx.__layout
        Networkx layout.
        (e.g., nx.kamada_kawai_layout, nx.spring_layout)
    with_labels : boolean
        True or false boolean on whether or not to show labels.
        (Default value = False)
    title : str
        Title of the plot. (Default value = '')

    Returns
    -------
    None

    """
    cmap = plt.get_cmap("viridis")
    graph = model.G
    pos = layout(graph)

    states = [int(i.k) for i in model.grid.get_all_cell_contents()] # FIX
    colors = [cmap(30 + i * 30) for i in states]
    sizes = [30 + i * 30 for i in states]
    nx.draw(
        graph,
        pos,
        node_size=sizes,
        edge_color='gray',
        node_color=colors,
        with_labels=with_labels,
        alpha=0.9,
        font_size=14,
        ax=ax)
    ax.set_title(title)
    return


def nxNetworkMP4(full_graph, Gs, labels, layout, save_path, remove_inactive_nodes=False):
    """Create an MP4 from the network dynamics over time.

    Parameters
    ----------
    full_graph : nx.Graph
        Networkx graph with all nodes and edges.
    Gs : List[nx.Graph
        List of networkx graphs that change over time.
    labels : List[str
        List of labels showing the current time.
    layout : nx.__layout
        Networkx layout.
        (e.g., nx.kamada_kawai_layout, nx.spring_layout)
    save_path : str
        Where do you want to save your mp4?
    remove_inactive_nodes : bool
        True to remove inactive nodes.
        Otherwise full nodelist is always visible. Defaults to False.

    Returns
    -------
    None

    """
    assert len(Gs) == len(labels), "Desired (len(Gs) == len(labels))"

    pos = layout(full_graph)
    fig, ax = plt.subplots(figsize=(15, 15))
    ax.axis("off")

    # Add Edges
    segments = np.array([[pos[x], pos[y]] for x, y in Gs[0].edges()])
    edges = LineCollection(segments, alpha=0.4, linewidths=2, color="#727272")
    ax.add_artist(edges)

    # Add Nodes
    coordinates = np.array([i for i in pos.values()]).T
    nodes = ax.scatter(*coordinates, s=8, alpha=1, color="#ba0000")

    # Add Time indication
    text = ax.text(1.1, 1, labels[0], ha="right", fontsize=56, color='C1', wrap=True)

    # Combine elements into list to pass later on
    actors = [edges, nodes, text]

    def update(i: int, edges, nodes, text, pos, ax):
        """

        Parameters
        ----------
        i: int
            Index of frames.
        edges : np.array
            List of edge locations of previous step.
        nodes : np.array
            List of node locations of previous step.
        text : str
            Text to be shown in upper right corner at each update.
        pos : dict
            Networkx - Matplotlib positional layout dictionary.
        ax : matplotlib.axis
            Matplotlib axis to plot in.


        Returns
        -------
        None

        """
        segments = [[pos[x], pos[y]] for x, y in Gs[i].edges()]
        edges.set_paths(segments)
        if remove_inactive_nodes:
            points = [pos[node] for node in Gs[i].nodes()]
            nodes.set_offsets(points)
        text.set_text(labels[i])

    # Create animation and save it
    ani = animation.FuncAnimation(fig,
                                  update,
                                  frames=len(Gs),
                                  fargs=(*actors, pos, ax),
                                  interval=350,
                                  repeat=False)
    ani.save(save_path)


def heatmap(data, row_labels, col_labels, ax=None, fig=None,
            cbar_kw={}, cbarlabel="", title="", **kwargs):
    """Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data : np.array(
        A 2D numpy array of shape (N, M).
    row_labels : List[str]
        A list or array of length N with the labels for the rows.
    col_labels : List[str]
        A list or array of length M with the labels for the columns.
    ax : matplotlib.axes.Axes
        A `matplotlib.axes.Axes` instance to which the
        heatmap is plotted. If not provided, use current axes or create a new one. Defaults to None.
    fig : matplotlib.figure
        Matplotlib figure object. Defaults to None.
    cbar_kw : dict
        A dictionary with arguments to `matplotlib.Figure.colorbar`. Defaults to {}.
    cbarlabel : str
        The label for the colorbar. Defaults to "".
    title : str
        Title for subfigure. Defaults to "".
    **kwargs : dict
        All other arguments are forwarded to `imshow`.

    Returns
    -------
    im : matplotlib.axis.imshow
        The heatmap object.
    cb : fig.colorbar
        The matplotlib colorbar object as a color legend.

    """
    if not ax:
        ax = plt.gca()

    # Set title
    ax.set_title(title, size=15, pad=20)

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    ax_divider = make_axes_locatable(ax)
    # Add an axes to the right of the main axes.
    cax = ax_divider.append_axes("right", size="5%", pad="2%")
    cb = fig.colorbar(im, cax=cax)
    cb.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=0, ha="right",
             rotation_mode="anchor")

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_yticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    ax.spines[:].set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cb


def annotate_heatmap(im, data=None, valfmt="{x:.2d}",
                     textcolors=("black", "white"),
                     threshold=None, **textkw):
    """Annotate a heatmap.

    Source:
        https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html

    Parameters
    ----------
    im : AxesImage
        The AxesImage to be labeled.
    data : List[str]
        Data used to annotate.  If None, the image's
        data is used. Defaults to None.
    valfmt : str
        The format of the annotations inside the heatmap.
        This should either use the string format method, e.g. "$ {x:.2f}",
        or be a `matplotlib.ticker.Formatter`. Defaults to "{x:.2d}".
    textcolors : tuple
        A pair of colors.  The first is used for values
        below a threshold, the second for those above. Defaults to ("black", "white").
    threshold : float
        Value in data units according to which the colors from
        textcolors are applied.  If None (the default) uses the middle of the colormap as
        separation. Defaults to None.
    "white") :

    **textkw :


    Returns
    -------
    texts : List[str]
        The texts that go in each cell of the heatmap.

    """
    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts


def plotHeatmaps(gs, dm, cmaps, suptitle="Degree measures over time",
                 path="centralities.png"):
    """Plot network heatmap centrality mappings changing over time.

    Parameters
    ----------
    gs : List[nx.Graph]
        List of networkx graphs over time.
    dm : List[List[nx.__centrality function]]
        2d list of centrality measures.
        Shape will be same as grid for heatmap visualizations
    cmaps : List[List[matplotlib colormaps]]
        2d list of same shape as dm.
    suptitle :
         (Default value = "Degree measures over time")
    path :
         (Default value = "centralities.png")

    Returns
    -------
    None

    """
    fig, axes = plt.subplots(dm.shape[0], dm.shape[1], figsize=(30, 13.5))
    fig.suptitle(suptitle, fontsize=20)
    for i, axs in enumerate(axes):
        for j, ax in enumerate(axs):
            # Get degree data
            try:
                degrees = [dm[i][j](g) for g in gs]
            except nx.exception.PowerIterationFailedConvergence:
                degrees = [dm[i][j](g, max_iter=500) for g in gs]

            # Find max degree value
            max_ = max([max(list(degree.values())) for degree in degrees])

            # Create histogram for each timestep
            freqs = [
                np.histogram(list(degree.values()), bins=np.linspace(0, max_,
                                                                     10))[0]
                for degree in degrees
            ]
            # Normalize frequencies
            freqs = np.array([f / sum(f) for f in freqs])

            # Create datastruct
            data = {
                "timepoints": list(range(len(freqs))),
                "bins": ['{0:.1e}'.format(t) for t in np.linspace(0, max_, 10)][:-1],
                "data": freqs.T
            }

            # Make heatmap
            im, cbar = heatmap(data["data"],
                               data["bins"],
                               data["timepoints"],
                               ax=ax,
                               fig=fig,
                               cmap=cmaps[i][j],
                               cbarlabel="Frequency in %",
                               title=f"{dm[i][j].__name__}")
            annotate_heatmap(im, valfmt="{x:.2f}")

    fig.tight_layout()
    plt.savefig(path)
    plt.show()
