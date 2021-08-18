########
# title: template_autothresh_slide.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-06-25
#
# description:
#     template script for python base if marker auto threhsolding.
#
# instruction:
#     use feat.thresh.auto_thresh_spawn function to generate and run executables from this template.
#####

# libraries
from jinxif import feat
import resource
import time

# set variables
poke_s_slide = 'peek_s_slide'
poke_i_thresh_manual = peek_i_thresh_manual
poke_s_thresh_marker = 'peek_s_thresh_marker'
poke_s_afsubdir = 'peek_s_afsubdir'
poke_s_segdir = 'peek_s_segdir'
poke_s_format_segdir_cellpose = 'peek_s_format_segdir_cellpose'

# off we go
print(f'run jinxif.feat.feature_correct_labels on {poke_s_slide} ...')
r_time_start = time.time()

# feature correcgt labels
feat.feature_correct_labels(
    s_slide = poke_s_slide,
    i_thresh_manual = poke_i_thresh_manual,  # 1000,
    s_thresh_marker = poke_s_thresh_marker,  # 'Ecad',
    # file system
    s_afsubdir = poke_s_afsubdir,
    s_segdir = poke_s_segdir,
    s_format_segdir_cellpose = poke_s_format_segdir_cellpose,  # s_segdir, s_slide
)

# rock to the end
r_time_stop = time.time()
print('done jinxif.feature_correct_labels!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
