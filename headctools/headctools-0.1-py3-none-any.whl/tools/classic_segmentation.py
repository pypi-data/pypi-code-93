import csv
import os

import SimpleITK as sitk
import numpy as np
import scipy
from raster_geometry import cube

import headctools.utilities as utils


def flood_fill_hull(inp_im):
    """ Get the convex hull of a binary mask.

    Taken from https://stackoverflow.com/a/46314485.

    :param inp_im: Input image (it could be numpy array or SimpleITK.Image).
    :return: Binary image containing the pixels laying in the convex hull.
    """
    is_sitk = True if type(inp_im) == sitk.Image else False
    image = sitk.GetArrayFromImage(inp_im) if is_sitk else inp_im

    points = np.transpose(np.where(image))
    hull = scipy.spatial.ConvexHull(points)
    deln = scipy.spatial.Delaunay(points[hull.vertices])
    idx = np.stack(np.indices(image.shape), axis=-1)
    out_idx = np.nonzero(deln.find_simplex(idx) + 1)
    out_img = np.zeros(image.shape)
    out_img[out_idx] = 1

    if not is_sitk:
        return out_img
    else:
        out_sitk = sitk.GetImageFromArray(out_img)
        out_sitk.CopyInformation(inp_im)
        if 'bitpix' in inp_im.GetMetaDataKeys():
            if inp_im.GetMetaData('bitpix') == '8':
                out_sitk = sitk.Cast(out_sitk, sitk.sitkUInt8)
        return out_sitk


def otsu_segmentation(img_sitk):
    """ Perform the Otsu segmentation of a given SimpleITK image.

    :param img_sitk: Input image (SimpleITK image).
    :return: SimpleITK image of the Otsu segmentation.
    """
    otsu_filter = sitk.OtsuThresholdImageFilter()
    mask = otsu_filter.Execute(img_sitk)
    return mask


def erode(sitk_img, times=1):
    """ Given a SimpleITK image, erode it according to the times parameter

    :param sitk_img: SimpleITK binary image.
    :param times: Number of erosions performed.
    :return: 
    """
    for _ in range(times):
        sitk_img = sitk.ErodeObjectMorphology(sitk_img)
    return sitk_img


def dilate(sitk_img, times=1):
    """ Given a SimpleITK image, dilate it according to the times parameter

    :param sitk_img: SimpleITK binary image.
    :param times: Number of dilations performed.
    :return:
    """
    for _ in range(times):
        sitk_img = sitk.DilateObjectMorphology(sitk_img)
    return sitk_img


def close(sitk_img, times=1):
    """ Given a SimpleITK image, close it according to the times parameter

    :param sitk_img: SimpleITK binary image.
    :param times: Number of closings performed.
    :return:
    """
    for _ in range(times):
        sitk_img = sitk.BinaryMorphologicalClosing(sitk_img)
    return sitk_img


def get_percentile_intensity(img, mask, perc=85, n_bins=128):
    roi_mask = sitk.GetArrayFromImage(mask)
    img_roi = img[roi_mask > 0]

    histo, bins = np.histogram(img_roi.flatten(), n_bins)

    cdf = np.cumsum(histo)
    cdf = cdf / cdf[-1] * 100

    # Get the value corresponding to that percentile
    val = bins[np.sum(cdf <= perc)] + ((bins[1] - bins[0]) / 2)
    return val


def level_sets(img, seed, prop_scaling=1., curv_scaling=.2, adv_scaling=3,
               max_rms_err=0.01, it_n=200):
    """ Apply Level Sets segmentation, based in GeodesicActiveContourLevelSet.

    See https://itk.org/Doxygen/html/classitk_1_1GeodesicActiveContourLevelSetImageFilter.html  # noqa

    :param img: Base image.
    :param seed: Seed from which the segmentation will grow (or shrink).
    :param prop_scaling: can be used to switch from propagation outwards
    (POSITIVE scaling parameter) versus propagating inwards (NEGATIVE scaling
    parameter).
    :param curv_scaling: In general, the larger the CurvatureScaling, the
    smoother the resulting contour.
    :param adv_scaling: Set to 1.
    :param max_rms_err: Maximum error tolerance.
    :param it_n: Number of iterations.
    :return:
    """
    img = sitk.Cast(img, sitk.sitkFloat32)
    seed = sitk.Cast(seed, sitk.sitkFloat32) * -1 + 0.5

    gac = sitk.GeodesicActiveContourLevelSetImageFilter()
    gac.SetPropagationScaling(prop_scaling)
    gac.SetCurvatureScaling(curv_scaling)
    gac.SetAdvectionScaling(adv_scaling)
    gac.SetMaximumRMSError(max_rms_err)
    gac.SetNumberOfIterations(it_n)

    gac_3d = gac.Execute(seed, img)

    level_set_result_matrix = sitk.GetArrayFromImage(gac_3d)
    level_set_resultimg = 1 - sitk.GetImageFromArray(
        level_set_result_matrix) > 0
    level_set_resultimg.CopyInformation(img)
    return level_set_resultimg


def filter_img(img):
    print("    Applying CAD filter..")
    time_step, conduct, num_iter = (0.04, 9.0, 5)
    img_recast = sitk.Cast(img, sitk.sitkFloat32)
    curv_diff = sitk.CurvatureAnisotropicDiffusionImageFilter()
    curv_diff.SetTimeStep(time_step)
    curv_diff.SetConductanceParameter(conduct)
    curv_diff.SetNumberOfIterations(num_iter)
    img_filter = curv_diff.Execute(img_recast)

    print("    Applying GMRGaussian..")
    sigma_ = 2.0
    img_gauss = sitk.GradientMagnitudeRecursiveGaussian(
        image1=img_filter, sigma=sigma_)
    k1, k2 = 18.0, 8.0
    alpha_ = (k2 - k1) / 6
    beta_ = (k1 + k2) / 2

    print("    Applying sigmoid filter..")
    sig_filt = sitk.SigmoidImageFilter()
    sig_filt.SetAlpha(alpha_)
    sig_filt.SetBeta(beta_)
    sig_filt.SetOutputMaximum(1.0)
    sig_filt.SetOutputMinimum(0.0)
    img_sigmoid = sig_filt.Execute(img_gauss)
    return img_sigmoid


def normalize(img):
    data = sitk.GetArrayFromImage(img).astype(float)

    mean = np.mean(data)
    sigma = np.std(data)
    data = data - mean
    data = data / sigma

    r_img = sitk.GetImageFromArray(data)
    r_img.CopyInformation(img)
    return r_img


def connected_components_segmentation(imgp):
    img = sitk.ReadImage(imgp)
    coords_mask = [tuple([int(i) for i in s]) for s in
                   np.argwhere(cube(img.GetSize(), 50))]

    n_iter, multip, init_rad, replace_val = 0, 2, 0, 1

    seg_imp_thr = sitk.ConfidenceConnected(img,
                                           seedList=coords_mask,
                                           numberOfIterations=n_iter,
                                           multiplier=multip,
                                           initialNeighborhoodRadius=init_rad,
                                           replaceValue=replace_val)

    # Apply opening for separating big regions
    vector_radius = (1, 1, 1)
    kernel = sitk.sitkBall
    seg_imp_thr = sitk.BinaryMorphologicalOpening(
        seg_imp_thr, vector_radius, kernel)

    return seg_imp_thr


def fast_marching(img_p, stop_val=700):
    img = sitk.ReadImage(img_p)
    seed = tuple([i // 2 for i in img.GetSize()])
    feature_img = sitk.GradientMagnitudeRecursiveGaussian(img, sigma=.5)
    speed_img = sitk.BoundedReciprocal(
        feature_img)  # This is parameter free unlike the Sigmoid

    fm_filter = sitk.FastMarchingBaseImageFilter()
    fm_filter.SetTrialPoints([seed])
    fm_filter.SetStoppingValue(stop_val)
    fm_img = fm_filter.Execute(speed_img)
    o_img = sitk.Threshold(fm_img,
                           lower=0.0,
                           upper=fm_filter.GetStoppingValue(),
                           outsideValue=stop_val + 1)
    return o_img < stop_val + 1


def level_sets_segmentation(image_path):
    print("  Opening img_path..")
    if type(image_path) is list:
        for i, path in enumerate(image_path):
            if i == 0:
                img_sitk = sitk.ReadImage(path)
            else:
                img_sitk += sitk.ReadImage(path)
    else:
        img_sitk = sitk.ReadImage(image_path)  # Load image

    spacing = img_sitk.GetSpacing()
    origin = img_sitk.GetOrigin()
    direction = img_sitk.GetDirection()

    # Make sure the image is bimodal (for applying Otsu) by clipping the
    # very low and very high intensities
    print("  clipping intensities..")
    img_np_clipped = np.clip(sitk.GetArrayFromImage(img_sitk), -20, 300)
    img_sitk = sitk.GetImageFromArray(img_np_clipped)  # Convert to sitk

    img_sitk.SetSpacing(spacing)
    img_sitk.SetOrigin(origin)
    img_sitk.SetDirection(direction)

    print("  Mask..")
    print("    Applying otsu..")
    img_sitk_otsu = otsu_segmentation(img_sitk)  # Apply Otsu segmentation

    print("    Morphological ops to outsu img_path..")
    bin_img_sitk = close(img_sitk_otsu, times=3)  # Close 3 times
    bin_img_sitk = sitk.BinaryFillhole(bin_img_sitk)  # Fill holes
    bin_img_sitk = erode(bin_img_sitk, times=8)  # Erode 5 times
    bin_img_sitk = dilate(bin_img_sitk, times=5)  # Erode 15 times
    bin_img_sitk = sitk.BinaryFillhole(bin_img_sitk)  # Fill holes
    bin_img_np = sitk.GetArrayFromImage(bin_img_sitk)

    print("   getting stats..")
    # Get the intensity of the 85th percentile
    val = get_percentile_intensity(img_np_clipped, bin_img_sitk, perc=85)
    print("    mask according to stats..")
    skull_mask_np = np.where(img_np_clipped > val, bin_img_np, 0)
    skull_mask_sitk = sitk.GetImageFromArray(skull_mask_np)
    skull_mask_sitk.CopyInformation(img_sitk)

    print("    max cc..")
    # brain_initial_mask = sitk.And(bin_img_sitk, sitk.BinaryNot(skull_mask_sitk))
    brain_initial_mask = utils.get_largest_cc(skull_mask_sitk)
    brain_initial_mask = sitk.BinaryFillhole(brain_initial_mask)

    print("  Filering img_path..")
    img_filt = filter_img(img_sitk)

    print("  Level sets..")
    segmentation = level_sets(img_filt, brain_initial_mask)

    o_path = image_path.replace('.nii.gz', '_lvlsets.nii.gz')
    print(" saving {}".format(o_path))

    segmentation.SetSpacing(spacing)
    segmentation.SetOrigin(origin)
    segmentation.SetDirection(direction)

    sitk.WriteImage(segmentation, o_path)


def level_sets_skull(image_path, ext='.nii.gz',
                     overwrite=False, out_id='_brain'):
    if type(image_path) is list:
        print(f"  Loading {os.path.split(image_path[0])[1]}..")
        out_path = image_path[0].replace(ext, out_id + ext)
        for i, path in enumerate(image_path):
            if i == 0:
                img_sitk = sitk.ReadImage(path)
            else:
                img_sitk += sitk.ReadImage(path)
        img_sitk = img_sitk > 0
        sitk.WriteImage(img_sitk, out_path.replace(out_id, '_sum'))
    else:
        print(f"  Loading {os.path.split(image_path)[1]}..")
        out_path = image_path.replace(ext, out_id + ext)
        img_sitk = sitk.ReadImage(image_path)  # Load image

    if not overwrite and os.path.exists(out_path):
        print(f"{out_path} already exists, skipping...")
        return

    initial_mask = flood_fill_hull(img_sitk)
    initial_mask = sitk.And(sitk.Cast(initial_mask, sitk.sitkUInt8),
                                  sitk.Cast(1 - img_sitk, sitk.sitkUInt8))
    initial_mask = erode(initial_mask, times=5)
    initial_mask = utils.get_largest_cc(initial_mask)

    segmentation = level_sets(1 - img_sitk, initial_mask,
                              curv_scaling=.5,
                              prop_scaling=1,
                              adv_scaling=3,
                              it_n=200,
                              max_rms_err=.001)
    sitk.WriteImage(segmentation, out_path)


def level_sets_skull_folder(folder_path, id_1='image_i.nii.gz',
                            id_2='image.nii.gz', is_skull=True,
                            overwrite=False, out_id='_brain'):
    for file in os.listdir(folder_path):
        if id_2 is not None:
            if file.endswith((id_2, '_brain.nii.gz', '_sum.nii.gz',
                              '_head_mask.nii.gz')) or not file.endswith(id_1):
                continue
            skull = os.path.join(folder_path, file)
            implant = os.path.join(folder_path, file.replace(id_1, id_2))

            if is_skull:
                level_sets_skull([skull, implant], overwrite=overwrite,
                                 out_id=out_id)
            else:
                level_sets_segmentation(skull)
        else:
            if id_1:
                if not file.endswith(id_1):
                    continue
            skull = os.path.join(folder_path, file)
            if is_skull:
                level_sets_skull(skull, overwrite=overwrite,
                                 out_id=out_id)
            else:
                level_sets_segmentation(skull)


def csv_volumes(folder_path, ext='.nii.gz'):
    out_file = os.path.join(folder_path, 'volumes.csv')
    volumes = [('image', 'volume')]
    for file in os.listdir(folder_path):
        if not file.endswith(ext) or os.path.isdir(os.path.join(folder_path,
                                                                file)):
            continue
        f1 = os.path.join(folder_path, file)
        v1 = sitk.GetArrayFromImage(sitk.ReadImage(f1))
        voxel_vol = np.prod(sitk.ReadImage(f1).GetSpacing())
        volumes.append((file, np.count_nonzero(v1) * voxel_vol))

    with open(out_file, "w") as fp:
        writer = csv.writer(fp, delimiter=",")
        writer.writerows(volumes)

    print(f"Written {out_file}")


# level_sets_skull(['/home/fmatzkin/Code/datasets/SamCook-FAVO/craniectomy'
#                   '/pp_cr/pred_AIFR_0909_ep6/1002_20215_3_image_i.nii.gz',
#                  '/home/fmatzkin/Code/datasets/SamCook-FAVO/craniectomy'
#                   '/pp_cr/pred_AIFR_0909_ep6/1002_20215_3_image.nii.gz'],
#                  atlas_path)
# level_sets_segmentation('/home/fmatzkin/Code/datasets/SamCook-FAVO/craniectomy/1002_23215_image.nii.gz')

folder_path = '/home/fmatzkin/Code/datasets/SamCook-FAVO/craniectomy/pp_cr/pred_210326-FR_SP_DO_wcat_ep59'
level_sets_skull_folder(folder_path, id_1='image_i.nii.gz',
                        id_2=None, is_skull=True, overwrite=False,
                        out_id='_postop_icv')

# csv_volumes('/home/fmatzkin/Code/datasets/SamCook-FAVO/volumes')
