import math
import os

import SimpleITK as sitk
import numpy as np
import pandas as pd

from . import utilities as common
from .antspyregistration import register_ants_sitk

ATLAS_PATH = "assets/atlas/atlas3_nonrigid_masked_1mm.nii.gz"


class Preprocessor:
    def __init__(self, sitk_img=None, is_binary=False, save_path="",
                 image_path=None, mask_path=None, f_ext=".nii.gz",
                 subfolders=None):
        self.image = sitk_img if sitk_img else None
        self.mask = None

        self.image_path = ""
        self.mask_path = ""
        self.is_binary = is_binary

        self.direction = None
        self.origin = None

        self.ext = f_ext

        self.subfold = subfolders

        self.load_image_and_mask(image_path, mask_path)

        # Looks like a pred_folder path.
        if os.path.splitext(save_path)[1] == "":
            self.save_path = common.veri_folder(save_path)
        else:  # Looks like a file path
            common.veri_folder(os.path.split(save_path)[0])
            self.save_path = save_path

    def load_image_and_mask(self, image_path=None, mask_path=None,
                            check_metadata=True):
        """Loads an image for pre processing.

        :param image_path: path of the file
        :return:
        """
        print(f"  Image: {image_path}\n  Mask: {mask_path}")
        self.image = sitk.ReadImage(image_path) if image_path else None
        self.mask = sitk.ReadImage(mask_path) if mask_path else None

        self.image_path = image_path
        self.mask_path = mask_path

        if self.image:
            self.direction = self.image.GetDirection()
            self.origin = self.image.GetOrigin()
            self.spacing = self.image.GetSpacing()

            if self.mask and check_metadata:
                self.mask.SetSpacing(self.spacing)
                self.mask.SetOrigin(self.origin)
                self.mask.SetDirection(self.direction)

    def set_filename(self, file_name=None):
        """Change the default filename

        :param file_name: new file name.
        """
        if file_name:
            self.image_path = file_name
            return file_name
        else:
            return self.image_path

    def set_save_path(self, save_path=None):
        """Set the path used for saving the preprocessed image in sh.save_file()

        :param save_path: output pred_folder.
        :return:
        """
        if save_path:
            self.save_path = save_path
            common.veri_folder(self.save_path)

    def save_file(self):
        """Save the preprocessed file in the pred_folder set in set_save_path.

        The output filename will be the same as the input, but you can add
        some text to it with the image_path parameter.

        :param image_path: text to add to the original filename (optional).
        :return:
        """
        if self.save_path is None:
            return None

        # Extract path and filename
        path_img, filename_img = os.path.split(self.image_path)

        _, file_ext = os.path.splitext(self.save_path)
        out_is_folder = file_ext == ""

        out_folder = os.path.split(  # Extract the folder
            self.save_path)[0] if not out_is_folder else self.save_path

        out_folder = os.path.join(out_folder,  # Append sub folder tree
                                  self.subfold) if self.subfold else out_folder
        common.veri_folder(out_folder)

        if out_is_folder:  # Seems like a pred_folder path
            save_path_image = os.path.join(out_folder, filename_img)
        else:  # Seems like a file path
            save_path_image = self.save_path
        sitk.WriteImage(self.image, save_path_image)  # Write image
        print("\n   Preprocessed image saved in {}.".format(save_path_image))

        if self.mask:
            path_mask, filename_mask = os.path.split(self.mask_path)
            save_path_mask = os.path.join(self.save_path, filename_mask) if \
                out_is_folder else save_path_image.replace(self.ext,
                                                           '_mask' + self.ext)
            sitk.WriteImage(self.mask, save_path_mask)  # Write mask
            print("\n   Preprocessed mask saved in {}.".format(save_path_mask))

        return save_path_image

    def resample_spacing(self, target_spacing=None, direction=None,
                         origin=None):
        """Resample the image size (without deforming the image).

        Resample the image size (without deforming the image) and spacing
        for matching the spacing given as parameter.

        :param target_spacing: desired spacing.
        :param direction: custom direction.
        :param origin: custom origin.
        :return:
        """
        if target_spacing is None:
            return None

        print("  Resampling...")

        if direction is None:
            direction = self.image.GetDirection()
        if origin is None:
            origin = self.image.GetOrigin()

        orig_sz = self.image.GetSize()
        orig_sp = self.image.GetSpacing()

        t_sz = lambda osz, osp, tsp: int(math.ceil(osz * (osp / tsp)))

        target_size = [t_sz(orig_sz[0], orig_sp[0], target_spacing[0]),
                       t_sz(orig_sz[1], orig_sp[1], target_spacing[1]),
                       t_sz(orig_sz[2], orig_sp[2], target_spacing[2])]

        interpolator = sitk.sitkNearestNeighbor if self.is_binary \
            else sitk.sitkLinear

        print("    Image")
        self.image = sitk.Resample(self.image, target_size, sitk.Transform(),
                                   interpolator, origin, target_spacing,
                                   direction, 0.0,
                                   self.image.GetPixelIDValue())

        if self.mask:
            print("    Mask")
            self.mask = sitk.Resample(self.mask, target_size, sitk.Transform(),
                                      sitk.sitkNearestNeighbor, origin,
                                      target_spacing, direction, 0.0,
                                      self.mask.GetPixelIDValue())

        return self.image

    def zero_threshold(self, apply=True):
        if apply:
            print("  Zero threshold...")
            pixel_id = self.image.GetPixelIDValue()
            self.image = self.image > 0
            sitk.Cast(self.image, pixel_id)
            return self.image
        return None

    def register_antspy(self, fixed_im_path, save_transform=False,
                        transformation="Rigid", apply=True,
                        img_interp="linear"):
        if not apply:
            return None

        print("  Registering using ANTsPy...")
        print(f"    Fixed image: {fixed_im_path}")

        if save_transform or self.mask is not None:
            mat_path = os.path.join(
                (self.save_path if os.path.isdir(self.save_path) else
                 os.path.split(self.save_path)[0]),
                os.path.split(self.image_path)[1] + "_reg.mat"
            )
            print(f"    Transformation will be saved in {mat_path}")

        if self.image:
            print("    Registering image")
            self.image = register_ants_sitk(self.image,
                                            fixed_im_path,
                                            mat_path,
                                            interp=img_interp,
                                            transformation=transformation)

            if self.mask:  # Transform also the mask
                print("    Registering mask")
                self.mask = register_ants_sitk(self.mask,
                                               mat_to_apply=mat_path,
                                               reference=self.image,
                                               transformation=transformation,
                                               interp="nearestNeighbor")

    def z_scores_normalization(self):
        """Normalize intenisities using z-scores

        :return:
        """
        data = sitk.GetArrayFromImage(self.image)

        # image has integer values, so it needs to be casted to float
        data_aux = data.astype(float)

        # Find mean, std then min_max_normalization
        mean = data_aux.mean()
        std = data_aux.std()
        data_aux = data_aux - float(mean)
        data_aux = data_aux / float(std)

        # Save edited image
        out_img = sitk.GetImageFromArray(data_aux)
        out_img.SetSpacing(self.image.GetSpacing())
        out_img.SetOrigin(self.image.GetOrigin())
        out_img.SetDirection(self.image.GetDirection())

        self.image = out_img

    def resample_to_maxpx(self, maxpx=None):
        """Resize the image proportionately using maxpx as the max side size.

        :param maxpx: Largest side size. The other sides will scale
        proportionately.
        """
        if maxpx is None:
            return None

        original_size = self.image.GetSize()
        maxval = max(original_size)

        target_spacing = list(self.image.GetSpacing())
        target_spacing = [1.0 * x * maxval / maxpx for x in target_spacing]

        if self.is_mask:
            interpolator = sitk.sitkNearestNeighbor
        else:
            interpolator = sitk.sitkLinear

        target_size = [maxpx, maxpx, maxpx]
        resampled_img = sitk.Resample(
            self.image,
            target_size,
            sitk.Transform(),
            interpolator,
            self.image.GetOrigin(),
            target_spacing,
            self.image.GetDirection(),
            0.0,
            self.image.GetPixelIDValue(),
        )

        self.image = resampled_img

    def clip_intensities(self, values=None):
        """Clip the intensity values of self.image, making values outside that
        range imin or imax.

        :param values: imin, imax values for performing the clip.
        """
        if values is None or len(values) != 2:
            return None

        print("  Intensities clipping...")
        imin, imax = values
        arr = sitk.GetArrayFromImage(self.image)
        outimg = sitk.GetImageFromArray(np.clip(arr, imin, imax))
        outimg.SetSpacing(self.image.GetSpacing())
        outimg.SetOrigin(self.image.GetOrigin())
        outimg.SetDirection(self.image.GetDirection())
        self.image = outimg

    def min_max_normalization(self, apply=True):
        """Map the image intensities to the [0, 1] range."""
        if apply:
            self.image = sitk.Cast(self.image, sitk.sitkFloat32)

            arr = sitk.GetArrayFromImage(
                self.image
            )  # For getting the max and min values
            outimg = (self.image - arr.min()) / (arr.max() - arr.min())

            self.image = outimg

    def convert_to_fixed_size(self, fixed_size_pad):
        if fixed_size_pad:
            print("  Padding to fixed size...")

            self.image = common.fixed_pad_sitk(self.image, fixed_size_pad)
            if self.mask:
                self.mask = common.fixed_pad_sitk(self.mask, fixed_size_pad)

    def keep_largest_cc(self, apply=True):
        if apply:
            print("  Retaining largest connected component...")
            self.image = common.get_largest_cc(self.image)

    def crop_random_blank_patch(self, apply=True):
        if apply:
            print("  Cropping random patch in image...")

            self.image = common.skull_random_hole(self.image)
            self.image_path = self.image_path.replace(".nii.gz",
                                                      "_crop.nii.gz")


def prep_image_or_mask(image_path=None, output_ff=None, mask_path=None,
                       clip_intensity_values=None, target_spacing=None,
                       fixed_size_pad=None, threshold=False, largest_cc=False,
                       register=False, transformation='Rigid',
                       random_blank_patch=False, img_is_binary=False,
                       atlas_path=None, img_interp='linear',
                       subfolders=None):
    """Preprocess the images.

    From an image, mask (optional) and output path, it preprocess the
    images to the output pred_folder (if provided) or it returns the preprocessed
    SimpleITK image.

    :param random_blank_patch:
    :param atlas_path: Path of the atlas if register=True.
    :param image_path: input image (optional)
    :param output_ff: output file or pred_folder, where the preprocessed image
    will be saved.
    :param mask_path: input mask (optional)
    :param clip_intensity_values: List with two intensity values for
    clipping  itensities in that range (optional).
    :param target_spacing: List contanining a custom spacing for resampling
    the  image for fitting it (optional).
    :param fixed_size_pad: List with a fixed size for zero-padding the image
    for reaching that size (optional).
    :param fixed_size_pad: List with a fixed size for zero-padding the image
    for reaching that size (optional).
    :param threshold: Apply threshold to non binary images.
    :param largest_cc: keep the largest connected component.
    :param register: Apply rigid registration to images.
    :param transformation: Type of transformation during registration.
    :param img_is_binary: Main image is is binary.
    :param subfolders: subfolder output tree.

    :return:
    """

    pp = Preprocessor(save_path=output_ff, image_path=image_path,
                      mask_path=mask_path, is_binary=img_is_binary,
                      subfolders=subfolders)

    pp.register_antspy(atlas_path, True, transformation, register, img_interp)
    pp.clip_intensities(clip_intensity_values)
    pp.min_max_normalization(threshold)
    pp.zero_threshold(threshold)
    pp.resample_spacing(target_spacing)
    pp.convert_to_fixed_size(fixed_size_pad)
    pp.keep_largest_cc(largest_cc)
    pp.crop_random_blank_patch(random_blank_patch)

    if not pp.save_path:
        return pp.image if not pp.mask else (pp.image, pp.mask)
    else:
        pp.save_file()


def diff_subfolders(image_path, output_ff):
    """ Extract common prefix between two paths and return the difference.

    Note that the difference will be performed in the first string. Example:
    image_path = '/a/b/c/e/f' output_ff = '/a/b/c/g'
    The result will be 'e/f'.

    In case that both paths don't contain a common string, it will include the
    full image path.

    :param image_path: Image path.
    :param output_ff: Output folder.
    :return:
    """
    comm_pref = os.path.commonprefix((image_path, output_ff))
    diff = image_path.replace(comm_pref, '')
    diff = diff[1:] if diff.startswith(('/', '\\')) else diff
    return diff


def preprocess_ct_files(input_ff, output_ff,
                        target_spacing=None, clip_intensity_values=None,
                        image_extension=".nii.gz", image_identifier=None,
                        mask_identifier=None, overwrite_files=False,
                        fixed_size_pad=None, include_subfolders=True,
                        threshold=False, largest_cc=False, register=False,
                        random_blank_patch=False, binary=False,
                        atlas_path=None, transformation='Rigid',
                        img_interp='linear', keep_folders=False):
    """
    Method for preprocessing the images in a pred_folder (and it subfold)

    :param input_ff: Input images. It could be a directory (files
    and folders to preprocess) or a CSV file of the format:

        image_identifier,mask_identifier
        file001_image.nii.gz,file001_head_mask.nii.gz
        ...

    :param output_ff: Output directory or file.
    :param target_spacing: Resample image to the spacing provided as parameter.
    :param clip_intensity_values: Clip intensity values to the provided range
    (default is None).
    :param image_extension: File extension for the images. By default .nii.gz.
    It could be a list of strings
    :param image_identifier: Part of the filename that indicates it is an
    image.
    :param mask_identifier: Part of the filename that indicates it is a mask.
    :param fixed_size_pad: zero-padding the output to the size provided in this
    list.
    :param overwrite_files: overwrite the output files if exist.
    :param include_subfolders: Preprocess also subfold.
    :param threshold: Apply threshold to non binary images.
    :param largest_cc: Keep the largest connected component in the image.
    :param register: Apply rigid registration to images.
    :param transformation: Type of transformation during registration.
    :param img_interp:
    :param keep_folders: Keep the folder structure.
    """
    print("Preprocessing...")
    if overwrite_files:
        print(" Overwrite output files flag is ON.")

    # Decide if preprocess a pred_folder or the files in the csv
    filelist = [
        (
            (image_identifier if image_identifier else "image"),
            (mask_identifier if mask_identifier else "mask"),
        )
    ]
    if os.path.isfile(input_ff):
        # Single image
        f_ext = os.path.splitext(input_ff)[1]
        if f_ext in image_extension:
            if mask_identifier:
                if image_identifier:
                    names = (
                        input_ff,
                        input_ff.replace(
                            image_identifier, mask_identifier
                        ),
                    )
                else:
                    names = (
                        input_ff,
                        input_ff.replace(
                            image_extension, "_" + mask_identifier +
                                             image_extension,
                        ),
                    )
            else:
                names = (input_ff, "")
            filelist.append(names)
        elif f_ext.endswith('.csv'):
            if not os.path.exists(input_ff):
                raise FileNotFoundError(f"The input csv file {input_ff} does "
                                        f"not exist.")
            df = pd.read_csv(input_ff)
            filelist = [df.columns.values.tolist()] + \
                       df.replace(np.nan, '', regex=True).values.tolist()
    else:  # Folder with images
        print((" Input pred_folder: {}".format(input_ff)))
        # Files and subfold
        for root, dirs, files in os.walk(input_ff):
            if root == output_ff:  # Avoid output pred_folder.
                continue

            if not include_subfolders and root != input_ff:
                continue

            for i, name in enumerate(sorted(files, key=len)):
                filepath = os.path.join(root, name)
                f_ext = os.path.splitext(name)[1]
                if f_ext in image_extension:
                    if image_identifier and image_identifier in name:
                        if mask_identifier:
                            if mask_identifier in name:
                                continue
                            names = (
                                filepath,
                                filepath.replace(
                                    image_identifier, mask_identifier
                                ),
                            )
                    elif mask_identifier:
                        if mask_identifier in name:
                            continue
                        names = (
                            filepath,
                            filepath.replace(image_extension,
                                             "_" + mask_identifier +
                                             image_extension,
                                             ),
                        )
                    else:  # Assume there is no mask
                        names = (filepath, "")
                    filelist.append(names)
                else:
                    continue  # Not an image file

    for image_path, mask_path in filelist[1:]:  # First element is the header
        img_folder, filename = os.path.split(image_path)

        # If it has no extension, append a filename
        out_file = os.path.join(output_ff, filename) if os.path.splitext(
            output_ff)[1] == "" else output_ff

        if (
                os.path.exists(out_file)
                and not overwrite_files
                and os.path.getsize(out_file) > 0
        ):
            print(("File already preprocessed. ({})".format(out_file)))
            continue

        subfolders = diff_subfolders(img_folder,
                                     output_ff) if keep_folders else None

        try:
            prep_image_or_mask(image_path, output_ff, mask_path,
                               clip_intensity_values, target_spacing,
                               fixed_size_pad, threshold, largest_cc, register,
                               transformation, random_blank_patch,
                               binary, atlas_path, img_interp, subfolders)
        except Exception as e:
            print(f"Preprocessing raised an exception {e}.\n")


def prep_img_s(
        input_ff,
        out_ff=None,
        image_identifier=None,
        mask_identifier=None,
        generate_csv=True,
        overwrite=False,
):
    """Preprocess a single file or a pred_folder for segmentation purposes.

    :param input_ff: File or pred_folder with the images to be preprocessed.
    :param out_ff:  output pred_folder.
    :param image_identifier: image identifier in filenames.
    :param mask_identifier: mask identifier in filenames.
    :param generate_csv:  Generate csv for training a NN flag.
    :param overwrite:  Overwrite files if already exist.
    :return:
    """
    base_folder = (
        os.path.split(input_ff)[0] if not os.path.isdir(input_ff) else input_ff
    )
    out_ff = (
        os.path.join(base_folder, "pp_seg") if not out_ff else out_ff
    )
    preprocess_ct_files(
        input_ff,
        out_ff,
        image_identifier=image_identifier,
        mask_identifier=mask_identifier,
        clip_intensity_values=[20, 150],
        overwrite_files=overwrite,
        include_subfolders=False,
        transformation='rigid',
        register=True
    )

    if generate_csv is True:  # Create a csv file of the preprocessed files
        csv_path, splits = common.create_csv(
            out_ff,
            splits=[0.7, 0.1, 0.2],
            image_identifier=image_identifier,
            mask_identifier=mask_identifier,
        )
        return out_ff, csv_path, splits

    return out_ff


def prep_img_cr(input_ff, out_ff=None, image_identifier=None,
                mask_identifier=None, generate_csv=False, overwrite=False):
    """Preprocess a single file or pred_folder for craniectomy reconstruction.

    :param input_ff: File or pred_folder with the images to be preprocessed.
    :param out_ff:  output file/pred_folder.
    :param image_identifier: Image identifier in the filename.
    :param mask_identifier: Mask identifier in the filename.
    :param generate_csv:  Generate csv for training a NN flag.
    :param overwrite:  Overwrite files if already exist.
    :return:
    """
    base_folder = (
        os.path.split(input_ff)[0] if not os.path.isdir(input_ff) else input_ff
    )
    out_ff = (
        os.path.join(base_folder, "pp_cr") if not out_ff else out_ff
    )
    preprocess_ct_files(
        input_ff,
        out_ff,
        register=True,
        atlas_path='~/headctools/assets/atlas/atlas3_nonrigid_masked_304_224'
                   '.nii.gz',
        image_identifier=image_identifier,
        mask_identifier=mask_identifier,
        clip_intensity_values=[150, 151],
        overwrite_files=overwrite,
        include_subfolders=False,
        threshold=True,
        largest_cc=True,
        transformation='DenseRigid'
    )

    if generate_csv is True:  # Create a csv file of the preprocessed files
        common.simple_csv(out_ff, csv_name='UNetSP.csv',
                          image_identifier=image_identifier,
                          mask_identifier=mask_identifier,
                          ext='.nii.gz')

    return out_ff


def prep_img_autoimpl(input_ff, out_ff=None, image_identifier=None,
                      mask_identifier=None, generate_csv=False,
                      overwrite=False):
    base_folder = (
        os.path.split(input_ff)[0] if not os.path.isdir(input_ff) else input_ff
    )
    out_ff = (
        os.path.join(base_folder, "pp_cr") if not out_ff else out_ff
    )
    preprocess_ct_files(
        input_ff,
        out_ff,
        register=True,
        atlas_path='/home/fmatzkin/Code/headctools/assets/atlas/reg/atlas_304_224.nii.gz',
        image_identifier=image_identifier,
        mask_identifier=mask_identifier,
        overwrite_files=overwrite,
        include_subfolders=False,
        transformation='DenseRigid',
        img_interp='nearestNeighbor'
    )

    if generate_csv is True:  # Create a csv file of the preprocessed files
        common.simple_csv(out_ff, csv_name='UNetSP.csv',
                          image_identifier=image_identifier,
                          mask_identifier=mask_identifier,
                          ext='.nii.gz')

    return out_ff


if __name__ == "__main__":
    # prep_img_cr(
    #    '/home/franco/Code/datasets/test_pypi',
    #    image_identifier=None,
    #    mask_identifier=None, generate_csv=True,
    #    overwrite=False)

    # prep_img_autoimpl(
    #     '/home/fmatzkin/Code/datasets/autoimplant-challenge/test_set_for_participants/ext_renamed',
    #     image_identifier='',
    #     mask_identifier=None, generate_csv=True,
    #     overwrite=False)

    preprocess_ct_files(
        '/home/franco/Code/datasets/test',
        '/home/franco/Code/datasets/test/2mm/',
        target_spacing=[3,3,3],
        overwrite_files=True,
        threshold=True,
        fixed_size_pad=[64,80,80]
    )
