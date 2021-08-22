####
# title: metadata.py
#
# language: Python3.8
# date: 2020-07-00
# license: GPL>=v3
# author: Jenny, bue
#
# description:
#   jinxif pipeline python3 library using python aicsimageio library and xml elemnttree to extract image metadata.
#   spezial thanks to AICSImageIO: https://github.com/AllenCellModeling/aicsimageio
#   spezial thanks  to Step Howson: https://www.datacamp.com/community/tutorials/python-xml-elementtree
#   spezial thanks to python xml element tree library: https://docs.python.org/3/library/xml.etree.elementtree.html#module-xml.etree.ElementTree 
####


# libraries
from aicsimageio import AICSImage
from jinxif import basic
from jinxif import config
import matplotlib.pyplot as plt
import os
import pandas as pd
from PIL import Image
import re
import seaborn as sns
import sys
import xml.etree.ElementTree as ET


# development
#import importlib
#importlib.reload()


# functions
def fetch_meta_slide_exposuretime(
        df_img,
        s_metadir = config.d_nconv['s_metadir'],  #'./MetaImages/'
    ):
    '''
    version: 2021-08-21

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
                    s_pathimage = df_img_mscene.index.name+s_image
                    print(f'process image: {s_pathimage} ...')

                    # load metadata
                    o_img = AICSImage(s_pathimage)
                    x_root = o_img.metadata
                    #print(x_root.tag)

                    # get exposure time
                    di_exposuretime_ms = {}
                    for x_channel in x_root.findall("./Metadata/Information/Image/Dimensions/Channels/Channel"):
                        x_exposuretime = x_channel.find('./ExposureTime')
                        #print(x_channel.attrib)
                        #print(x_exposuretime.text)
                        s_color = x_channel.attrib['Id'].replace('Channel:', config.d_nconv['s_color_czi']) # trafo to filename acceptable channel string
                        di_exposuretime_ms.update({s_color: int(x_exposuretime.text) / 1000000}) # trafo ns to ms

                    # append exposure time to metadata tabel
                    se_meta = pd.Series(di_exposuretime_ms, name=s_image)
                    se_meta.sort_index(inplace=True)
                    se_meta = df_img_mscene.loc[s_image,:].append(se_meta)
                    df_meta = df_meta.append(se_meta)

        else:
            # for each slide image get relevant meta data
            for s_image in df_img_slide.index:
                s_pathimage = df_img_slide.index.name+s_image
                print(f'process image: {s_pathimage} ...')

                # load metadata
                o_img = AICSImage(s_pathimage)
                x_root = o_img.metadata
                #print(x_root.tag)

                # get exposure time
                di_exposuretime_ms = {}
                for x_channel in x_root.findall('./Metadata/Information/Image/Dimensions/Channels/Channel'):
                    x_exposuretime = x_channel.find('./ExposureTime')
                    #print(x_channel.attrib)
                    #print(x_exposuretime.text)
                    s_color = x_channel.attrib['Id'].replace('Channel:', config.d_nconv['s_color_czi']) # trafo to filename acceptable channel string
                    di_exposuretime_ms.update({s_color: int(x_exposuretime.text) / 1000000}) # trafo ns to ms

                # append exposure time to metadata tabel
                se_meta = pd.Series(di_exposuretime_ms, name=s_image)
                se_meta.sort_index(inplace=True)
                se_meta = df_img_slide.loc[s_image,:].append(se_meta)
                df_meta = df_meta.append(se_meta)

        # write relevant image metadata per slide dataframe to file
        df_meta.index.name = 'exposure_time_ms'
        os.makedirs(s_metadir, exist_ok=True)
        s_opathfile = s_metadir+config.d_nconv['s_format_csv_exposuretime'].format(s_slide)
        df_meta.to_csv(s_opathfile)
        print(f'write file: {s_opathfile}')


def fetch_meta_slide_sceneposition(
        s_slide,
        s_czidir_original,
        s_metadir = config.d_nconv['s_metadir'],  #'./MetaImages/'
    ):
    '''
    version: 2021-08-21

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
    print(f'\nfetch_meta_slide_sceneposition: {s_slide} {s_czidir_original} ...')
    for s_file in sorted(os.listdir(s_czidir_original)):
        s_pathfile = s_czidir_original + s_file
        if os.path.isfile(s_pathfile) and (s_file.endswith('.czi') or s_file.endswith('.tif') or s_file.endswith('.tiff')):
            print(f'process file: {s_file} ...')

            # get s_slide for nameing convention conform filename
            if (s_slide is None):
                o_found = re.search(config.d_nconv['s_regex_czi_original'], s_file)
                s_slide = o_found[config.d_nconv['di_regex_czi_original']['slide']]
                print(f'detected slide id: {s_slide} ...')

            # load metadata
            o_img = AICSImage(s_pathfile)
            x_root = o_img.metadata
            #print(x_root.tag)

            # for each scene get sceneposition
            dlr_sceneposition_xy = {}
            for x_scene in x_root.findall('./Metadata/Information/Image/Dimensions/S/Scenes/Scene'):
                x_centerposition = x_scene.find('./CenterPosition')
                #print(x_scene.attrib)
                #print(x_centerposition.text)
                dlr_sceneposition_xy.update({x_scene.attrib['Index'] : [float(s_value) for s_value in x_centerposition.text.split(',')]})

            # check if data found
            if (len(dlr_sceneposition_xy) > 0):
                # pack dataframe
                df_coor = pd.DataFrame(dlr_sceneposition_xy, index=['scene_x','scene_y']).T
                df_coor.index.name = f'{s_slide}_mscene_order'
                # output
                os.makedirs(s_metadir, exist_ok=True)
                s_opathfile = s_metadir+config.d_nconv['s_format_csv_sceneposition'].format(s_slide)
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
        batch wraper function that calls for each slide the fetch_meta_slide_* functions.
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
        s_metadir+config.d_nconv['s_format_csv_exposuretime'].format(s_slide),
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
        s_metadir+config.d_nconv['s_format_csv_sceneposition'].format(s_slide),
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
    df_all.to_csv(s_metadir+config.d_nconv['s_format_csv_etmatrix'].format(s_batch))

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
    img_result.save(s_metadir + config.d_nconv['s_format_png_etmatrix'].format(s_batch), dpi=(720,720))
    os.remove(s_metadir + s_file_heat)
    os.remove(s_metadir + s_file_flatiline)
