####
# title: feat.py
#
# language: Python3.7
# date: 2020-06-00
# license: GPL>=v3
# author: Jenny, bue
#
# description:
#   python3 script for single cell feature extraction
####

# libraries
import numpy as np
import os
import pandas as pd
import re
import scipy
from skimage import filters, io, measure, segmentation 
from jinxif.extract import basic

# functions
def extract_feat(labels, intensity_image, properties=('centroid','mean_intensity','area','eccentricity')):
    '''
    bue 20210514: used

    given labels and intensity image, extract features to dataframe
    '''
    props = measure.regionprops_table(labels, intensity_image, properties=properties)
    df_prop = pd.DataFrame(props)
    return(df_prop)


def contract_label(labels, distance=3):
    '''
    bue 20210514: used {subcellular_regions}

    contract labels by a fixed number of pixels
    '''
    boundaries = segmentation.find_boundaries(labels, mode='outer')
    shrunk_labels = labels.copy()
    shrunk_labels[boundaries] = 0
    foreground = shrunk_labels != 0
    distances, (i, j) = scipy.ndimage.distance_transform_edt(
        foreground, 
        return_indices=True,
    )
    mask = foreground & (distances <= distance)
    shrunk_labels[mask] = shrunk_labels[i[mask], j[mask]]
    rim_labels = labels - shrunk_labels
    return(rim_labels)


def expand_label(labels, distance=3):
    '''
    bue 20210514: used {subcellular_regions, combine_labels}

    expand the nucelar labels by a fixed number of pixels
    '''
    boundaries = segmentation.find_boundaries(labels, mode='outer') #thick
    shrunk_labels = labels.copy()
    shrunk_labels[boundaries] = 0
    background = shrunk_labels == 0
    distances, (i, j) = scipy.ndimage.distance_transform_edt(
        background, 
        return_indices=True,
    )
    grown_labels = labels.copy()
    mask = background & (distances <= distance)
    grown_labels[mask] = shrunk_labels[i[mask], j[mask]]
    ring_labels = grown_labels - shrunk_labels

    return(ring_labels, grown_labels) #shrunk_labels, grown_labels,


def straddle_label(labels, distance=3):
    '''
    bue 20210514: used {subcellular_regions}

    expand and contract labels by a fixed number of pixels
    '''
    boundaries = segmentation.find_boundaries(labels, mode='outer') #outer
    shrunk_labels = labels.copy()
    grown_labels = labels.copy()
    shrunk_labels[boundaries] = 0
    foreground = shrunk_labels != 0
    background = shrunk_labels == 0
    distances_f, (i, j) = scipy.ndimage.distance_transform_edt(
        foreground, 
        return_indices=True
    )
    distances_b, (i, j) = scipy.ndimage.distance_transform_edt(
        background, 
        return_indices=True
    )
    mask_f = foreground & (distances_f <= distance)
    mask_b = background & (distances_b <= distance + 1)
    shrunk_labels[mask_f] = 0
    grown_labels[mask_b] = grown_labels[i[mask_b], j[mask_b]]
    membrane_labels = grown_labels - shrunk_labels
    return(membrane_labels, grown_labels, shrunk_labels)


def subcellular_regions(labels, distance_short=2, distance_long=5):
    '''
    bue 20210514: used
    bue 20210514: biotransistor.imagine might be faster

    calculate subcellular segmentation regions from segmentation mask
    '''
    membrane_short = contract_label(labels, distance=distance_short)
    membrane_long = contract_label(labels, distance=distance_long)
    ring_short, grown_short = expand_label(labels, distance=distance_short)
    ring_long, grown_long = expand_label(labels, distance=distance_long)
    straddle_short, _, shrink_short = straddle_label(labels, distance=distance_short)
    straddle_long, _, shrink_long = straddle_label(labels, distance=distance_long)
    d_loc_sl={
        'membrane': (membrane_short, membrane_long),
        'ring': (ring_short, ring_long),
        'straddle': (straddle_short, straddle_long),
        'grown': (grown_short, grown_long),
        'shrunk': (shrink_short, shrink_long)
    }
    return(d_loc_sl)


def label_difference(labels,cell_labels):
    '''
    bue 20210514: used

    given matched nuclear and cell label IDs,return cell_labels minus labels
    '''
    overlap = cell_labels==labels
    ring_rep = cell_labels.copy()
    ring_rep[overlap] = 0
    return(ring_rep)


def extract_cellpose_features(
        s_slide,  # necessary
        ls_seg_markers,  # bue 20210514: some proper generic regex for matchedcell cell segmentation basins file might do!
        i_nuc_diam,  # bue 20210514: some proper generic regex for matchedcell cell segmentation basins file might do!
        i_cell_diam,  # bue 20210514: some proper generic regex for matchedcell cell segmentation basins file might do!
        s_segdir = './Segmentation/',  # necessary
        s_subdir = './SubtractedRegisteredImages/',   # necessary
    ): 
    #b_big=False,  # this is some different way of output for very big slides, because output is per slide and not per side_pxscene
    #b_thresh=False  this was some break, for if Jenny needed only df_thresh output
    '''
    version: 2021-05-14
    bue 20210514: used
    bue 20210514: should be propper spawned in future!

    input:
        s_slide: slide to extract cellpose feature from (maybe in future es_slide).
        s_segdir: directory to find segementation basin files.
        s_subdir: dictionary to find af subtracted tiff images.

    output:
        df_featslide: whole slide feature dataframe.
        df_thresh: whole slide automatic generated threshold values dataframe.

    description:
        load the segmentation results, the input images, and the channels images
        extract mean intensity from each image, and centroid, area and eccentricity for
    '''

    df_featslide = pd.DataFrame()
    df_thresh = pd.DataFrame()

    # bue: get the slide related pxscene related nuc and matchedcell segmentation basing files
    #os.chdir(f'{s_segdir}/{s_slide}Cellpose_Segmentation')
    s_path = f'{s_segdir}{s_slide}Cellpose_Segmentation/'
    d_match = {}
    es_slide_pxscene = set()
    for s_file in os.listdir(s_path):
        if s_file.find(f'{".".join(ls_seg_markers)} matchedcell{i_cell_diam} - Cell Segmentation Basins') >-1:
            # bue 20210514: i never have dealed with this case, think it is only cell segementaion without nuc, but why is it then matched?
            s_slide_pxscene = s_file.split('_')[0]
            es_slide_pxscene.add(s_slide_pxscene)
            d_match.update({s_slide_pxscene: s_file})

        elif s_file.find(f'{".".join(ls_seg_markers)} nuc{i_nuc_diam} matchedcell{i_cell_diam} - Cell Segmentation Basins') >- 1:
            s_slide_pxscene = s_file.split('_')[0]
            es_slide_pxscene.add(s_slide_pxscene)
            d_match.update({s_slide_pxscene: s_file})
        # bue 20210426: else missing

    # for each scene of the given sample
    for s_slide_pxscene in sorted(es_slide_pxscene):
        #os.chdir(f'{s_segdir}/{s_slide}Cellpose_Segmentation')
        s_path = f'{s_segdir}{s_slide}Cellpose_Segmentation/'

        print(f'processing {s_slide_pxscene}')
        # bue 20210426: carefull, this for loop will only go for the last dapi.png file that matches!
        # regex might be able to do the trick
        for s_file in os.listdir(s_path):
            if s_file.find(s_slide_pxscene) > -1:
                if s_file.find("DAPI.png") > -1:
                    s_dapi = s_file

        # load dapi, nuclei and related cell segmentation basin files
        s_dir_cellposesegement = f'{s_slide}Cellpose_Segmentation/'
        s_file_basinnuc = f'{s_slide_pxscene} nuclei{i_nuc_diam} - Nuclei Segmentation Basins.tif'

        dapi = io.imread(f'{s_segdir}{s_dir_cellposesegement}{s_dapi}')

        print(f'loading {s_file_basinnuc}')
        labels = io.imread(f'{s_segdir}{s_dir_cellposesegement}{s_file_basinnuc}')

        print(f'loading {d_match[s_slide_pxscene]}')
        cell_labels = io.imread(f'{s_segdir}/{s_dir_cellposesegement}{d_match[s_slide_pxscene]}')  # basin cell file

        # extrct nuclear features
        # bue 20210514: biotransistor.imagine might be faster
        df_feat = extract_feat(
            labels = labels,
            intensity_image = dapi,
            properties = (['label'])
        )
        df_feat.columns = [f'{s_item}_segmented-nuclei' for s_item in df_feat.columns]
        df_feat.index = [f'{s_slide}_scene{s_slide_pxscene.split("-Scene-")[1].split("_")[0]}_cell{s_item}' for s_item in df_feat.loc[:,'label_segmented-nuclei']]

        # get subcellular regions
        cyto = label_difference(labels, cell_labels)
        d_loc_nuc = subcellular_regions(labels=labels, distance_short=2, distance_long=5) # her the error happens
        d_loc_cell = subcellular_regions(labels=cell_labels, distance_short=2, distance_long=5)
        d_loc = {
            'nuclei': labels,
            'cell': cell_labels,
            'cytoplasm': cyto,
            'nucmem': d_loc_nuc['membrane'][0],
            'cellmem': d_loc_cell['membrane'][0],
            'perinuc5': d_loc_nuc['ring'][1],
            'exp5': d_loc_nuc['grown'][1],
            'nucadj2': d_loc_nuc['straddle'][0],
            'celladj2': d_loc_cell['straddle'][0]
        }

        # is s_subdir organized by slide or scene
        # bue 20210514: should not be necessary if stanadisized
        if os.path.exists(f'{s_subdir}/{s_slide}/'):
            #os.chdir(f'{s_subdir}/{s_slide}/')
            s_subsubdir = f'{s_subdir}/{s_slide}/'
        elif os.path.exists(f'{s_subdir}/{s_slide_pxscene}/'):
            #os.chdir(f'{s_subdir}/{s_slide_pxscene}/')
            s_subsubdir = f'{s_subdir}/{s_slide_pxscene}/'
        else:
            #os.chdir(f'{s_subdir}')
            s_subsubdir = s_subdir

        # some nameing convention hack to extract scenes, i guess
        df_img = basic.parse_org(s_type='reg_feat', s_wd=s_subsubdir)
        df_img['round_int'] = [int(re.sub('[^0-9]','', s_item)) for s_item in df_img.rounds]
        df_img = df_img[df_img.round_int < 90]
        df_img = df_img.sort_values('round_int')
        df_scene = df_img[df_img.scene==s_slide_pxscene.split("-Scene-")[1].split("_")[0]]

        # for each image file (one per slide_pxscene, round, channel)
        for s_index in df_scene.index:
            intensity_image = io.imread(f'{df_scene.index.name}{s_index}')
            df_thresh.loc[s_index,'threshold_li'] =  filters.threshold_li(intensity_image)
            if intensity_image.mean() > 0:
                # intensity treshold
                df_thresh.loc[s_index, 'threshold_otsu'] = filters.threshold_otsu(intensity_image)
                df_thresh.loc[s_index, 'threshold_triangle'] = filters.threshold_triangle(intensity_image)
                s_marker = df_scene.loc[s_index,'marker']

                #if b_thresh:
                #    break

                print(f'extracting features {s_marker}')
                if s_marker == 'DAPI':
                    s_marker = s_marker + f'{df_scene.loc[s_index,"rounds"].split("R")[1]}'
                # for each cell partition
                for s_loc, a_loc in d_loc.items():
                    if s_loc == 'nuclei':
                        df_marker_loc = extract_feat(
                            labels=a_loc,
                            intensity_image=intensity_image,
                            properties=(['mean_intensity','centroid','area','eccentricity','label'])
                        )
                        df_marker_loc.columns = [
                            f'{s_marker}_{s_loc}',
                            f'{s_marker}_{s_loc}_centroid-0',
                            f'{s_marker}_{s_loc}_centroid-1',
                            f'{s_marker}_{s_loc}_area',
                            f'{s_marker}_{s_loc}_eccentricity',
                            f'{s_marker}_{s_loc}_label',
                        ]
                    elif s_loc == 'cell':
                        df_marker_loc = extract_feat(
                            labels=a_loc,
                            intensity_image=intensity_image,
                            properties=(['mean_intensity', 'euler_number', 'area', 'eccentricity', 'label'])
                        )
                        df_marker_loc.columns = [
                            f'{s_marker}_{s_loc}',
                            f'{s_marker}_{s_loc}_euler',
                            f'{s_marker}_{s_loc}_area',
                            f'{s_marker}_{s_loc}_eccentricity',
                            f'{s_marker}_{s_loc}_label'
                        ]
                    else:
                        df_marker_loc = extract_feat(
                            labels=a_loc,
                            intensity_image=intensity_image,
                            properties=(['mean_intensity','label'])
                        )
                        df_marker_loc.columns = [
                            f'{s_marker}_{s_loc}',
                            f'{s_marker}_{s_loc}_label'
                        ]
                    #drop zero from array, set array ids as index
                    #old df_marker_loc.index = sorted(np.unique(a_loc)[1::])
                    df_marker_loc.index = df_marker_loc.loc[:,f'{s_marker}_{s_loc}_label']
                    df_marker_loc.index = [f'{s_slide}_scene{s_slide_pxscene.split("-Scene-")[1].split("_")[0]}_cell{s_item}' for s_item in df_marker_loc.index]
                    df_feat = df_feat.merge(df_marker_loc, left_index=True,right_index=True,how='left',suffixes=('',f'{s_marker}_{s_loc}'))
        #if b_big:
        #    df_feat.to_csv(f'{s_segdir}/{s_slide}Cellpose_Segmentation/features_{s_slide}-{s_slide_pxscene}.csv')

        # update output
        df_featslide = df_featslide.append(df_feat)

    # return
    df_featslide.index.name = 'index'
    df_featslide.to_csv(f'{s_segdir}features_{s_slide}_MeanIntensity_Centroid_Shape.csv')
    df_thresh.index.name = 'index'
    df_thresh.to_csv(f'{s_segdir}thresh_{s_slide}_ThresholdLi.csv')
    #return(df_featslide, df_thresh)


def extract_bright_features(
        s_slide,  # necessary
        ls_membrane,  # necessary
        ls_seg_markers,  # bue 20210514: maybe obsolete with proper regex
        i_nuc_diam,  # bue 20210514: maybe obsolete with proper regex
        i_cell_diam,  # bue 20210514: maybe obsolete with proper regex
        s_segdir = './Segmentation/',  # necessary
        s_subdir = './SubtractedRegisteredImages/',  # necessary
    ):
    '''
    version: 2021-04-26
    bue 20210514: used
    bue 20210514: most is the same as extract_cellpose_features. this hould fuse into one and ls_membrane is the trigger.

    load the features, segmentation results, the input images, and the channels images
    extract mean intensity of the top 25% of pixel in from each label region
    '''
    df_featslide = pd.DataFrame()

    # bue: get the slide related pxscenes and pxscene related nuc and matchedcell segmentation basing files
    #os.chdir(f'{s_segdir}/{s_slide}Cellpose_Segmentation')
    s_path = f'{s_segdir}{s_slide}Cellpose_Segmentation/'
    es_slide_pxscene = set()
    d_match = {}
    for s_file in os.listdir(s_path):
        if s_file.find(f'{".".join(ls_seg_markers)} matchedcell{i_cell_diam} - Cell Segmentation Basins')>-1:
            s_slide_pxscene = s_file.split('_')[0]
            es_slide_pxscene.add(s_slide_pxscene)
            d_match.update({s_slide_pxscene: s_file})
        elif s_file.find(f'{".".join(ls_seg_markers)} nuc{i_nuc_diam} matchedcell{i_cell_diam} - Cell Segmentation Basins')>-1:
            s_slide_pxscene = s_file.split('_')[0]
            es_slide_pxscene.add(s_slide_pxscene)
            d_match.update({s_slide_pxscene: s_file})
        # bue 20210426: else missing

    # each slide_pxscene
    for s_slide_pxscene in sorted(es_slide_pxscene):
        #os.chdir(f'{s_segdir}/{s_slide}Cellpose_Segmentation')
        s_path = f'{s_segdir}{s_slide}Cellpose_Segmentation/'

        print(f'processing {s_slide_pxscene}')
        # bue 20210426: dangerous dins only last file with DAPI.png in it
        for s_file in os.listdir(s_path):
            if s_file.find(s_slide_pxscene) > -1:
                if s_file.find("DAPI.png") > -1:
                    s_dapi = s_file

        # load dapi, nuclei and related nucleus segmentation basin files
        s_dir_cellposesegement = f'{s_slide}Cellpose_Segmentation/'
        s_file_basinnuc = f'{s_slide_pxscene} nuclei{i_nuc_diam} - Nuclei Segmentation Basins.tif'

        dapi = io.imread(f'{s_segdir}{s_dir_cellposesegement}/{s_dapi}')

        print(f'loading {s_file_basinnuc}')
        labels = io.imread(f'{s_segdir}{s_dir_cellposesegement}{s_file_basinnuc}')
        print(labels.shape)

        print(f'loading {d_match[s_slide_pxscene]}')
        cell_labels = io.imread(f'{s_segdir}{s_dir_cellposesegement}/{d_match[s_slide_pxscene]}')
        print(cell_labels.shape)

        # extract nuclear features
        df_feat = extract_feat(
            labels=labels,
            intensity_image=dapi,
            properties=(['label']),
        )
        df_feat.columns = [f'{s_item}_segmented-nuclei' for s_item in df_feat.columns]
        df_feat.index = [f'{s_slide}_scene{s_slide_pxscene.split("-Scene-")[1].split("_")[0]}_cell{s_item}' for s_item in df_feat.loc[:,'label_segmented-nuclei']]

        # get subcellular regions
        d_loc_nuc = subcellular_regions(labels=labels, distance_short=2, distance_long=5)
        d_loc_cell = subcellular_regions(labels=cell_labels, distance_short=2, distance_long=5)
        d_loc = {
            'nucmem25': d_loc_nuc['membrane'][0],
            'exp5nucmembrane25': d_loc_nuc['grown'][1],
            'cellmem25': d_loc_cell['membrane'][0],
            'nuclei25': labels
        }

        # s_subdir organized by slide or scene
        if os.path.exists(f'{s_subdir}{s_slide}/'):
            #os.chdir(f'{s_subdir}/{s_slide}/')
            s_subsubdir = f'{s_subdir}{s_slide}/'
        elif os.path.exists(f'{s_subdir}{s_slide_pxscene}/'):
            #os.chdir(f'{s_subdir}/{s_slide_pxscene}/')
            s_subsubdir = f'{s_subdir}{s_slide_pxscene}/'
        else:
            #os.chdir(f'{s_subdir}')
            s_subsubdir = s_subdir

        # some nameing convention hack to find scenes and marker?
        df_img = basic.parse_org(s_type='reg_feat', s_wd=s_subsubdir)
        df_img['round_int'] = [int(re.sub('[^0-9]','', s_item)) for s_item in df_img.rounds]
        df_img = df_img[df_img.round_int < 90]
        df_img = df_img.sort_values('round_int')
        df_scene = df_img[df_img.scene==s_slide_pxscene.split("-Scene-")[1].split("_")[0]]
        df_marker = df_scene[df_scene.marker.isin(ls_membrane)]

        # for each image file (one per slide_pxscene, round, channel)
        for s_index in df_marker.index:
            # loade file get marker
            print(f'loading {s_index}')
            intensity_image = io.imread(f'{df_marker.index.name}{s_index}')
            #print(intensity_image.shape)
            s_marker = df_marker.loc[s_index,'marker']
            print(f'extracting features {s_marker}')

            # dapi
            if s_marker == 'DAPI':
                s_marker = s_marker + f'{df_marker.loc[s_index,"rounds"].split("R")[1]}'

            # other markers
            for s_loc, a_loc in d_loc.items():
                #print(a_loc.shape)
                df_marker_loc = pd.DataFrame(columns = [f'{s_marker}_{s_loc}'])
                df_prop = extract_feat(
                    labels=a_loc,
                    intensity_image=intensity_image,
                    properties=(['intensity_image','image','label'])
                )
                for idx in df_prop.index:
                    label_id = df_prop.loc[idx,'label']
                    intensity_image_small = df_prop.loc[idx,'intensity_image']
                    image = df_prop.loc[idx,'image']
                    pixels = intensity_image_small[image]
                    pixels25 = pixels[pixels >= np.quantile(pixels,.75)]
                    df_marker_loc.loc[label_id, f'{s_marker}_{s_loc}'] = pixels25.mean()
                df_marker_loc.index = [f'{s_slide}_scene{s_slide_pxscene.split("-Scene-")[1].split("_")[0]}_cell{s_item}' for s_item in df_marker_loc.index]
                df_feat = df_feat.merge(df_marker_loc, left_index=True, right_index=True,how='left', suffixes=('',f'{s_marker}_{s_loc}'))
        df_featslide = df_featslide.append(df_feat)
        #break
    # output
    df_featslide.index.name = 'index'
    df_featslide.to_csv(f'{s_segdir}/features_{s_slide}_BrightMeanIntensity.csv')
    #return(df_featslide)
