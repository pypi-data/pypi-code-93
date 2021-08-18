#####
# title: afsub.py
#
# language: python3
# author: Jenny, bue
# license: GPLv>=3
# date: 2021-04-00
#
# description:
#     jinxif python3 library to run auto fluorescence subtraction
#####


# library
from jinxif.extract import config
import numpy as np
import os
import shutil
import skimage
from skimage import io
import subprocess
import time



# global var
s_path_module = os.path.abspath(os.path.dirname(__file__))
s_path_module = s_path_module.replace('extract','')

# functions
def afsubtract_images(
        df_img,
        ds_early = {'c2':'R0c2','c3':'R0c3','c4':'R0c4','c5':'R0c5'},
        ds_late = {'c2':'R5Qc2','c3':'R5Qc3','c4':'R5Qc4','c5':'R5Qc5'},
        es_exclude = {},
        s_subdir = './SubtractedRegisteredImages/',
        b_8bit = False
    ):
    '''
    version: 2021-04-30

    input: 
        the RoundsCyclesTable with real exposure times
        df_img: dataframe of images to process can be generated with basic.pars_org and imgmeta.add_exposure.
            columns [ 'color', 'exposure', 'marker'] and, if ds_early ['round_ord'], are important.
            index with image names.
        ds_early: dictionary mapping channel color to the early round Qc marker to subtract.
            if no such round exist set to {}.
        ds_late: dictionary mapping channel color to the late round Qc marker to subtract.
        es_exclude: list of markers not needing subtraction.
            note that DAPI and all marker on (>)c5 and ds_early and ds_late will be excluded automatically.

    description:
        this code loads 16 bit grayscale tiffs, 
        performs, if d_eraly not given {}, simple AF subtraction 
        else scaled AF subtraction based on the round position between early and late AF
        of channels/rounds defined by the user,
        and outputs 8 bit or 16 bit AF subtracted tiffs for visualization.
    '''
    # generate dataframe of markers excluded from subtraction
    df_nonafsub = df_img.loc[df_img.marker.isin(es_exclude), :]

    # generate dataframe of markers which have to be af subtracted
    es_nonafsub_marker = set(ds_early.values()).union(set(ds_late.values())).union(es_exclude)
    es_afsub_marker = set(df_img.marker).difference(es_nonafsub_marker)
    df_afsub = df_img.loc[df_img.marker.isin(es_afsub_marker), :]
    print(f'The background images {df_afsub.index.tolist}')
    print(f'The background markers {df_afsub.marker.tolist}')

    # copy markers excluded from subtraction tiffs
    for s_file in df_nonafsub.index.tolist():
        print(f'Copy {s_file} to {s_subdir} ...')
        os.makedirs(s_subdir, exist_ok=True)
        shutil.copyfile(f'{df_img.index.name}{s_file}', f'{s_subdir}{s_file}')

    # add columns with input needed for af subtraction
    # BUE 20210430: maybe simple panda merge and some operation would do, no loop needed?
    for s_index in df_afsub.index.tolist():
        print(f'Add AF subtraction calculation input for {s_index} ...')
        s_scene = df_afsub.loc[s_index, 'scene']
        s_color = df_afsub.loc[s_index, 'color']
        i_round = df_afsub.loc[s_index, 'round_num']
        df_scene = df_img.loc[df_img.scene == s_scene, :]

        # handle late qc round
        s_late = ds_late[s_color]
        if df_scene.loc[(df_scene.marker == s_late), :].shape == (0,0):
            sys.exit(f' Missing late AF channel for {s_scene} {s_color}')
        df_afsub.loc[s_index, 'sub_late'] = df_scene.loc[(df_scene.marker == s_late), :].index[0]
        df_afsub.loc[s_index, 'sub_late_exp'] = df_scene.loc[(df_scene.marker == s_late), 'exposure'][0]

        # if early qc round exist
        s_early = ''
        if len(ds_early) > 0:

            #  handle early qc round
            s_early = ds_early[s_color]
            if df_scene.loc[(df_scene.marker == s_early), :].shape == (0,0):
                sys.exit(f' Missing early AF channel for {s_scene} {s_color}')
            i_early = df_scene.loc[(df_scene.marker == s_early), 'round_num'][0]
            i_late = df_scene.loc[(df_scene.marker == s_late), 'round_num'][0]
            df_afsub.loc[s_index, 'sub_early'] = df_scene.loc[(df_scene.marker == s_early), :].index[0]
            df_afsub.loc[s_index, 'sub_early_exp'] = df_scene.loc[(df_scene.marker == s_early),'exposure'][0]
            df_afsub.loc[s_index, 'sub_ratio_late'] = np.clip((i_round - i_early) / (i_late - i_early), 0, 1)
            df_afsub.loc[s_index, 'sub_ratio_early'] = np.clip(1 - (i_round - i_early) / (i_late - i_early), 0, 1)

        # finalize
        df_afsub.loc[s_index,'sub_name'] = f'{s_early}{s_late}' # used for filename only


    # loop to subtract
    for s_index in df_afsub.index.tolist():
        print(f'\nProcessing AF subtractionf for: {s_index} ...')
        # load images
        a_img = io.imread(f'{df_afsub.index.name}{s_index}')
        a_late = io.imread(f"{df_afsub.index.name}{df_afsub.loc[s_index,'sub_late']}")  # background

        if len(ds_early) > 0:

            # divide each image by exposure time
            a_img_exp = a_img / df_afsub.loc[s_index, 'exposure']
            a_early = io.imread(f"{df_afsub.index.name}{df_afsub.loc[s_index,'sub_early']}")
            a_early_exp = a_early / df_afsub.loc[s_index,'sub_early_exp']
            a_late_exp = a_late / df_afsub.loc[s_index, 'sub_late_exp']

            # combine early and late based on round_num
            a_early_exp = a_early_exp * df_afsub.loc[s_index, 'sub_ratio_early']
            a_late_exp = a_late_exp * df_afsub.loc[s_index, 'sub_ratio_late']

            # subtract 1 ms AF from 1 ms signal
            # multiply by original image exposure time
            a_sub = (a_img_exp - a_early_exp - a_late_exp) * df_afsub.loc[s_index,'exposure']

        else:
            # divide each image by exposure time
            # subtract 1 ms AF from 1 ms signal
            # multiply by original image exposure time
            a_sub = (a_img / df_afsub.loc[s_index, 'exposure'] - a_late / df_afsub.loc[s_index, 'sub_late_exp']) * df_afsub.loc[s_index, 'exposure']

        # generate af subtracted tiff
        a_zero = (a_sub.clip(min=0)).astype(int)
        if b_8bit:
            a_bit = (a_zero / 256).astype(np.uint8)
        else:
            a_bit = skimage.img_as_uint(a_zero)
        # BUE 20210430: chinlab filename convention dependent
        s_color = '_' + df_afsub.loc[s_index, 'color'] + '_'
        s_fname = f'{s_subdir}{s_index.split(s_color)[0]}_Sub{df_afsub.loc[s_index,"sub_name"]}{s_color}{s_index.split(s_color)[1]}'
        io.imsave(s_fname, a_bit)

    # output
    return(df_afsub, df_nonafsub)


def afsub_spawn(
        es_slide,
        ds_early = {'c2':'R0c2','c3':'R0c3','c4':'R0c4','c5':'R0c5'},
        ds_late = {'c2':'R5Qc2','c3':'R5Qc3','c4':'R5Qc4','c5':'R5Qc5'},
        es_exclude = {},
        b_parallel = True,
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '128G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        s_codedir = './',
        s_regdir = './RegisteredImages/',
        s_subdir = './SubtractedRegisteredImages/',
    ):
    '''
    version: 2021-04-30
    bue: should be come a propper subprocess.run implementation
    notes: ls_exclude = [DAPI, channel5, round 6q round 0 (used in ds_late, ds_early)]
      extraction time have to exist at codedir
      c5 and DAPI are naming convention to be excluded
    '''
    for s_slide in sorted(es_slide):
        # this have to be a python template!
        print(f'afsub_spawn: {s_slide}')

        # set run commands
        s_pathfile_afsubtraction_template = 'template_afsubtraction_slide.py'
        s_pathfile_afsubtraction = f'afsubtraction_slide_{s_slide}.py'.replace('-','')
        s_srun_cmd = f'python3 {s_pathfile_afsubtraction}'
        ls_run_cmd = ['python3', s_pathfile_afsubtraction]

        ## any ##
        # load template afsubtraction script code
        with open(f'{s_path_module}src/template_afsubtraction_slide.py') as f:
            s_stream = f.read()

        # edit code generic
        s_stream = s_stream.replace('s_slide', s_slide)
        s_stream = s_stream.replace('s_path_wd', './')
        s_stream = s_stream.replace('s_path_regist', s_regdir)
        s_stream = s_stream.replace('s_path_dest', s_subdir)
        s_stream = s_stream.replace('dsstream_early', str(ds_early))
        s_stream = s_stream.replace('dsstream_late', str(ds_late))
        s_stream = s_stream.replace('esstream_exclude', str(es_exclude))

        # write executable afsubtraction script code to file
        with open(s_pathfile_afsubtraction, 'w') as f:
            f.write(s_stream)

        # execute afsubtraction script
        if b_parallel and (s_type_processing == 'slurm'):
            # generate sbatch file
            s_pathfile_sbatch = f'afsubtraction_{s_slide}.sbatch'.replace('-','')
            config.slurmbatch(
                s_pathfile_sbatch=s_pathfile_sbatch,
                s_srun_cmd=s_srun_cmd,
                s_jobname=f'a{s_slide}',
                s_partition=s_slurm_partition,
                s_gpu=None,
                s_mem=s_slurm_mem,
                s_time=s_slurm_time,
                s_account=s_slurm_account,
            )
            # Jenny this is cool! Popen rocks.
            time.sleep(4)
            subprocess.run(
                ['sbatch', s_pathfile_sbatch],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        else:  # non-slurm
           # Jenny this is cool! Popen rocks.
               s_file_stdouterr = 'slurp-afsubtraction_{s_slide}.out'.replace('-','')
               time.sleep(4)
               o_process = subprocess.run(
                   ls_run_cmd,
                   stdout=open(s_file_stdouterr, 'w'),
                   stderr=subprocess.STDOUT,
               )
               if not b_parallel:
                   o_process.wait()

