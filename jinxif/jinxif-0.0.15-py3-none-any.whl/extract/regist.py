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
from jinxif.extract import config
import os
import subprocess
import sys
import time

# global var
s_path_module = os.path.abspath(os.path.dirname(__file__))
s_path_module = s_path_module.replace('extract','')

# function
def regist_spawn(
        ddd_crop,
        es_filter_slide,
        s_type_registration = 'matlab',
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '128G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        s_dir_tiff_raw = './RawImages/',
        s_dir_tiff_registered = './RegisteredImages/',
    ):
    '''
    version: 2021-04-23

    input:
        ddd_crop: slide | scene_microscopy | scene_20000px dictionary with or without crop coordinates.
            a 20000px scene is scene that has <= 20000px whide and height.
            crop cordinates can be specified by None, [0,0,0,0,'xyxy'], or [0,0,0,0,'xyhw'].
            xyxy rectangle is specified by uper left and lower right corner.
            xyhw rectangle is specified by uper lefy corner and height and whide.

        es_filter_slide: a set of slide ids to process only sudden slides specified in dddl_crop.
            default is None wich will process all slides found in dddl_crop.

        s_type_registration: to specify which registraton algorythmen should be run.
            implemented is a matlab and a python keypoint registrationa
            which run a slightly different math in the back.
            at the moment default registration is matlab based.

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
    if es_filter_slide is None:
        es_filter_slide = set(ddd_crop.keys())

    # for each px scene
    for s_slide in sorted(es_filter_slide):
        for s_mscene, d_crop in sorted(ddd_crop[s_slide].items()):
            # load from one slide one mscene (even slide migth have more then one). outputs all pxscenes
            print(f'registration: {s_slide} {s_mscene} {sorted(ddd_crop[s_slide][s_mscene])} by {s_type_registration}')

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
                        sls_pxscene += "'-" + s_pxscene + "'"
                        sll_pxcrop += "[" + s_crop + "]"
                    else:
                        sls_pxscene += " '-" + s_pxscene + "'"
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
            with open(f'{s_path_module}/src/{s_pathfile_registration_template}') as f:
                s_stream = f.read()

            # edit code generic
            s_stream = s_stream.replace('s_slide', s_slide)
            s_stream = s_stream.replace('s_mscene', s_mscene)
            s_stream = s_stream.replace('s_regex_ext', r'_(ORG.tif)$')  # bue: might become function input because of file nameing convention
            s_stream = s_stream.replace('s_regex_round', r'^(R\d+Q?_).+$')  # bue: might become function input because of file nameing convention
            s_stream = s_stream.replace('s_regex_marker', r'^.+_(.+\..+\..+\.[^_]+_).+$')  # bue: might become function input because of file nameing convention
            s_stream = s_stream.replace('s_regex_micchannel', r'^.*(_c\d+_).*$')  # bue: might become function input because of file nameing convention
            s_stream = s_stream.replace('s_imgall_glob', 'R*_*_{}_*-{}_c*_ORG.tif'.format(s_slide, s_mscene))  # bue: might become function input because of file nameing convention
            s_stream = s_stream.replace('s_imgdapi_glob', 'R*_*_{}_*-{}_c1_ORG.tif'.format(s_slide, s_mscene))  # bue: might become function input because of file nameing convention
            s_stream = s_stream.replace('s_imgdapi_ref_glob', 'R1_*_{}_*-{}_c1_ORG.tif'.format(s_slide, s_mscene))  # bue: might become function input because of file nameing convention
            s_stream = s_stream.replace('s_src_dir', '{}{}/'.format(s_dir_tiff_raw, s_slide))  # bue: might become function input because of folder convention
            s_stream = s_stream.replace('s_dst_dir', s_dir_tiff_registered)  # bue: might become function input because of folder convention
            s_stream = s_stream.replace('i_npoint', str(10000))  # bue: number of key points used for registration, might become function input
            # edit code matlab only
            s_stream = s_stream.replace('sls_pxscene', sls_pxscene)   # all pxsenes belonging to one mscene in the same order as crop coorinates
            s_stream = s_stream.replace('sll_pxcrop', sll_pxcrop)  # crop ccorinates for one mscene maybe many pxscene
            # edit code python only
            s_stream = s_stream.replace('sd_pxcrop', str(ddd_crop[s_slide][s_mscene]))  # crop ccorinates for one mscene maybe many pxscene
            s_stream = s_stream.replace('s_qcregistration_dir', './QC/RegistrationPlots/')  # bue: might become function input because of folder convention

            # write executable registration script code to file
            with open(s_pathfile_registration, 'w') as f:
                f.write(s_stream)

            # execute registration script
            if s_type_processing == 'slurm':
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
                time.sleep(4)
                subprocess.run(
                    ['sbatch', s_pathfile_sbatch],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
            else:  # non-slurm
               # Jenny this is cool! Popen rocks.
               s_file_stdouterr = 'slurp-registration_{s_type_registration}_{s_slide}_{s_mscene}.out'.replace('-','')
               time.sleep(4)
               subprocess.run(
                   ls_run_cmd,
                   stdout=open(s_file_stdouterr, 'w'),
                   stderr=subprocess.STDOUT,
               )


# run from the command line
#if __name__ == '__main__':

