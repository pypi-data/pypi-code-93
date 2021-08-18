#####
# title: jfplt.py
#
# language: python3
# author: Jenny, bue
# license: GPLv>=3
# date: 2021-04-00
#
# description:
#     jinxif python3 library to generat output for quality control
#####


# library
import matplotlib.pyplot as plt
import numpy as np
import os
from skimage import io, exposure

# development
#import importlib
#importlib.reload()


# generic function
# BUE 20210430: maybe core can be fused with array_roi?
def array_img_scatter(
        df_img,
        s_xlabel = 'color',
        ls_ylabel = ['round','exposure'],
        s_title = 'marker',
        ti_array = (2,4),
        ti_fig = (8,11),
        cmap = 'gray',
        dl_crop = {},
        s_pathfile = './array_img_scatter.png',
    ):
    '''
    version: 2021-06-29
    BUE: internal function, but ther is an mpimage.array_roi, mpimage.array_roi_if, mpimage.roi_if_border too.

    input:
        df_img: image metadata datafarme, indexed by filenames, index.name is the path.
        s_xlabel: figure x label, which have to be a df_img column label.
        ls_ylabel: figure y labels, which have to be df_img column labels.
        s_title: figure title, which have to be a df_img column label.
        ti_array: x,y image grid parameter.
        ti_fig: x,y figure size parameter in inch.
        cmap: matplotlib colormap name.
        dl_crop: dictionary of crop parameters. the dictionary format is something like
            {'slide_scene': [0,0, 0,0, 'xyxy'], 'slide_scene': [0,0, 0,0, 'xywh']}
        s_pathfile: string to specify output path and filename.

    output:
        fig: matplotlib figure.

    description:
        generate a grid of scatter plot images.
    '''
    # generate figure
    fig, ax = plt.subplots(ti_array[0], ti_array[1], figsize=ti_fig)
    ax = ax.ravel()
    for i_ax, s_index in enumerate(df_img.index):

        # generate subplot labels
        s_row_label = f'{df_img.loc[s_index, ls_ylabel[0]]}\n {df_img.loc[s_index, ls_ylabel[1]]}'
        s_col_label = df_img.loc[s_index, s_xlabel]
        s_label_img = df_img.loc[s_index, s_title]

        # load, rescale and crop subplot image
        a_image = io.imread(f'{df_img.index.name}{s_index}')
        i_rescale_max = int(np.ceil(1.5 * np.quantile(a_image, 0.98)))
        a_rescale = exposure.rescale_intensity(a_image, in_range=(0, i_rescale_max))

        # cropping
        if len(dl_crop)!= 0:
            l_crop = dl_crop[df_img.loc[s_index,'slide_scene']]
            if (l_crop[-1] == 'xywh'):
                a_rescale = a_rescale[l_crop[1]:(l_crop[1]+l_crop[3]), l_crop[0]:(l_crop[0]+l_crop[2])]
            elif (l_crop[-1] == 'xyxy'):
                a_rescale = a_rescale[l_crop[1]:(l_crop[1]+l_crop[3]), l_crop[0]:(l_crop[0]+l_crop[2])]
            else:
                sys.exit('Error : @ jinxif.jfplt._array_img : unknown crop coordinate specification in dl_crop {l_crop[-1]}.\nknowen are xyxy and xywh.')

        # generate subplot
        ax[i_ax].imshow(a_rescale, cmap=cmap)
        ax[i_ax].set_title(s_label_img)
        ax[i_ax].set_ylabel(s_row_label)
        ax[i_ax].set_xlabel(f'{s_col_label}\n 0 - {i_rescale_max}[px intensity]')

    # earse empty ax
    for i_ax in range(df_img.shape[0], len(ax)):
        ax[i_ax].axis('off')

    # title
    fig.suptitle(f'{df_img.loc[s_index, s_xlabel]} {df_img.loc[s_index, ls_ylabel[1]]}')

    # output figure
    plt.tight_layout()
    s_path = '/'.join(s_pathfile.replace('\\','/').split('/')[:-1])
    os.makedirs(s_path, exist_ok=True)
    fig.savefig(s_pathfile, facecolor='white')
    plt.close()
    print(f'save plot: {s_pathfile}')

