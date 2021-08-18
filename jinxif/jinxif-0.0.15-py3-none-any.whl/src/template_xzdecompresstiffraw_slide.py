########
# title: template_decompresstiffraw_slide.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-06-25
#
# description:
#     template script for decompressing xz compressed raw tiff files.
#
# instruction:
#     use jinxif.util.decompress_tiff_raw_spawn function to generate and run executables from this template.
#####

# libraries
from jinxif import util
import resource
import time

# set variables
poke_s_slide = 'peek_s_slide'
poke_s_rawdir = 'peek_s_rawdir'
poke_s_format_rawdir = 'peek_s_format_rawdir'

# off we go
print(f'run jinxif.util.decompress_tiff_raw on {poke_s_slide} ...')
r_time_start = time.time()

# match nuclei
util.decompress_tiff_raw(
    s_slide = poke_s_slide,
    s_rawdir = poke_s_rawdir,  # input and output
    s_format_rawdir = poke_s_format_rawdir,  # s_rawdir, s_slide
)

# rock to the end
r_time_stop = time.time()
print('done jinxif.util.decompress_tiff_raw!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
