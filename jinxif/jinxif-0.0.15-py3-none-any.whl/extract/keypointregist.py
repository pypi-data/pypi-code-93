#####
# code from adapted chandler gatenbee and brian white
# https://github.com/IAWG-CSBC-PSON/registration-challenge
#
#
# Guillaume 20210427: email python image registration code
# for python registration I used:
#
# + SIFT
#     - cv2.SIFT_create()
#     - I extract the features kp1, desc1 = SIFT.detectAndCompute(moving, None)
# + match the features:
#     - matcher = cv2.BFMatcher(normType=cv2.NORM_L2, crossCheck=True)
#     - matches = matcher.match(desc1, desc2)
# + find homography:
#     - H, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC, ransacReprojThreshold=10)
#     - Estimate the transformation
#     - transformer.estimate(moving_pts, target_pts)
# + make the final transform
#    - transform.warp(moving, transformer.inverse, output_shape=output_shape_rc)
#
# most of it if from the hackathon, but I normalize the images first (they didn't do) and then use SIFT.
# the last part is the bottleneck and makes the entire code useless.
#
# SO I'm testing some of the libraries listed here: http://pyimreg.github.io
#####

# library
import cv2
from matplotlib import pyplot as plt
import numpy as np
from skimage import io, transform, util
import sys

# function
def match_keypoints(moving, target, feature_detector):
    '''
    :param moving: image that is to be warped to align with target image
    :param target: image to which the moving image will be aligned
    :param feature_detector: a feature detector from opencv
    :return:
    '''

    kp1, desc1 = feature_detector.detectAndCompute(moving, None)
    kp2, desc2 = feature_detector.detectAndCompute(target, None)

    matcher = cv2.BFMatcher(normType=cv2.NORM_L2, crossCheck=True)
    matches = matcher.match(desc1, desc2)

    src_match_idx = [m.queryIdx for m in matches]
    dst_match_idx = [m.trainIdx for m in matches]

    src_points = np.float32([kp1[i].pt for i in src_match_idx])
    dst_points = np.float32([kp2[i].pt for i in dst_match_idx])

    H, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC, ransacReprojThreshold=10)

    good = [matches[i] for i in np.arange(0, len(mask)) if mask[i] == [1]]

    filtered_src_match_idx = [m.queryIdx for m in good]
    filtered_dst_match_idx = [m.trainIdx for m in good]

    filtered_src_points = np.float32([kp1[i].pt for i in filtered_src_match_idx])
    filtered_dst_points = np.float32([kp2[i].pt for i in filtered_dst_match_idx])

    return filtered_src_points, filtered_dst_points


def apply_transform(moving, target, moving_pts, target_pts, transformer, output_shape_rc=None):
    '''
    :param transformer: transformer object from skimage. See https://scikit-image.org/docs/dev/api/skimage.transform.html for different transformations
    :param output_shape_rc: shape of warped image (row, col). If None, uses shape of traget image
    return
    '''
    if output_shape_rc is None:
        output_shape_rc = target.shape[:2]

    if str(transformer.__class__) == "<class 'skimage.transform._geometric.PolynomialTransform'>":
        transformer.estimate(target_pts, moving_pts)
        warped_img = transform.warp(moving, transformer, output_shape=output_shape_rc)

        ### Restimate to warp points
        transformer.estimate(moving_pts, target_pts)
        warped_pts = transformer(moving_pts)
    else:
        transformer.estimate(moving_pts, target_pts)
        warped_img = transform.warp(moving, transformer.inverse, output_shape=output_shape_rc)
        warped_pts = transformer(moving_pts)

    return warped_img, warped_pts


def keypoint_distance(moving_pts, target_pts, img_h, img_w):
    dst = np.sqrt(np.sum((moving_pts - target_pts)**2, axis=1)) / np.sqrt(img_h**2 + img_w**2)
    return np.mean(dst)


def register(s_target_file, s_moving_file, b_plot=False):
    '''
    '''
    s_round = s_moving_file.split('_')[0]
    s_sample = s_moving_file.split('_')[2]
    print(s_round)
    target = util.img_as_ubyte(util.img_as_float(io.imread(s_target_file)))
    moving = util.img_as_ubyte(util.img_as_float(io.imread(s_moving_file)))

    # bue 20201112: jenny why you use akaze insted of kaze. what is the difference?
    fd = cv2.AKAZE_create()
    #fd = cv2.KAZE_create(extended=True)
    moving_pts, target_pts = match_keypoints(moving, target, feature_detector=fd)

    transformer = transform.SimilarityTransform()
    warped_img, warped_pts = apply_transform(moving, target, moving_pts, target_pts, transformer=transformer)
    warped_img = util.img_as_ubyte(warped_img)

    print("Unaligned offset:", keypoint_distance(moving_pts, target_pts, moving.shape[0], moving.shape[1]))
    print("Aligned offset:", keypoint_distance(warped_pts, target_pts, moving.shape[0], moving.shape[1]))
    if b_plot:
        # bue 20210413: this is an additional qc plot and should maybe be handled separately?
        fig, ax = plt.subplots(2,2, figsize=(10,10))
        ax[0][0].imshow(target)
        ax[0][0].imshow(moving, alpha=0.5)
        ax[1][0].scatter(target_pts[:,0], -target_pts[:,1])
        ax[1][0].scatter(moving_pts[:,0], -moving_pts[:,1])

        ax[0][1].imshow(target)
        ax[0][1].imshow(warped_img, alpha=0.5)
        ax[1][1].scatter(target_pts[:,0], -target_pts[:,1])
        ax[1][1].scatter(warped_pts[:,0], -warped_pts[:,1])
        # bue 20201111: can maybe be combined wit b_plot
        plt.savefig(f"../../QC/RegistrationPlots/{s_sample}_{s_round}_rigid_align.png", format="PNG")
    return(moving_pts, target_pts, transformer)

