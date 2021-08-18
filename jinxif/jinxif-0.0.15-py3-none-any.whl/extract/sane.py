#####
# title: sane.py
#
# language: python3
# author: Jenny, bue
# license: GPLv>=3
# date: 2021-04-00
#
# description:
#     jinxif python3 library to sanity check
#     + filename nameing convention
#     + completeness of the file set
#####


# library
from jinxif.extract import config
import sys

# function
def count_images(df_img):
    '''
    version: 2021-03-31

    input:
        df_img: czi image dataframe

    output:
        stdout

    description:
        count and list slides, scenes, rounds
    '''
    # bue: jenny this is very creative code!
    ls_slide = sorted(set(df_img.slide))
    print(f'\nSlide names: {ls_slide}')
    for s_slide in ls_slide:
        print(f'Slide: {s_slide}')
        df_img_slide = df_img[df_img.slide==s_slide]
        print('Scene: rounds')
        [print(f'{s_scene}: {sum(df_img_slide.scene==s_scene)}') for s_scene in sorted(set(df_img_slide.scene))]
        print(f'Round: scenes')
        [print(f'{s_round}: {sum(df_img_slide.rounds==s_round)}') for s_round in sorted(set(df_img_slide.rounds))]
        print(f'Number of images = {len(df_img_slide)}\n')


def check_markers(df_img, es_marker_standard=config.es_marker_standard):  # s_file_type='tiff'
    """
    version: 2021-05-18
    oldname: check_names

    input:
        df_img
        s_file_type: file type from which the df_img is derived.
            known are czi and tiff

    output:
        stdout
        es_wrong: set of wrong markers

    description:
        Based on filenames in segment folder,
        checks marker names against standard list of biomarkers
    """
    # tiff s_file_type
    if 'marker' in set(df_img.columns):
        es_found = set(df_img.marker)
    # czi s_file_type
    else:
        es_found = set()
        for s_markers in df_img.markers:
            es_found = es_found.union(set(s_markers.replace('_','.').split('.')))

    print(f'\nSlide names: {sorted(set(df_img.slide))}')
    es_wrong = es_found.difference(es_marker_standard)
    es_right = es_found.intersection(es_marker_standard)
    print(f'Wrong stain names: {sorted(es_wrong)}')
    print(f'Right stain names: {sorted(es_right)}')
    print(f'Standard stain names: {sorted(es_marker_standard)}\n')
    des_marker = {'marker_wrong': es_wrong, 'marker_right': es_right}
    return(des_marker)

