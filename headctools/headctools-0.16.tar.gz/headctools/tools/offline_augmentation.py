# This file is a simple script for generating simulated craniectomies using the same process as during training

import csv
import os

import SimpleITK as sitk
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

import headctools.utilities as utils


def simulate_and_save(fpath, n_reps, out_folder, min_s=0.005, max_s=0.25):
    print("Input: {}.".format(fpath))
    folder, name = os.path.split(fpath)

    if not out_folder:
        out_folder = os.path.join(folder, 'augm')
        utils.veri_folder(out_folder)

    s_img = sitk.ReadImage(fpath)
    origin = s_img.GetOrigin()
    direction = s_img.GetDirection()
    spacing = s_img.GetSpacing()
    np_img = sitk.GetArrayFromImage(s_img).astype(np.uint8)

    global vols

    for i in range(n_reps):
        while True:
            o_n_img, e_n_img = utils.random_blank_patch(np_img, prob=1,
                                                        return_extracted=True,
                                                        p_type='sphere')
            flap_size = np.count_nonzero(e_n_img)
            skull_size = np.count_nonzero(o_n_img)
            vols.append(flap_size * 8)
            min_s = 0
            max_s = 1
            size_cond = (flap_size > min_s * skull_size) and (
                    flap_size < max_s * skull_size)

            if size_cond:
                break

        # with np.sum(e_n_img) I can get the bone flap size

        # masked image
        sitk_out_img = sitk.GetImageFromArray(o_n_img)
        sitk_out_img.SetOrigin(origin)
        sitk_out_img.SetDirection(direction)
        sitk_out_img.SetSpacing(spacing)

        # 1-mask * image
        sitk_out_tip = sitk.GetImageFromArray(e_n_img)
        sitk_out_tip.SetOrigin(origin)
        sitk_out_tip.SetDirection(direction)
        sitk_out_tip.SetSpacing(spacing)

        name_out_i = name.replace("image", "{}_sim".format(i))
        name_out_o = name.replace("image", "{}_sim_orig".format(i))
        name_out_t = name.replace("image", "{}_sim_t.nii.gz".format(i))

        sitk.WriteImage(sitk_out_img, os.path.join(out_folder,
                                                   name_out_i))  # Input of the model
        sitk.WriteImage(s_img, os.path.join(out_folder,
                                            name_out_o))  # Original image (input)
        sitk.WriteImage(sitk_out_tip,
                        os.path.join(out_folder, name_out_t))  # Simulated flap
        print("  Saved: {}.".format(name_out_i))

    return out_folder


def simulate_cr_images(input_ff, n_reps=1, out_folder=None, ext='.nii.gz',
                       image_id=None, create_csv=True, overwrite=False):
    if not out_folder:
        out_folder = os.path.join(input_ff, 'augm')
    out_folder = utils.veri_folder(out_folder)

    if os.path.isdir(input_ff):  # Folder
        print("Folder: {}".format(input_ff))
        files = [os.path.join(input_ff, f) for f in os.listdir(input_folder) if
                 f.endswith(ext)]

    if os.path.isfile(input_ff) and input_ff.endswith(
            '.csv'):  # CSV file
        with open(input_ff) as csv_file:
            sniffer = csv.Sniffer()
            has_header = sniffer.has_header(csv_file.read(256))

        with open(input_ff) as csv_file:
            files_aux = csv.reader(csv_file, delimiter=',')
            files = []
            for i, row in enumerate(files_aux):
                if (i == 0 and has_header) or row == '' or not os.path.exists(
                        row[0]):
                    continue
                files.append(row[0])
    elif os.path.isfile(input_ff):
        files = [input_ff]

    for file in files:
        if image_id:
            if image_id not in file or not file.endswith(ext):
                continue
        out_folder = simulate_and_save(file, n_reps, out_folder)

    if files and create_csv:
        utils.create_csv(out_folder, csvname='test_simulated.csv', splits=[],
                         image_identifier='sim',
                         mask_identifier='sim_orig', image_extension='.nii.gz')


def test_shape_generator(shape='sphere', size=10):
    center = [25, 25, 25]
    size = [size]
    image_size = [80, 106, 106]
    shap = 1 - utils.shape_3d(center, size, image_size, shape)
    sitk.Show(sitk.GetImageFromArray(shap))


def subtract_images(list_of_pairs):
    for images in list_of_pairs:
        im_A = sitk.ReadImage(images[0])
        im_B = sitk.ReadImage(images[1])

        out_path = images[0].replace('.nii.gz', '_diff.nii.gz')

        diff = utils.diff_sitk(im_A, im_B)
        sitk.WriteImage(diff, out_path)


# vols = []
# input_folder = '/home/fmatzkin/Code/datasets/autoimplant-challenge' \
#                '/training_set/complete_skull/ext_renamed/prep_304_224' \
#                '/generated'
# out_folder = os.path.join(input_folder, 'defects')
# simulate_cr_images(input_folder,
#                    5,
#                    out_folder)

# utils.simple_csv(out_folder, csv_name='test_simulated.csv',
#                  image_identifier='sim.nii.gz',
#                  mask_identifier='sim_t.nii.gz')

# if __name__ == '__main__':
#     # global vols
#     vols = []
#     # Simulate craniectomy images
#     # files_csv = '../image/normal/clip90-91_sp2-2-2-rigid'
#     files_csv = 'splits/191223cr-rec/files_test.csv'
#     out = '../image/normal/clip90-91_sp2-2-2-rigid/test'
#     simulate_cr_images(files_csv, n_reps=10, image_id='image',
#                        out_folder=out)
#     plt.hist(vols, bins=20)
#     plt.show()

################################
# Generate CSV used for PCA (the same CSV but without the paths)
# out_ff = '/home/fmatzkin/Code/image/normal/clip90-91_sp2-2-2-rigid/augm'
# utils.create_csv(out_ff, csv_name='test_simulated_pca.csv', splits=None, image_identifier='sim',
#                mask_identifier='sim_orig', image_extension='.nii.gz', include_path=False)

################################
# Shape generator
# test_shape_generator(shape='sphere', size=5)
# test_shape_generator(shape='sphere', size=53)
# test_shape_generator(shape='box')

###############################
# subtract images
# s_images = [['/home/fmatzkin/Escritorio/favo/prep/2181150_image_pos.nii.gz',
#              '/home/fmatzkin/Escritorio/favo/prep/2181150_image_prev.nii.gz'],
#             ['/home/fmatzkin/Escritorio/favo/prep/3764350_image_pos.nii.gz',
#              '/home/fmatzkin/Escritorio/favo/prep/3764350_image_prev.nii.gz'],
#             ['/home/fmatzkin/Escritorio/favo/prep/3797770_image_pos.nii.gz',
#              '/home/fmatzkin/Escritorio/favo/prep/3797770_image_prev.nii.gz']]
# subtract_images(s_images)
