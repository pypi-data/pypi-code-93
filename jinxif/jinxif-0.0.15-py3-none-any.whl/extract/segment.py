####
# title: segment.py
#
# language: Python3.7
# date: 2020-06-00
# license: GPL>=v3
# author: Jenny, bue
#
# description:
#   python3 script for cell segmentation
####

from cellpose import models
from jinxif.extract import basic
from jinxif.extract import config
#import mxnet as mx
import numba
from numba import jit
from numba.extending import overload
from numba.experimental import jitclass
import numpy as np
import os
#import pandas as pd
import subprocess
import scipy
import skimage
from skimage import io
import sys
import time
import torch


# global var
s_path_src = os.path.abspath(os.path.dirname(__file__))
s_path_src = s_path_src.replace('extract', 'src')


# functions
# BUE 20210510: I don't think this is ever used!
#def gpu_device():
#    try:
#        _ = mx.nd.array([1, 2, 3], ctx=mx.gpu())
#        mx_gpu = mx.gpu()
#    except mx.MXNetError:
#        return None
#    return mx_gpu


#def cellpose_nuc(key, dapi, diameter=30):
#    '''
#    BUE 20210510: not sure if try except fallback is clever. if you want tu run gpu you want!
#
#    smallest nuclei are about 9 pixels, lymphocyte is 15 pixels, tumor is 25 pixels
#    using 20 can capture large tumor cells, without sacrificing smaller cells,
#    '''
#    try:
#        nd_array = mx.nd.array([1, 2, 3], ctx=mx.gpu())
#        print(nd_array)
#        mx_gpu = mx.gpu()
#    except mx.MXNetError:
#        print('Mxnet error')
#        mx_gpu = None
#    model = models.Cellpose(model_type='nuclei', device=mx_gpu)
#    newkey = f"{key.split(' - Z')[0]} nuclei{diameter}"
#    print(f"modelling {newkey}")
#    channels = [0,0]
#    print(f'Minimum nuclei size = {int(np.pi*(diameter/10)**2)}')
#    masks, flows, styles, diams=model.eval(dapi, diameter=diameter, channels=channels, flow_threshold=0, min_size=int(np.pi*(diameter/10)**2))
#    return({newkey:masks})


#def cellpose_cell(key, zdh, diameter=25):
#    '''
#    BUE 20210510: not sure if try except fallback is clever. if you want tu run gpu you want!
#
#    big tumor cell is 30 pixels, lymphocyte about 18 pixels, small fibroblast 12 pixels
#    '''
#    try:
#        _ = mx.nd.array([1, 2, 3], ctx=mx.gpu())
#        mx_gpu = mx.gpu()
#    except mx.MXNetError:
#        mx_gpu = None
#    model = models.Cellpose(model_type='cyto', device=mx_gpu)
#    newkey = f"{key.split(' - Z')[0]} cell{diameter}"
#    print(f"modelling {newkey}")
#    channels = [2,3]
#    print(f'Minimum cell size = {int(np.pi*(diameter/5)**2)}')
#    masks, flows, styles, diams = model.eval(zdh, diameter=diameter, channels=channels, flow_threshold=0.6, cellprob_threshold=0.0, min_size= int(np.pi*(diameter/5)**2))
#    return({newkey:masks})

def cellpose_torch(s_imglabel, a_imgscaled, i_diameter, s_model_type, b_gpu=False):
    '''
    version: 2021-05-13

    input:
        s_imglabel:
        a_imgscaled:
        i_diameter:
        s_model_type:
        b_gpu:

    output:

    description:
    '''
    # got gpu?
    # bue 20210513: maybe check this earlyer!
    if b_gpu and not torch.cuda.is_available():
        sys.exit(f'Error @ segment.cellpose_torch : function called with b_gpu set {b_gpu},\nthough torch.cuda.is_available ({torch.cuda.is_available()}) could not detect any gpu.')
    
    # run model
    model = models.Cellpose(model_type=s_model_type, device=None, torch=b_gpu)

    if s_model_type == 'nuclei':
        s_imglabelnew = f"{s_imglabel.split(' - Z')[0]} nuclei{i_diameter}"
        li_channel = [0,0]
        r_flow_threshold = 0.0
        r_cellprob_threshold = 0.0
        i_min_size = int(np.pi * (i_diameter / 10)**2) # could be real

    elif s_model_type == 'cyto':
        s_imglabelnew = f"{s_imglabel.split(' - Z')[0]} cell{i_diameter}"
        li_channel = [2,3]
        r_flow_threshold = 0.6
        r_cellprob_threshold = 0.0
        i_min_size = int(np.pi * (i_diameter/5)**2)

    else:
        sys.exit(f'Error @ segment.cellpose_torch : unknowen s_model_type {s_model_type}.\nknowen are nuclei and cyto.')

    print(f"modelling: {s_imglabelnew}")
    print(f'minimum cell size = {i_min_size}')
    masks, flows, styles, diams = model.eval(
        x = a_imgscaled,
        channels = li_channel,
        diameter = i_diameter,  # bue: could be real
        flow_threshold = r_flow_threshold,
        cellprob_threshold = r_cellprob_threshold,
        min_size = i_min_size,
    )

    # output
    return({s_imglabelnew: masks})


def save_seg(processed_list, s_segdir, s_type='nuclei'):
    '''
    save the segmentation basins
    '''
    for d_item in processed_list:
        for newkey,mask in d_item.items():
            print(f"saving {newkey.split(' - ')[0]} {s_type} Basins")
            if s_type=='nuclei':
                os.makedirs(s_segdir, exist_ok=True)
                io.imsave(f"{s_segdir}{newkey} - Nuclei Segmentation Basins.tif", mask) #Scene 002 - Nuclei Segmentation Basins.tif
            elif s_type=='cell':
                os.makedirs(s_segdir, exist_ok=True)
                io.imsave(f"{s_segdir}{newkey} - Cell Segmentation Basins.tif", mask) #Scene 002 - Nuclei Segmentation Basins.tif
            #bue 20210422: else missing


def save_img(d_img, s_segdir,s_type='nuclei',ls_seg_markers=[]):
    '''
    save the segmentation basins
    BUE 20210510: can directely be integrated in load_single and load_stack!
    '''
    #save dapi or save the cyto projection
    if s_type=='nuclei':
        for key,dapi in d_img.items():
            print('saving DAPI')
            print(key)
            os.makedirs(s_segdir, exist_ok=True)
            io.imsave(f"{s_segdir}{key} - DAPI.png",dapi)
    elif s_type=='cell':
        for key,zdh in d_img.items():
            print('saving Cyto Projection')
            os.makedirs(s_segdir, exist_ok=True)
            io.imsave(f"{s_segdir}{key.split(' - ')[0]} - {'.'.join(ls_seg_markers)}_CytoProj.png",(zdh/255).astype('uint8'))
    else:
        print('choose nuceli or cell')


def load_single(s_wd, s_find, s_scene):
    '''
    load a single image containing the find strin, scale, return {filename:scaled image}
    '''
    d_img = {}
    for s_file in os.listdir(s_wd):
        if s_file.find(s_find) >-1:
            a_img = io.imread(f'{s_wd}{s_file}')
            a_scale = skimage.exposure.rescale_intensity(a_img, in_range=(np.quantile(a_img, 0.03), 1.5 * np.quantile(a_img, 0.9999)))
            d_img.update({f"{s_scene}": a_scale})
    print(f'Number of images = {len(d_img)}')
    return(d_img)


def load_stack(s_wd, df_img, s_find, s_scene, ls_markers, ls_rare):
    '''
    load an image stack in df_img, (df_img must have "path")
    scale, get mip, return {filename:mip}
    '''
    # BUE 20210510: whar is the point of this d_img dictionary, the way it is programmed it will always be one entry with a name and zdh!
    # it is used in segment.save_img
    # load_stack output is one entry but load_single output might be more, depends on s_find, but it looks like it is the round 1 dapi file from a specific slide_scene.
    # used for segment.cellpose_cell segment.cellpose_nuc imput which differ!
    # but could be directely called after load and save
    # used for segment.save_seg which as input has a list which will exactely have one d_result entry.
    # and can bedirectely called after load, save, cellpose_
    d_img = {}
    for s_file in os.listdir(s_wd):
        if s_file.find(s_find)>-1:
            a_img = io.imread(f'{s_wd}{s_file}')
            dapi = skimage.exposure.rescale_intensity(a_img, in_range=(np.quantile(a_img, 0.03), 1.5 * np.quantile(a_img, 0.9999)))

    #images
    imgs = []
    print(f'BUE ls_markers: {ls_markers}')
    print(f'BUE ls_rare: {ls_rare}')
    print(f'BUE df_img.marker: {df_img.marker}')
    df_common = df_img.loc[df_img.marker.isin(ls_markers) & ~df_img.marker.isin(ls_rare),:]
    df_rare =  df_img.loc[df_img.marker.isin(ls_markers) & df_img.marker.isin(ls_rare),:]
    print(f'BUE common paths: {df_common.path}')
    for s_path in df_common.path:
        print(s_path)
        img = io.imread(s_path)
        img_scale = skimage.exposure.rescale_intensity(img, in_range=(np.quantile(img, 0.03), 1.5 * np.quantile(img, 0.9999)))
        imgs.append(img_scale)
    print(f'BUE rare paths: {df_rare.path}')
    for s_path in df_rare.path:
        img = io.imread(s_path)
        img_scale = skimage.exposure.rescale_intensity(img, in_range=(np.quantile(img,0.03), 1.5 * np.quantile(img, 0.99999)))
        imgs.append(img_scale)
    print(f"BUE: number of images are {len(imgs)}")
    mip = np.stack(imgs).max(axis=0)
    zdh = np.dstack((np.zeros(mip.shape), mip, dapi)).astype('uint16')

    #name
    #s_index = df_common.index[0]
    #s_common_marker = df_common.loc[s_index,'marker_string']
    #s_name = os.path.splitext(df_common.index[0])[0]
    #s_name = s_name.replace(s_common_marker,".".join(ls_markers))
    # name
    s_name = f'{s_scene}_{".".join(ls_markers)}'
    d_img.update({s_name: zdh})
    print(f'Number of projection images = ({len(d_img)}')
    return(d_img)


# BUE 20210510: I don't think this is ever used!
#def load_img(s_subdir, s_find, s_sample, s_scene, ls_seg_markers, ls_rare):
#    '''
#    load dapi round and cell segmentation images
#    '''
    # image dataframe
#    df_seg = pd.DataFrame()
#    for s_dir in os.listdir(s_subdir):
#        if s_dir.find(s_sample) > -1:
#            df_img = basic.parse_org(s_wd=f'{s_subdir}{s_dir}/', s_type='reg_seg')
#            df_markers = df_img[df_img.marker.isin(ls_seg_markers)]
#            df_markers['path'] = [f'{s_subdir}/{s_dir}/{item}' for item in df_markers.index]
#            if df_img.index.str.contains(s_find).sum() == 1:
#                s_file = s_dir
#                dapi = io.imread(df_img[df_img.index.str.contains(s_find)].index[0])
#            df_seg = df_seg.append(df_markers)

    # load z_projection DAPIs
#    d_dapi = {}
#    d_cyto = {}

#    dapi_scale = skimage.exposure.rescale_intensity(dapi, in_range=(np.quantile(dapi, 0.03), 1.5 * np.quantile(dapi, 0.9999)))
#    d_dapi.update({f"{s_sample}-{s_scene}": dapi_scale})
#    imgs = []
    # images
#    df_common = df_seg[(df_seg.scene==s_scene) & (~df_seg.marker.isin(ls_rare))]
#    df_rare =  df_seg[(df_seg.scene==s_scene) & (df_seg.marker.isin(ls_rare))]
#    for s_path in df_common.path:
#        print(s_path)
#        img = io.imread(f'{s_subdir}{s_path}')
#        img_scale = skimage.exposure.rescale_intensity(img, in_range=(np.quantile(img, 0.03), 1.5 * np.quantile(img, 0.9999)))
#        imgs.append(img_scale)
#    for s_path in df_rare.path:
#        img = io.imread(s_path)
#        img_scale = skimage.exposure.rescale_intensity(img, in_range=(np.quantile(img, 0.03), 1.5 * np.quantile(img, 0.99999)))
#        imgs.append(img_scale)
#    mip = np.stack(imgs).max(axis=0)
#    zdh = np.dstack((np.zeros(mip.shape), mip,dapi)).astype('uint16')
#    d_cyto.update({f"{s_sample}-{s_scene}": zdh})
#    print(f'Number of images = {len(d_dapi)} dapi projections ({len(d_cyto)} cytoplasm projections) ')

#    return(d_dapi,d_cyto)


# BUE 20210510: i think pwn segement and match template would be better. spawner can be the same
def segment_spawn(
        # input
        es_slide,
        # segementation
        i_nuc_diam=30,
        i_cell_diam=30,
        s_type='nuclei', # this is kind of the seg partition nuclei or cell
        s_match='both',   # this specify the processing should be nucleus, cell, or match it is kind of overlaping with s_type, both is inconsistent
        s_seg_markers="['Ecad']", # this is only for the cell not the nucleus  this should be a list, not a string!
        s_rare="[]",  # this are markers that have to be enhanced
        s_data='cmif', # maybe diffeernt template for codex or so
        # slurm
        s_type_processing='slurm',
        s_slurm_partition='exacloud',
        s_slurm_gpu=None,  # if gpu is used depends on environment!  'gpu:p100:1'
	s_slurm_mem='128G',
	s_slurm_time='36:00:00',
	s_slurm_account='gray_lab',
        # filesustem
	s_regdir='./RegisteredImages/',
        s_segdir='./Segmentation/',
    ):
    '''
    version: 2021-04-23

    input:
        es_slide: set of slidenames that shoul get segmented.

        i_nuc_diam:
        i_cell_diam:
        s_type: what to segement 'cell' 'nuclei'
        s_seg_markers: "['Ecad']"
        s_rare: "[]"

        s_match: what should be run? 'seg' for segmentation, 'match' for matching
            nucleus and cytoplasm, 'both' to perform seg and match.
            seg workd definitely better with gpu, match works fine without gpu.

        s_data: knowen are 'cmif' or 'codex'.

        s_type_processing: to specify if registration should be run on the slurm cluster
            or on a simple slurp machine.

        s_partition: slurm cluster partition to use. options are 'exacloud', 'light'.
        s_gpu: slurm cluster gpu allocation. none None, any 'gpu:1',  faster 'gpu:v100:1', slower 'gpu:p100:1', not rapids compatible 'gpu:rtx2080:1'
        s_mem: slurm cluster memory allocation. format '64G'.
        s_time: slurm cluster time allocation in hour or day format. max '36:00:00' [hour] or '30-0' [day].
        s_account: slurm cluster account to credit time from. 'gray_lab', 'chin_lab', 'heiserlab'.

    description:
        spawns cellpose segmentation jobs by modifying a python and bash script,
        saving them and calling with subprocess.
        run either on slurm cluster or normal machine.
    '''
    # for each folder in regdir
    for s_folder in os.listdir(s_regdir):
        b_found = any([s_folder.startswith(s_slide) for s_slide in es_slide])  # bue 202104: maybe startswith is ok or maybe find in filename needed

        if b_found:
            print(f'Processing {s_folder}')

            # detect input folder which can be a registered slide or in a slide-pxscene folder
            s_imgdir = f'{s_regdir}{s_folder}/'

            # for each pxscene
            df_img = basic.parse_org(s_wd=f'{s_regdir}{s_folder}/', s_type='reg_seg')  # bue 20210422: dry
            print(df_img)
            for s_pxscene in sorted(set(df_img.scene)):

                # generate output slide-pxscene sting
                s_slide = s_folder.split('-Scene-')[0]  # BUE 20210510: should be part of parse_org!
                s_slide_pxscene= f'{s_slide}-Scene-{s_pxscene}' # BUE 20210510: should be part of parse_org!
                s_find = df_img[(df_img.rounds=='R1') & (df_img.color=='c1') & (df_img.scene==s_pxscene)].index[0]


                # load template script
                s_pathfile_template = f'{s_path_src}/template_cellpose_{s_data}.py'
                with open(s_pathfile_template) as f:
                    s_stream = f.read()

                # edit template code
                s_stream = s_stream.replace('SceneName', s_slide_pxscene)
                s_stream = s_stream.replace('FindDAPIString', s_find)
                s_stream = s_stream.replace('i_nuc_diam=int', f'i_nuc_diam={str(i_nuc_diam)}')
                s_stream = s_stream.replace('i_cell_diam=int', f'i_cell_diam={str(i_cell_diam)}')
                s_stream = s_stream.replace('cell_or_nuclei', s_type)
                s_stream = s_stream.replace("['Ecad']", s_seg_markers)
                s_stream = s_stream.replace("ls_rare = []", f"ls_rare = {s_rare}")
                s_stream = s_stream.replace('PathtoImages', s_imgdir)  # input directory
                s_stream = s_stream.replace('PathtoSegmentation', f'{s_segdir}/{s_slide}Cellpose_Segmentation/')  # bue 20210510: output directory and only thing that is slide and not slide_pxscene based
                if s_match == 'match':
                    s_stream = s_stream.replace('#MATCHONLY',"'''")
                elif s_match == 'seg':
                    s_stream = s_stream.replace('#SEGONLY',"'''")
                else:
                    pass

                # write executable code to file
                s_pathfile_executable = f'cellpose_{s_type}_{s_slide_pxscene}.py'.replace('-','')
                with open(s_pathfile_executable, 'w') as f:
                    f.write(s_stream)

                # execute segmentation script
                if s_type_processing == 'slurm':
                    # generate sbatch file
                    s_pathfile_sbatch = f'segmentation_cellpose_{s_type}_{s_slide_pxscene}.sbatch'.replace('-','')
                    config.slurmbatch(
                        s_pathfile_sbatch=s_pathfile_sbatch,
                        s_srun_cmd=f'python3 {s_pathfile_executable}',
                        s_jobname=f's{s_type[0]}{s_slide_pxscene}',
                        s_partition=s_slurm_partition,
                        s_gpu=s_slurm_gpu,
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
                    s_file_stdouterr = 'slurp-segmentation_{s_type}_{s_slide_pxscene}.out'.replace('-','')
                    time.sleep(4)
                    subprocess.run(
                        ['python3', s_pathfile_executable],
                        stdout=open(s_file_stdouterr, 'w'),
                        stderr=subprocess.STDOUT,
                    )


# numba functions
'''
use numba to quickly iterate over each label and replace pixels with new pixel values
Input:
container = numba container class, with key-value pairs of old-new cell IDs
labels: numpy array with labels to rename
    #cell_labels = np.where(np.array(cell_labels,dtype=np.int64)==key, value, np.array(labels,dtype=np.int64))
'''

kv_ty = (numba.types.int64, numba.types.int64)


@jitclass([('d', numba.types.DictType(*kv_ty)),
           ('l', numba.types.ListType(numba.types.float64))])
class ContainerHolder(object):
    def __init__(self):
        # initialize the containers
        self.d = numba.typed.Dict.empty(*kv_ty)
        self.l = numba.typed.List.empty_list(numba.types.float64)


@overload(np.array)
def np_array_ol(x):
    if isinstance(x, numba.types.Array):
        def impl(x):
            return np.copy(x)
        return impl


@jit(nopython=True)
def relabel_numba(container, cell_labels):
    '''
    BUE 20210510: called from template

    faster; replace pixels accorind to dictionsry (i.e. numba container)
    key is original cell label, value is replaced label
    '''
    cell_labels = np.array(cell_labels)
    for key, value in container.d.items():
        cell_labels = np.where(cell_labels==key, value, cell_labels)
    print('done matching')
    return(cell_labels)


def nuc_to_cell(labels, cell_labels):
    '''
    BUE 20210510: called from template

    associate the largest nucleaus contained in each cell segmentation
    Input:
    labels: nuclear labels
    cell_labels: cell labels that need to be matched
    Ouput:
    container: numba container of key-value pairs of old-new cell IDs
    '''
    start = time.time()

    # dominant nuclei
    d_replace = {}
    for idx in np.unique(cell_labels)[::-1]:
        if idx == 0:
            continue

        # iterate over each cell label, find all non-zero values contained within that mask
        cell_array = labels[cell_labels == idx]
        cell_array = cell_array[cell_array != 0]

        # for multiple nuclei, choose largest (most common pixels, i.e. mode)
        if len(np.unique(cell_array)) > 1:
            new_id = scipy.stats.mode(cell_array, axis=0)[0][0]
            d_replace.update({idx: new_id})

        elif len(np.unique(cell_array)) == 1:
            d_replace.update({idx: cell_array[0]})

        else:
            d_replace.update({idx: 0})

    # fix matching bug
    d_replace = {item[0]: item[1] for item in sorted(d_replace.items(), key=lambda x: x[1], reverse=True)}

    # convert to numba container
    container = ContainerHolder()
    for key, value in d_replace.items():
        container.d[key] = value
    end = time.time()
    print(end - start)
    return(container, d_replace)


#BUE 20210510: i think this is never called
#@numba.njit
#def test(a):
#    b = np.array(a)


#BUE 20210510: i think this is never called
#def relabel_numpy(d_replace, cell_labels):
#    '''
#    slow replace pixels accorind to dictionary
#    key is original cell label, value is replaced label
#    '''
#    #key is original cell albel, value is replaced label
#    for key, value in d_replace.items():
#        cell_labels = np.where(cell_labels==key, value, cell_labels)
#    print('done matching')
#    return(cell_labels)


#BUE 20210510: i think this is never called
#def relabel_gpu(d_replace, cell_labels):
#    '''
#    not implemented yet
#    key is original cell label, value is replaced label
#    '''
#    #key is original cell albel, value is replaced label
#    for key, value in d_replace.items():
#        cell_labels = np.where(cell_labels==key, value, cell_labels)
#    print('done mathcing')
#    return(cell_labels)


#BUE 20210510: i think this is never called
#def nuc_to_cell_new(labels, cell_labels):
    '''

    problem - still not giving same result as original function
    associate the largest nucleaus contained in each cell segmentation
    Input:
    labels: nuclear labels
    cell_labels: cell labels that need to be matched
    Ouput:
    container: numba container of key-value pairs of old-new cell IDs
    '''
#    start = time.time()

     # dominant nuclei
#    props = skimage.measure.regionprops_table(cell_labels, labels, properties=(['intensity_image','image','label']))
#    df_prop = pd.DataFrame(props)

#    d_replace = {}
#    for idx in df_prop.index[::-1]:

#        label_id = df_prop.loc[idx, 'label']
#        intensity_image = df_prop.loc[idx, 'intensity_image']
#        image = df_prop.loc[idx,'image']
#        nuc_labels = intensity_image[image & intensity_image!=0]

#        if len(nuc_labels) == 0:
#            d_replace.update({label_id: 0})

#        elif len(np.unique(nuc_labels)) == 1:
#            d_replace.update({label_id: nuc_labels[0]})

#        else:
#            new_id = scipy.stats.mode(nuc_labels)[0][0]
#            d_replace.update({label_id: new_id})

#    # convert to numba container
#    # bue: same as old
#    container = ContainerHolder()
#    for key, value in d_replace.items():
#        container.d[key] = value
#    end = time.time()
#    print(end - start)
#    return(container, d_replace, df_prop)



# test code
'''
import napari
#os.chdir('./Desktop/BR1506')
labels = io.imread('Scene 059 nuclei20 - Nuclei Segmentation Basins.tif')
cell_labels = io.imread('Scene 059 cell25 - Cell Segmentation Basins.tif')
cyto_img = io.imread('Scene 059 - CytoProj.png')
dapi_img = io.imread('Scene 059 - ZProjectionDAPI.png')
viewer = napari.Viewer()
viewer.add_labels(labels,blending='additive')
viewer.add_labels(cell_labels,blending='additive')
viewer.add_image(cyto_img,blending='additive')
viewer.add_image(dapi_img,blending='additive',colormap='blue')
#cell_boundaries = skimage.segmentation.find_boundaries(cell_labels,mode='outer')
#viewer.add_labels(cell_boundaries,blending='additive')
#nuclear_boundaries = skimage.segmentation.find_boundaries(labels,mode='outer')
#viewer.add_labels(nuclear_boundaries,blending='additive',num_colors=2)
closing = skimage.morphology.closing(cell_labels)
viewer.add_labels(closing,blending='additive')
container = nuc_to_cell(labels,closing)#cell_labels)

#matched cell labels
cells_relabel = relabel_numba(container[0],closing)
#remove background
mode = scipy.stats.mode(cells_relabel,axis=0)[0][0][0]
black = cells_relabel.copy()
black[black==mode] = 0
viewer.add_labels(black,blending='additive')
cell_boundaries = skimage.segmentation.find_boundaries(cells_relabel,mode='outer')
viewer.add_labels(cell_boundaries,blending='additive')
#ring
overlap = black==labels
viewer.add_labels(overlap, blending='additive')
#cytoplasm
ring_rep = black.copy()
ring_rep[overlap] = 0
viewer.add_labels(ring_rep, blending='additive')
#membrane
rim_labels = contract_membrane(black)
viewer.add_labels(rim_labels, blending='additive')

#expanded nucleus
__,__,peri_nuc = expand_nuc(labels,distance=3)
viewer.add_labels(peri_nuc, blending='additive')
'''
