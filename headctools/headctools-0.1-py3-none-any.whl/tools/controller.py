import os

import SimpleITK as sitk
from Preprocessor import Preprocessor, prep_image_or_mask
from common import veri_folder
from trainTestModel import predict_mask_here


def predict_brain_mask_in_orig_dims(ct_path, model_path, custom_filename=None,
                                    save_folder=None, device='cpu'):
    """ This function is used as intermediary of the Preprocessor and the neural network classes, allowing to test the
        brain mask of an image (given its path) using the model provided in model.

        The input image will be preprocessed and then be fed as input of the NN, who'll make a prediction for the mask in
        the preprocessed space. After that, the output segmentation is taken to the original image space

    :param ct_path: Input image (CT scan in Hounsfield scale).
    :param model_path: Trained PyTorch model path.
    :param custom_filename: (optional) set a custom output filename (without extension). Default will be the same file
            name as input plus "_nnmask".
    :param save_folder: (optional) set a custom output pred_folder. Default will be the same pred_folder as input.
    :param device: Device to use for predicting the brain mask (cpu-gpu).
    :return:
    """

    img_sitk = sitk.ReadImage(ct_path)
    filename = os.path.split(ct_path)

    if ct_path.endswith(".nii.gz"):  # Save the extension
        ext = ".nii.gz"  # Splitext only takes the last file extension
    else:
        ext = os.path.splitext(filename)

    o_size = img_sitk.GetSize()  # Save image original parameters
    o_spacing = img_sitk.GetSpacing()
    o_direction = img_sitk.GetDirection()
    o_origin = img_sitk.GetOrigin()

    prep_img = prep_image_or_mask(ct_path, clip_intensity_values=[20, 150],
                                  target_spacing=[1, 1,
                                                  5])  # Preprocess the image

    pred_mask = predict_mask_here(model_path, prep_img,
                                  device=device)  # Get the mask of the image

    pred_mask = Preprocessor(pred_mask, is_mask=True).resample_spacing(
        o_spacing, o_direction, o_origin)  # Go back to orig spacing
    pred_mask = pred_mask[0:o_size[0], 0:o_size[1],
                0:o_size[2]]  # Remove padding

    if save_folder is None:
        save_folder = filename[0]  # Set output pred_folder if provided
    else:
        veri_folder(save_folder)  # Create pred_folder if not exists

    if custom_filename is None:
        custom_filename = filename[1].replace(ext,
                                              '_nnmask' + ext)  # Use the same input pred_folder plus "_nnmask".
    else:
        custom_filename = custom_filename + ext  # Set custom filename if provided.

    save_path = os.path.join(save_folder, custom_filename)

    sitk.WriteImage(pred_mask, save_path)

    print("  Mask saved in: {}.\n".format(save_path))


def predict_brain_mask_in_orig_dims_folder(inp_folder, out_folder=None,
                                           model_path='models/default.pt',
                                           image_extension=".nii.gz",
                                           device='cpu'):
    for name in os.listdir(inp_folder):
        if os.path.splitext(name)[
            1] in image_extension and '_nnmask' not in name:
            if os.path.exists(os.path.join(inp_folder, name).replace('.nii.gz',
                                                                     '_nnmask.nii.gz')):
                print("Output file already exists. Skipping... ")
                continue
            else:
                filepath = os.path.join(inp_folder,
                                        name)  # Reconstruct file path.
                predict_brain_mask_in_orig_dims(filepath, model_path,
                                                save_folder=out_folder,
                                                device=device)  # Predict the mask
        else:
            continue  # Not an image file


if __name__ == '__main__':
    # Usage example
    # ct_path = '../image/all/1002_23215_image.nii.gz'
    # model = 'models/26apr19_500_1e-3_0_sgd_bz1_90.pt'
    # predict_mask_in_orig_dims(ct_path, model)

    input_folder = '../../DATOS/FAVO/only_images'
    output_folder = '../../DATOS/FAVO/only_images/predictions'
    predict_brain_mask_in_orig_dims_folder(input_folder, output_folder)
