import os
import argparse
import nibabel as nib
from nilearn.image import resample_to_img
import numpy as np
import urllib.request
from tigerseg.unet3d.training import load_old_model
from tigerseg.unet3d.prediction import run_validation_cases, Run_validation_case
from tigerseg.unet3d.utils.utils import  read_image
from distutils.util import strtobool


config = dict()
config["image_shape"] = (128, 128, 128)  # This determines what shape the images will be cropped/resampled to.
config["labels"] = (2,3,4,5,7,8,10,11,12,13,14,15,16,17,18,24,26,28,30,31,41,42,43,44,46,47,49,50,51,52,53,54,58,60,62,63,77,85,251,252,253,254,255)
config["training_modalities"] = [""]  # set for the data



def apply(path,image='CANDI_HC_001.nii.gz',output_name='test.nii.gz',model='raw_nu_NKI_freesurfer',permute=False):

    # log_dir = 'https://github.com/JoHof/lungmask/releases/download/v0.0/unet_r231-d5d2fc3d.pth'
    # if not os.path.exists(log_dir):
    #     print('Downloading model files....')
    #     urllib.request.urlretrieve(model_zip[count], os.path.join(appdir,zip_name))
    #     shutil.unpack_archive(os.path.join(appdir, zip_name), extract_dir=os.path.join(appdir,'model'))
    #     os.remove(os.path.join(appdir, zip_name))
    WORKING_PATH = path
    DATA = 'data'
    MODEL = 'model'
    prediction_dir = os.path.join(WORKING_PATH,'src','tigerseg','result')
    print(WORKING_PATH)
    output_label_map = True
    config['model_file'] =  os.path.join(WORKING_PATH,'src','tigerseg', MODEL,model + '_unet_model.h5')
    config["permute"] = bool(permute)
    #
    data_file = os.path.join(WORKING_PATH,'src','SubBrainSegment','example',image)
    single_file = read_image(data_file, image_shape=(128,128,128), crop=False, interpolation='linear')
    model = load_old_model(config["model_file"])
    Run_validation_case(output_dir=prediction_dir,
                        model=model,
                        data_file=single_file,
                        training_modalities=config["training_modalities"],
                        output_label_map=output_label_map,
                        labels=config["labels"],
                        threshold=0.5,
                        overlap=16,
                        permute=False,
                        output_basename=output_name,
                        test=False)
    prediction_filename = os.path.join(os.path.join(prediction_dir,output_name))
    ref = nib.load(data_file)
    pred = nib.load(prediction_filename)
    pred_resampled = resample_to_img(pred, ref, interpolation="nearest")
    label = pred_resampled.get_fdata()
    nib.save(nib.Nifti1Image(label.astype(np.uint8),pred_resampled.affine),prediction_filename)
    return nib.Nifti1Image(label.astype(np.uint8),pred_resampled.affine)
