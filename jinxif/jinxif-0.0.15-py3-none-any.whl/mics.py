############
# title: mics.py
#
# langue: Python3
# date: 2020-04-07
# license: GPL>=v3
# author: Jenny, bue
#
# description:
#     functions to fork miltenyi output into our pipeline.
############


# library
from jinxif import basic
from jinxif import config
import numpy as np
import os
import re
from skimage import io
import subprocess
import sys
import time

# developemnt
#import importlib
#importlib.reload()

# global var
s_path_module = os.path.abspath(os.path.dirname(__file__))
s_path_module = re.sub(r'jinxif$','jinxif/', s_path_module)

# function
def _slide_up(a):
    """
    input:
      a: numpy array

    output:
      a: input numpy array shifted one row up.
        top row get deleted,
        bottom row of zeros is inserted.

    description:
      inspired by np.roll function, though elements that roll
      beyond the last position are not re-introduced at the first.
    """
    a = np.delete(np.insert(a, a.shape[0], 0, axis=0), 0, axis=0)
    return(a)


def _slide_down(a):
    """
    input:
      a: numpy array

    output:
      a: input numpy array shifted one row down.
        top row of zeros is inserted.
        bottom row get deleted,

    description:
      inspired by np.roll function, though elements that roll
      beyond the last position are not re-introduced at the first.
    """
    a = np.delete(np.insert(a, 0, 0, axis=0), -1, axis=0)
    return(a)


def _slide_left(a):
    """
    input:
      a: numpy array

    output:
      a: input numpy array shifted one column left.
        left most column gets deleted,
        right most a column of zeros is inserted.

    description:
      inspired by np.roll function, though elements that roll
      beyond the last position are not re-introduced at the first.
    """
    a = np.delete(np.insert(a, a.shape[1], 0, axis=1), 0, axis=1)
    return(a)


def _slide_right(a):
    """
    input:
      a: numpy array

    output:
      a: input numpy array shifted one column right.
        left most a column of zeros is inserted.
        right most column gets deleted,

    description:
      inspired by np.roll function, though elements that roll
      beyond the last position are not re-introduced at the first.
    """
    a = np.delete(np.insert(a, 0, 0, axis=1), -1, axis=1)
    return(a)


def _grow(ab_segment, i_step=1):
    """
    input:
      ai_segment: numpy array representing a cells basin file.
        it is assumed that basin borders are represented by 0 values,
        and basins are represented with any values different from 0.
        ai_segment = skimage.io.imread("cells_basins.tif")

      i_step: integer which specifies how many pixels the basin
        to each direction should grow.
        function can handle shrinking. enter negative steps like -1.

    output:
      ai_grown: numpy array with the grown basins

    description:
      algorithm to grow the basis in a given basin numpy array.
      growing happens counterclockwise, starting at noon.
    """
    ab_tree = ab_segment.copy()  # initialize output
    # growing
    for i in range(i_step):
        # next grow cycle
        print(f'grow {i+1}[px] ring ...')
        ab_treering = ab_tree.copy()
        for o_slide in [_slide_up, _slide_left, _slide_down, _slide_right]:
            ab_evolve = o_slide(ab_tree)
            ab_treering[ab_evolve] = True
            #print(ab_treering)
        # update output
        ab_tree = ab_treering
    # output
    return(ab_tree)


#copy_processed
def trafo(
        #ds_marker_rename = {},
        #ds_slidescene_rename = {},
        #i_line_intensity = 32639,
        i_exp_line = 0,  # should be one more as the common doughnut. 
        s_micsdir = config.d_nconv['s_micsdir'],  #'./MicsImages/'
        s_afsubdir = config.d_nconv['s_afsubdir'],  #'./SubtractedRegisteredImages/'
        s_format_afsubdir = config.d_nconv['s_format_afsubdir'],  # {}{}/  s_afsubdir, slide_scene
    ):
    '''
    description:
        copy the highest exposure time images for processing into s_afsubdir.
        therby erases the stitching lines and additionaly saves a mask image for this line for downstrem processing.
    '''
    # parse mics filenames
    df_img = basic.parse_tiff_mics(s_wd=s_micsdir)

    # count overexpressed pixel
    i_16bit_max = 2**16 - 1
    df_img['overex_count'] = None
    for s_file in df_img.index:
        a_img = io.imread(df_img.index.name + s_file)
        i_overex = (a_img >= i_16bit_max).sum()
        df_img.loc[s_file, 'overex_count'] = i_overex
        print(f'counted {i_overex}[px] overexpressed {a_img.max()} >= {i_16bit_max}: {s_file} ...')
  
    # trafo and move files to afsub
    for s_marker in sorted(df_img.loc[df_img.marker.notna(),'marker'].unique()):
        df_img_marker = df_img.loc[df_img.marker == s_marker, :]
        for s_file in df_img_marker.sort_values(['overex_count','exposure_time_ms'], ascending=[True,False]).index.tolist():
            # load image
            s_ipath = df_img.index.name + s_file
            a_img = io.imread(s_ipath)
            # generate line mask
            ab_xaxis = (a_img == a_img.mean(axis=0)).all(axis=0)  # get vertical lines
            ab_yaxis = (a_img.T == a_img.mean(axis=1)).all(axis=0)  # get horizontal lines
            i_xaxis = ab_xaxis.sum()
            i_yaxis = ab_yaxis.sum()
            if (i_xaxis == 0) or (i_yaxis == 0):
                sys.exit(f'Error @ jinxif.mics.trafo: no x-axis {i_xaxis} or y-axis {i_yaxis} lines detected in miltenyi PreprocessedData/02_Processed/*_processed_combined images.')
            ab_mask_line = np.zeros(shape=a_img.shape, dtype=bool)
            ab_mask_line[ab_yaxis, ab_xaxis] = True
            # erase line
            a_img[ab_mask_line] = a_img.min()
            # generate output directory
            s_slide_scene = df_img_marker.loc[s_file, 'slide_scene']
            s_opath = s_format_afsubdir.format(s_afsubdir, s_slide_scene)
            os.makedirs(s_opath, exist_ok=True)
            # save image
            i_round_int = df_img_marker.loc[s_file, 'round_int']
            s_markers = df_img_marker.loc[s_file, 'markers'] # implement!
            s_slide = df_img_marker.loc[s_file, 'slide']
            s_scene = df_img_marker.loc[s_file, 'scene']
            s_color = config.d_nconv['ls_color_order_jinxif'][df_img_marker.loc[s_file, 'color_int']]  # transalte!
            s_ofile_img = config.d_nconv['s_format_tiff_afsubreg'].format(config.d_nconv['s_round_jinxif'], i_round_int, s_markers, s_slide, s_scene, s_color, 'SubMics_ORG')  # Registered-R{}_{}_{}_{}_{}_Sub{}.tif
            io.imsave(s_opath+s_ofile_img, a_img, check_contrast=False)  # plugin='tifffile', check_contrast=False
            print(f'detected lines: yaxis {i_yaxis} xaxis {i_xaxis} | transform {s_file} ...')
            # only for R0 dapi
            if s_marker.startswith(config.d_nconv['s_marker_dapi']) and (i_round_int == 0):
                # extend linemask
                _grow(ab_segment=ab_mask_line, i_step=i_exp_line)
                # save line mask as numpy array!
                s_ofile_mask = config.d_nconv['s_format_tiff_micsstitchline'].format(s_slide_scene)
                np.save(s_opath+s_ofile_mask, ab_mask_line)
            # breake loop for this marker
            break


def trafo_spawn(
        s_batch,
        #ds_marker_rename = {},
        #ds_slidescene_rename = {},
        i_exp_line = 6,  # should be one more as the common doughnut which is usually exp5.
        # processing
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '64G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # file system
        s_micsdir = config.d_nconv['s_micsdir'],  #'./MicsImages/'
        s_afsubdir = config.d_nconv['s_afsubdir'],  #'./SubtractedRegisteredImages/'
        s_format_afsubdir = config.d_nconv['s_format_afsubdir'],  # {}{}/  s_afsubdir, slide_scene
    ):
    '''
    '''
    # for the batch
    print(f'trafo_spawn: {s_batch}')

    # set run commands
    s_pathfile_template = 'template_micstrafo_batch.py'
    s_pathfile = f'micstrafo_batch_{s_batch}.py'
    s_srun_cmd = f'python3 {s_pathfile}'
    ls_run_cmd = ['python3', s_pathfile]

    ## any ##
    # load template script code
    with open(f'{s_path_module}src/{s_pathfile_template}') as f:
        s_stream = f.read()

    # edit code generic
    #s_stream = s_stream.replace('peek_s_batch', s_batch)
    #s_stream = s_stream.replace('peek_i_line_intensity', str(i_line_intensity))
    s_stream = s_stream.replace('peek_i_exp_line', str(i_exp_line))
    s_stream = s_stream.replace('peek_s_micsdir', s_micsdir)
    s_stream = s_stream.replace('peek_s_afsubdir', s_afsubdir)
    s_stream = s_stream.replace('peek_s_format_afsubdir', s_format_afsubdir)

    # write executable script code to file
    time.sleep(4)
    with open(s_pathfile, 'w') as f:
        f.write(s_stream)

    # execute script
    if s_type_processing == 'slurm':
        # generate sbatch file
        s_pathfile_sbatch = f'micstrafo_batch_{s_batch}.sbatch'
        config.slurmbatch(
            s_pathfile_sbatch = s_pathfile_sbatch,
            s_srun_cmd = s_srun_cmd,
            s_jobname = f'mt{s_batch}',
            s_partition = s_slurm_partition,
            s_gpu = None,
            s_mem = s_slurm_mem,
            s_time = s_slurm_time,
            s_account = s_slurm_account,
        )
        # Jenny this is cool! Popen rocks.
        subprocess.run(
            ['sbatch', s_pathfile_sbatch],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    else:  # non-slurm
        # Jenny this is cool! Popen rocks.
        s_file_stdouterr = 'slurp-micstrafo_batch_{s_batch}.out'.replace('-','')
        o_process = subprocess.run(
            ls_run_cmd,
            stdout=open(s_file_stdouterr, 'w'),
            stderr=subprocess.STDOUT,
        )


#def patch_stichlines(
#):
#'''
#i_line_exp = 5,
#descrption:
#  remove nucleus and cells that touch the stiching lines plus exp5 px?
#  do this for every basinfile?!
#'''
# load linemask
# expand linemaska <= trafo step
# for each basin file
# extract labels below the linemask
# erase extracted labeles entierly
# save modified linemask
#pass

