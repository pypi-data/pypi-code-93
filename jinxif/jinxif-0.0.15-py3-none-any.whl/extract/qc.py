#####
# title: qc.py
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
import os
from jinxif.extract import basic
import matplotlib.pyplot as plt
import numpy as np
import skimage
from skimage import io

# BUE 20210430: maybe core can be fused with array_roi
def _array_img(
        df_img,
        s_xlabel='color',
        ls_ylabel=['rounds','exposure'],
        s_title='marker',
        ti_array=(2,4),
        ti_fig=(10,20),
        cmap='gray',
        d_crop={}
    ):
    '''
    version: 2021-03-31
    BUE: internal function, but ther is an mpimage.array_roi, mpimage.array_roi_if, mpimage.roi_if_border too.

    input:
        df_img: image metadata datafarme, indexed by filenames, index.name is the path.
        s_xlabel: figure x label, which have to be a df_img column label.
        ls_ylabel: figure y labels, which have to be df_img column labels.
        s_title: figure title, which have to be a df_img column label.
        ti_array: x,y image grid parameter.
        ti_fig: x,y figure size parameter in inch.
        cmap: matplotlib colormap name.
        d_crop: dictionary of crop parameters. bue 20201114: a bit more details for this parameter would be good.

    output:
        fig: matplotlib figure.

    description:
        generate a grid of images.
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
        a_image = skimage.io.imread(f'{df_img.index.name}{s_index}')
        a_rescale = skimage.exposure.rescale_intensity(a_image, in_range=(0, 1.5*np.quantile(a_image,0.98)))
        if len(d_crop)!= 0:
            ti_crop = d_crop[df_img.loc[s_index,'scene']]
            a_rescale = a_rescale[(ti_crop[1]):(ti_crop[1]+ti_crop[3]),(ti_crop[0]):(ti_crop[0]+ti_crop[2])]

        # generate subplot
        ax[i_ax].imshow(a_rescale,cmap=cmap)
        ax[i_ax].set_title(s_label_img)
        ax[i_ax].set_ylabel(s_row_label)
        ax[i_ax].set_xlabel(f'{s_col_label}\n 0 - {int(1.5*np.quantile(a_image,0.98))}')

    # earse empty ax
    for i_ax in range(df_img.shape[0], len(ax)):
        ax[i_ax].axis('off')

    # title
    fig.suptitle(f'{df_img.loc[s_index, s_xlabel]} {df_img.loc[s_index, ls_ylabel[1]]}')

    # output figure
    plt.tight_layout()
    return(fig)


# BUE 20210430: maybe core visualize_raw_images and visualize_reg_images can be fused?
# and codex.visualize_reg_images and mics.visualize_reg_images
def visualize_raw_images(df_img, s_qcdir, s_color='c1'):
    '''
    version: 2020-03-31

    input:
        df_img: data farme which contains metadata information about the images,
            idexed by image filenames, index.name is the path.
        s_qcdir: qc directory path.
        s_color: microscpy channel to check. default is c1 is DAPI.

    output:
        png plot

    description:
        generte array raw images to check tissue identity, focus, etc.
    '''
    for s_slide in sorted(set(df_img.slide)):
        print(f'\nvisualize_raw_images for slide: {s_slide} ...')
        df_img_slide = df_img[df_img.slide==s_slide]
        for s_scene in sorted(df_img_slide.scene.unique()):
            print(f'scene: {s_scene}')
            # generate figure
            df_dapi = df_img_slide[(df_img_slide.color==s_color) & (df_img_slide.scene==s_scene)].sort_values(['round_ord','rounds'])
            df_dapi.index.name = df_img.index.name
            fig = _array_img(
                df_img=df_dapi,
                s_xlabel='slide',  # reg: marker
                ls_ylabel=['scene','color'],
                s_title='rounds',
                ti_array=(2, len(df_dapi)//2 + 1),  # // is floor division
                ti_fig=(24,10),
                cmap='gray',
                d_crop={},
            )
            # ouput figure
            s_path = f'{s_qcdir}RawImages/'
            s_pathfile = f'{s_path}{s_slide}-Scene-{s_scene}_{s_color}_all.png'
            os.makedirs(s_path, exist_ok=True)
            fig.savefig(s_pathfile)
            print(f'save plot: {s_pathfile}')


def visualize_reg_images(s_regdir, s_qcdir, s_color='c1', s_slide=None):
    '''
    version: 2021-04-20

    input:
        s_regdir: registered image path.
        s_qcdir: qc directory path.
        s_color: microscpy channel to check. default is c1 is DAPI.
        s_slide: BUE 20210510 maybe better give as a filter set, None will generate it

    output:
        png plot

    description:
        array registered images to check tissue identity, focus, etc.
    '''
    # check registration
    for s_dir in sorted(os.listdir(s_regdir)):
        s_path = f'{s_regdir}/{s_dir}/'
        if os.path.isdir(s_path) and (s_slide is None or s_dir.startswith(s_slide)):
            s_theslide = s_dir.split('-Scene')[0]  # bue 20210505: actually only used for print command

            # bue: nearly the same as visualize_raw_images
            print(f'\nvisualize_reg_images for slide: {s_theslide} ...')
            df_img = basic.parse_org(s_wd=s_path, s_start='R', s_end='ORG.tif', s_type='reg')  # raw: df_img_slide and here s_type='reg'
            for s_scene in sorted(df_img.scene.unique()):
                print(f'scene: {s_scene}')
                # generate figure
                df_img_scene = df_img[df_img.scene == s_scene]
                df_img_stain = df_img_scene[df_img_scene.color == s_color]
                df_img_sort = df_img_stain.sort_values(['round_ord','rounds'])
                fig = _array_img(
                    df_img_sort,
                    s_xlabel='marker',
                    ls_ylabel=['scene','color'],
                    s_title='rounds',
                    ti_array=(2, len(df_img_sort)//2 + 1),  # // is floor division
                    ti_fig=(24,10)
                )
                # output figure
                s_path = f'{s_qcdir}RegisteredImages/'
                s_pathfile = f'{s_path}{s_scene}_registered_{s_color}.png'
                os.makedirs(s_path, exist_ok=True)
                fig.savefig(s_pathfile)
                print(f'save plot: {s_pathfile}')

