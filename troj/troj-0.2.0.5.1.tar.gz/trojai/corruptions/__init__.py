import numpy as np
from PIL import Image
import os
import random
from .Corruptions import *

corruption_tuple = (gaussian_noise, shot_noise, impulse_noise, defocus_blur,
                    glass_blur, motion_blur, zoom_blur, snow, frost, fog,
                    brightness, contrast, elastic_transform, pixelate,
                    jpeg_compression, speckle_noise, gaussian_blur, spatter,
                    saturate)

corruption_dict = {corr_func.__name__: corr_func for corr_func in
                   corruption_tuple}


def corrupt(image, severity=1, corruption_name=None, corruption_number=-1):
    """This function returns a corrupted version of the given image.

    Args:
        image (numpy.ndarray):      image to corrupt; a numpy array in [0, 255], expected datatype is np.uint8
                                    expected shape is either (height x width x channels) or (height x width);
                                    width and height must be at least 32 pixels;
                                    channels must be 1 or 3;
        severity (int):             strength with which to corrupt the image; an integer in [1, 5]
        corruption_name (str):      specifies which corruption function to call, must be one of
                                        'gaussian_noise', 'shot_noise', 'impulse_noise', 'defocus_blur',
                                        'glass_blur', 'motion_blur', 'zoom_blur', 'snow', 'frost', 'fog',
                                        'brightness', 'contrast', 'elastic_transform', 'pixelate', 'jpeg_compression',
                                        'speckle_noise', 'gaussian_blur', 'spatter', 'saturate';
                                    the last four are validation corruptions
        corruption_number (int):    the position of the corruption_name in the above list; an integer in [0, 18];
                                        useful for easy looping; 15, 16, 17, 18 are validation corruption numbers
    Returns:
        numpy.ndarray:              the image corrupted by a corruption function at the given severity; same shape as input
    """

    if not isinstance(image, np.ndarray):
        raise AttributeError('Expecting type(image) to be numpy.ndarray')
    if not (image.dtype.type is np.uint8):
        raise AttributeError('Expecting image.dtype.type to be numpy.uint8')

    if not (image.ndim in [2, 3]):
        raise AttributeError('Expecting image.shape to be either (height x width) or (height x width x channels)')
    if image.ndim == 2:
        image = np.stack((image,) * 3, axis=-1)

    height, width, channels = image.shape

    if (height < 32 or width < 32):
        raise AttributeError('Image width and height must be at least 32 pixels')

    if not (channels in [1, 3]):
        raise AttributeError('Expecting image to have either 1 or 3 channels (last dimension)')

    if channels == 1:
        image = np.stack((np.squeeze(image),) * 3, axis=-1)

    if not severity in [1, 2, 3, 4, 5]:
        raise AttributeError('Severity must be an integer in [1, 5]')

    if not (corruption_name is None):
        image_corrupted = corruption_dict[corruption_name](Image.fromarray(image),
                                                           severity)
    elif corruption_number != -1:
        image_corrupted = corruption_tuple[corruption_number](Image.fromarray(image),
                                                              severity)
    else:
        raise ValueError("Either corruption_name or corruption_number must be passed")

    return np.uint8(image_corrupted)


def get_corruption_names(subset='common'):
    if subset == 'common':
        return [f.__name__ for f in corruption_tuple[:15]]
    elif subset == 'validation':
        return [f.__name__ for f in corruption_tuple[15:]]
    elif subset == 'all':
        return [f.__name__ for f in corruption_tuple]
    elif subset == 'noise':
        return [f.__name__ for f in corruption_tuple[0:3]]
    elif subset == 'blur':
        return [f.__name__ for f in corruption_tuple[3:7]]
    elif subset == 'weather':
        return [f.__name__ for f in corruption_tuple[7:11]]
    elif subset == 'digital':
        return [f.__name__ for f in corruption_tuple[11:15]]
    else:
        raise ValueError("subset must be one of ['common', 'validation', 'all']")





def im_loc_splitter_classification(location):
    '''
    Retrieves the class of the image and the filename for classification datasets
    :param location: Location of image file.
    :returns: The class of the image and the filename
    '''
    folderwise_split = location.split('/')
    img_file = folderwise_split[-1]
    img_class = folderwise_split[-2]
    return img_file, img_class

def rename_img(img_file, corruption_name, severity):
    '''
    :param img_file: name of the image file
    :param corruption_name: corruption name
    :param severity: severity of the corruption
    :returns: new file name for corrupt image in format {original name}_cor_{corruption name}_sev_{severity of corruption}.extension
    '''
    split_file_extension = img_file.split('.')
    file_extension = '.{}'.format(split_file_extension[-1])
    img_name_extension = '_cor_{}_sev_{}'.format(corruption_name, severity)
    corrupt_img_name = split_file_extension[0] + img_name_extension + file_extension
    return corrupt_img_name

def corrupt_and_save_classification(original_location, new_root, corruption, severity, image_array=None):
    '''
    :param original_location: Original image location.
    :param new_root: The new root folder.
    :param corruption: The corruption to apply.
    :param severity: The severity of the corruption.
    :param image_array: A preloaded image array, if none, the image is loaded from the original_location parameter
    :returns: saves corrupt image at the location {new_root}/{class}/{corrupt image name}

    '''
    im_file, im_class = im_loc_splitter_classification(original_location)
    corrupt_im_name = rename_img(im_file, corruption, severity)
    save_loc = os.path.join(new_root, im_class)
    if os.path.exists(new_root)==False:
        os.makedirs(new_root)
    if os.path.exists(os.path.join(new_root, im_class))==False:
        os.makedirs(save_loc)
    if image_array is None:
        image_array=np.asarray(Image.open(original_location))
    original_image = image_array
    corrupted = corrupt(original_image, corruption_name=corruption, severity=severity)
    corrupted_image = Image.fromarray(corrupted)
    corrupted_image.save(os.path.join(save_loc, corrupt_im_name))


def corrupt_dset_random(original_folder, new_folder, corruptions, severities,  include_original=False, verbose=True):
    '''
    :param original_folder: The original split folder (test folder).
    :param new_folder: New folder location to save corrupt images to.
    :param corruptions: A list of corruptions.
    :param severities: A list of severity levels.
    :param include_original: Whether or not to include the original image in the new test set.
    :param verbose: Whether or not to print generation progress.
    :returns: Creates a new dataset at new_folder containing images which are corrupted according to a random sampling
    of the corruptions and severity
    '''
    classes = os.listdir(original_folder)
    num_classes = len(classes)
    class_counter = 0
    if os.path.exists(new_folder)==False:
        os.makedirs(new_folder)
    for class_name in classes:
        class_counter += 1
        im_counter = 0
        class_folder = os.path.join(original_folder, class_name)
        im_files = os.listdir(class_folder)
        num_imgs = len(im_files)
        new_class_folder = os.path.join(new_folder, class_name)
        if os.path.exists(new_class_folder) == False:
            os.makedirs(new_class_folder)
        for img_file in im_files:
            im_counter += 1
            im_loc = os.path.join(class_folder, img_file)
            image = Image.open(im_loc)
            if include_original==True:
                uncorrupt_name= rename_img(img_file, 'none', 0)
                image.save(os.path.join(new_class_folder, uncorrupt_name))
            image_arr = np.asarray(image)
            corrupt_name = random.choice(corruptions)
            severity = random.choice(severities)
            corrupt_and_save_classification(im_loc, new_folder, corrupt_name, severity, image_arr)
            if verbose==True:
                progress_str = 'Class {}/{}: Image {}/{}'.format(class_counter, num_classes, im_counter, num_imgs)
                print(progress_str)


def corrupt_dset_all(original_folder, new_folder, corruptions, severities,  include_original=False, verbose=True):
    '''
    :param original_folder: The original split folder (test folder).
    :param new_folder: New folder location to save corrupt images to.
    :param corruptions: A list of corruptions.
    :param severities: A list of severity levels.
    :param include_original: Whether or not to include the original image in the new test set.
    :param verbose: Whether or not to print generation progress.
    :returns: Creates a new dataset at new_folder where every image is corrupted by each corruption and each severity and saved.
    '''
    classes = os.listdir(original_folder)
    num_classes = len(classes)
    class_counter = 0
    if os.path.exists(new_folder)==False:
        os.makedirs(new_folder)
    for class_name in classes:
        class_counter += 1
        im_counter = 0
        class_folder = os.path.join(original_folder, class_name)
        im_files = os.listdir(class_folder)
        num_imgs = len(im_files)
        new_class_folder = os.path.join(new_folder, class_name)
        if os.path.exists(new_class_folder) == False:
            os.makedirs(new_class_folder)
        for img_file in im_files:
            im_counter += 1
            im_loc = os.path.join(class_folder, img_file)
            image = Image.open(im_loc)
            if include_original==True:
                uncorrupt_name= rename_img(img_file, 'none', 0)
                image.save(os.path.join(new_class_folder, uncorrupt_name))
            image_arr = np.asarray(image)
            for corrupt_name in corruptions:
                for severity in severities:
                    corrupt_and_save_classification(im_loc, new_folder, corrupt_name, severity, image_arr)
            if verbose==True:
                progress_str = 'Class {}/{}: Image {}/{}'.format(class_counter, num_classes, im_counter, num_imgs)
                print(progress_str)



def MakeCorruptDsetClassification(original_folder, new_folder, corruptions, severities, mode='random',  include_original=False, verbose=True):
    '''
    :param original_folder: The original split folder (test folder).
    :param new_folder: New folder location to save corrupt images to.
    :param corruptions: A list of corruptions.
    :param severities: A list of severity levels.
    :param mode: One of either 'random' or 'all'. If random, each image is corrupted by randomly sampling a corruption and severity level.
    If all, every corruption and every severity is applied to each image one at a time and saved.
    :param include_original: Whether or not to include the original image in the new test set.
    :param verbose: Whether or not to print generation progress.
    :returns: Creates a new dataset at new_folder containing corrupt images.
    '''
    if mode.lower()=='random':
        corrupt_dset_random(original_folder, new_folder, corruptions, severities, include_original, verbose)
    if mode.lower()=='all':
        corrupt_dset_all(original_folder, new_folder, corruptions, severities, include_original, verbose)

