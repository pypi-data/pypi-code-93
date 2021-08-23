#####
# title: template_extractfeatures_slide.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-07-05
#
# description:
#     template script for python based image segmentation feature extraction.
#
# instruction:
#     use jinxif.thresh.extract_feature_spawn function to generate and run executables from this template.
#####

# library
from jinxif import feat
import resource
import time

# input parameters
poke_s_slide = 'peek_s_slide'
poke_s_thresh_marker = 'peek_s_thresh_marker'
poke_s_segdir = 'peek_s_segdir'
poke_s_format_segdir_cellpose = 'peek_s_format_segdir_cellpose'
poke_s_afsubdir = 'peek_s_afsubdir'
poke_s_format_afsubdir = 'peek_s_format_afsubdir'

# off we go
print(f'run jinxif.feat.extract_features on {poke_s_slide} ...')
r_time_start = time.time()

# run feature extraction
feat.extract_features(
    s_slide = poke_s_slide,
    s_thresh_marker = poke_s_thresh_marker,
    s_segdir = poke_s_segdir,
    s_format_segdir_cellpose = poke_s_format_segdir_cellpose,  # s_segdir, s_slide
    s_afsubdir = poke_s_afsubdir,
    s_format_afsubdir = poke_s_format_afsubdir,  # s_afsubdir, s_slide_pxscene
)

# rock to the end
r_time_stop = time.time()
print('done jinxif.feat.extract_features!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
