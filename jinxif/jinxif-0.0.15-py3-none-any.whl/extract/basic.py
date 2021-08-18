#####
# title: sane.py
#
# language: python3
# author: Jenny, bue
# license: GPLv>=3
# date: 2021-04-00
#
# description:
#     jinxif python3 basic function library that are used other jinxif libraries.
#     BUE 20210429: when resolved, should maybe become part of util?
#####


# library
import os
import pandas as pd
import re
import sys

# function
def _filename_dataframe(s_wd='./', s_start='R', s_end='.czi'):
    '''
    version: 2021-03-30
    internal function

    input:
        s_wd: working directory. default is present working directory.
        s_start: string at beginning of filenames
        s_end: string at end of filenames

    output:
        df_img: empty dataframe with filenames as index.

    descrition:
        get a dataframe whit filenames as index,
        that fit the choosen start end pattern as index.
    '''
    es_img = set()
    for s_file in os.listdir(s_wd):
        if s_file.startswith(s_start) and s_file.endswith(s_end):
            es_img.add(s_file)
    df_img = pd.DataFrame(index=sorted(es_img))
    return(df_img)


def parse_czi(s_czidir='./', s_czitype='r'):
    # BUE 20210429: parse_czi and parse_org can maybe be unified?
    '''
    version: 2021-04-01

    input:
        s_czidir: directory path.
        s_czitype: 'r' for regular, 's' for stitched

    output:
        df_img: dataframe with informative columns extracted form a standardisized file name.

    description:
        parse_czi is written along to koei's file naming convention:
        + the batch id is the folder:  cmif_YYYY-MM-DD_landmark
          the landmark can be a project name or a major sample something.
        the file names are like this:
        + round_markerchannel2.markerchannel3.markerchannel4.markerchannel5_slide_YYYY_MM_DD__hh_mm__scanid[-rescann]-Scene-n.czi
        + marker channel 1: always DAPI
        + slide : can contain dashes but no underscores!
        + scan id:  -scanid- or -scanid-rescan- both is possible
        the function get filenames for the requested path and extract sudden information.
    '''
    # change directory
    s_cwd = os.getcwd()
    os.chdir(s_czidir)

    # processing
    df_img = _filename_dataframe(s_end='.czi', s_start='R')
    if s_czitype == 'r':  # regular
        df_img['slide'] = [s_item[2] for s_item in [s_item.split('_') for s_item in df_img.index]]
    elif s_czitype == 's':  # stitched
        df_img['slide'] = [s_item[5] for s_item in [s_item.split('_') for s_item in df_img.index]]
    else:
        sys.exit('Error @ parse_czi : unknowen s_czitype {s_czitype}.\nknowen are: r (regular) and s (stitched)')
    df_img['rounds'] = [s_item[0] for s_item in [s_item.split('_') for s_item in df_img.index]]
    df_img['markers'] = [s_item[1] for s_item in [s_item.split('_') for s_item in df_img.index]]

    # contain all filename scenes?
    b_scenes = True
    for s_item in df_img.index:
        if (s_item.find('-Scene-') < 0):
            b_scenes = False
            break
    if b_scenes:
        try:
            df_img['scene'] = [s_item[1].split('.')[0] for s_item in [s_item.split('Scene-') for s_item in df_img.index]]
        except IndexError:
            print(f"{set([s_item[0] for s_item in [s_item.split('Scene-') for s_item in df_img.index]])}")
        df_img['scanID'] = [s_item[-1].split('-Scene')[0] for s_item in [s_item.split('__') for s_item in df_img.index]]

    # change directory back
    os.chdir(s_cwd)
    print(df_img.info())
    return(df_img)


def parse_org(s_type, s_wd='./', s_start='R', s_end='ORG.tif'):
    # BUE 20210425: in future no default seting for s_type!
    # BUE 20210425: in future make more explicite with parse_org_raw and a parse_org_reg function?
    # BUE 20210429: on the other hand function should as well handle parse_czi
    # BUE 20210425: also check what of the columns are really used in the remaining code.
    '''
    version: 2021-04-26
    old filename: mpimage.parse_org

    input:
        s_type: 'raw', 'raw_noscene', 'reg', 'reg_seg', 'reg_feat'
        s_wd: working directory. default is present working directory.
        s_start: string at beginning of filenames
        s_end: string at end of file names

    output:
        df_img: dataframe with image filename in index, path is index.name,
        and rounds, color, imagetype, scene (/tissue), and marker in the columns

    description:
        This function will parse images following koei's naming convention
        Example: Registered-R1_PCNA.CD8.PD1.CK19_Her2B-K157-Scene-002_c1_ORG.tif
        and extraxt its information into  a dataframe.
    '''
    df_img = _filename_dataframe(s_wd=s_wd, s_start=s_start, s_end=s_end)

    #  raw
    if s_type == 'raw':
        df_img['rounds'] = [s_item.split('_')[0] for s_item in df_img.index]
        df_img['color'] = [s_item.split('_')[-2] for s_item in df_img.index]
        df_img['imagetype'] = [s_item.split('_')[-1].split('.tif')[0] for s_item in df_img.index]
        df_img['slide'] = [s_item.split('_')[2] for s_item in df_img.index]
        df_img['scene'] = [s_item.split('-Scene-')[1].split('_')[0] for s_item in df_img.index]

    # noscenes
    # raw nonscenes
    elif s_type == 'raw_noscenes':
        df_img['rounds'] = [s_item.split('_')[0] for s_item in df_img.index]
        df_img['color'] = [s_item.split('_')[-2] for s_item in df_img.index]
        df_img['imagetype'] = [s_item.split('_')[-1].split('.tif')[0] for s_item in df_img.index]
        df_img['slide'] = [s_item.split('_')[2] for s_item in df_img.index]
        df_img['scene'] = 'Scene-001'

    # registration (mpimage.pares_org and features.parse_org)
    elif s_type == 'reg':  # bue 20210505: reg scene is not the same string as reg_feat scene! I have to boil this down to a clear strycture.
        df_img['rounds'] = [s_item.split('_')[0].split('Registered-')[1] for s_item in df_img.index]
        df_img['color'] = [s_item.split('_')[-2] for s_item in df_img.index]
        df_img['imagetype'] = [s_item.split('_')[-1].split('.tif')[0] for s_item in df_img.index]
        df_img['slide'] = [s_item.split('_')[2] for s_item in df_img.index]  # actually slidescene
        df_img['scene'] = [s_item.split('_')[2] for s_item in df_img.index] # bue 20210505: reg scene is not the same string as reg_feat scene! I have to boil this down to a clear strycture.

    # registration (segmentation.parse_org)
    elif s_type == 'reg_seg':
        df_img['rounds'] = [s_item.split('_')[0].split('Registered-')[1] for s_item in df_img.index]
        df_img['color'] = [s_item.split('_')[-2] for s_item in df_img.index]
        df_img['imagetype'] = [s_item.split('_')[-1].split('.tif')[0] for s_item in df_img.index] # bue 20210424: not in original segmentation
        df_img['slide'] = [s_item.split('_')[2] for s_item in df_img.index] # actually slidescene
        df_img['scene'] = [item.split('-Scene-')[1] for item in df_img.slide]
        df_img['marker_string'] = [item.split('_')[1] for item in df_img.index]  # bue 20210424: unique to segmentation
        df_img['path'] = [f'{s_wd}{item}/' for item in df_img.index]  # bue 20210424: unique to segmentation can maybe be droped because of index.name

    # registration (mpimage.pares_org and features.parse_org)
    elif s_type == 'reg_feat':
        df_img['rounds'] = [s_item.split('_')[0].split('Registered-')[1] for s_item in df_img.index]
        df_img['color'] = [s_item.split('_')[-2] for s_item in df_img.index]
        df_img['imagetype'] = [s_item.split('_')[-1].split('.tif')[0] for s_item in df_img.index]
        df_img['slide'] = [s_item.split('_')[2] for s_item in df_img.index]  # actually slidescene
        df_img['scene'] = [item.split('-Scene-')[1] for item in df_img.slide]  # 20210330: features.parse_org splited by -Scene- seems more corect then original

    else:
        sys.exit(f'Error @ basic.parse_org : unknown s_type {s_type}.\nknowen are raw, raw_noscenes, reg, reg_seg, reg_feat.')

    # round_ord and round_num
    df_img['round_ord'] = [float(re.sub('[^0-9.]','', re.sub('Q','.5', s_item))) for s_item in df_img.rounds]
    df_img = df_img.sort_values(['round_ord','color'])
    for i_idx, r_round in enumerate(sorted(df_img.round_ord.unique())):
        df_img.loc[df_img.round_ord==r_round, 'round_num'] = i_idx

    # parse file name for biomarker
    b_warning = False
    for s_index in df_img.index:
        #print(f'process: {s_index}')
        s_color = df_img.loc[s_index,'color']
        if s_color == 'c1':
            s_marker = 'DAPI'
        elif s_color == 'c2':
            s_marker = s_index.split('_')[1].split('.')[0]
        elif s_color == 'c3':
            s_marker = s_index.split('_')[1].split('.')[1]
        elif s_color == 'c4':
            s_marker = s_index.split('_')[1].split('.')[2]
        elif s_color == 'c5':
            s_marker = s_index.split('_')[1].split('.')[3]
        # these are only included in sardana shading corrected images
        elif s_color == 'c6':
            b_warning = True
            s_marker = s_index.split('_')[1].split('.')[2]  # bue 20201114: should this not be s_index.split('_')[1].split('.')[4]
        elif s_color == 'c7':
            b_warning = True
            s_marker = s_index.split('_')[1].split('.')[3]  # bue 20201114: should this not be s_index.split('_')[1].split('.')[5]
        else:
            sys.exit(f'Error: in filename inexisting microscope channel {s_color} found.\n{s_index}')
        df_img.loc[s_index,'marker'] = s_marker
    if (b_warning):
        print('WARNING: this filename contain channel c6 and/or c7.\nit is assumed this are sardana shading corrected channels which shadow the markers from channel c4 and c5, respective.\nif not so, function have to be re-written to become more sophisticated!')

    # output
    df_img.index.name = s_wd
    print(df_img.info())
    return(df_img)


def add_exposure(df_img, df_t, s_type='roundcycles'):
    '''
    version: 20210430
    input:
        df_img: dataframe of images with columns [ 'color', 'exposure', 'marker','sub_image','sub_exposure'] and index with image names
        df_t: metadata with dataframe with ['marker','exposure']
    output:
    description:

    '''
    if s_type == 'roundscycles':
        for s_index in df_img.index:

            # look up exposure time for marker in metadata
            s_marker = df_img.loc[s_index, 'marker']
            df_t_image = df_t.loc[(df_t.marker == s_marker), :]

            if df_t_image.shape[0] == 0:
                sys.exit(f'Error @ add_exposure : marker {s_marker} has no recorded exposure time.')
            else:
                i_exposure = df_t_image.loc[:, 'exposure'][0]
                df_img.loc[s_index,' exposure'] = i_exposure

    elif s_type == 'czi':
        # BUE 20210430: chinlab nomenclature depending
        # add exposure
        df_t['rounds'] = [item.split('_')[0] for item in df_t.index]
        #df_t['tissue'] = [item.split('_')[2].split('-Scene')[0] for item in df_t.index] #not cool with stiched
        for s_index in df_img.index:
            s_tissue = df_img.loc[s_index,'scene'].split('-Scene')[0]
            s_color = str(int(df_img.loc[s_index,'color'].split('c')[1])-1)
            s_round = df_img.loc[s_index,'rounds']
            print(s_index)
            df_img.loc[s_index,'exposure'] = df_t[(df_t.index.str.contains(s_tissue)) & (df_t.rounds==s_round)].loc[:,s_color][0]

    else:
        sys.exit(f'Error @ add_exposure: unknowen s_type {s_type}.\nknowen are roundcycles and czi')

    # output
    print(df_img.info())
    return(df_img)

