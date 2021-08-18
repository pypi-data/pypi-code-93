########
# title: template_nuccellzprojlabel_slide.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-06-25
#
# description:
#     template script for python base qc for nuc and cell z projection and segementaion label files.
#
# instruction:
#     use jinxif.segment.nuccell_zprojlabel_imgs_spawn function to generate and run executables from this template.
#####

# libraries
from jinxif import segment
import resource
import time

# set variables
poke_s_slide = 'peek_s_slide'
poke_s_segdir = 'peek_s_segdir'
poke_s_format_segdir_cellpose = 'peek_s_format_segdir_cellpose'
poke_s_qcdir = 'peek_s_qcdir'

# off we go!
print(f'run jinxif.segment.nuccell_zprojlabel_imgs on {poke_s_slide} ...')
r_time_start = time.time()

# match nuclei
segment.nuccell_zprojlabel_imgs(
    s_slide = poke_s_slide,
    s_segdir = poke_s_segdir,  # input
    s_format_segdir_cellpose = poke_s_format_segdir_cellpose,  # s_segdir, s_slide
    s_qcdir = poke_s_qcdir,  # output
)

# rock to the end
r_time_stop = time.time()
print('done jinxif.segment.nuccell_zprojlabel_imgs!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
