#####
# title: util.py
#
# language: python3
# author: Jenny, bue
# license: GPLv>=3
# date: 2021-04-00
#
# description:
#     jinxif python3 utility library.
#     this are helpfull functions that are not a direct task of the pipeline.
#####


# library
import json
import os

# functions
def underscore_to_dot(s_batch, s_wd='./', s_start='R', ei_underscore_to_dot = {1,2,3}, s_end='ORG.tif'):
    '''
    version: 2021-03-29

    input:
        s_batch: batch id. this is only used for the output filename.
        s_wd: work directory. default is present working directory.  # bue2021-03-29: actually RawImage/slide directory
        s_start: file name starts with.
        s_end: file name ends with.
        ei_underscore_to_dot: set of underscore indexes that should be replaced by dots.

    output:
        ds_rename: renameing dictionary

    description:
        for nameing convention ok image files
        change stain separator from underscore to dot
    '''
    i_max = max(ei_underscore_to_dot)
    ds_replace = {}
    for s_file in sorted(os.listdir(s_wd)):
        if s_file.startswith(s_start) and s_file.endswith(s_end):
            print(f'process: {s_file}')
            s_old = ''
            s_new = ''
            for i_stain, s_stain in enumerate(s_file.split('_')):
                s_old += s_stain + '_'
                if i_stain in ei_underscore_to_dot:
                    s_new += s_stain + '.'
                else:
                    s_new += s_stain + '_'
                if (i_stain > i_max):
                   break
            if (s_new != s_old):
                ds_replace.update({s_old: s_new})
    # output
    s_pathfile = f'{s_wd}{s_batch}__replace_underscore_to_dot.json'
    json.dump(ds_replace, open(s_pathfile, 'w'), indent=4, sort_keys=True)
    print(f'write: {s_pathfile}')
    return(ds_replace)


def dchange_fname(
        ds_rename={'_oldstring_':'_newstring_'},
        b_test=True,
        s_wd='./',
    ):
    """
    version: 2021-03-30

    input:
        d_rename: {'_oldstring_':'_newstring_'}.
        b_test: set boolean True to check result befor dryrun. default is True.
        s_wd: working directory. default is present working directory. # bue 20210330: actually ./RawImages/slide/

    output:
        stdout
        changed filesames, if b_test=False

    description:
        replace anything in file name, based on dictionary of key = old values = new
    """
    for s_old, s_new in sorted(ds_rename.items()):
        i_change = 0
        for s_file in os.listdir(s_wd):
            if s_file.find(s_old) > -1:
                i_change += 1
                s_file_old = s_file
                s_file_new = s_file.replace(s_old,s_new)
                #print(f'changed file {s_file_old}\tto {s_file_new}')
                if not (b_test):
                    os.rename(f'{s_wd}{s_file}', f'{s_wd}{s_file_new}')
        if i_change > 0:
            print(f'changed {s_old} file\n{s_file_old} to\n{s_file_new} ...')
        print(f'total number of {s_old} files changed is {i_change}\n')

