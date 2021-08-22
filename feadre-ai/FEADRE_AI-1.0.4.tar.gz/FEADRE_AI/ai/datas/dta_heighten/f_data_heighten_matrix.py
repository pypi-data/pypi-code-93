import random
import numpy as np
import cv2
import math
import matplotlib.pyplot as plt


def _flip_matrix4nanodet(prob=0.5):
    '''
    随机水平翻转
    :param prob: 概率
    :return:
    '''
    F = np.eye(3)
    if random.random() < prob:
        F[0, 0] = -1
    return F


def _perspective_matrix4nanodet(perspective=0):
    """

    :param perspective:
    :return:
    """
    P = np.eye(3)
    P[2, 0] = random.uniform(-perspective, perspective)  # x perspective (about y)
    P[2, 1] = random.uniform(-perspective, perspective)  # y perspective (about x)
    return P


def _rotation_matrix4nanodet(degree=0):
    """

    :param degree:
    :return:
    """
    R = np.eye(3)
    a = random.uniform(-degree, degree)
    R[:2] = cv2.getRotationMatrix2D(angle=a, center=(0, 0), scale=1)
    return R


def _scale_matrix4nanodet(ratio=(1, 1)):
    """

    :param width_ratio:
    :param height_ratio:
    """
    Scl = np.eye(3)
    scale = random.uniform(*ratio)
    Scl[0, 0] *= scale
    Scl[1, 1] *= scale
    return Scl


def _stretch_matrix4nanodet(width_ratio=(1, 1), height_ratio=(1, 1)):
    """

    :param width_ratio:
    :param height_ratio:
    """
    Str = np.eye(3)
    Str[0, 0] *= random.uniform(*width_ratio)
    Str[1, 1] *= random.uniform(*height_ratio)
    return Str


def _shear_matrix4nanodet(degree):
    """

    :param degree:
    :return:
    """
    Sh = np.eye(3)
    Sh[0, 1] = math.tan(random.uniform(-degree, degree) * math.pi / 180)  # x shear (deg)
    Sh[1, 0] = math.tan(random.uniform(-degree, degree) * math.pi / 180)  # y shear (deg)
    return Sh


def _translate_matrix4nanodet(translate, width, height):
    """

    :param translate:
    :return:
    """
    T = np.eye(3)
    T[0, 2] = random.uniform(0.5 - translate, 0.5 + translate) * width  # x translation
    T[1, 2] = random.uniform(0.5 - translate, 0.5 + translate) * height  # y translation
    return T


def _resize_matrix4nanodet(raw_shape, dst_shape, keep_ratio):
    """
    Get resize matrix for resizing raw img to input size
    :param raw_shape: (width, height) of raw image
    :param dst_shape: (width, height) of input image
    :param keep_ratio: whether keep original ratio
    :return: 3x3 Matrix
    """
    r_w, r_h = raw_shape
    d_w, d_h = dst_shape
    Rs = np.eye(3)
    if keep_ratio:
        C = np.eye(3)
        C[0, 2] = - r_w / 2
        C[1, 2] = - r_h / 2

        if r_w / r_h < d_w / d_h:
            ratio = d_h / r_h
        else:
            ratio = d_w / r_w
        Rs[0, 0] *= ratio
        Rs[1, 1] *= ratio

        T = np.eye(3)
        T[0, 2] = 0.5 * d_w
        T[1, 2] = 0.5 * d_h
        return T @ Rs @ C
    else:
        Rs[0, 0] *= d_w / r_w
        Rs[1, 1] *= d_h / r_h
        return Rs


def _warp_boxes4nanodet(boxes, M, width, height):
    n = len(boxes)
    if n:
        # warp points
        xy = np.ones((n * 4, 3))
        xy[:, :2] = boxes[:, [0, 1, 2, 3, 0, 3, 2, 1]].reshape(n * 4, 2)  # x1y1, x2y2, x1y2, x2y1
        xy = xy @ M.T  # transform
        xy = (xy[:, :2] / xy[:, 2:3]).reshape(n, 8)  # rescale
        # create new boxes
        x = xy[:, [0, 2, 4, 6]]
        y = xy[:, [1, 3, 5, 7]]
        xy = np.concatenate((x.min(1), y.min(1), x.max(1), y.max(1))).reshape(4, n).T
        # clip boxes
        xy[:, [0, 2]] = xy[:, [0, 2]].clip(0, width)
        xy[:, [1, 3]] = xy[:, [1, 3]].clip(0, height)
        return xy.astype(np.float32)
    else:
        return boxes


def data_heighten4nanodet(img_np, target, dst_shape, keep_ratio=True):
    h_src, w_src = img_np.shape[:2]  # shape(h,w,c)

    # center
    C = np.eye(3)
    C[0, 2] = - w_src / 2
    C[1, 2] = - h_src / 2

    # do not change the order of mat mul
    if random.randint(0, 1):
        # 随机透视0.0
        P = _perspective_matrix4nanodet()
        C = P @ C
    if random.uniform(0, 1) > 0.5:
        # 缩放[0.6, 1.4]
        Scl = _scale_matrix4nanodet([0.6, 1.4])
        C = Scl @ C
    if random.randint(0, 1):
        # 拉伸[[1, 1], [1, 1]]
        Str = _stretch_matrix4nanodet(width_ratio=(1, 1), height_ratio=(1, 1))
        C = Str @ C
    if random.randint(0, 1):
        # 旋转没用
        R = _rotation_matrix4nanodet(degree=0)
        C = R @ C
    if random.randint(0, 1):
        # 切变没用
        Sh = _shear_matrix4nanodet(degree=0)
        C = Sh @ C
    if random.randint(0, 1):
        # 翻转0.5
        F = _flip_matrix4nanodet(prob=1.0)
        C = F @ C
    if random.randint(0, 1):
        # 随机移动
        T = _translate_matrix4nanodet(0.5, w_src, h_src)
    else:
        T = _translate_matrix4nanodet(0, w_src, h_src)
    M = T @ C
    # M = T @ Sh @ R @ Str @ P @ C
    ResizeM = _resize_matrix4nanodet((w_src, h_src), dst_shape, keep_ratio)
    M = ResizeM @ M
    img_np_new = cv2.warpPerspective(img_np, M, dsize=tuple(dst_shape))
    target['warp_matrix'] = M
    if 'boxes' in target:
        boxes = target['boxes']
        target['boxes'] = _warp_boxes4nanodet(boxes, M, dst_shape[0], dst_shape[1])
    if 'gt_masks' in target:
        for i, mask in enumerate(target['gt_masks']):
            target['gt_masks'][i] = cv2.warpPerspective(mask, M, dsize=tuple(dst_shape))

    return img_np_new


def filter_box4yolox(box1, box2, wh_thr=2, ar_thr=20, area_thr=0.2):
    # box1(4,n), box2(4,n)
    # Compute candidate boxes which include follwing 5 things:
    # box1 before augment, box2 after augment, wh_thr (pixels), aspect_ratio_thr, area_ratio
    w1, h1 = box1[2] - box1[0], box1[3] - box1[1]
    w2, h2 = box2[2] - box2[0], box2[3] - box2[1]
    ar = np.maximum(w2 / (h2 + 1e-16), h2 / (w2 + 1e-16))  # aspect ratio
    return (
            (w2 > wh_thr)
            & (h2 > wh_thr)
            & (w2 * h2 / (w1 * h1 + 1e-16) > area_thr)
            & (ar < ar_thr)
    )  # candidates


def data_heighten4yolox(img, target, degrees=10, translate=0.1,
                        scale=(0.5, 1.5), shear=10, perspective=0.0,
                        border=(0, 0),
                        ):
    if 'boxes' in target:
        g_ltrb_mosaic = target['boxes']

        height = img.shape[0] + border[0] * 2  # shape(h,w,c)
        width = img.shape[1] + border[1] * 2

        # Center
        C = np.eye(3)
        C[0, 2] = -img.shape[1] / 2  # x translation (pixels)
        C[1, 2] = -img.shape[0] / 2  # y translation (pixels)

        # Rotation and Scale 旋转及缩放
        R = np.eye(3)
        a = random.uniform(-degrees, degrees)
        # a += random.choice([-180, -90, 0, 90])  # add 90deg rotations to small rotations
        s = random.uniform(scale[0], scale[1])
        # s = 2 ** random.uniform(-scale, scale)
        R[:2] = cv2.getRotationMatrix2D(angle=a, center=(0, 0), scale=s)

        # Shear 剪切
        S = np.eye(3)
        S[0, 1] = math.tan(random.uniform(-shear, shear) * math.pi / 180)  # x shear (deg)
        S[1, 0] = math.tan(random.uniform(-shear, shear) * math.pi / 180)  # y shear (deg)

        # Translation 平移
        T = np.eye(3)
        T[0, 2] = (random.uniform(0.5 - translate, 0.5 + translate) * width)  # x translation (pixels)
        T[1, 2] = (random.uniform(0.5 - translate, 0.5 + translate) * height)  # y translation (pixels)

        # Combined rotation matrix
        M = T @ S @ R @ C  # order of operations (right to left) is IMPORTANT

        ###########################
        # For Aug out of Mosaic
        # s = 1.
        # M = np.eye(3)
        ###########################

        if (border[0] != 0) or (border[1] != 0) or (M != np.eye(3)).any():  # image changed
            if perspective:
                img = cv2.warpPerspective(img, M, dsize=(width, height), borderValue=(128, 128, 128))
            else:  # affine
                img = cv2.warpAffine(img, M[:2], dsize=(width, height), borderValue=(128, 128, 128))

        # Transform label coordinates
        n = len(g_ltrb_mosaic)
        if n:
            # warp points
            xy = np.ones((n * 4, 3))
            xy[:, :2] = g_ltrb_mosaic[:, [0, 1, 2, 3, 0, 3, 2, 1]].reshape(n * 4, 2)  # x1y1, x2y2, x1y2, x2y1
            xy = xy @ M.T  # transform
            if perspective:
                xy = (xy[:, :2] / xy[:, 2:3]).reshape(n, 8)  # rescale
            else:  # affine
                xy = xy[:, :2].reshape(n, 8)

            # create new boxes
            x = xy[:, [0, 2, 4, 6]]
            y = xy[:, [1, 3, 5, 7]]
            xy = np.concatenate((x.min(1), y.min(1), x.max(1), y.max(1))).reshape(4, n).T

            # clip boxes
            xy[:, [0, 2]] = xy[:, [0, 2]].clip(0, width)
            xy[:, [1, 3]] = xy[:, [1, 3]].clip(0, height)

            # filter candidates
            i = filter_box4yolox(box1=g_ltrb_mosaic[:, :4].T * s, box2=xy.T)
            # g_ltrb_mosaic = g_ltrb_mosaic[i]
            # g_ltrb_mosaic[:, :4] = xy[i]
            target['boxes'] = xy[i]
            target['labels'] = target['labels'][i]
    else:
        raise Exception('boxes 为空')
    return img, target


if __name__ == '__main__':
    file_img = r'/_test_pic/test_99.jpg'  # 650 466
    img_np = cv2.imread(file_img)  # 这个打开是hwc bgr
    img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
    target = {}
    img_np_new = data_heighten4nanodet(img_np, target, dst_shape=(320, 320))
    plt.imshow(img_np_new)
    plt.show()
    # img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
    pass
