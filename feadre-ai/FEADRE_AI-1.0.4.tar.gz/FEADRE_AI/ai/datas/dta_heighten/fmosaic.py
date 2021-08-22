import random

import cv2
import torch
import numpy as np

from ftools.ai.object_detection.boxes.f_boxes import adjust_box_anns, fverify_bbox
from ftools.ai.datas.dta_heighten.f_data_heighten_matrix import filter_box4yolox
from ftools.ai.datas.dta_heighten.f_data_heighten_matrix import data_heighten4yolox


def get_mosaic_coordinate(mosaic_index, xc, yc, w_img, h_img, input_h, input_w):
    '''
    以 xc, yc 为固定点
    :param mosaic_index:
    :param xc:
    :param yc:
    :param w_img:
    :param h_img:
    :param input_h:
    :param input_w:
    :return:
        背景的 ltrb
        粘图的 ltrb
    '''
    # index0 to top left part of image
    if mosaic_index == 0:
        x1, y1, x2, y2 = max(xc - w_img, 0), max(yc - h_img, 0), xc, yc
        ltrb_pic = w_img - (x2 - x1), h_img - (y2 - y1), w_img, h_img
    # index1 to top right part of image
    elif mosaic_index == 1:
        x1, y1, x2, y2 = xc, max(yc - h_img, 0), min(xc + w_img, input_w * 2), yc
        ltrb_pic = 0, h_img - (y2 - y1), min(w_img, x2 - x1), h_img
    # index2 to bottom left part of image
    elif mosaic_index == 2:
        x1, y1, x2, y2 = max(xc - w_img, 0), yc, xc, min(input_h * 2, yc + h_img)
        ltrb_pic = w_img - (x2 - x1), 0, w_img, min(y2 - y1, h_img)
    # index2 to bottom right part of image
    elif mosaic_index == 3:
        x1, y1, x2, y2 = xc, yc, min(xc + w_img, input_w * 2), min(input_h * 2, yc + h_img)  # noqa
        ltrb_pic = 0, 0, min(w_img, x2 - x1), min(y2 - y1, h_img)
    # ltrb_mosaic, ltrb_pic
    else:
        raise Exception('mosaic_index = %s 越界 ' % mosaic_index)
    return (x1, y1, x2, y2), ltrb_pic


def get_mosaic_img(imgs, targets, size_hw_m=(640, 640),
                   thr_wh=5, thr_area=25, is_filter=False):
    '''

    :param id_img:
    :param size_hw_m: 输入 mosaic 的图片尺寸 mosaic尺寸为  *2
    :param is_filter: 启用框过滤过滤   thr_wh=5, thr_area=25
    :return:
    '''

    # yc, xc = s, s  # mosaic center x, y
    yc = int(random.uniform(0.5 * size_hw_m[0], 1.5 * size_hw_m[0]))
    xc = int(random.uniform(0.5 * size_hw_m[1], 1.5 * size_hw_m[1]))

    target_mosaic = {}
    size_mosaic = (size_hw_m[0] * 2, size_hw_m[1] * 2)
    # target_mosaic['image_id'] = np.array([]) # 这个训练没用
    target_mosaic['size'] = np.array(size_mosaic)
    target_mosaic['boxes'] = np.empty((0, 4))  # 创建空数组
    target_mosaic['labels'] = np.empty((0))

    for i_mosaic, (img_np, target), in enumerate(zip(imgs, targets)):
        h_img, w_img, = img_np.shape[:2]
        scale = min(1. * size_hw_m[0] / h_img, 1. * size_hw_m[1] / w_img)
        # resize 的参数是 w,h
        img_np = cv2.resize(img_np, dsize=(int(w_img * scale), int(h_img * scale)), interpolation=cv2.INTER_LINEAR)
        h_img, w_img, c = img_np.shape  # resize后的尺寸
        if i_mosaic == 0:
            img_mosaic = np.full((*size_mosaic, c), 114, dtype=np.uint8)
        ltrb_mosaic, ltrb_pic = get_mosaic_coordinate(mosaic_index=i_mosaic, xc=xc, yc=yc,
                                                      w_img=w_img, h_img=h_img,
                                                      input_h=size_hw_m[0], input_w=size_hw_m[1], )
        (l_x1, l_y1, l_x2, l_y2), (s_x1, s_y1, s_x2, s_y2) = ltrb_mosaic, ltrb_pic
        img_mosaic[l_y1:l_y2, l_x1:l_x2] = img_np[s_y1:s_y2, s_x1:s_x2]
        offw, offh = l_x1 - s_x1, l_y1 - s_y1

        # g_ltrb = target['boxes']  # 前面已处理了有效性
        if len(target['boxes']) > 0:
            target['boxes'][:, 0] = scale * target['boxes'][:, 0] + offw
            target['boxes'][:, 1] = scale * target['boxes'][:, 1] + offh
            target['boxes'][:, 2] = scale * target['boxes'][:, 2] + offw
            target['boxes'][:, 3] = scale * target['boxes'][:, 3] + offh

        target_mosaic['boxes'] = np.concatenate([target_mosaic['boxes'], target['boxes']], 0)
        target_mosaic['labels'] = np.concatenate([target_mosaic['labels'], target['labels']], 0)

    # 图内剪切
    np.clip(target_mosaic['boxes'][:, ::2], 0, 2 * size_hw_m[1], out=target_mosaic['boxes'][:, ::2])
    np.clip(target_mosaic['boxes'][:, 1::2], 0, 2 * size_hw_m[0], out=target_mosaic['boxes'][:, 1::2])

    if is_filter:
        mask = fverify_bbox(target_mosaic['boxes'], thr_wh=thr_wh, thr_area=thr_area)
        target_mosaic['boxes'] = target_mosaic['boxes'][mask]
        target_mosaic['labels'] = target_mosaic['labels'][mask]

    # 原装数据增加过滤
    img_mosaic, target_mosaic = data_heighten4yolox(img_mosaic, target_mosaic)

    return img_mosaic, target_mosaic


def mixup(img_src, target_src, img_det, target_det, size_hw_m, mixup_scale=(0.5, 1.5)):
    if isinstance(target_det['boxes'], np.ndarray):
        fun_copy = np.copy
        fun_flip = np.flip
        fun_cat = np.concatenate
    elif isinstance(target_det['boxes'], torch.Tensor):
        fun_copy = torch.clone
        fun_flip = torch.flip
        fun_cat = torch.cat
    else:
        raise Exception('输入类型错误 %s' % type(target_det['boxes']))

    jit_factor = random.uniform(*mixup_scale)
    FLIP = random.uniform(0, 1) > 0.5
    # FLIP = True

    # (640,640) 背景
    img_temp = np.ones((size_hw_m[0], size_hw_m[1], 3)) * 114.0
    h_img, w_img, = img_det.shape[:2]
    scale_ratio_det = min(1. * size_hw_m[0] / h_img, 1. * size_hw_m[1] / w_img)
    # 缩小到背景中
    resized_img = cv2.resize(img_det,
                             (int(w_img * scale_ratio_det), int(h_img * scale_ratio_det)),
                             interpolation=cv2.INTER_LINEAR)
    # 把图装到
    img_temp[: int(h_img * scale_ratio_det), : int(w_img * scale_ratio_det)] = resized_img
    # 随机缩放
    img_temp = cv2.resize(img_temp,
                          (int(img_temp.shape[1] * jit_factor), int(img_temp.shape[0] * jit_factor)),
                          )
    scale_ratio_det *= jit_factor
    # f_show_od_np4plt_v3(img_temp, )
    if FLIP:
        img_temp = img_temp[:, ::-1, :]  # 水平翻转
        # f_show_od_np4plt_v3(img_temp)
        pass
    # 这里有可能放大或缩小
    origin_h, origin_w = img_temp.shape[:2]
    target_h, target_w = img_src.shape[:2]

    img_pad = np.zeros((max(origin_h, target_h), max(origin_w, target_w), 3)).astype(np.uint8)
    # 这里有是剪切或填充
    img_pad[:origin_h, :origin_w] = img_temp

    x_offset, y_offset = 0, 0  # 如果是填充 随机确定一个左上角点
    if img_pad.shape[0] > target_h:
        y_offset = random.randint(0, img_pad.shape[0] - target_h - 1)
    if img_pad.shape[1] > target_w:
        x_offset = random.randint(0, img_pad.shape[1] - target_w - 1)
    padded_cropped_img = img_pad[y_offset: y_offset + target_h, x_offset: x_offset + target_w]

    # 处理bbox
    boxes_det_origin = adjust_box_anns(target_det['boxes'],
                                       scale_ratio_det, 0, 0,
                                       origin_w, origin_h
                                       )
    if FLIP:
        # torch 不支持 ::-1
        # boxes_det_origin[:, 0::2] = (origin_w - boxes_det_origin[:, 0::2][:, ::-1])
        # 这里反转的水平
        boxes_det_origin[:, 0::2] = (origin_w - fun_flip(boxes_det_origin[:, 0::2], 1))

    # cp_bboxes_transformed_np = cp_bboxes_origin_np.copy()
    # boxes_det_origin_transformed = boxes_det_origin.clone()
    boxes_det_origin_transformed = fun_copy(boxes_det_origin)
    boxes_det_origin_transformed[:, 0::2] = np.clip(boxes_det_origin_transformed[:, 0::2] - x_offset,
                                                    0, target_w
                                                    )
    boxes_det_origin_transformed[:, 1::2] = np.clip(boxes_det_origin_transformed[:, 1::2] - y_offset,
                                                    0, target_h
                                                    )
    keep_list = filter_box4yolox(boxes_det_origin.T, boxes_det_origin_transformed.T, 5)

    if keep_list.sum() >= 1.0:
        # f_show_od_np4plt_v3(padded_cropped_img, cp_bboxes_transformed_np[keep_list])
        # 这里合并
        target_src['labels'] = fun_cat([target_src['labels'], target_det['labels'][keep_list]], 0)
        target_src['boxes'] = fun_cat([target_src['boxes'], boxes_det_origin_transformed[keep_list]], 0)
        img_src = img_src.astype(np.float32)
        img_src = 0.5 * img_src + 0.5 * padded_cropped_img.astype(np.float32)

    return img_src.astype(np.uint8), target_src


if __name__ == '__main__':
    from ftools.ai.datas.z_dataloader import get_data_cocomin, get_data_type3
    from ftools.ai.picture.f_show import f_show_od_np4plt_v3
    from ftools.ai.CONFIG_BASE import FCFG_BASE

    path_host = 'M:'
    mode = 'bbox'
    cfg = FCFG_BASE()
    cfg.IS_TRAIN = True
    cfg.IS_VAL = False
    cfg.IS_TEST = False
    cfg.IS_MULTI_SCALE = False
    cfg.num_workers = 0
    cfg.SIZE_WH_INPUT_TRAIN = (640, 640)
    cfg.is_mosaic = False
    data_info, dataloader_train, dataloader_test = get_data_type3(
        cfg,
        path_host=path_host,
        mode_train=mode, batch_train=10
    )

    dataset = dataloader_train.dataset

    for i in range(len(dataset)):
        id_img = dataset.ids_img[i]  # 公用
        ids_img = [id_img] + np.random.choice(dataset.ids_img, 3).tolist()
        imgs, targets = [], []
        for id_img in ids_img:
            img_np, target = dataset.fgetitem(id_img)
            imgs.append(img_np)
            targets.append(target)

        img_np, target = get_mosaic_img(imgs=imgs,
                                        targets=targets,
                                        size_hw_m=cfg.SIZE_WH_INPUT_TRAIN)

        # img_src, target_src = dataset.fgetitem(id_img)
        # _id_img = np.random.choice(dataset.ids_img, 1)[0]
        # img_det, target_det = dataset.fgetitem(_id_img)  # dataset 已确保有目标
        # img_np, target = mixup(img_src, target_src, img_det, target_det, cfg.SIZE_WH_INPUT_TRAIN )
        # # f_show_od_np4plt_v3(img_np, target['boxes'], g_texts=target['labels'])

        # 数据增强
        # img_mosaic, g_ltrb_mosaic = data_heighten4yolox(
        #     img_mosaic, g_ltrb_mosaic,
        #     degrees=10,
        #     translate=0.1,
        #     scale=(0.5, 1.5),
        #     shear=2.,
        #     perspective=0.,
        #     border=[-size_hw_m[0] // 2, -size_hw_m[1] // 2],
        # )

        text = [str(l) for l in target['labels']]
        f_show_od_np4plt_v3(img_np, target['boxes'], g_texts=text, )

        pass
