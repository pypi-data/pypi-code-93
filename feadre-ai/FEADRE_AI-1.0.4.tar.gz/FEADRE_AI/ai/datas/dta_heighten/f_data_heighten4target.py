import math
import os

import torch
import cv2
import numpy as np
from numpy import random

from ftools.GLOBAL_LOG import flog
from ftools.ai.object_detection.boxes.f_boxes import ltwh2ltrb, fverify_bbox
from ftools.ai.datas.dataset_coco import CustomCocoDataset
from ftools.ai.object_detection.boxes.f_kps import fcre_kps_min_bbox, fverify_kps, fsplit_kps
from ftools.ai.picture.f_size_handler import resize_np_keep
from ftools.ai.picture.f_show import f_show_od_np4plt_v3, f_show_kp_np4cv, f_show_od_np4cv
from ftools.ai.datas.z_dataloader import KEYPOINTS_Mirror


def ftransform_nanodet_train(size_wh_input):
    return FCompose([
        Uint2Float32_np(),
        FResizeKeep(size_wh_input),
        RandomBrightness(50),
        RandomContrast(lower=0.8, upper=1.2),
        ConvertColor(current='BGR', transform='HSV'),  # bgr -> hsv
        RandomSaturation(lower=0.8, upper=1.2),  # 随机色彩'
        ConvertColor(current='HSV', transform='BGR'),  # hsv -> bgr
        FRandomMirror(),
        Normalize_v2(),
        to_tensor_target2one(is_box_oned=False),
    ])


def ftransform_nanodet_test(size_wh_input):
    return FCompose([
        FResizeKeep(size_wh_input),
        Normalize_v2(),
        to_tensor_target2one(is_box_oned=False),
    ])


# -----------------------------------------------------------
def ftransform_yolox_train4mosaic(size_wh_input):
    return FCompose([
        Uint2Float32_np(),
        RandomContrast_v2(),
        ConvertColor(current='BGR', transform='HSV'),
        FRandomHSV(),
        RandomSaturation(),
        ConvertColor(current='HSV', transform='BGR'),
        FRandomMirror(),
        Normalize_v2(),
        ConvertColor(current='BGR', transform='RGB'),
        to_tensor_target2one(is_box_oned=False),
    ])


def ftransform_yolox_train(size_wh_input):
    return FCompose([
        Uint2Float32_np(),
        RandomContrast_v2(),
        ConvertColor(current='BGR', transform='HSV'),
        FRandomHSV(),
        RandomSaturation(),
        ConvertColor(current='HSV', transform='BGR'),
        FRandomMirror(),
        FResizeKeep(size_wh_input, fill_color=(128, 128, 128)),
        Normalize_v2(),
        ConvertColor(current='BGR', transform='RGB'),
        to_tensor_target2one(is_box_oned=False),
    ])


def ftransform_yolox_test(size_wh_input):
    return FCompose([
        FResizeKeep(size_wh_input, fill_color=(128, 128, 128)),
        Normalize_v2(),
        ConvertColor(current='BGR', transform='RGB'),
        to_tensor_target2one(is_box_oned=False),
    ])


# -----------------------------------------------------------
def ftransform_ssd_train(size_wh_input, is_multi_scale=None, multi_scale_val=None):
    return FCompose([
        Uint2Float32_np(),  # image int8转换成float [0,256)
        # --------------- 图形整体 ------------
        PhotometricDistort(),
        # --------------- 变换 ------------
        FExpand(),  # 放大缩小图片 只会缩小
        FRandomSampleCrop(),  # 随机剪切定位 keypoints 只会放大
        FRandomMirror(),  # 水平镜像
        FResize(size_wh_input, is_multi_scale, multi_scale_val),

        # --------------- 后处理 ------------
        Normalize(),
        ConvertColor(current='BGR', transform='RGB'),
        to_tensor_target2one(is_box_oned=False),
    ])


def ftransform_cpm_train(size_wh_input, is_multi_scale=None, multi_scale_val=None):
    return FCompose([
        FRandomRotate(40),
        FRandomSampleCrop(),
        FRandomMirror(KEYPOINTS_Mirror['lsp']),
        FResize(size_wh_input, is_multi_scale, multi_scale_val),
        Normalize(),
        ConvertColor(current='BGR', transform='RGB'),
        to_tensor_target2one(is_box_oned=False),
    ])


def ftransform_ssd_test(size_wh_input, is_multi_scale=None, multi_scale_val=None):
    return FCompose([
        FResize(size_wh_input, is_multi_scale, multi_scale_val),
        Normalize(),
        ConvertColor(current='BGR', transform='RGB'),
        to_tensor_target2one(is_box_oned=False),
    ])


''' ------------------ 以上是套装 ----------------------  '''


def _copy_box(boxes):
    if isinstance(boxes, np.ndarray):
        boxes_ = boxes.copy()
    elif isinstance(boxes, torch.Tensor):
        boxes_ = boxes.clone()
    else:
        raise Exception('类型错误', type(boxes))

    return boxes_


def intersect(box_a, box_b):
    max_xy = np.minimum(box_a[:, 2:], box_b[2:])
    min_xy = np.maximum(box_a[:, :2], box_b[:2])
    inter = np.clip((max_xy - min_xy), a_min=0, a_max=np.inf)
    return inter[:, 0] * inter[:, 1]


def jaccard_numpy(box_a, box_b):
    """Compute the jaccard overlap of two sets of boxes.  The jaccard overlap
    is simply the intersection over union of two boxes.
    E.g.:
        A ∩ B / A ∪ B = A ∩ B / (area(A) + area(B) - A ∩ B)
    Args:
        box_a: Multiple bounding boxes, Shape: [num_boxes,4]
        box_b: Single bounding box, Shape: [4]
    Return:
        jaccard overlap: Shape: [box_a.shape[0], box_a.shape[1]]
    """
    inter = intersect(box_a, box_b)
    area_a = ((box_a[:, 2] - box_a[:, 0]) *
              (box_a[:, 3] - box_a[:, 1]))  # [A,B]
    area_b = ((box_b[2] - box_b[0]) *
              (box_b[3] - box_b[1]))  # [A,B]
    union = area_a + area_b - inter
    return inter / union  # [A,B]


class FCompose:

    def __init__(self, transforms):
        super(FCompose, self).__init__()
        self.transforms = transforms

    def __call__(self, img, target={}):
        # f_plt_show_cv(image,boxes)
        for t in self.transforms:
            img, target = t(img, target)
            if target is not None:
                if 'boxes' in target and 'labels' in target:
                    if len(target['boxes']) != len(target['labels']):
                        flog.warning('!!! 数据有问题 Compose  %s %s %s ', len(target['boxes']), len(target['labels']), t)
        return img, target


class Uint2Float32_np(object):
    ''' 在处理开始时使用 '''

    def __call__(self, image, target):
        ''' cv打开的np 默认是uint8 '''
        return image.astype(np.float32), target


class ts2img_np_bgr(object):
    def __call__(self, tensor, target):
        return tensor.cpu().numpy().astype(np.float32).transpose((1, 2, 0)), target


# --------------- 图形整体 ------------

class FRandomNoise:
    '''
    随机噪声 噪点
    :param image:
    :param threshold:
    :return:
    '''

    def __init__(self, threshold=32) -> None:
        super().__init__()
        self.threshold = threshold

    def __call__(self, img_np, target):
        if random.randint(2):
            noise = np.random.uniform(low=-1, high=1, size=img_np.shape)
            img_np = img_np + noise * self.threshold
            img_np = np.clip(img_np, 0, 255)

        return img_np, target


class Ffilter_gaussian:
    '''
    高斯滤波器是根据高斯函数的形状来选择权值的线性平滑滤波器，滤波器符合二维高斯分布
    模糊
    :param image:
    :param threshold:
    :return:
    '''

    def __init__(self, k_size=5) -> None:
        super().__init__()
        self.k_size = k_size

    def __call__(self, img_np, target):
        if random.randint(2):
            img_np = cv2.GaussianBlur(img_np, (self.k_size, self.k_size), 3)
        return img_np, target


class Fgamma_transform:
    '''
    Gamma变换就是用来图像增强，通过非线性变换提升了暗部细节
    :param image:
    :param threshold:
    :return:
    '''

    def __init__(self, gamma=1.6) -> None:
        super().__init__()
        self.gamma = gamma

    def __call__(self, img_np, target):
        if random.randint(2):
            max_value = np.max(img_np)
            min_value = np.min(img_np)
            value_l = max_value - min_value
            img_np = (img_np - min_value) / value_l
            img_np = np.power(img_np, self.gamma)
            img_np = img_np * 255
        return img_np, target


class RandomSaturation(object):
    '''随机色彩 需要HSV'''

    def __init__(self, lower=0.5, upper=1.5):
        self.lower = lower
        self.upper = upper
        assert self.upper >= self.lower, "contrast upper must be >= lower."
        assert self.lower >= 0, "contrast lower must be non-negative."

    def __call__(self, image, target):
        if random.randint(2):
            image[:, :, 1] *= random.uniform(self.lower, self.upper)
        return image, target


class FRandomHSV:
    '''随机色彩 需要HSV'''

    def __init__(self, lower=0.5, upper=1.5):
        self.lower = lower
        self.upper = upper

    def __call__(self, image, target):
        if random.randint(2):
            tmp = image[:, :, 0].astype(int) + random.randint(-18, 18)
            tmp %= 180
            image[:, :, 0] = tmp

        return image, target


class RandomHue(object):
    def __init__(self, delta=18.0):
        assert delta >= 0.0 and delta <= 360.0
        self.delta = delta

    def __call__(self, image, target):
        if random.randint(2):
            image[:, :, 0] += random.uniform(-self.delta, self.delta)
            image[:, :, 0][image[:, :, 0] > 360.0] -= 360.0
            image[:, :, 0][image[:, :, 0] < 0.0] += 360.0
        return image, target


class RandomContrast(object):
    '''随机透明度'''

    def __init__(self, lower=0.5, upper=1.5):
        self.lower = lower
        self.upper = upper
        assert self.upper >= self.lower, "contrast upper must be >= lower."
        assert self.lower >= 0, "contrast lower must be non-negative."

    # expects float image
    def __call__(self, image, target):
        if random.randint(2):  # 50%
            alpha = random.uniform(self.lower, self.upper)
            image *= alpha
            np.clip(image, a_min=0, a_max=255, out=image)
        # f_plt_show_cv(image)
        return image, target


class RandomContrast_v2():
    '''随机透明度'''

    def __init__(self):
        pass

    # expects float image
    def __call__(self, image, target):
        if random.randint(2):
            self._convert(image, beta=random.uniform(-32, 32))
        if random.randint(2):
            self._convert(image, beta=random.uniform(0.5, 1.5))
        # f_plt_show_cv(image)
        return image, target

    def _convert(self, image, alpha=1, beta=0):
        image = image.astype(float) * alpha + beta
        np.clip(image, a_min=0, a_max=255, out=image)
        return image


class RandomGray:
    '''随机灰度'''

    def __call__(self, image, target):
        if random.random() > 0.9:
            _img = np.zeros(image.shape, dtype=np.uint8)
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            _img[:, :, 0] = gray
            _img[:, :, 1] = gray
            _img[:, :, 2] = gray
            image = _img

        return image, target


class RandomBrightness(object):
    def __init__(self, delta=32):
        assert delta >= 0.0
        assert delta <= 255.0
        self.delta = delta

    def __call__(self, image, target):
        '''随机亮度增强'''
        if random.randint(2):  # 50%
            delta = random.uniform(-self.delta, self.delta)
            image += delta
        # f_plt_show_cv(image)
        return image, target


# --------------- 变换 ------------
class FRandomRotate:
    '''
    有框不能用旋转
    '''

    def __init__(self, max_degree=20):
        self.max_degree = max_degree

    def __call__(self, img_np, target):
        degree = random.uniform(-self.max_degree, self.max_degree)
        img_h, img_w, c = img_np.shape
        cx, cy = img_w / 2.0, img_h / 2.0

        ''' 图片处理 '''
        # mat rotate 1 center 2 angle 3 缩放系数 (2, 3)
        rotate_matrix = cv2.getRotationMatrix2D((cx, cy), degree, 1.0)
        img_np = cv2.warpAffine(img_np, rotate_matrix, (img_w, img_h),
                                borderValue=(128, 128, 128))
        # debug
        # f_show_od_np4cv(img_np)

        if 'boxes' in target:
            boxes_new = []
            boxes_ltrb = target['boxes']
            for bbox in boxes_ltrb:
                a = rotate_matrix[:, :2]  # a.shape (2,2)
                b = rotate_matrix[:, 2:]  # b.shape(2,1)
                b = np.reshape(b, newshape=(1, 2))
                a = np.transpose(a)

                [left, up, right, down] = bbox
                corner_point = np.array([[left, up], [right, up], [left, down], [right, down]])
                corner_point = np.dot(corner_point, a) + b
                min_left = np.min(corner_point[:, 0])
                min_up = np.min(corner_point[:, 1])
                max_right = np.max(corner_point[:, 0])
                max_down = np.max(corner_point[:, 1])
                boxes_new.append(np.array([min_left, min_up, max_right, max_down]))
            target['boxes'] = np.stack(boxes_new, 0)
            np.clip(target['boxes'][:, ::2], a_min=0, a_max=img_w, out=target['boxes'][:, ::2])
            np.clip(target['boxes'][:, 1::2], a_min=0, a_max=img_h, out=target['boxes'][:, 1::2])

            mask_pos = fverify_bbox(target['boxes'])
            target['boxes'] = target['boxes'][mask_pos]
            if 'labels' in target:
                target['labels'] = target['labels'][mask_pos]

        if 'kps' in target:
            kps = target['kps'].reshape(target['kps'].shape[0], -1, 3)
            for i, kp in enumerate(kps):
                for j, xyt in enumerate(kp):
                    if xyt[2] == 0:
                        continue
                    p = np.array([xyt[0], xyt[1], 1])
                    p = rotate_matrix.dot(p)

                    # 越界判断
                    if p[0] > img_w or p[0] < 0 or p[1] > img_h or p[1] < 0:
                        xyt[2] = 0

                    xyt[0] = p[0]
                    xyt[1] = p[1]
                    kps[i, j] = xyt

            # 共享内存不用赋值
            # target['kps'] = kps.reshape(target['kps'].shape[0], -1)
            # debug
            # f_show_kp_np4cv(img_np, kps=target['kps'],
            #                 kps_seq=kps_seq)
        return img_np, target


class FExpand:
    '''随机 缩小放在图片中某处  其它部份为黑色'''

    def __init__(self, mean=(128, 128, 128), num_keypoints=None):
        ''' 均值用于扩展边界 '''
        self.mean = mean  # 这个用于背景
        self.num_keypoints = num_keypoints

    def __call__(self, image, target):
        if random.randint(2):
            return image, target

        height, width, depth = image.shape
        ratio = random.uniform(1, 3)  # 缩小 1~4的一个比例  这个必须大于1 只能缩小
        left = random.uniform(0, width * ratio - width)
        top = random.uniform(0, height * ratio - height)

        expand_image = np.zeros(
            (int(height * ratio), int(width * ratio), depth),
            dtype=image.dtype)
        expand_image[:, :, :] = self.mean
        expand_image[int(top):int(top + height), int(left):int(left + width)] = image
        image = expand_image

        if target is None:
            return image, target

        # 这个只缩小不存在越界问题
        if 'boxes' in target:
            # 原尺寸不要了
            boxes = target['boxes']
            if isinstance(boxes, np.ndarray):
                boxes[:, :2] += (int(left), int(top))  # lt
                boxes[:, 2:] += (int(left), int(top))  # rb
            elif isinstance(boxes, torch.Tensor):
                boxes[:, :2] += torch.tensor((int(left), int(top)))
                boxes[:, 2:] += torch.tensor((int(left), int(top)))
            else:
                raise Exception('target[boxes]类型错误', type(boxes))

        if 'kps' in target:
            _kps, mask = fsplit_kps(target['kps'])
            _kps[..., :2] += (int(left), int(top))

        # f_plt_show_cv(image,torch.tensor(boxes))
        return image, target


class FRandomSampleCrop:
    """
    随机Crop
    """

    def __init__(self, num_keypoints=None):
        # 随机源
        self.sample_options = (
            # using entire original input image
            None,
            # sample a patch s.t. MIN jaccard w/ obj in .1,.3,.4,.7,.9
            (0.1, None),
            (0.3, None),
            (0.7, None),
            (0.9, None),
            # randomly sample a patch
            (None, None),
        )
        self.num_keypoints = num_keypoints

    def __call__(self, image, target):
        height, width, _ = image.shape
        # bbox = fcre_kps_min_bbox(target['kps'])
        # f_show_kp_np4cv(image,
        #                 kps=target['kps'],
        #                 kps_seq=target['kps_seq'],
        #                 g_ltrb=bbox,
        #                 )
        while True:
            # randomly choose a mode
            mode = random.choice(self.sample_options)
            if mode is None:
                return image, target

            min_iou, max_iou = mode
            if min_iou is None:
                min_iou = float('-inf')
            if max_iou is None:
                max_iou = float('inf')

            # max trails (50) 找一个 iou在范围内 且 保留BOX中心的剪切
            for _ in range(50):

                w = random.uniform(0.3 * width, width)
                h = random.uniform(0.3 * height, height)

                # aspect ratio constraint b/t .5 & 2
                if h / w < 0.5 or h / w > 2:
                    continue

                left = random.uniform(width - w)
                top = random.uniform(height - h)

                # convert to integer rect x1,y1,x2,y2
                rect = np.array([int(left), int(top), int(left + w), int(top + h)])

                # calculate IoU (jaccard overlap) b/t the cropped and gt boxes
                if 'boxes' in target:
                    bbox = target['boxes']
                    overlap = jaccard_numpy(bbox, rect)
                elif 'kps' in target:
                    # 外接框
                    bbox = fcre_kps_min_bbox(target['kps'])
                    overlap = jaccard_numpy(bbox, rect)
                else:
                    raise Exception('boxes 和 kps 不存在,无法使用 FRandomSampleCrop')

                # is min and max overlap constraint satisfied? if not try again
                if len(overlap) == 0 or (overlap.min() < min_iou and max_iou < overlap.max()):
                    continue

                # 只保留中心点在剪切框内的 cut the crop from the image
                img_new = image[rect[1]:rect[3], rect[0]:rect[2], :]

                # keep overlap with gt box IF center in sampled patch
                centers = (bbox[:, :2] + bbox[:, 2:]) / 2.0
                # --- 是否切到box 需修正
                # mask in all gt boxes that above and to the left of centers
                m1 = (rect[0] < centers[:, 0]) * (rect[1] < centers[:, 1])
                # mask in all gt boxes that under and to the right of centers
                m2 = (rect[2] > centers[:, 0]) * (rect[3] > centers[:, 1])
                # mask in that both m1 and m2 are true
                mask = m1 * m2

                #  have any valid boxes? try again if not
                if not mask.any():  # 一个都没有
                    continue

                # 关键点需要直接修复
                if 'kps' in target:
                    target['kps'] = fverify_kps(target['kps'], rect)
                    # 共享内存
                    _kps, _mask = fsplit_kps(target['kps'])
                    _kps[:, :, :2] = _kps[:, :, :2] - rect[:2][None, None, :]
                    # raise Exception('暂不支持')

                # take only matching gt labels
                if 'boxes' in target:
                    # 取出要修复的
                    current_boxes = bbox[mask, :]
                    # should we use the box left and top corner or the crop's
                    current_boxes[:, :2] = np.maximum(current_boxes[:, :2], rect[:2])
                    # adjust to crop (by substracting crop's left,top)
                    current_boxes[:, :2] -= rect[:2]

                    current_boxes[:, 2:] = np.minimum(current_boxes[:, 2:], rect[2:])
                    # adjust to crop (by substracting crop's left,top)
                    current_boxes[:, 2:] -= rect[:2]

                    target['boxes'] = current_boxes

                    # 校验有效性
                    mask_pos = fverify_bbox(target['boxes'])
                    target['boxes'] = target['boxes'][mask_pos]
                    if 'labels' in target:
                        target['labels'] = target['labels'][mask][mask_pos]

                    # debug
                    # f_show_od_np4cv(img_new, current_boxes)

                # debug
                # f_show_kp_np4cv(img_new,
                #                 kps=target['kps'],
                #                 kps_seq=None,
                #                 g_ltrb=target['boxes'],
                #                 is_color_same=True,
                #                 )
                return img_new, target


class FRandomMirror:
    '''随机水平镜像'''

    def __init__(self, rules_flip=None) -> None:
        super().__init__()
        self.rules_flip = rules_flip

    def __call__(self, image, target):
        _, width, _ = image.shape
        if random.randint(2):
            # flog.debug('FRandomMirror %s', )
            image = image[:, ::-1]
            # boxes = boxes.copy()

            if target is None:
                return image, target

            if 'boxes' in target:
                target['boxes'][:, [0, 2]] = width - target['boxes'][:, [2, 0]]

            if 'kps' in target:
                ''' 这个需要订制一个翻转规则  '''
                assert self.rules_flip is not None, 'RandomMirror keypoints 不支持 需传入 rules_flip '
                # 批量修改x值 y不变
                target['kps'][:, ::3] = width - target['kps'][:, ::3]

                _kps, mask = fsplit_kps(target['kps'])

                for xyt in _kps:
                    # 改变 kk可以改变 target['kps'] 共享内存
                    for s, d in self.rules_flip:
                        _t = xyt[s].copy()
                        xyt[s] = xyt[d]
                        xyt[d] = _t
                    pass
                # 共享内存直接调整 无需这个
                # target['kps'] = kks.reshape(n, -1)

            # target['kps'].view(-1,2).flip(0)

        return image, target


class FResizeKeep:
    def __init__(self, size_wh_new, fill_color=(128, 128, 128)):
        '''

        '''
        self.size_wh_new = size_wh_new
        self.fill_color = fill_color

    def __call__(self, img_np, target):
        img_np, ratio, hw, (left, top, right, bottom) = resize_np_keep(
            img_np,
            self.size_wh_new,
            mode='center',
            # mode='lt',
            fill_color=self.fill_color,
        )

        # debug
        # import matplotlib.pyplot as plt
        # plt.imshow(img_np)
        # plt.show()

        if target is not None:
            if 'boxes' in target:
                target['boxes'][:, [0, 2]] = target['boxes'][:, [0, 2]] * ratio
                target['boxes'][:, [1, 3]] = target['boxes'][:, [1, 3]] * ratio
                # target['boxes'] += np.array((left, top, right, bottom), dtype=np.float32)
                target['boxes'] += np.array((left, top, left, top), dtype=np.float32)
            if 'kps' in target:
                # 保持第三维不变
                num_keypoints = target['kps'].shape[1] // 3
                target['kps'] = target['kps'] \
                                * np.tile(np.array([ratio] * 2 + [1])[None, :], (1, num_keypoints))
                target['kps'] += np.tile(np.array([left, top, 0])[None, :], (1, num_keypoints))
                # debug
                # f_show_kp_np4cv(img_np, kps=target['kps'],
                #                 kps_seq=target['kps_seq'])

            # 修正偏移
            target['off_ltrb'] = (left, top, right, bottom)

        return img_np, target


class FResize:
    def __init__(self, size_wh=None, is_multi_scale=False, multi_scale_val=(800, 1333)):
        '''
        直接拉伸和 多尺度
        '''
        self.size_wh = size_wh
        self.is_multi_scale = is_multi_scale
        self.multi_scale_val = multi_scale_val

    def __call__(self, img_np, target):
        if self.is_multi_scale:
            min_side, max_side = self.multi_scale_val
            h, w, _ = img_np.shape
            smallest_side = min(w, h)
            largest_side = max(w, h)
            scale = min_side / smallest_side
            if largest_side * scale > max_side:
                scale = max_side / largest_side
            nw, nh = int(scale * w), int(scale * h)
            image_resized = cv2.resize(img_np, (nw, nh))

            if target is not None:
                target['toone'] = image_resized.shape[:2][::-1]
            pad_w = 32 - nw % 32
            pad_h = 32 - nh % 32
            # 右下加上pad 不影响targets
            image_res = np.zeros(shape=[nh + pad_h, nw + pad_w, 3], dtype=np.uint8)
            image_res[:nh, :nw, :] = image_resized

            scale_w = scale
            scale_h = scale
        else:
            assert self.size_wh is not None
            size_wh_z = self.size_wh
            w_ratio, h_ratio = np.array(img_np.shape[:2][::-1]) / np.array(size_wh_z)

            image_res = cv2.resize(img_np, (size_wh_z[0], size_wh_z[1]))

            scale_w = 1 / w_ratio
            scale_h = 1 / h_ratio

        if target is not None:
            if 'boxes' in target:
                target['boxes'][:, [0, 2]] = target['boxes'][:, [0, 2]] * scale_w
                target['boxes'][:, [1, 3]] = target['boxes'][:, [1, 3]] * scale_h
            if 'kps' in target:
                # 保持第三维不变
                num_keypoints = target['kps'].shape[1] // 3
                target['kps'] = target['kps'] \
                                * np.tile(np.array([scale_w, scale_h, 1])[None, :], (1, num_keypoints))
                # # debug
                # f_show_kp_np4cv(image_res, kps=target['kps'],
                #                 kps_seq=kps_seq)

        return image_res, target


# --------------- 后处理 ------------
class Normalize:
    # def __init__(self, mean=(0.406, 0.456, 0.485), std=(0.225, 0.224, 0.229)):
    def __init__(self, mean=(128.0, 128.0, 128.0), std=(256.0, 256.0, 256.0)):
        self.mean = np.array(mean, dtype=np.float32)
        self.std = np.array(std, dtype=np.float32)

    def __call__(self, image, target):
        ''' -0.5 ~ 0.5 '''
        # bgr
        # f_show_pic_np4plt(image)

        # (928, 1216, 3)
        image = image.astype(np.float32).clip(0.0, 255.)
        # image /= 255.
        image -= self.mean.reshape(1, 1, -1)
        image /= self.std

        if image.max() > 0.5 or image.min() < -0.5:
            raise Exception('图片有问题 mean = %s ,std = %s, max=%s,min=%s'
                            % (str(self.mean), str(self.std), image.max(), image.min()))

        # f_show_pic_np4plt(image)
        # image = f_recover_normalization4np(image)
        # f_show_pic_np4plt(image)

        return image, target


class Normalize_v2:
    def __init__(self, mean_bgr=(103.53, 116.28, 123.675), std_bgr=(57.375, 57.12, 58.395), is_tooned=False):
        '''

        mean_bgr = (103.53, 116.28, 123.675)
        mean_bgr_one = (103.53, 116.28, 123.675)
        std_bgr = (0.406, 0.456, 0.485)
        std_bgr_one = (0.225, 0.224, 0.229)

        :param mean_bgr:
        :param std_bgr:
        :param is_tooned:
        '''
        self.mean = np.array(mean_bgr, dtype=np.float32)
        self.std = np.array(std_bgr, dtype=np.float32)
        self.is_tooned = is_tooned

    def __call__(self, image, target):
        # f_show_od_np4plt_v3(image, target['boxes'],
        #                     is_recover_size=False
        #                     )

        img = image.astype(np.float32) / 255
        if self.is_tooned:
            mean = np.array(self.mean, dtype=np.float32).reshape(1, 1, 3)
            std = np.array(self.std, dtype=np.float32).reshape(1, 1, 3)
        else:
            # 维度匹配
            mean = np.array(self.mean, dtype=np.float32).reshape(1, 1, 3) / 255
            std = np.array(self.std, dtype=np.float32).reshape(1, 1, 3) / 255
        img = (img - mean) / std

        return img, target


class ConvertColor:
    '''bgr -> hsv'''

    def __init__(self, current='BGR', transform='HSV'):
        self.transform = transform
        self.current = current

    def __call__(self, image, target):
        # plt.imshow(image)
        # plt.show()
        if self.current == 'BGR' and self.transform == 'HSV':
            image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        elif self.current == 'HSV' and self.transform == 'BGR':
            image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
        elif self.current == 'BGR' and self.transform == 'RGB':
            # image = image[:, :, ::-1]
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            raise NotImplementedError
        return image, target


class to_tensor_target2one:
    def __init__(self, is_box_oned=False) -> None:
        super().__init__()
        self.is_box_oned = is_box_oned

    def __call__(self, cvimage, target):
        if target is not None and self.is_box_oned:
            # np整体复制 wh
            whwh = np.tile(cvimage.shape[:2][::-1], 2)
            if 'boxes' in target:
                target['boxes'][:, :] = target['boxes'][:, :] / whwh

            if 'kps' in target:
                target['kps'][:, ::3] /= whwh[0]
                target['kps'][:, 1::3] /= whwh[1]

        # (h,w,c -> c,h,w) = bgr
        return torch.from_numpy(cvimage.astype(np.float32)).permute(2, 0, 1), target


# ------------------------------ 无用 --------------------------------
class Target2one:
    '''原图转归一化尺寸  ToAbsoluteCoords 相反'''

    def __call__(self, image, target):
        if target is None:
            return image, target
        whwh = np.tile(image.shape[:2][::-1], 2)
        if 'boxes' in target:
            target['boxes'][:, :] = target['boxes'][:, :] / whwh

        if 'kps' in target:
            target['kps'][:, ::3] /= whwh[0]
            target['kps'][:, 1::3] /= whwh[1]
        return image, target


class ToAbsoluteCoords:
    ''' boxes 恢复原图尺寸  归一化尺寸转原图  Target2one 相反'''

    def __call__(self, image, target):
        '''
        归一化 -> 绝对坐标
        :param image:
        :param boxes:
        :param labels:
        :return:
        '''
        if target is None:
            return image, target
        whwh = np.tile(image.shape[:2][::-1], 2)
        if 'boxes' in target:
            target['boxes'][:, :] = target['boxes'][:, :] * whwh

        if 'kps' in target:
            target['kps'][:, ::3] *= whwh[0]
            target['kps'][:, 1::3] *= whwh[1]
        return image, target


class PhotometricDistort(object):
    '''图片增强'''

    def __init__(self):
        self.pd = [
            RandomContrast(),  # 随机透明度
            ConvertColor(transform='HSV'),  # bgr -> hsv
            RandomSaturation(),  # 随机色彩'
            RandomHue(),
            ConvertColor(current='HSV', transform='BGR'),  # hsv -> bgr
            RandomContrast()  # 随机透明度
        ]
        self.rand_brightness = RandomBrightness()  # 随机亮度增强
        # self.rand_light_noise = RandomLightingNoise()  # 颜色杂音

    def __call__(self, image, target):
        im = image.copy()
        im, target = self.rand_brightness(im, target)
        if random.randint(2):  # 先转换还是后转换
            distort = FCompose(self.pd[:-1])
        else:
            distort = FCompose(self.pd[1:])
        im, target = distort(im, target)
        return im, target
    # return self.rand_light_noise(im, boxes, labels)


def f_recover_normalization4ts(img_ts, mean_bgr=(128.0, 128.0, 128.0), std_bgr=(256.0, 256.0, 256.0)):
    '''

    :param img_ts: c,h,w
    :return:
    '''
    device = img_ts.DEVICE
    # torch.Size([3, 928, 1536]) -> torch.Size([928, 1536, 3])
    # img_ts_show = img_ts.permute(1, 2, 0) # rgb -> bgr
    mean_bgr = torch.tensor(mean_bgr, device=device)[:, None, None]  # 3,1,1
    std_bgr = torch.tensor(std_bgr, device=device).unsqueeze(-1).unsqueeze(-1)
    img_ts = img_ts * std_bgr + mean_bgr
    # img_ts_show = img_ts_show.permute(2, 0, 1)# bgr -> rgb
    return img_ts


def f_recover_normalization4ts_v2(img_ts, mean_bgr=(103.53, 116.28, 123.675), std_bgr=(57.375, 57.12, 58.395)):
    '''

    :param img_ts: c,h,w
    :return:
    '''
    device = img_ts.DEVICE
    mean_bgr = (torch.tensor(mean_bgr, device=device) / 255)[:, None, None]  # 3,1,1
    std_bgr = (torch.tensor(std_bgr, device=device) / 255).unsqueeze(-1).unsqueeze(-1)
    img_ts = (img_ts * std_bgr + mean_bgr) * 255
    return img_ts


def f_recover_normalization4np(img_np_bgr, mean_bgr=(128.0, 128.0, 128.0),
                               std_bgr=(256.0, 256.0, 256.0)):
    '''

    :param img_np_bgr: c,h,w
    :return:
    '''
    mean_bgr = np.array(mean_bgr)
    std_bgr = np.array(std_bgr)
    img_np_bgr = img_np_bgr * std_bgr + mean_bgr
    return img_np_bgr


def x_random_rotation4ts(img_np, boxes_ltrb_ts, kps_3d_ts, degree=10):
    '''
    kps_ts: torch.Size([1, 5, 3])
    '''
    angle = random.uniform(-degree, degree)
    h, w, c = img_np.shape
    cx, cy = w / 2.0, h / 2.0

    ''' 图片处理 '''
    # mat rotate 1 center 2 angle 3 缩放系数
    matRotate = cv2.getRotationMatrix2D((cy, cx), angle, 1.0)
    img_np = cv2.warpAffine(img_np, matRotate, (h, w))

    # debug
    # print(angle)
    # plt.imshow(img_np)
    # plt.show()

    ''' box处理 '''
    a = -angle / 180.0 * math.pi
    # boxes = torch.from_numpy(boxes)
    new_boxes_ltrb_ts = torch.zeros_like(boxes_ltrb_ts)
    new_boxes_ltrb_ts[:, 0] = boxes_ltrb_ts[:, 1]
    new_boxes_ltrb_ts[:, 1] = boxes_ltrb_ts[:, 0]
    new_boxes_ltrb_ts[:, 2] = boxes_ltrb_ts[:, 3]
    new_boxes_ltrb_ts[:, 3] = boxes_ltrb_ts[:, 2]
    for i in range(boxes_ltrb_ts.shape[0]):
        ymin, xmin, ymax, xmax = new_boxes_ltrb_ts[i, :]
        xmin, ymin, xmax, ymax = float(xmin), float(ymin), float(xmax), float(ymax)
        x0, y0 = xmin, ymin
        x1, y1 = xmin, ymax
        x2, y2 = xmax, ymin
        x3, y3 = xmax, ymax
        z = torch.FloatTensor([[y0, x0], [y1, x1], [y2, x2], [y3, x3]])
        tp = torch.zeros_like(z)
        tp[:, 1] = (z[:, 1] - cx) * math.cos(a) - (z[:, 0] - cy) * math.sin(a) + cx
        tp[:, 0] = (z[:, 1] - cx) * math.sin(a) + (z[:, 0] - cy) * math.cos(a) + cy
        ymax, xmax = torch.max(tp, dim=0)[0]
        ymin, xmin = torch.min(tp, dim=0)[0]
        new_boxes_ltrb_ts[i] = torch.stack([ymin, xmin, ymax, xmax])
    new_boxes_ltrb_ts[:, 1::2].clamp_(min=0, max=h - 1)
    new_boxes_ltrb_ts[:, 0::2].clamp_(min=0, max=w - 1)
    boxes_ltrb_ts[:, 0] = new_boxes_ltrb_ts[:, 1]
    boxes_ltrb_ts[:, 1] = new_boxes_ltrb_ts[:, 0]
    boxes_ltrb_ts[:, 2] = new_boxes_ltrb_ts[:, 3]
    boxes_ltrb_ts[:, 3] = new_boxes_ltrb_ts[:, 2]
    # boxes_ts = boxes_ts.numpy()

    ngt, nkey, c = kps_3d_ts.shape
    for i in range(ngt):
        for j in range(nkey):
            x = kps_3d_ts[i][j][0]
            y = kps_3d_ts[i][j][1]
            p = np.array([x, y, 1])
            p = matRotate.dot(p)
            kps_3d_ts[i][j][0] = p[0]
            kps_3d_ts[i][j][1] = p[1]

    return img_np, boxes_ltrb_ts, kps_3d_ts


def x_random_rotation4np(img_np, boxes_ltrb_np, kps_3d_np, degree=10):
    angle = random.uniform(-degree, degree)
    h, w, c = img_np.shape
    cx, cy = w / 2.0, h / 2.0

    ''' 图片处理 '''
    # mat rotate 1 center 2 angle 3 缩放系数
    matRotate = cv2.getRotationMatrix2D((cy, cx), angle, 1.0)
    img_np = cv2.warpAffine(img_np, matRotate, (h, w))

    # debug
    # print(angle)
    # plt.imshow(img_np)
    # plt.show()

    ''' box处理 '''
    a = -angle / 180.0 * math.pi
    # boxes = torch.from_numpy(boxes)
    new_boxes_ltrb_np = np.zeros_like(boxes_ltrb_np)
    new_boxes_ltrb_np[:, 0] = boxes_ltrb_np[:, 1]
    new_boxes_ltrb_np[:, 1] = boxes_ltrb_np[:, 0]
    new_boxes_ltrb_np[:, 2] = boxes_ltrb_np[:, 3]
    new_boxes_ltrb_np[:, 3] = boxes_ltrb_np[:, 2]
    for i in range(boxes_ltrb_np.shape[0]):
        ymin, xmin, ymax, xmax = new_boxes_ltrb_np[i, :]
        xmin, ymin, xmax, ymax = float(xmin), float(ymin), float(xmax), float(ymax)
        x0, y0 = xmin, ymin
        x1, y1 = xmin, ymax
        x2, y2 = xmax, ymin
        x3, y3 = xmax, ymax
        z = np.array([[y0, x0], [y1, x1], [y2, x2], [y3, x3]], dtype=np.float32)
        tp = np.zeros_like(z)
        tp[:, 1] = (z[:, 1] - cx) * math.cos(a) - (z[:, 0] - cy) * math.sin(a) + cx
        tp[:, 0] = (z[:, 1] - cx) * math.sin(a) + (z[:, 0] - cy) * math.cos(a) + cy
        ymax, xmax = np.max(tp, axis=0)
        ymin, xmin = np.min(tp, axis=0)
        new_boxes_ltrb_np[i] = np.stack([ymin, xmin, ymax, xmax])

    new_boxes_ltrb_np[:, 1::2] = np.clip(new_boxes_ltrb_np[:, 0::2], a_min=0, a_max=h - 1)
    new_boxes_ltrb_np[:, 1::2] = np.clip(new_boxes_ltrb_np[:, 0::2], a_min=0, a_max=w - 1)
    boxes_ltrb_np[:, 0] = new_boxes_ltrb_np[:, 1]
    boxes_ltrb_np[:, 1] = new_boxes_ltrb_np[:, 0]
    boxes_ltrb_np[:, 2] = new_boxes_ltrb_np[:, 3]
    boxes_ltrb_np[:, 3] = new_boxes_ltrb_np[:, 2]

    ngt, nkey, c = kps_3d_np.shape
    for i in range(ngt):
        for j in range(nkey):
            x = kps_3d_np[i][j][0]
            y = kps_3d_np[i][j][1]
            p = np.array([x, y, 1])
            p = matRotate.dot(p)
            kps_3d_np[i][j][0] = p[0]
            kps_3d_np[i][j][1] = p[1]

    return img_np, boxes_ltrb_np, kps_3d_np


def t_transformer():
    from ftools.ai.datas.z_dataloader import get_data_voc2007, get_data_widerface, get_data_face5, \
        get_data_face98, get_data_lsp
    mode = 'keypoints'  # bbox segm keypoints caption

    # mode = 'bbox'  # bbox segm keypoints caption

    class CFG:
        pass

    path_host = 'M:'
    cfg = CFG()
    cfg.IS_TRAIN = True
    cfg.IS_VAL = False
    cfg.IS_TEST = True
    cfg.IS_MULTI_SCALE = False
    cfg.SIZE_WH_INPUT_TRAIN = (320, 320)
    cfg.IS_MOSAIC = False
    cfg.IS_MIXUP = False
    cfg.IS_MOSAIC_FILTER = False
    cfg.THR_WH = 5
    cfg.THR_AREA = 25
    cfg.NUM_WORKERS = 0

    transformer_train = FCompose(
        [
            # FRandomRotate(40),
            FRandomSampleCrop(),
            # FExpand(),
            # FResizeKeep(cfg.SIZE_WH_INPUT_TRAIN),
            # FResize(cfg.SIZE_WH_INPUT_TRAIN),
            # FRandomMirror(KEYPOINTS_Mirror['face5']),
            # Normalize_v2(),
            # to_tensor_target2one(is_box_oned=False),
        ])
    # get_data_widerface 数据中自带校验方法
    data_info, dataloader_train, dataloader_test = get_data_lsp(
        cfg, path_host=path_host,
        transform_train=transformer_train,
        mode_train=mode, batch_train=10)

    dataset = dataloader_train.dataset
    ids_classes = dataset.ids_classes

    # image, target = dataset[17]
    # f_show_kp_np4cv(image,
    #                 kps=target['kps'],
    #                 kps_seq=None,
    #                 g_ltrb=target['boxes'],
    #                 is_color_same=True,
    #                 )

    for i in range(0, 16):
        image, target = dataset[i]
        f_show_kp_np4cv(image,
                        g_kps_l=target['kps'],
                        kps_seq=None,
                        g_ltrb=target['boxes'],
                        is_color_same=True,
                        )


if __name__ == '__main__':
    class cfg:
        pass


    t_transformer()  # 测试 transformer

    # from nanodet.detect_pic import get_image_list
    #
    # path_pic = r'M:\AI\datas\coco2017\imgs\val2017_5000'
    # if os.path.isdir(path_pic):
    #     files_pic = get_image_list(path_pic)
    # else:
    #     files_pic = [path_pic]
    #
    # size_wh_input = (320, 320)
    # _transform_test = f_get_transform_val_base(size_wh_input)
    #
    # for file in files_pic:
    #     img_np_file = cv2.imread(file)  # h,w,c bgr
    #     h, w = img_np_file.shape[:2]
    #     size_wh_file = np.array([w, h])
    #
    #     img_ts_3d, target = _transform_test(img_np_file)
    #     f_show_od_ts4plt_v3(img_ts_3d, target['boxes'], is_normal=True, is_torgb=True)
