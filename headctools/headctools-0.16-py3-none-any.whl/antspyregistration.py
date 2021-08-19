import tempfile

import ants
import os
from os import path as osp
import SimpleITK as sitk
from .utilities import veri_folder


def register_antspy(moving_img_path, fixed_image, out_image=None,
                    mat_path=None, transformation="AffineFast",
                    overwrite=False):
    atlas_name = osp.split(fixed_image)[1].split(".")[0]
    mv_img_p, mv_img_n = osp.split(moving_img_path)

    out_dir = osp.join(mv_img_p, atlas_name)
    veri_folder(out_dir)

    out_image = (
        osp.join(out_dir, mv_img_n) if out_image is None else out_image
    )

    mat_path = (
        osp.join(out_dir, mv_img_n.replace(".nii.gz", ".mat"))
        if mat_path is None
        else mat_path
    )

    if osp.exists(out_image) and not overwrite and osp.getsize(out_image) > 0:
        print("\n  The output file already exists (skipping).")
        return
    else:
        ct = ants.image_read(moving_img_path)
        fixed = ants.image_read(fixed_image)

        my_tx = ants.registration(fixed=fixed, moving=ct,
                                  type_of_transform=transformation)
        transf_ct = my_tx['warpedmovout']
        reg_transform = my_tx['fwdtransforms']
        ants.write_transform(ants.read_transform(reg_transform[0]), mat_path)
        ants.image_write(transf_ct, out_image)


def register_folder_flirt(
        folder,
        fixed_image,
        mask_id=None,
        ext=".nii.gz",
        transformation="rigid",
        interp="nearestneighbour",
        overwrite=False,
):
    print("[Registering images to atlas] Folder: {}".format(folder))

    commands_reg = []
    commands_reg_masks = []
    for file in os.listdir(folder):
        if file.endswith(ext) and mask_id not in file:
            print("    File: {}...".format(file), end="")
            moving_image = os.path.join(folder, file)

            command = register_fsl(
                moving_image,
                fixed_image,
                return_command=True,
                transformation=transformation,
                interp=interp,
                overwrite=overwrite,
            )
            reg_img_path = command[
                           command.find("-out") + 6: command.find("-omat") - 2
                           ]
            if overwrite or not os.path.exists(reg_img_path):
                commands_reg.append(command) if command else 0

            if mask_id:
                mat_path = command[
                           command.find("-omat") + 7: command.find("-bins") - 2
                           ]
                mask_file_path = os.path.join(
                    folder, file.replace(ext, "_" + mask_id + ext)
                )

                out_image_name = os.path.split(mask_file_path)[1]
                out_image = os.path.join(
                    os.path.split(mat_path)[0], out_image_name
                )
                if os.path.exists(mask_file_path):
                    comm = apply_mat(
                        mask_file_path,
                        out_image,
                        mat_path,
                        reg_img_path,
                        interp="nearestneighbour",
                        return_command=True,
                        overwrite=overwrite,
                    )
                    if overwrite or not os.path.exists(out_image):
                        commands_reg_masks.append(comm) if comm else 0

    process_pool = Pool(processes=8)
    process_pool.map(execute, commands_reg)
    process_pool.map(execute, commands_reg_masks)

def apply_mat(moving_img_path, out_image, mat_path, reference_path,
              interp="nearestNeighbor", overwrite=False, invert=False):
    """ Apply a saved transformation to a moving image.


    :param moving_img_path: Input image path.
    :param out_image: Output image path.
    :param mat_path: Transform path.
    :param reference_path: Image used as reference for determining dimensions.
    :param interp: Interpolation method used.
    :param overwrite: Overwrite the output image if it already exists.
    :return:
    """
    if osp.exists(out_image) and not overwrite and osp.getsize(out_image) > 0:
        print("already exists (skipping).")
        return

    moving_img = ants.image_read(moving_img_path)
    reference = ants.image_read(reference_path)

    transf_img = ants.apply_transforms(fixed=reference, moving=moving_img,
                                       transformlist=[mat_path],
                                       interpolator=interp,
                                       whichtoinvert=[invert])

    ants.image_write(transf_img, out_image)

    print(" saved in {}.".format(out_image))


def register_ants_sitk(moving_image, fixed_image=None, mat_save_path=None,
                       transformation="Rigid", interp="nearestNeighbor",
                       mat_to_apply=None, reference=None):
    """ Register images using ANTsPy and SimpleITK.

    :param moving_image: Image to register.
    :param fixed_image: Atlas image.
    :param mat_save_path: Tasnformation parameters path.
    :param transformation: Type of transform.
    :param interp: Interpolator used.
    :param mat_to_apply: If given, it will apply this transformation.
    :param reference: If mat_to_apply, reference_path image for applying the
    transform and determining the dimensions.
    :return:

    transformation can be one of: “Translation”, “Rigid”, “Similarity”,
    “QuickRigid”, “DenseRigid”, “BOLDRigid”, “Affine”, “AffineFast”,
    “BOLDAffine”, “TRSAA”, “ElasticSyN”, “SyN”, “SyNRA”, “SyNOnly”, “SyNCC”,
    “SyNabp”, “SyNBold”, “SyNBoldAff”, “SyNAggro”, “TVMSQ” or “TVMSQC”.

    interpolator may be:
    linear nearestNeighbor multiLabel for label images but genericlabel is
    preferred gaussian bSpline cosineWindowedSinc welchWindowedSinc
    hammingWindowedSinc lanczosWindowedSinc genericLabel use this for label
    images.

    Find more info about these params in https://antspy.readthedocs.io/en/latest/registration.html  # noqa
    """
    mv_img = tempfile.NamedTemporaryFile(suffix='.nii.gz', delete=False)
    mv_img_path = mv_img.name

    sitk.WriteImage(moving_image, mv_img_path)

    out_img = tempfile.NamedTemporaryFile(suffix='.nii.gz', delete=False)
    out_img_path = out_img.name

    if fixed_image and type(fixed_image) is not str:
        fx_img = tempfile.NamedTemporaryFile(suffix='.nii.gz', delete=False)
        fx_img_path = fx_img.name
        sitk.WriteImage(fixed_image, fx_img_path)
    elif fixed_image:
        fx_img_path = fixed_image

    if mat_to_apply and reference:
        # Used only when applying .mat transform to mask
        ref_img = tempfile.NamedTemporaryFile(suffix='.nii.gz', delete=False)
        ref_img_path = ref_img.name
        sitk.WriteImage(reference, ref_img_path)

        apply_mat(mv_img_path, out_img_path, mat_to_apply, ref_img_path,
                  interp, overwrite=False)
    else:
        register_antspy(mv_img_path, fx_img_path, out_img_path,
                        mat_save_path, transformation)

    ret_img = sitk.ReadImage(out_img_path)
    return ret_img


def undo_reg_in_pred(pred_folder, prep_id=None, pred_id=None, ext='.nii.gz',
                     interp="nearestNeighbor", overwrite=False, reg_id=""):
    """ Take the predictions to the original image space.

    The images must be organized in the following way (each level is a
    subfolder):
        - F1: Images folder in the orig size.
            - F2: Preprocessed images.
                - F3: Predictions folder.

    The transforms will be looked-up in F2, as antspy .mat transforms and
    will be reversed before applying them to the images in F3. It will aso
    take the images in F1 as reference.

    :param pred_folder: Predictions folder.
    :param prep_id: Preprocessed files identifier. Set this parameter in
    case the preprocessed file names don't match with the original file names,
    and they differ in a suffix, such as "image001.nii" and "image001_prp.nii".
    :param pred_id: Prediction files identifier. Set this parameter in
    case the predictions and preprocessed file names don't match, and they
    differ in a suffix, such as "image001.nii" and "image001_pred.nii".
    :param ext: Image extension.
    :param interp: Interpolation method.
    :param overwrite: Overwrite files.
    :param reg_id: Registered file identifier.

    :return:
    """
    files = [f for f in os.listdir(pred_folder) if f.endswith(ext)]
    files = [f for f in files if pred_id in f] if pred_id else files  # Filter

    prep_folder, _ = osp.split(pred_folder)
    orig_folder, _ = osp.split(prep_folder)

    for pred_fname in files:
        prep_fname = pred_fname.replace(pred_id, '') if pred_id else pred_fname
        orig_fname = prep_fname.replace(prep_id, '') if prep_id else prep_fname

        mat_fpath = osp.join(prep_folder,
                             prep_fname.replace(ext, ext + reg_id + ".mat"))
        ref_fpath = osp.join(orig_folder, orig_fname)
        pred_fpath = osp.join(pred_folder, pred_fname)

        out_folder = veri_folder(osp.join(pred_folder, "orig_dims"))
        out_fpath = osp.join(out_folder, pred_fname)

        if osp.exists(out_fpath) and overwrite is False:
            print("{} skipped (already exists).".format(out_fpath))
            continue
        elif not osp.exists(mat_fpath) or not osp.exists(ref_fpath):
            print("{} skipped. Check that the .mat and reference files "
                  "exist.".format(pred_fname))
            continue
        else:
            apply_mat(pred_fpath, out_fpath, mat_fpath, ref_fpath, interp,
                      overwrite=True, invert=True)


if __name__ == "__main__":
    icv_full = '/home/fmatzkin/Code/datasets/SamCook-FAVO/full/pp_cr/icvs'
    icv_recons = '/home/fmatzkin/Code/datasets/SamCook-FAVO/craniectomy/pp_cr/pred_210326-FR_SP_DO_wcat_ep59'

    undo_reg_in_pred(icv_recons, pred_id='_i_postop_icv', reg_id='_reg')
