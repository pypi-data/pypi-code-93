import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import cm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import networkx as nx
from fury import actor, window, colormap as fury_cm

from .utils import check_parcellation, to_density, rescale

COLORS = {'ipsi': '#d4d8de',
          'contra': '#c0c4cb',
          'source': '#c0c4cb',
          'Isocortex': '#97d3bb',
          'OLF': '#9dd08c',
          'HPF': '#07a56e',
          'CTXsp': '#b7dcb9',
          'STR': '#c7daf0',
          'PAL': '#7aa0d4',
          'TH': '#ee512c',
          'HY': '#f58e8d',
          'MB': '#8568ae',
          'P': '#f47836',
          'MY': '#f7e2e5',
          'CB':  '#f5ee74'}

TEXT = {'ipsi': 'Ipsilateral Target',
        'contra': 'Contralateral Target',
        'source': 'Source',
        'Isocortex': 'ICTX',
        'OLF': 'OLF',
        'HPF': 'HPF',
        'CTXsp': 'CTXsp',
        'STR': 'STR',
        'PAL': 'PAL',
        'TH': 'TH',
        'HY': 'HY',
        'MB': 'MB',
        'P': 'P',
        'MY': 'MY',
        'CB':  'CB'}


def _label_rect(rect, text, ax, rotation=0):
    '''
    Utility function for labeling a Rectangle object.

    Parameters
    __________
    rect : matplotlib.patches.Rectangle
        Rectangle object to be labeled
    text : str
        Label text
    ax : matplotlib.axes._subplots.AxesSubplot
        Figure ax
    rotation : float
        Rotation angle for label. Default is 0.

    Returns
    _______
    ax : matplotlib.axes._subplots.AxesSubplot
        Figure ax
    '''
    ax.add_patch(rect)
    rx, ry = rect.get_xy()
    cx = rx + rect.get_width() / 2.0
    cy = ry + rect.get_height() / 2.0
    ax.annotate(text, (cx, cy), ha='center', va='center',
                rotation=rotation, fontsize=17.5)

    return ax


def connectivity_matrix(data, parcellation, vmin, vmax, cmap='inferno'):
    '''
    Function for generating a labeled connectivity matrix figure
    in a similar style to Figure 3 in "A mesoscale connectome of
    the mouse brain" (Oh et al, 2014). Note that this assumes

    Parameters
    __________
    data : ndarray
        2D connectivity matrix. Assumes hemispheric symmetry with "sources"
        as rows, and ipsi- and contralateral "targets" as columns,
        respectively.
    parcellation : pandas DataFrame
        Must contain a row for every node and a "Brain Division" column
        with strings matching the names of one of the 12 major brain
        divisions listed in the Allen atlas.
    vmin : float
        Minimum display value
    vmax : float
        Maximum display value
    cmap : str
        Matplotlib colormap. Default is 'inferno'


    Returns
    _______
    fig : matplotlib.figure.Figure
        Matplotlib figure
    ax : matplotlib.axes._subplots.AxesSubplot
        Figure ax
    '''

    # Error if division labels aren't as expected
    check_parcellation(parcellation)

    # 12 major brain divisions in Allen Atlas
    brain_divisions = ['Isocortex', 'OLF', 'HPF', 'CTXsp', 'STR',
                       'PAL', 'TH', 'HY', 'MB', 'P', 'MY', 'CB']
    brain_divisions = parcellation['Brain Division'].unique()

    # Maps nodes to brain divisions
    masks = {}
    for division in brain_divisions:
        masks[division] = np.array(parcellation['Brain Division'] == division)
    ny, nx = data.shape

    # Get mpl colormap and set nan/inf values to black
    cmap = getattr(cm, cmap).with_extremes(bad='k')

    # Pad matrix to include labels
    hemilabel_dx = 20
    structlabel_dx = 40
    buff = hemilabel_dx + structlabel_dx
    mat = np.zeros((ny + buff, nx + buff))
    mat[buff:, buff:] = data

    # Initialize figure
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_axis_off()

    # Display data
    im = ax.imshow(mat, cmap=cmap, vmin=vmin, vmax=vmax)

    # Add gray blocks for contra/ipsi/source and add text
    ipsi_rect = patches.Rectangle(xy=(buff-0.5, -0.5),
                                  width=nx // 2,
                                  height=hemilabel_dx,
                                  facecolor=COLORS['ipsi'])
    contra_rect = patches.Rectangle(xy=(buff + nx//2 - 0.5, -0.5),
                                    width=nx // 2,
                                    height=hemilabel_dx,
                                    facecolor=COLORS['contra'])
    source_rect = patches.Rectangle(xy=(-0.5, buff-0.5),
                                    width=hemilabel_dx,
                                    height=ny,
                                    facecolor=COLORS['source'])
    _label_rect(ipsi_rect, TEXT['ipsi'], ax)
    _label_rect(contra_rect, TEXT['contra'], ax)
    _label_rect(source_rect, TEXT['source'], ax, rotation=90)

    # Adds white rect for colorbar
    corner_rect = patches.Rectangle(xy=(-0.5, -0.5), width=buff,
                                    height=buff, facecolor='white')
    ax.add_patch(corner_rect)

    # Add colored patch labels for each brain division
    for division in brain_divisions:
        src_rect = ax.add_patch(
            patches.Rectangle(xy=(hemilabel_dx - 0.5,
                                  buff-0.5 + np.where(masks[division])[0][0]),
                              width=structlabel_dx,
                              height=masks[division].sum(
            ),
                facecolor=COLORS[division]))
        _label_rect(src_rect, TEXT[division], ax)

        # Rotate so they will fit
        if division in ['OLF', 'HPF', 'CTXsp', 'STR', 'PAL']:
            rotation = 90
        else:
            rotation = 0

        tgt_r_rect = ax.add_patch(
            patches.Rectangle(xy=(buff - 0.5 + np.where(masks[division])[0][0],
                                  hemilabel_dx-0.5),
                              width=masks[division].sum(
            ),
                height=structlabel_dx,
                facecolor=COLORS[division]))
        _label_rect(tgt_r_rect, TEXT[division], ax, rotation=rotation)

        tgt_l_rect = ax.add_patch(
            patches.Rectangle(
                xy=(nx // 2 + buff - 0.5 + np.where(masks[division])[0][0],
                    hemilabel_dx-0.5),
                width=masks[division].sum(
                ),
                height=structlabel_dx,
                facecolor=COLORS[division]))

        _label_rect(tgt_l_rect, TEXT[division], ax, rotation=rotation)

    fig.tight_layout()

    # Add colorbar
    cbax = inset_axes(ax, width="75%", height="20%", loc='center',
                      bbox_to_anchor=corner_rect.get_bbox(),
                      bbox_transform=ax.transData,
                      borderpad=0)
    cbar = fig.colorbar(im, cax=cbax, orientation='horizontal',
                        ticks=[vmin, vmax])
    cbar.ax.set_xticklabels([vmin, vmax], fontdict={'fontsize': 13})
    cbar.ax.set_title(r'Log$_{10}$', fontsize=13)

    return fig, ax


def plot_spearman_correlation_matrix(corr):
    '''
    Function for generating a labeled heatmap of spearman correlation
    values between the 12 major brain divisions defined in the Allen
    Atlas. 

    Parameters
    __________
    corr : ndarray
        Correlation matrix (shape=(12,24)) between two brain graphs. 
        Assumes hemispheric symmetry and that there are values for all 12
        divisions.

    Returns
    _______
    fig : matplotlib.figure.Figure
        Matplotlib figure
    ax : matplotlib.axes._subplots.AxesSubplot
        Figure ax
    '''

    # Check shape
    if corr.shape != (12, 24):
        raise ValueError('Incorrect brain divisions')

    # Make division text labels
    division_labs = ['ICTX', 'OLF', 'HPF', 'CTXsp', 'STR', 'PAL', 'TH',
                     'HY', 'MB', 'P', 'MY', 'CB']
    i_labs = [lab + '-I' for lab in division_labs]
    c_labs = [lab + '-C' for lab in division_labs]
    target_labs = i_labs + c_labs

    fig, ax = plt.subplots(figsize=(14, 8))
    ax = sns.heatmap(data=corr,
                     vmin=-1,
                     vmax=1,
                     center=0,
                     cmap='coolwarm',
                     cbar=True,
                     cbar_kws={'shrink': 0.7},
                     annot=False,
                     square=True,
                     ax=ax)
    ax.axvline(12, color='k', lw=2.5)
    ax.xaxis.tick_top()
    ax.set_xticks(np.arange(24))
    ax.set_xticklabels(target_labs, rotation=45, fontsize=20)
    ax.set_yticklabels(division_labs, rotation=0, fontsize=20)
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=18)
    fig.tight_layout()
    return fig, ax


def vis_strongest_nodes(positions, edges, out_path, n_nodes=85, density=30.):
    '''
    Function for generating a network diagram of hub-node connectivity in
    physical coordinates. Saves results to three .pngs along the three major
    axes: coronal, sagittal, and axial. Built with fury, which is a wrapper
    for vtk.

    Parameters
    __________
    positions : 2D ndarray, shape=(n_nodes,3)
        Gives the 3D coordinates of the nodes
    edges : ndarray
        2D Connectivity matrix
    out_path : str
        Path to save three output images
    n_nodes : int
        The function will plot connections between the top n_nodes strongest
        nodes. Default is 85.
    density : float
        For visual clarity, only the top density% of edges will be retained
        before plotting. Default is 30.

    Returns
    _______
    fig : matplotlib.figure.Figure
        Matplotlib figure
    ax : matplotlib.axes._subplots.AxesSubplot
        Figure ax
    '''

    # Get node strengths
    s = edges.sum(0)
    n = s.size
    topinds = np.argpartition(s, -n_nodes)[-n_nodes:]  # hub mask

    # Get node colormap
    node_colors = fury_cm.create_colormap(rescale(s), name='Reds')

    # Set node radii
    node_radii = np.ones(n)
    node_radii[topinds] = 2

    # Draw nodes
    sphere_actor = actor.sphere(centers=positions,
                                colors=node_colors,
                                radii=node_radii,
                                theta=16,
                                phi=16)

    # Cut off weak edges
    edges = to_density(edges, density)

    # Set hub-hub edge mask
    indicator = np.zeros(n)
    indicator[topinds] = 1
    hub_mask = np.outer(indicator, indicator).astype(bool)

    # Get line coordinates
    hub = []
    G = nx.from_numpy_array(edges)
    for i, (source, target) in enumerate(G.edges):
        if hub_mask[source, target]:
            hub.append([positions[source], positions[target]])

    # Plot hub=hub connections
    hub_actor = actor.line(hub,
                           colors=(10/255, 146/255, 170/255),
                           opacity=0.9,
                           fake_tube=False,
                           linewidth=2)

    # Add all drawings
    scene = window.Scene()
    scene.SetBackground(1, 1, 1)
    scene.add(sphere_actor)
    scene.add(hub_actor)

    # Axial view
    ax = ((56.95265197753906, 62.10136151313782, 298.74040937106),
          (56.95265197753906, 62.10136151313782, 39.182297468185425),
          (0.0, 1.0, 0.0))

    # Sagittal view
    sag = ((314.91325665203874, 56.29049421834477, 67.34208638488903),
           (56.95265197753906, 62.10136151313782, 39.182297468185425),
           (0, 0, 1.0))

    # Coronal view
    cor = ((51.835648827121794, 320.87046418270796, 58.747093325219794),
           (56.95265197753906, 62.10136151313782, 39.182297468185425),
           (0, 0, 1))

    # Save all
    for view, name in zip([ax, sag, cor], ['ax', 'sag', 'cor']):
        scene.set_camera(*view)
        window.record(scene,
                      size=(1000, 1000),
                      magnification=2,
                      reset_camera=False,
                      out_path=out_path + name + '.png')
