#####
# title: regist.py
#
# language: python3
# author: Jenny, bue
# license: GPLv>=3
# date: 2021-04-00
#
# description:
#     jinxif python3 library to run the matlab and python registration scripts
#####


# library
from jinxif import basic
from jinxif import config
from jinxif import jfplt
import json
import numpy as np
import os
import re
from skimage import io
import subprocess
import sys
import time

# development
#import importlib
#importlib.reload()

# global var
s_path_module = os.path.abspath(os.path.dirname(__file__))
s_path_module = re.sub(r'jinxif$','jinxif/', s_path_module)


# function
def save_cropcoor(
        s_batch,
        ddd_crop,
        s_rawdir = config.d_nconv['s_rawdir'],  #'./RawImages/',
    ):
    '''
    version:  2021-06-18

    input:
        s_batch: string to specify the batch.
        ddd_crop: batch whide standartisized crop coordinate dictionary.
        s_rawdir: raw image driectory.

    output:
        crop_coordinates.json file in s_rawdir.

    description:
        save batch realted crop coordinate dictionary as json file.
    '''
    # write crop coordinates to file
    s_pathfile = f'{s_rawdir}{config.d_nconv["s_format_json_crop"].format(s_batch)}'
    print(f'ddd_crop content:', ddd_crop)
    print(f'write to file: {s_pathfile}')
    json.dump(ddd_crop, open(s_pathfile, 'w'), sort_keys=True)  # indent=4


def save_exposuretimecorrect(
        s_batch,
        ddd_slidepxscene_marker_exposuretime_correct,
        s_metadir = config.d_nconv['s_metadir'],  #'./MetaImages/',
    ):
    '''
    version:  2021-07-31

    input:
        s_batch: string to specify the batch.
        ddd_slidepxscene_marker_exposuretime_correct: batch whide exposure time correction dictionary.
        s_metadir: image metadata driectory.

    output:
        exposuretime_correct.json file in s_metadir.

    description:
        save batch realted exposure time correct dictionary as json file.
    '''
    # write exposure time correction to file
    s_pathfile = f'{s_metadir}{config.d_nconv["s_format_json_etc"].format(s_batch)}'
    print(f'ddd_slidepxscene_marker_exposuretime_correct, content:', ddd_slidepxscene_marker_exposuretime_correct)
    print(f'write to file: {s_pathfile}')
    json.dump(ddd_slidepxscene_marker_exposuretime_correct, open(s_pathfile, 'w'), sort_keys=True, indent=4)


################
# registration #
#################

# spawner
def regist_spawn(
        ddd_crop,
        es_slide = None,
        s_type_registration = 'matlab',
        #  naming convention setting
        s_regex_ext = r'_(ORG.tif)$',  # regex file extension?
        s_regex_round = r'^(R\d+Q?_).+$',  # regex round of raw tiff
        s_regex_marker = r'^.+_(.+\..+\..+\.[^_]+_).+$',  # regex markers in raw tiff
        s_regex_micchannel = r'^.*(_c\d+_).*$',  # regex color microscopy channel
        s_imgall_glob = 'R*_*_{}_*-{}_c*_ORG.tif', # regex raw tiff
        s_imgdapi_glob = 'R*_*_{}_*-{}_c1_ORG.tif', # regex raw dapi tiff
        s_imgdapi_ref_glob = 'R1_*_{}_*-{}_c1_ORG.tif', # regex raw dapi refernce tiff
        i_npoint = str(10000),  # number of key points used for registration
        # processing
        b_parallel = True,
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '64G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # output
        s_dir_tiff_raw = config.d_nconv['s_rawdir'],  #'./RawImages/',
        s_dir_tiff_registered = config.d_nconv['s_regdir'],  #'./RegisteredImages/',
    ):
    '''
    version: 2021-04-23

    input:
        ddd_crop: slide | scene_microscopy | scene_20000px dictionary with or without crop coordinates.
            a 20000px scene is scene that has <= 20000px whide and height.
            crop cordinates can be specified by None, [0,0,0,0,'xyxy'], or [0,0,0,0,'xyhw'].
            xyxy rectangle is specified by uper left and lower right corner.
            xyhw rectangle is specified by uper lefy corner and height and whide.

        es_slide: set of slide ids to process only sudden slides specified in dddl_crop.
            default is None wich will process all slides found in dddl_crop.

        s_type_registration: to specify which registraton algorythmen should be run.
            implemented is a matlab and a python keypoint registrationa
            which run a slightly different math in the back.
            at the moment default registration is matlab based.

        b_parallel: boolean to specify if slides shoudl be parallel processed.
            set to False if your hardware can't take it.
        s_type_processing: to specify if registration should be run on the slurm cluster
            or on a simple slurp machine.
        s_slurm_partition: slurm cluster partition to use. options are 'exacloud', 'light'.
        s_slurm_mem: slurm cluster memory allocation. format '64G'.
        s_slurm_time: slurm cluster time allocation in hour or day format. max '36:00:00' [hour] or '30-0' [day].
        s_slurm_account: slurm cluster account to credit time from. 'gray_lab', 'chin_lab', 'heiserlab'.

        s_dir_tiff_raw: input directory which contains a folder for each requested slide
            with tiffs for each microscopy scene in it.

        s_dir_tiff_registered: output directory where for each 20000px scene
            a folder will registered tiffs will be generated.

    output:
        for each slide 20000px scene a folder with registered tiffs, one for each round channel.

    description:
        main routine for registration and cropping.
        this is done in one function, because the read but not write big tiffs (>4[GB]).
    '''
    # handlde input
    if es_slide is None:
        ls_slide = sorted(ddd_crop.keys())
    else:
        ls_slide = sorted(es_slide)

    # for each px scene
    for s_slide in ls_slide:
        for s_mscene, d_crop in sorted(ddd_crop[s_slide].items()):
            # load from one slide one mscene (even slide migth have more then one). outputs all pxscenes
            print(f'spawn jinxif.regist.registration for: {s_slide} {s_mscene} {sorted(ddd_crop[s_slide][s_mscene])} by {s_type_registration}')

            ## matlab registration ##
            if s_type_registration == 'matlab':
                # set run commands
                s_pathfile_registration_template = 'template_registration_mscene.m'
                s_pathfile_registration = f'registration_and_crop_slide_{s_slide}_mscene_{s_mscene}.m'.replace('-','')
                s_srun_cmd = f'matlab -nodesktop -nosplash -r "{s_pathfile_registration.replace(".m","")}; exit;"'
                ls_run_cmd = ['matlab', '-nodesktop', '-nosplash', '-r "{s_pathfile_registration.replace(".m","")}; exit;"']

                # hadle crop dictionary
                sls_pxscene = '{'
                sll_pxcrop = '{'
                for s_pxscene, l_crop in  ddd_crop[s_slide][s_mscene].items():
                    if l_crop is None:
                        s_crop = "'none'"
                    elif l_crop[-1] == 'xyxy':
                        s_crop = f'{l_crop[0]} {l_crop[1]} {l_crop[2] - l_crop[0]} {l_crop[3] - l_crop[1]}'
                    elif l_crop[-1] == 'xywh':
                        s_crop = f'{l_crop[0]} {l_crop[1]} {l_crop[2]} {l_crop[3]}'
                    else:
                        sys.exit(f"Error @ preprocessing.registration_and_crop_matlab_slide_pxscene : unknowen crop coordinte type in {l_crop}.\nknowen are None, [0,0,0,0,'xyxy'], and [0,0,0,0,'xywh'].")
                    if sls_pxscene == '{':
                        sls_pxscene += "'_" + s_pxscene + "'"
                        sll_pxcrop += "[" + s_crop + "]"
                    else:
                        sls_pxscene += " '_" + s_pxscene + "'"
                        sll_pxcrop += " [" + s_crop + "]"
                sls_pxscene += '}'
                sll_pxcrop += '}'

            ## python ##
            else:
                # set run commands
                s_pathfile_registration_template = 'template_registration_mscene.py'
                s_pathfile_registration = f'registration_and_crop_slide_{s_slide}_pxscene_{s_pxscene}.py'.replace('-','')
                s_srun_cmd = f'python3 {s_pathfile_registration}',
                ls_run_cmd = ['python3', s_pathfile_registration],

            ## any ##
            # load template registration script code
            with open(f'{s_path_module}src/{s_pathfile_registration_template}') as f:
                s_stream = f.read()

            # edit code generic
            s_stream = s_stream.replace('peek_s_slide', s_slide)
            s_stream = s_stream.replace('peek_s_mscene', s_mscene)
            s_stream = s_stream.replace('peek_s_regex_ext', s_regex_ext)  # bue: might become function input because of file nameing convention
            s_stream = s_stream.replace('peek_s_regex_round', s_regex_round)  # bue: might become function input because of file nameing convention
            s_stream = s_stream.replace('peek_s_regex_marker', s_regex_marker)  # bue: might become function input because of file nameing convention
            s_stream = s_stream.replace('peek_s_regex_micchannel', s_regex_micchannel)  # bue: might become function input because of file nameing convention
            s_stream = s_stream.replace('peek_s_imgall_glob', s_imgall_glob.format(s_slide, s_mscene))  # bue: might become function input because of file nameing convention
            s_stream = s_stream.replace('peek_s_imgdapi_glob', s_imgdapi_glob.format(s_slide, s_mscene))  # bue: might become function input because of file nameing convention
            s_stream = s_stream.replace('peek_s_imgdapi_ref_glob', s_imgdapi_ref_glob.format(s_slide, s_mscene))  # bue: might become function input because of file nameing convention
            s_stream = s_stream.replace('peek_s_src_dir', '{}{}/'.format(s_dir_tiff_raw, s_slide))  # bue: might become function input because of folder convention
            s_stream = s_stream.replace('peek_s_dst_dir', s_dir_tiff_registered)  # bue: might become function input because of folder convention
            s_stream = s_stream.replace('peek_i_npoint', str(10000))  # bue: number of key points used for registration, might become function input
            # edit code matlab only
            s_stream = s_stream.replace('peek_sls_pxscene', sls_pxscene)   # all pxsenes belonging to one mscene in the same order as crop coorinates
            s_stream = s_stream.replace('peek_sll_pxcrop', sll_pxcrop)  # crop ccorinates for one mscene maybe many pxscene
            # edit code python only
            s_stream = s_stream.replace('peek_d_pxcrop', str(ddd_crop[s_slide][s_mscene]))  # crop ccorinates for one mscene maybe many pxscene
            s_stream = s_stream.replace('peek_s_qcregistration_dir', './QC/RegistrationPlots/')  # bue: might become function input because of folder convention

            # write executable registration script code to file
            time.sleep(4)
            with open(s_pathfile_registration, 'w') as f:
                f.write(s_stream)

            # execute registration script
            if b_parallel and (s_type_processing == 'slurm'):
                # generate sbatch file
                s_pathfile_sbatch = f'registration_{s_type_registration}_{s_slide}_{s_mscene}.sbatch'.replace('-','')
                config.slurmbatch(
                    s_pathfile_sbatch=s_pathfile_sbatch,
                    s_srun_cmd=s_srun_cmd,
                    s_jobname=f'r{s_slide}_{s_mscene}',
                    s_partition=s_slurm_partition,
                    s_gpu=None,
                    s_mem=s_slurm_mem,
                    s_time=s_slurm_time,
                    s_account=s_slurm_account,
                )
                # Jenny this is cool! Popen rocks.
                subprocess.run(
                    ['sbatch', s_pathfile_sbatch],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
            else:  # non-slurm
                # Jenny this is cool! Popen rocks.
                s_file_stdouterr = 'slurp-registration_{s_type_registration}_{s_slide}_{s_mscene}.out'.replace('-','')
                subprocess.run(
                    ls_run_cmd,
                    stdout=open(s_file_stdouterr, 'w'),
                    stderr=subprocess.STDOUT,
                )
                if not b_parallel:
                    o_process.wait()



############################
# exposure time correction #
###########################

def exposure_time_correct(
        s_slidepxscene,
        dd_marker_exposuretime_correct,
        s_imagetype_original = 'ORG', 
        # filesystem
        s_regdir = config.d_nconv['s_regdir'],  #'./RegisteredImages/',
        s_format_regdir = config.d_nconv['s_format_regdir'],  #'{}{}/',  s_regdir, s_slide_pxscene
    ):
    '''
    version: 2021-07-31

    input:
        s_slidepxscen: slide pxscene hat should be corrected for expression time.
        dd_marker_exposuretime_correct: dictionary of dictionary that specifies for each marker 
            the is and should_be exposure time value.
        s_imagetype_original: string to specify the original image type that should be transformed
            to the ETC exposure time corrected image type.
        s_regdir: registration directory.
        s_format_regdir: registration directory subdirectory where the registerted tiff are.

    output:
        exposure time corrected registered tiff images replaceing the original register tiff images.

    description:
        function to correct for image intensity mistakes, cased by human error by wrongly entered exposure time on the microscope.
    '''
    # parse image files
    s_path = s_format_regdir.format(s_regdir, s_slidepxscene)
    df_img_reg = basic.parse_tiff_reg(s_wd=s_path)
    # for each marker that have to be corrected
    for s_marker, d_exposuretime_correct in dd_marker_exposuretime_correct.items():
        for s_ifile in df_img_reg.loc[(df_img_reg.marker == s_marker) & (df_img_reg.imagetype == s_imagetype_original),:].index:
            print(f'exposure_time_coorect: {s_ifile} ...')
            s_ofile = s_ifile.replace('_{}.'.format(s_imagetype_original), r'_ETC.')  # change output file image type to exposure time corrected
            # load registered image
            ai_image = io.imread(s_path + s_ifile)
            # adjust intensity
            i_shouldbe = d_exposuretime_correct['should_be']
            i_is = d_exposuretime_correct['is']
            # clip values to 8[bit] or 16[bit] image. 
            if (ai_image.dtype.type is np.uint8):
                np.clip(ai_image, a_min=0, a_max=int((2**8 - 1) * (i_is / i_shouldbe)), out=ai_image) 
            elif (ai_image.dtype.type is np.uint16):
                np.clip(ai_image, a_min=0, a_max=int((2**16 - 1) * (i_is / i_shouldbe)), out=ai_image) 
            else:
                sys.exit(f'Error @ jinxif.regist.exposure_time_correct : unknowen tiff image bit type {ai_image.dtype.type}.\nknown are 8[bit] and 16[bit] tiff images.')
            # do correction
            ai_image = (ai_image * i_shouldbe / i_is).astype(ai_image.dtype)
            # save registered intensity correctd image
            print(f'save: {s_ofile}')
            io.imsave(s_path + s_ofile, ai_image)
            # delete original registered image file
            print(f'delete: {s_ifile}')
            os.remove(s_path + s_ifile)


# spawner function
def exposure_time_correct_spawn(
        ddd_slidepxscene_marker_exposuretime_correct,
        s_imagetype_original = 'ORG', 
        # processing
        b_parallel = True,
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '64G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # file system
        s_regdir = config.d_nconv['s_regdir'],  #'./RegisteredImages/',
        s_format_regdir = config.d_nconv['s_format_regdir'],  #'{}{}/',  s_regdir, s_slide_pxscene
    ):
    '''
    version: 2021-07-30

    input:
        ddd_slidepxscene_marker_exposuretime_correct:
        s_imagetype_original: string to specify the original image type that should be transformed
            to the ETC exposure time corrected image type.
        b_parallel: boolean to specify if slides shoudl be parallel processed.
            set to False if your hardware can't take it.
        s_type_processing: string to specify if pipeline is run on a slum cluster on not.
            knowen vocabulary is slurm and any other string.
        s_slurm_partition: slurm cluster partition to use.
            OHSU ACC options are 'exacloud', 'light', (and 'gpu').
            the default is tweaked to OHSU ACC settings.
        s_slurm_mem: slurm cluster memory allocation. format '64G'.
        s_slurm_time: slurm cluster time allocation in hour or day format.
            OHSU ACC max is '36:00:00' [hour] or '30-0' [day].
            the related qos code is tewaked to OHSU ACC settings.
        s_slurm_account: slurm cluster account to credit time from.
            my OHSU ACC options are 'gray_lab', 'chin_lab', 'heiserlab'.

        s_regdir: registerd tiff images directory path.
        s_format_regdir: regdir subdirectory  structure, which is a subdirectery per slide.

    output:

    description:
    '''
    for s_slidepxscene,  dd_marker_exposuretime_correct in  sorted(ddd_slidepxscene_marker_exposuretime_correct.items()):
        # this have to be a python template!
        print(f'spawn jinxif.regist.exposure_time_correct for: {s_slidepxscene} ...')

        # set run commands
        s_pathfile_template = 'template_exposuretimecorrect_slidepxscene.py'
        s_pathfile = f'exposuretimecorrect_slidepxscene_{s_slidepxscene}.py'
        s_srun_cmd = f'python3 {s_pathfile}'
        ls_run_cmd = ['python3', s_pathfile]

        ## any ##
        # load template script code
        with open(f'{s_path_module}src/{s_pathfile_template}') as f:
            s_stream = f.read()

        # edit code generic
        s_stream = s_stream.replace('peek_s_slidepxscene', s_slidepxscene)
        s_stream = s_stream.replace('peek_dd_marker_exposuretime_correct', str(dd_marker_exposuretime_correct))
        s_stream = s_stream.replace('peek_s_imagetype_original', s_imagetype_original)
        s_stream = s_stream.replace('peek_s_regdir', s_regdir)
        s_stream = s_stream.replace('peek_s_format_regdir', s_format_regdir)

        # write executable script code to file
        time.sleep(4)
        with open(s_pathfile, 'w') as f:
            f.write(s_stream)

        # execute script code
        if b_parallel and (s_type_processing == 'slurm'):
            # generate sbatch file
            s_pathfile_sbatch = f'exposuretimecorrect_slidepxscene_{s_slidepxscene}.sbatch'
            config.slurmbatch(
                s_pathfile_sbatch = s_pathfile_sbatch,
                s_srun_cmd = s_srun_cmd,
                s_jobname = f'c{s_slidepxscene}',
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
            s_file_stdouterr = 'slurp-exposuretimecorrect_slidepxscene_{s_slidepxscene}.out'.replace('-','')
            o_process = subprocess.run(
                ls_run_cmd,
                stdout=open(s_file_stdouterr, 'w'),
                stderr=subprocess.STDOUT,
            )
            if not b_parallel:
                o_process.wait()


############
# qc plot #
###########

def visualize_reg_images(
        s_slide,
        s_color = config.d_nconv['s_color_dapi_jinxif'],  #'c1'
        dl_crop = {},
        s_regdir = config.d_nconv['s_regdir'],  #'./RegisteredImages/',
        s_format_regdir = config.d_nconv['s_format_regdir'],  #'{}{}/', # s_regdir, s_slide_pxscene
        s_qcdir = config.d_nconv['s_qcdir'],  #'./QC/',
    ):
    '''
    version: 2021-06-29

    input:
        s_slide: slide id from which per mscene qc images should be generated.
        s_color: microscpy channel to check. default is c1 which is DAPI.
        dl_crop: dictionary of crop parameters. the dictionary format is something like
            {'slide_scene': [0,0, 0,0, 'xyxy'], 'slide_scene': [0,0, 0,0, 'xywh']}
        s_regdir: registerd tiff images directory path.
        s_format_regdir: regdir subdirectory  structure, which is a subdirectery per slide.
        s_qcdir: qc directory path.

    output:
        png plot under s_qcdir + s_regdir.split("/")[-2]

    description:
        generte array reg images to check tissue identity, focus, etc.
    '''
    print(f'run jinxif.regist.visualize_reg_images for slide: {s_slide} ...')
    for s_dir in sorted(os.listdir(s_regdir)):
        s_path = s_format_regdir.format(s_regdir, s_dir)
        if s_dir.startswith(s_slide) and os.path.isdir(s_path):
            print(f'visualize_reg_images for: {s_dir} ...')
            df_img_slide = basic.parse_tiff_reg(s_wd=s_path)  # actually this is already slide_pxscene
            for s_slide_pxscene in sorted(df_img_slide.slide_scene.unique()):
                print(f'slide_scene: {s_slide_pxscene}')

                # generate output path and filename
                s_path = f'{s_qcdir}{s_regdir.split("/")[-2]}/'
                s_pathfile = f'{s_path}{s_slide_pxscene}_{s_color}_reg.png'

                # filter data
                df_img_slidepxscene = df_img_slide.loc[
                    (df_img_slide.color == s_color) & (df_img_slide.slide_scene == s_slide_pxscene),
                    :
                ].sort_values('round_order')
                df_img_slidepxscene.index.name = df_img_slide.index.name

                # generate figure
                jfplt.array_img_scatter(
                    df_img = df_img_slidepxscene,
                    s_xlabel = 'marker',
                    ls_ylabel = ['slide_scene','color'],
                    s_title = 'round',
                    ti_array = (2, len(df_img_slidepxscene)//2 + 1),  # // is floor division
                    ti_fig = (22,8),
                    cmap = 'gray',
                    dl_crop = dl_crop,
                    s_pathfile = s_pathfile,
                )


# spawner function
def visualize_reg_images_spawn(
        es_slide,
        s_color = config.d_nconv['s_color_dapi_jinxif'],  #'c1'
        dl_crop = {},
        # processing
        b_parallel = True,
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '64G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # file system
        s_regdir = config.d_nconv['s_regdir'],  #'./RegisteredImages/'
        s_format_regdir = config.d_nconv['s_format_regdir'],  #'{}{}/' # s_regdir, s_slide_pxscene
        s_qcdir = config.d_nconv['s_qcdir'],  #'./QC/'
    ):
    '''
    version: 2021-06-29

    input:
        es_slide: set of slide id from which per mscene qc images should be generated.
        s_color: microscpy channel to check. default is c1 which is DAPI.
        dl_crop: dictionary of crop parameters. the dictionary format is something like
            {'slide_scene': [0,0, 0,0, 'xyxy'], 'slide_scene': [0,0, 0,0, 'xywh']}
        b_parallel: boolean to specify if slides shoudl be parallel processed.
            set to False if your hardware can't take it.
        s_type_processing: string to specify if pipeline is run on a slum cluster on not.
            knowen vocabulary is slurm and any other string.
        s_slurm_partition: slurm cluster partition to use.
            OHSU ACC options are 'exacloud', 'light', (and 'gpu').
            the default is tweaked to OHSU ACC settings.
        s_slurm_mem: slurm cluster memory allocation. format '64G'.
        s_slurm_time: slurm cluster time allocation in hour or day format.
            OHSU ACC max is '36:00:00' [hour] or '30-0' [day].
            the related qos code is tewaked to OHSU ACC settings.
        s_slurm_account: slurm cluster account to credit time from.
            my OHSU ACC options are 'gray_lab', 'chin_lab', 'heiserlab'.
        s_regdir: registerd tiff images directory path.
        s_format_regdir: regdir subdirectory  structure, which is a subdirectery per slide.
        s_qcdir: qc directory path.

    output:
        png plot under s_qcdir + s_regdir.split("/")[-2]

    description:
        generte array reg images to check tissue identity, focus, etc.
    '''
    for s_slide in sorted(es_slide):
        # this have to be a python template!
        print(f'spawn jinxif.regist.visualize_reg_images for: {s_slide} ...')

        # set run commands
        s_pathfile_template = 'template_vizregimage_slide.py'
        s_pathfile = f'vizregimage_slide_{s_slide}.py'
        s_srun_cmd = f'python3 {s_pathfile}'
        ls_run_cmd = ['python3', s_pathfile]

        ## any ##
        # load template script code
        with open(f'{s_path_module}src/{s_pathfile_template}') as f:
            s_stream = f.read()

        # edit code generic
        s_stream = s_stream.replace('peek_s_slide', s_slide)
        s_stream = s_stream.replace('peek_s_color', s_color)
        s_stream = s_stream.replace('peek_dl_crop', str(dl_crop))
        s_stream = s_stream.replace('peek_s_regdir', s_regdir)
        s_stream = s_stream.replace('peek_s_format_regdir', s_format_regdir)
        s_stream = s_stream.replace('peek_s_qcdir', s_qcdir)

        # write executable script code to file
        time.sleep(4)
        with open(s_pathfile, 'w') as f:
            f.write(s_stream)

        # execute script code
        if b_parallel and (s_type_processing == 'slurm'):
            # generate sbatch file
            s_pathfile_sbatch = f'vizregimage_slide_{s_slide}.sbatch'
            config.slurmbatch(
                s_pathfile_sbatch = s_pathfile_sbatch,
                s_srun_cmd = s_srun_cmd,
                s_jobname = f'q{s_slide}',
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
            s_file_stdouterr = 'slurp-vizregimage_slide_{s_slide}.out'.replace('-','')
            o_process = subprocess.run(
                ls_run_cmd,
                stdout=open(s_file_stdouterr, 'w'),
                stderr=subprocess.STDOUT,
            )
            if not b_parallel:
                o_process.wait()
