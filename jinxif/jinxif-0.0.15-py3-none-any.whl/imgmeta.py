####
# title: metadata.py
#
# language: Python3.8
# date: 2020-07-00
# license: GPL>=v3
# author: Jenny, bue
#
# description:
#   jinxif pipeline python3 library using python bioformats to extract image metadata.
#
# note 20201103 and 20210621:
#   unfortunately bioformats needs to run java and javabridge, which is ok with linux.
#   I never could figure out who to get this cascade propperly instaled under windows10 and macosx. And belive me, i tried hard.
#   also, only bioformats will put czi metadata into ome standard, the python libraris aicsimageio and czifile will not work.
#   and the python libraries tiffle and apeer-ometiff-library can't read czi files.
#
#   for linux conda installation
#   1. conda install -c conda-forge openjdk
#   2. conda install -c conda-forge python-javabridge
#   3. conda install -c bioconda python-bioformats
####


# libraries
#import argparse
import bioformats
from itertools import cycle
#import javabridge
from jinxif import basic
from jinxif import config
import matplotlib.pyplot as plt
import os
import pandas as pd
from PIL import Image
import re
import seaborn as sns
import sys


# development
#import importlib
#importlib.reload()


# functions
def fetch_meta_image(
        s_image,
        s_regex = None,
    ):
    '''
    version: 2021-07-30

    input:
        s_image: path and filename to image
        s_regex: dictionary of regular expression string to parse and extract e.g.
            'ExposureTime': r'<Key>Information\|Image\|Channel\|ExposureTime</Key><Value>\[([,\d ]+)]</Value>', # exposer time values in milisecond
            'ScenePosition': r'<Key>Information\|Image\|S\|Scene\|CenterPosition</Key><Value>\[([-.,\d ]+)]</Value>',

    output:
        ds_found: dictionary extracted metadata information, derived from ds_regex.
        s_meta: all bioformats metadata form this image stored as string.

    description:
        function to extract from a bioformat compatible image metadata.
    '''
    print(f'process image: {s_image} ...')
    # get bioformats metadata
    #javabridge.start_vm(class_path=bioformats.JARS)
    s_meta = bioformats.get_omexml_metadata(path=s_image)
    #o = bioformats.OMEXML(s_meta)
    #javabridge.kill_vm()
    #print(o.image().Name)
    #print(o.image().AcquisitionDate)
    #print('\n*** s_meta ***\n', s_meta)

    # extract information
    s_found = None
    if not (s_regex is None):
        o_found = re.search(s_regex, s_meta)
        if not (o_found is None):
            s_found = o_found[1]

    # output
    return(s_found, s_meta)


def fetch_meta_slide_exposuretime(
        df_img,
        s_metadir = config.d_nconv['s_metadir'],  #'./MetaImages/'
    ):
    '''
    version: 2021-07-30

    input:
        df_img: dataframe retrieved with basic.parse_czi function.
        s_metadir: exposer time csv file output directory.

    output:
        csv file with exposure time image metadata information.

    description:
        function which calles for every scene per slide,
        for each round the fetch_meta_image  function.
        the gathers exposure time results is writes them to a csv file.
    '''
    # export exposure time
    for s_slide in sorted(set(df_img.slide)):
        print(f'\nfetch_meta_slide_exposuretime: {s_slide} ...')

        # for each slide
        df_meta = pd.DataFrame()
        df_img_slide = df_img.loc[df_img.slide==s_slide,:]
        es_column = set(df_img_slide.columns)        

        if ('slide_mscene' in es_column):
            # for each slide_mscene
            for s_slidemscene in  sorted(set(df_img_slide.slide_mscene)):
                df_img_mscene = df_img_slide.loc[df_img_slide.slide_mscene==s_slidemscene,:]

                # for each image get relevant meta data
                for s_image in df_img_mscene.index:
                    s_found, _ = fetch_meta_image(
                        s_image = f'{df_img_mscene.index.name}{s_image}',
                        s_regex = r'<Key>Information\|Image\|Channel\|ExposureTime</Key><Value>\[([,\d ]+)]</Value>', # exposer time values in nanosecond
                    )
                    # exposure time metadata type specific manipulation
                    l_meta = [n.strip() for n in s_found.split(',')]
                    l_meta = [int(n) / 1000000 for n in l_meta]
                    # update output dataframe
                    se_meta = pd.Series(l_meta, name=s_image, index=config.d_nconv['ls_color_order_czi'][0:len(l_meta)])
                    se_meta = df_img_mscene.loc[s_image,:].append(se_meta)
                    df_meta = df_meta.append(se_meta)

        else:
            # for each slide image get relevant meta data
            for s_image in df_img_slide.index:
                s_found, _ = fetch_meta_image(
                    s_image = f'{df_img_slide.index.name}{s_image}',
                    s_regex = r'<Key>Information\|Image\|Channel\|ExposureTime</Key><Value>\[([,\d ]+)]</Value>', # exposer time values in nanosecond
                )
                # exposure time metadata type specific manipulation
                l_meta = [n.strip() for n in s_found.split(',')]
                l_meta = [int(n) / 1000000 for n in l_meta]
                # update output dataframe
                se_meta = pd.Series(l_meta, name=s_image, index=config.d_nconv['ls_color_order_czi'][0:len(l_meta)])
                se_meta = df_img_slide.loc[s_image,:].append(se_meta)
                df_meta = df_meta.append(se_meta)

        # write relevant image metadata per slide dataframe to file
        df_meta.index.name = 'exposure_time_ms'
        os.makedirs(s_metadir, exist_ok=True)
        s_opathfile = f'{s_metadir}{s_slide}_ExposureTimes_ms.csv'
        df_meta.to_csv(s_opathfile)
        print(f'write file: {s_opathfile}')


def fetch_meta_slide_sceneposition(
        s_slide,
        s_czidir_original,
        s_metadir = config.d_nconv['s_metadir'],  #'./MetaImages/'
    ):
    '''
    version: 2021-07-30

    input:
        s_slide: slide to be process.
        s_czidir_original: czi directory with at least one non  splited czi files 
            straight from the microscope (non imager processed).
        s_metadir: exposer time csv file output directory.

    output:
        csv file with scene position image metadata information.

    description:
        function which for a slide checks each round czi original file (non splitted), 
        to extract scene position.
        the scene position information is for all rounds the same.
        so, it is enough that one file with the information and is read out.
        gathers the result is writes them to a csv file.
    '''
    # scene position
    b_found = False
    print(f'\nfetch_meta_slide_sceneposition: {s_slide } {s_czidir_original} ...')
    for s_file in sorted(os.listdir(s_czidir_original)):
        print(f'process file: {s_file} ...')
        s_pathfile = s_czidir_original + s_file
        if os.path.isfile(s_pathfile) and (s_file.endswith('.czi') or s_file.endswith('.tif') or s_file.endswith('.tiff')):
            # for each image get relevant meta data
            s_found, _ = fetch_meta_image(
                s_image = s_pathfile,
                s_regex = r'<Key>Information\|Image\|S\|Scene\|CenterPosition</Key><Value>\[([-.,\d ]+)]</Value>',  # scene position values in pixel
            )
            if not (s_found is None):
                print(f'found scene position metadata!')
                # get value
                l_meta = [n.strip() for n in s_found.split(',')]
                df_coor = pd.Series(l_meta, name='value').to_frame()
                # get axis
                os_axis = cycle(['scene_x','scene_y'])
                df_coor['axis'] = [next(os_axis) for _ in range(df_coor.shape[0])]
                # get scene_index
                li_scene_index = list(range(int((df_coor.shape[0] / 2))))
                df_coor['scene_index'] = sorted(li_scene_index + li_scene_index)
                df_coor = df_coor.pivot(index='scene_index', columns='axis', values='value')
                # output
                os.makedirs(s_metadir, exist_ok=True)
                s_opathfile = f'{s_metadir}{s_slide}_ScenePositions_xy.csv'
                df_coor.index.name = f'{s_slide}_mscene_order'
                df_coor.to_csv(s_opathfile)
                print(f'write file: {s_opathfile}')
                b_found = True
                break

    # check if scene position metadata was found.
    if not b_found:
        sys.exit(f'Error @ jinxif.imgmeta.fetch_meta_slide_sceneposition : no original czi file with scene position image metdata found at\n{s_czidir_original}')


def fetch_meta_batch(
        es_slide,
        s_czidir,  #config.d_nconv['s_czidir'],  #'./',  # Cyclic_Image/{batch}/
        s_format_czidir_splitscene = config.d_nconv['s_format_czidir_splitscene'],  #'{}{}/splitscene/',  # s_czidir, s_slide
        s_format_czidir_original = config.d_nconv['s_format_czidir_original'],  #'{}{}/original/',  # s_czidir, s_slide
        b_exposuretime_original = False,
        b_exposuretime_splitscene = True,
        b_sceneposition_original = True,
        s_metadir = config.d_nconv['s_metadir'],  #'./MetaImages/',
    ):
    '''
    version: 2021-07-30

    input:
        es_slide: set of slide labels to fetch exposer time.
        s_czidir: czi main directory for this batch.
        s_format_czidir_splitscene: format string to the directory
            under which the expression time relevant czi files are located.
            it is assumed that the czi files are somehow grouped by slide.
        s_format_czidir_originl: format string to the directory
            under which the position relevant czi files are located.
            it is assumed that the czi files are somehow grouped by slide.
        b_exposuretime: boolean to specify if expression time image metadata should be extracted. 
        b_sceneposition: boolean to specify if scene position image metadata should be extracted.
        s_metadir: metadata csv file output directory.

    output:
        none

    description:
        batch wraper function that calls for each slide the exposure_times_slide function.
        this function will keep you sain, because when python is fired up,
        the javabridge can only be started once before python is re-started again.
        java and oracel sucks.
        + https://github.com/LeeKamentsky/python-javabridge/issues/88
        + https://bugs.java.com/bugdatabase/view_bug.do?bug_id=4712793
    '''
    print(f'run: jinxif.imgmeta.fetch_meta_batch for slide {sorted(es_slide)} ...')

    # for each slide
    for s_slide  in sorted(es_slide):
        # get path
        s_wd_original = s_format_czidir_original.format(s_czidir, s_slide)
        s_wd_splitmscene = s_format_czidir_splitscene.format(s_czidir, s_slide)
     
        # fetch exposure time
        if b_exposuretime_splitscene:
            # get path parse czi  file name
            df_img_splitmscene = basic.parse_czi_splitscene(s_wd=s_wd_splitmscene)
            # slide with one or many scenes
            fetch_meta_slide_exposuretime(
                df_img = df_img_splitmscene,
                s_metadir = s_metadir,
            )
        elif b_exposuretime_original:
            # get path parse czi  file name
            df_img_original = basic.parse_czi_original(s_wd=s_wd_original)
            # slide with one or many scenes
            fetch_meta_slide_exposuretime(
                df_img = df_img_original,
                s_metadir = s_metadir,
            )

        # fetch scene position
        if b_sceneposition_original:
            # slide with one or many scenes
            fetch_meta_slide_sceneposition(
                s_slide = s_slide,
                s_czidir_original = s_wd_original,
                s_metadir = s_metadir,
            )


def load_exposure_df(
        s_slide,
        s_metadir = config.d_nconv['s_metadir'],  #'./MetaImages/',
    ):
    '''
    version: 2021-07-30

    input:
        s_slide: slide to load exposure data from.
        s_metadir: metadata csv file directory.

    output:
        df_load: dataframe with exposure time data.

    description:
        load exposure time csv extracted form image metadata
        with imgmeta.fetch_meta_batch function.
    '''
    print(f'run: jinxif.imgmeta.load_exposure_df for slide {s_slide} ...')

    # load exposure metadata
    df_load = pd.read_csv(
        s_metadir + f'{s_slide}_ExposureTimes_ms.csv',
        index_col = 0,
        dtype = {'round_int': int, 'round_real': float, 'round_order': int},
    )

    # stack exposure values
    df_exposure = df_load.loc[:, df_load.columns.isin(config.d_nconv['ls_color_order_czi'])]
    df_exposure  = df_exposure.stack().reset_index()
    df_exposure.columns = ['exposure_time_filename','color','exposure_time_ms']

    # merge back to parse_czi_original information and get marker
    df_img = df_load.loc[:, ~df_load.columns.isin(config.d_nconv['ls_color_order_czi'])]
    df_img.index.name = 'exposure_time_filename'
    df_img.reset_index(inplace=True)
    df_load = pd.merge(df_img, df_exposure, on='exposure_time_filename')
    basic._handle_colormarker(
        df_img = df_load,
        s_round = config.d_nconv['s_round_jinxif'],
        s_quenching = config.d_nconv['s_quenching_jinxif'],
        s_color_dapi = config.d_nconv['s_color_dapi_jinxif'],
        ls_color_order = config.d_nconv['ls_color_order_jinxif'],
        s_sep_marker = config.d_nconv['s_sep_marker_jinxif'],
        s_sep_markerclone = config.d_nconv['s_sep_markerclone_jinxif'],
    )

    # output
    #print('jinxif.imgmeta.load_exposure_df:', df_load.info())
    return(df_load)


def load_position_df(
        s_slide,
        s_metadir = config.d_nconv['s_metadir'],  #'./MetaImages/',
    ):
    '''
    version: 2021-07-30

    input:
        s_slide: slide to load exposure data from.
        s_metadir: metadata csv file directory.

    output:
        df_load: dataframe with exposure time data.

    description:
        load scene center position csv extracted form image metadata
        with imgmeta.fetch_meta_batch function.
        position data is extracted from round 1.
        this make sense, as image registartion is always done against round 1.
    '''
    print(f'run: jinxif.imgmeta.load_position_df for slide {s_slide} ...')

    # load scene center position metadata
    df_load = pd.read_csv(
        s_metadir + f'{s_slide}_ScenePositions_xy.csv',
        index_col = 0,
    )

    # reshape loaded data
    # nop

    # output
    print('jinxif.imgmeta.load_position_df:', df_load.info())
    return(df_load)


def exposure_matrix(
        s_batch,
        es_slide,
        tr_figsize = (32,20),
        s_metadir = config.d_nconv['s_metadir'],  #'./MetaImages/',
    ):
    '''
    version: 2021-07-30

    input:
        s_batch: batch identifier.
        tr_figsize: flatline heatmap plot figure size defind by (w,h) in inch.
        es_slide: slides to load exposure data from.
        s_metadir: metadata csv file directory.

    output:
        batch_exposure_time_ms_matrix.png: a flat line and matrix plot to spot exposure time setting errors.
        batch_exposure_time_ms_matrix.csv: numeric matrix to spot exposure time setting errors.

    description:
        load exposure time csv extracted form image metadata
        with imgmeta.fetch_meta_batch function.
    '''
    # load an manipulate data
    b_first = True
    df_all = pd.DataFrame()
    for s_slide in sorted(es_slide):
        df_load =  load_exposure_df(
            s_slide = s_slide,
            s_metadir = s_metadir,
        )
        df_load.index = df_load.loc[:,'round'] + '_' + df_load.loc[:,'color'] + '_' + df_load.loc[:,'marker']
        df_load.index.name = 'round_color_marker'
        if b_first: 
            es_column = set(df_load.columns)
            if ('slide_mscene' in es_column):
                s_unit = 'slide_mscene'
            else:
                s_unit = 'slide'
            b_first = False
        df_all = df_all.append(df_load.loc[:,[s_unit,'exposure_time_ms']])
    df_all = df_all.pivot(columns=s_unit)
    df_all.columns = df_all.columns.droplevel(level=0)

    # add summary row and column
    df_all['exposure_mean'] = df_all.sum(axis=1) / df_all.notna().sum(axis=1)
    se_sum = df_all.sum()
    se_sum.name = 'exposure_sum'
    df_all = df_all.append(se_sum)

    # write data matrix to file
    df_all.to_csv(s_metadir + f'{s_batch}_exposure_time_ms_matrix.csv')

    # generate flatline plot
    fig,ax = plt.subplots(figsize=(tr_figsize[0] - 1, tr_figsize[1] * 1/5))
    se_sum.plot(kind='line', rot=90, grid=True, x_compat=True, title=f'{s_batch}_exposure_time_ms_summary', ax=ax)
    ax.set_xticks(range(se_sum.shape[0]))
    ax.set_xticklabels(list(se_sum.index))
    ax.set_ylabel('exposure time sum [ms]')
    s_file_flatiline = f'{s_batch}_exposure_time_ms_line.png'
    plt.tight_layout()
    fig.savefig(s_metadir + s_file_flatiline, facecolor='white')
    plt.close()

    # generate heatmap
    df_all.drop('exposure_sum', axis=0, inplace=True)
    fig,ax = plt.subplots(figsize=(tr_figsize[0], tr_figsize[1] * 4/5))
    sns.heatmap(df_all, annot=False, linewidths=.1, cmap='magma', ax=ax)
    s_file_heat = f'{s_batch}_exposure_time_ms_heat.png'
    plt.tight_layout()
    fig.savefig(s_metadir + s_file_heat, facecolor='white')
    plt.close()
 
    # merge tmp png to final png
    img_flatline = Image.open(s_metadir + s_file_flatiline)
    img_heat = Image.open(s_metadir + s_file_heat)
    img_result = Image.new('RGB', (img_heat.width, img_flatline.height + img_heat.height), color='white')
    img_result.paste(img_flatline, (0, 0), mask=img_flatline)
    img_result.paste(img_heat, (0, img_flatline.height), mask=img_heat)
    s_file_matrix = f'{s_batch}_exposure_time_ms_matrix.png'
    img_result.save(s_metadir + s_file_matrix, dpi=(720,720))
    os.remove(s_metadir + s_file_heat)
    os.remove(s_metadir + s_file_flatiline)


# run from the command line
#if __name__ == '__main__':

    # specify command line argument
#    parser = argparse.ArgumentParser(description='run jinxif.extract.imgmeta.fetch_meta_batch.')
#    parser.add_argument(
#        'slide',
#        help='one or more slide indetifier',
#        type=str,
#        nargs='+',
#    )
#    parser.add_argument(
#        '-o',
#        '--codedir',
#        help='path to write output file (default ./)',
#        default='./',
#        type=str,
#    )
#    parser.add_argument(
#        '-i',
#        '--czidir',
#        help='path format string to czi inputfile. it is assumed that czi files are organized by slides.',
#        default='./{}/original/',
#        type=str,
#    )
#    args = parser.parse_args()
#    print('ls_slide:', args.slide)
#    print('s_metadir:', args.codedir)
#    print('s_czidir:', args.czidir)

    # run code
#    javabridge.start_vm(class_path=bioformats.JARS)
#    fetch_meta_batch(
#        ls_slide = args.slide,
#        s_metadir = args.codedir,
#        s_czidir = args.czidir,
#        s_czitype='r',
#    )
#    javabridge.kill_vm()

