import os

import torch
import torch.nn.functional as F
import numpy as np

from ftools.ai.datas.dataset_coco import CustomCocoDataset, HeightenCocoDataset


def fcre_dataload(is_multi_scale, num_workers,
                  mode, batch, file_json, path_img, transform, name,
                  is_mosaic=False, is_mixup=False, is_mosaic_filter=False, thr_wh=5, thr_area=25,
                  size_hw_img=None, is_jump=False,  # is_mosaic 时必须传
                  kps_seq=None, is_debug=False,
                  ):
    if is_mosaic or is_mixup:
        dataset = HeightenCocoDataset(
            file_json=file_json,
            path_img=path_img,
            mode=mode,
            transform=transform,
            mode_balance_data=None,
            name=name,
            is_mosaic=is_mosaic,
            is_mixup=is_mixup,
            is_mosaic_filter=is_mosaic_filter,
            thr_wh=thr_wh,
            thr_area=thr_area,
            size_hw_img=size_hw_img,
            kps_seq=kps_seq,
            is_debug=is_debug,
        )
    else:
        dataset = CustomCocoDataset(
            file_json=file_json,
            path_img=path_img,
            mode=mode,
            transform=transform,
            mode_balance_data=None,
            name=name,
            is_jump=is_jump,
            kps_seq=kps_seq,
            is_debug=is_debug,
        )
    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=batch,
        num_workers=num_workers,
        shuffle=True,
        pin_memory=True,  # 不使用虚拟内存 GPU要报错
        # drop_last=True,  # 除于batch_size余下的数据
        # collate_fn=lambda x: fun_dataloader(x, cfg),
        collate_fn=CLS4collate_fn(is_multi_scale),
    )
    return dataloader


class CLS4collate_fn:
    # fdatas_l1
    def __init__(self, is_multi_scale):
        self.is_multi_scale = is_multi_scale

    def __call__(self, batch_datas):
        '''
        在这里重写collate_fn函数
        batch_datas: tuple[[tensor_img,dict_targets],...,[tensor_img,dict_targets]]
        '''
        # 训练才进这里
        if self.is_multi_scale:
            batch = len(batch_datas)
            imgs_list = []
            targets_list = []
            # 打开 tuple 数据
            for i, (img_ts, target) in enumerate(batch_datas):
                # flog.warning('fun4dataloader测试  %s %s %s ', target, len(target['boxes']), len(target['labels']))
                imgs_list.append(img_ts)
                targets_list.append(target)

            pad_imgs_list = []

            # 这里的最大一定能被32整除
            h_list = [int(s.shape[1]) for s in imgs_list]
            w_list = [int(s.shape[2]) for s in imgs_list]
            max_h = np.array(h_list).max()
            max_w = np.array(w_list).max()
            # self.cfg.tcfg_batch_size = [max_w, max_h] # 这样用多进程要报错
            for i in range(batch):
                img_ts = imgs_list[i]
                # 右下角添加 target 无需处理
                img_ts_pad = F.pad(img_ts, (0, int(max_w - img_ts.shape[2]), 0, int(max_h - img_ts.shape[1])), value=0.)
                pad_imgs_list.append(img_ts_pad)

                # debug 代码
                # fshow_pic_ts4plt(pad_img)  # 可视化 前面不要归一化
                # fshow_kp_ts4plt(pad_img,
                #                 targets_list[i]['boxes'],
                #                 targets_list[i]['kps'],
                #                 mask_kps=targets_list[i]['kps_mask'],
                #                 is_recover_size=False
                #                 )  # 可视化
                # f_show_od_ts4plt(img_ts_pad, targets_list[i]['boxes'], is_recover_size=False)
                # print('多尺度%s ' % str(pad_img.shape))

            imgs_ts_4d = torch.stack(pad_imgs_list)
        else:
            imgs_ts_3d = batch_datas[0][0]
            # 包装整个图片数据集 (batch,3,416,416) 转换到显卡
            imgs_ts_4d = torch.empty((len(batch_datas), *imgs_ts_3d.shape)).to(imgs_ts_3d)
            targets_list = []
            for i, (img, target) in enumerate(batch_datas):
                # flog.warning('fun4dataloader测试  %s %s %s ', target, len(target['boxes']), len(target['labels']))
                imgs_ts_4d[i] = img
                targets_list.append(target)
        return imgs_ts_4d, targets_list


def t001(cfg):
    from ftools.ai.datas.dta_heighten.f_data_pretreatment4np import ftransform_more_train, ftransform_nanodet_train
    path_host = ''
    mode = 'bbox'
    path_root = os.path.join(path_host, '/AI/datas/VOC2007')
    # path_img = os.path.join(path_root, 'train/JPEGImages')
    # file_json = os.path.join(path_root, 'coco/annotations/instances_type3_train_1066.json')
    # path_img = os.path.join(path_root, 'val/JPEGImages')
    # file_json = os.path.join(path_root, 'coco/annotations/instances_type3_val_413.json')
    path_img = os.path.join(path_root, 'train/JPEGImages')
    file_json = os.path.join(path_root, 'coco/annotations/instances_type3_train_1066.json')
    _transform_train = ftransform_more_train(cfg.SIZE_WH_INPUT_TRAIN)
    _transform_test = ftransform_nanodet_train(cfg.SIZE_WH_INPUT_TRAIN)
    cfg.NUM_CLASSES = 3
    dataset = CustomCocoDataset(
        file_json=file_json,
        path_img=path_img,
        mode=mode,
        transform=_transform_test,
        mode_balance_data=None,
    )
    dataloader_train = torch.utils.data.DataLoader(
        dataset,
        batch_size=32,
        num_workers=0,
        shuffle=True,
        pin_memory=True,  # 不使用虚拟内存 GPU要报错
        # drop_last=True,  # 除于batch_size余下的数据
        # collate_fn=lambda x: fun_dataloader(x, cfg),
        collate_fn=CLS4collate_fn(False),
    )
    return dataloader_train
