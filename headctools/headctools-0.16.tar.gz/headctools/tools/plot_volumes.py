import os
from collections import OrderedDict

import numpy as np
from matplotlib import pyplot as plt
import SimpleITK as sitk
from plot_utils import hex_color
from headctools import utilities as utils


def plot_volumes_patient(folder, id_1, id_2, title="Volumes", xlabel=None,
                         ylabel=None, figsize=(6, 6), show=False):
    """ Create an identity-volume plot.

    Lookup files in the provided pred_folder that match both IDs and create a
    volume plot, that shows how close are the segmentations in both IDs.

    Segmentation names must be in the following format:
        XXXX_YYYY_ID.nii.gz
        where XXXX denotes the patient, YYYY the CT no. and ID the type of
    segmentation. In this case, this function will compute the volume
    between every combination of segmentations of the same patient, for both
    types.

    :param folder: Input pred_folder.
    :param id_1: First type of segmentation ID. The file must end with this
    ID (including extension).
    :param id_2: Second type of segmentation ID.
    :param title: Plot title.
    :param xlabel: X axis title.
    :param ylabel: Y axis title.
    :param figsize: Figure size.
    """

    print(f'\nID,FileGT,FileR,Vol1,Vol2,Diff')
    t1_files = [f for f in os.listdir(folder) if f.endswith(id_1)]
    t2_files = [f for f in os.listdir(folder) if f.endswith(id_2)]

    div = 1000

    plt.figure(figsize=figsize)
    volumes = []
    for t1 in t1_files:
        for t2 in t2_files:
            if t1[0:t1.find('_')] == t2[0:t2.find('_')]:
                p1 = os.path.join(folder, t1)
                p2 = os.path.join(folder, t2)
                a1 = sitk.GetArrayFromImage(sitk.ReadImage(p1))
                a2 = sitk.GetArrayFromImage(sitk.ReadImage(p2))
                voxel_vol_1 = np.prod(sitk.ReadImage(p1).GetSpacing()) / div
                voxel_vol_2 = np.prod(sitk.ReadImage(p2).GetSpacing()) / div
                volumes.append((np.count_nonzero(a1) * voxel_vol_1,
                                np.count_nonzero(a2) * voxel_vol_2))
                plt.scatter(np.count_nonzero(a1) * voxel_vol_1,
                            np.count_nonzero(a2) * voxel_vol_2,
                            c=hex_color(t1),
                            label=utils.crop_str_from_n_ocurrence(t1, '_', 1))

                # ID, FileGT, FileR, Vol1, Vol2, Diff
                volume_diff = np.abs(volumes[-1][0] - volumes[-1][1])
                print(f"{t1[0:t1.find('_')]},{t1},{t2},{volumes[-1][0]},"
                      f"{volumes[-1][1]},{volume_diff}")

    # plt.scatter(*zip(*volumes))
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Remove duplicated legends
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    bounds = [min(plt.gca().dataLim.min), max(plt.gca().dataLim.max)]
    plt.plot(bounds, bounds, c='#000000')

    plt.show() if show else 0


def plot_volumes_study(folder, id_1, id_2, title="Volumes", xlabel=None,
                       ylabel=None, figsize=(6, 6), show=False,
                       study='StudyA', color='red'):
    """ Create an identity-volume plot.

    Lookup files in the provided pred_folder that match both IDs and create a
    volume plot, that shows how close are the segmentations in both IDs.

    Segmentation names must be in the following format:
        XXXX_YYYY_ID.nii.gz
        where XXXX denotes the patient, YYYY the CT no. and ID the type of
    segmentation. In this case, this function will compute the volume
    between every combination of segmentations of the same patient, for both
    types.

    :param folder: Input pred_folder.
    :param id_1: First type of segmentation ID. The file must end with this
    ID (including extension).
    :param id_2: Second type of segmentation ID.
    :param title: Plot title.
    :param xlabel: X axis title.
    :param ylabel: Y axis title.
    :param figsize: Figure size.
    """

    print(f'\nID,FileGT,FileR,Vol1,Vol2,Diff')
    t1_files = [f for f in os.listdir(folder) if f.endswith(id_1)]
    t2_files = [f for f in os.listdir(folder) if f.endswith(id_2)]

    div = 1000  # mm3 -> cm3

    # plt.figure(figsize=figsize)
    volumes = []
    for t1 in t1_files:
        for t2 in t2_files:
            if t1[0:t1.find('_')] == t2[0:t2.find('_')]:
                p1 = os.path.join(folder, t1)
                p2 = os.path.join(folder, t2)
                a1 = sitk.GetArrayFromImage(sitk.ReadImage(p1))
                a2 = sitk.GetArrayFromImage(sitk.ReadImage(p2))
                voxel_vol_1 = np.prod(sitk.ReadImage(p1).GetSpacing()) / div
                voxel_vol_2 = np.prod(sitk.ReadImage(p2).GetSpacing()) / div
                volumes.append((np.count_nonzero(a1) * voxel_vol_1,
                                np.count_nonzero(a2) * voxel_vol_2))
                plt.scatter(np.count_nonzero(a1) * voxel_vol_1,
                            np.count_nonzero(a2) * voxel_vol_2,
                            c=color,
                            label=study)

                # ID, FileGT, FileR, Vol1, Vol2, Diff
                volume_diff = np.abs(volumes[-1][0] - volumes[-1][1])
                print(f"{t1[0:t1.find('_')]},{t1},{t2},{volumes[-1][0]},"
                      f"{volumes[-1][1]},{volume_diff}")

    # plt.scatter(*zip(*volumes))
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Remove duplicated legends
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    bounds = [min(plt.gca().dataLim.min), max(plt.gca().dataLim.max)]
    plt.plot(bounds, bounds, c='#000000')

    # plt.show() if show else 0


if __name__ == '__main__':
    folder = '/home/fmatzkin/Code/datasets/SamCook-FAVO/volumes/AtlasSpace'
    gt_id = 'image_icv.nii.gz'
    lvlsets_rec_id = 'image_sk_icv.nii.gz'
    lvlsets_cran_id = 'image_i_postop_icv.nii.gz'

    plt.figure()

    plot_volumes_study(folder, gt_id, lvlsets_rec_id,
                       title="Volumes: GT vs Reconstructed skull (in cm$^3$)",
                       xlabel="Reconstructed skull levelsets volume",
                       ylabel="GT volume",
                       study="reconstructed",
                       color="green",
                       show=False)

    plot_volumes_study(folder, gt_id, lvlsets_cran_id,
                       title="Volumes: GT vs Non-reconstructed skull (in cm$^3$)",
                       xlabel="Non-reconstructed skull levelsets volume",
                       ylabel="GT volume",
                       study="non-reconstructed",
                       color="red",
                       show=False)

    plt.show()
