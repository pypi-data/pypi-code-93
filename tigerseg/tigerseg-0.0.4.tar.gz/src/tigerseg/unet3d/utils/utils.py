import pickle
import os
import collections
import time
import nibabel as nib
import numpy as np
from nilearn.image import reorder_img, new_img_like
from .nilearn_custom_utils.nilearn_utils import crop_img_to
from .sitk_utils import resample_to_spacing, calculate_origin_offset


def pickle_dump(item, out_file):
    with open(out_file, "wb") as opened_file:
        pickle.dump(item, opened_file)


def pickle_load(in_file):
    with open(in_file, "rb") as opened_file:
        return pickle.load(opened_file)

def normalize_data(data):


    data= data/np.max(data)
    print(np.max(data))

    return data


def get_affine(in_file):
    return read_image(in_file).affine


def read_image_files(image_files, image_shape=None, crop=None, label_indices=None):
    """
    :param image_files:
    :param image_shape:
    :param crop:
    :param use_nearest_for_last_file: If True, will use nearest neighbor interpolation for the last file. This is used
    because the last file may be the labels file. Using linear interpolation here would mess up the labels.
    :return:
    """

    if label_indices is None:
        label_indices = []
    elif not isinstance(label_indices, collections.Iterable) or isinstance(label_indices, str):
        label_indices = [label_indices]
    image_list = list()
    for index, image_file in enumerate(image_files):
        if (label_indices is None and (index + 1) == len(image_files)) \
                or (label_indices is not None and index in label_indices):
            interpolation = "nearest"
        else:
            interpolation = "linear"

        image_list.append(read_image(image_file, image_shape=image_shape, crop=crop, interpolation=interpolation))

    return image_list

def reorientation(img,img_array):
    init_axcodes = tuple(nib.aff2axcodes(img.affine)) # ('P', 'S', 'R')
    final_axcodes = nib.orientations.ornt2axcodes([[0, 1],[1,1],[2,1]]) # ('R', 'A', 'S')
    ornt_final = nib.orientations.axcodes2ornt(final_axcodes)
    affine = nib.orientations.inv_ornt_aff(ornt_final,img_array.shape)
    return nib.Nifti1Image(img_array,affine)



def labelto12(img):
    img_np = img.get_fdata()
    new_img = img_np * 0
    pairs = [(7,1), (27, 2), (8, 3), (28, 4), (9, 5), (29, 6), (10, 7),
    (30, 8), (14, 9), (31, 10), (15, 11), (32, 12)]
    for old,new in pairs:
        new_img[img_np==old]=new
    print("unique",np.unique(new_img))
    return nib.Nifti1Image(new_img,img.affine)



def read_image(in_file, image_shape=None, interpolation='linear', crop=None):
    print("Reading: {0}".format(in_file))
    subject_id = in_file.split('/')[-1][:-7]
    image = nib.load(os.path.abspath(in_file))
    # image = reorientation(image,image.get_fdata())
    print(image.shape,tuple(nib.aff2axcodes(image.affine)))
    image_np = normalize_data(image.get_fdata())
    image = nib.Nifti1Image(image_np,image.affine)
    image = fix_shape(image)

    if crop:
        image = crop_img_to(image, crop, copy=True)

    if image_shape:
        print(image_shape)
        # image = resize(image, new_shape=image_shape, interpolation=interpolation) #for training
        # nib.save(image,os.path.join(os.getcwd(),'..','data','freesurfer_all',subject_id,'resize_' + subject_id + '.nii.gz'))
        # exit()
        return resize(image, new_shape=image_shape, interpolation=interpolation) #for training

    else:
        return image


def fix_shape(image):
    if image.shape[-1] == 1:
        return image.__class__(dataobj=np.squeeze(image.get_data()), affine=image.affine)
    return image


def resize(image, new_shape, interpolation="linear"):  ###turn(RAS)
    print('1',tuple(nib.aff2axcodes(image.affine)),image.shape)
    image = reorder_img(image, resample=interpolation) # first RAS
    print('2',tuple(nib.aff2axcodes(image.affine)),image.shape)
    zoom_level = np.divide(new_shape, image.shape)
    new_spacing = np.divide(image.header.get_zooms(), zoom_level)
    new_data = resample_to_spacing(image.get_data(), image.header.get_zooms(), new_spacing,
                                   interpolation=interpolation)
    new_affine = np.copy(image.affine)
    np.fill_diagonal(new_affine, new_spacing.tolist() + [1])
    new_affine[:3, 3] += calculate_origin_offset(new_spacing, image.header.get_zooms())
    image = new_img_like(image, new_data, affine=new_affine)
    print('3',tuple(nib.aff2axcodes(image.affine)),image.shape)

    return new_img_like(image, new_data, affine=new_affine) # second RAS
