import os
import random

import cv2
import torch
from pycocotools.coco import COCO
from torch.utils.data import Dataset
import numpy as np

from ftools.GLOBAL_LOG import flog
from ftools.ai.datas.dta_heighten.fmosaic import get_mosaic_img, mixup
from ftools.ai.object_detection.boxes.f_kps import fsplit_kps


class CustomCocoDataset(Dataset):
    '''

    '''

    def __init__(self, file_json, path_img, mode, transform=None, is_debug=False,
                 s_ids_cats=None, nums_cat=None, is_ts_all=True, is_jump=False,
                 size_hw_img=None, mode_balance_data=None, name='fname',
                 kps_seq=None,
                 ):
        '''

        :param mode:  bbox segm keypoints caption
        :param s_ids_cats:  指定类别 或数据集的类别ID
        :param nums_cat:  限制类别的最大数量
        :param is_ts_all:  默认全部转TS
        :param is_jump:  是否跳过没有目标的图片 True 为必须重新加载
        :param size_hw_img:
        :param mode_balance_data: 平衡各类数据量 这个优先冲突于 s_ids_cats  数据类别平衡方法
            'max': 4舍五入倍数整体复制  确保类别尽量一致
            'min': 取最少的类型数,多的随机选
            None: 不处理
            int 指定数据数量
        :param name: dataset 标注
        '''
        self.path_img = path_img
        if not os.path.exists(path_img):
            raise Exception('coco path_img 路径不存在', path_img)

        self.size_hw_img = size_hw_img
        self.is_jump = is_jump
        self.kps_seq = kps_seq

        self.file_json = file_json
        self.transform = transform
        self.mode = mode
        self.coco_obj = COCO(file_json)
        # self.device = device  # 不能扩 use CUDA with multiprocessing

        self.name = name
        self.is_ts_all = is_ts_all

        # f_look_coco_type(self.coco_obj, ids_cats_ustom=None)
        print('创建dataset-----', name)

        self.s_ids_cats = []  # 初始化一下
        # 平衡各类数据量  模式
        if mode_balance_data is not None:
            cats = self.coco_obj.getCatIds()
            num_class = len(cats)
            _t_ids = []
            _t_len = np.zeros(num_class)
            for i, cat in enumerate(cats):
                ids = self.coco_obj.getImgIds(catIds=cat)
                _t_ids.append(ids)
                _t_len[i] = len(ids)

            self.ids_img = []

            if mode_balance_data == 'max':
                num_repeats = np.around((_t_len.max() / _t_len)).astype(np.int)
                for i in range(num_class):
                    self.ids_img.extend(np.tile(np.array(_t_ids[i]), num_repeats[i]).tolist())
            elif mode_balance_data == 'min':
                len_min = _t_len.min().astype(np.int)
                # flog.debug('_t_len = %s', _t_len)
                for i in range(num_class):
                    self.ids_img.extend(np.random.choice(_t_ids[i], len_min).tolist())
            elif isinstance(mode_balance_data, int):
                for cat_id in cats:
                    # 每一类的ID
                    ids_ = self.coco_obj.getImgIds(catIds=[cat_id])
                    if len(ids_) > 0:
                        self.s_ids_cats.append(cat_id)
                    self.ids_img.extend(np.random.choice(ids_, mode_balance_data).tolist())

        else:
            # 与 mode_balance_data 冲突
            if s_ids_cats is not None:
                flog.warning('指定coco类型 %s', self.coco_obj.loadCats(s_ids_cats))
                self.s_ids_cats = s_ids_cats
                ids_img = []

                # 限制每类的最大个数
                if nums_cat is None:
                    for idc in zip(s_ids_cats):
                        # 类型对应哪些文件 可能是一张图片多个类型
                        ids_ = self.coco_obj.getImgIds(catIds=idc)
                        ids_img += ids_
                else:
                    # 限制每类的最大个数
                    for idc, num_cat in zip(s_ids_cats, nums_cat):
                        # 类型对应哪些文件 可能是一张图片多个类型
                        ids_ = self.coco_obj.getImgIds(catIds=idc)[:num_cat]
                        # ids_ = self.coco.getImgIds(catIds=idc)[:1000]
                        ids_img += ids_
                        # print(ids_)  # 这个只支持单个元素

                self.ids_img = list(set(ids_img))  # 去重
            else:
                # 所有类别所有图片
                self.s_ids_cats = self.coco_obj.getCatIds()
                self.ids_img = self.coco_obj.getImgIds()  # 所有图片的id 画图数量

        #  创建 coco 类别映射
        self._init_load_classes(self.s_ids_cats)  # 除了coco数据集,其它不管

        self.is_debug = is_debug  # 备用 预留

    def __len__(self):
        if self.is_debug:
            return 9  # 用一云debug
        return len(self.ids_img)

    def open_img_tar(self, id_img):
        img = self.load_image(id_img)

        # bboxs, labels, or keypoints  np
        tars_list = self.load_anns(id_img, img_wh=img.shape[:2][::-1])

        # 没有标注就只有这两个属性
        target = {}
        target['image_id'] = id_img
        target['size'] = np.array(img.shape[:2][::-1])  # (w,h)

        if tars_list is None:  # 没有标注返回空
            # target['boxes'] = np.empty((0, 4), dtype=np.float32)
            # target['labels'] = np.empty((0), dtype=np.float32)
            return img, target

        # 根据标注模式 及字段自动添加 target['boxes', 'labels', 'kps']
        key_names = ['boxes', 'labels', 'kps', ]
        for i, tar in enumerate(tars_list):
            target[key_names[i]] = tar
        return img, target

    def fgetitem(self, id_img):
        '''
        这个方法不要返回空
        :param id_img:
        :return:
        '''
        # 这里生成的是原图尺寸的 target 和img_np_uint8 (375, 500, 3)
        img, target = self.open_img_tar(id_img)

        if 'boxes' in target:
            assert len(target['boxes']) == len(target['labels']), \
                '!!! 数据有问题 %s  %s %s %s ' % ('transform前', target, len(target['boxes']), len(target['labels']))
        else:
            if self.is_jump:
                # print('这个图片没有标注信息 id为 %s ,跳过', id_img)
                return self.fgetitem(self.ids_img[random.randint(0, len(self.ids_img) - 1)])
        # 二级检测无用
        # if target['boxes'].shape[0] == 0:
        #     flog.warning('数据有问题 重新加载 %s', id_img)
        #     return self.fgetitem(self.ids_img[random.randint(0, len(self.ids_img) - 1)])

        return img, target

    def __getitem__(self, index):
        '''

        :param index:
        :return: tensor or np.array 根据 out: 默认ts or other is np
            img: h,w,c
            target:
            coco原装是 ltwh
            dict{
                image_id: int,
                bboxs: ts n4 原图 ltwh -> ltrb
                labels: ts n,
                keypoints: 待定
                size: wh
            }
        '''
        id_img = self.ids_img[index]
        img, target = self.fgetitem(id_img)

        # debug
        # f_show_od_ts4plt_v3(
        #     img,
        #     target['boxes'],
        #     is_normal=True,
        # )

        # 以上img 确定是np格式(transform后出来一般是ts); target 全部是np 除imgid
        if self.transform is not None:
            img, target = self.transform(img, target)

        # 这里img输出 ts_3d
        if self.is_ts_all:
            if 'boxes' in target:
                target['boxes'] = torch.tensor(target['boxes'], dtype=torch.float)
                target['labels'] = torch.tensor(target['labels'], dtype=torch.int64)
            target['size'] = torch.tensor(target['size'], dtype=torch.float)  # file尺寸

        # 每个图片对应的target数量是不一致的 所以需要用target封装
        return img, target

    def load_image(self, id_img):
        '''

        :param id_img:
        :return:
        '''
        image_info = self.coco_obj.loadImgs(id_img)[0]
        file_img = os.path.join(self.path_img, image_info['file_name'])
        if not os.path.exists(file_img):
            raise Exception('file_img 加载图片路径错误', file_img)

        img = cv2.imread(file_img)
        return img

    def load_anns(self, id_img, img_wh):
        '''
        ltwh --> ltrb
        :param id_img:
        :return: tars_list 没有或有问题返回空
            bboxs: np(num_anns, 4)
            labels: np(num_anns)
        '''
        # annotation_ids = self.coco.getAnnIds(self.image_ids[index], iscrowd=False)
        annotation_ids = self.coco_obj.getAnnIds(id_img)  # ann的id
        # anns is num_anns x 4, (x1, x2, y1, y2)

        if len(annotation_ids) == 0:
            flog.error('这图标注ID不存在 id_img = %s', id_img)
            return None

        coco_anns = self.coco_obj.loadAnns(annotation_ids)
        bboxs_np = np.zeros((0, 4), dtype=np.float32)  # np创建 空数组 高级
        labels = []
        kps = []
        ''' 默认 bbox 一定是存在的 '''
        for ann in coco_anns:
            x, y, box_w, box_h = ann['bbox']  # ltwh
            # 修正超范围的框  得 ltrb
            x1 = max(0, x)  # 修正lt最小为0 左上必须在图中
            y1 = max(0, y)
            x2 = min(img_wh[0] - 1, x1 + max(0, box_w - 1))  # 右下必须在图中
            y2 = min(img_wh[1] - 1, y1 + max(0, box_h - 1))
            ''' --- bbox校验 --- '''
            if ann['area'] > 0 and x2 > x1 and y2 >= y1:
                bbox = np.array([[x1, y1, x2, y2]], dtype=np.float32)
                # bbox[0, :4] = ann['bbox']
                # ann['bbox'] = [x1, y1, x2, y2]  # 这样写回有BUG 共享内存会修改
            else:
                flog.error('标记框有问题 %s 跳过', ann)
                continue

            if self.mode == 'keypoints':
                ''' 这里只取了 v=2的转换为1(有效用于训练)  v=0:没有  v=1:标了不可见 v=2标了可见 '''
                _kp = np.array(ann['keypoints'])
                # 校验_kps 这里只会有一个标注
                # (ngt,dim_kps) ->  (ngt,num_keypoints,3)
                _kp = _kp.reshape(-1, 3)
                mask_pos = _kp[:, 2] == 2
                _kp[:, 2] = 0  # 全部为0后 只取可见 v=0 和v=1 都改为0
                _kp[:, 2][mask_pos] = 1
                kps.append(_kp.reshape(-1))

            # 全部通过后添加
            bboxs_np = np.append(bboxs_np, bbox, axis=0)
            labels.append(self.classes_coco2train[ann['category_id']])

        if len(labels) == 0:
            return None

        # bboxs = ltwh2ltrb(bboxs) # 前面 已转
        if bboxs_np.shape[0] == 0:
            flog.error('这图标注 不存在 %s', coco_anns)
            return None
            # raise Exception('这图标注 不存在 %s', coco_anns)

        # 转NP
        labels = np.array(labels, dtype=np.float32)

        if self.mode == 'bbox':
            return bboxs_np, labels
        elif self.mode == 'keypoints':
            # 转NP
            kps = np.array(kps, dtype=np.float32)
            return bboxs_np, labels, kps

    def _init_load_classes(self, ids_cat):
        '''
        self.classes_ids :  {'Parade': 1}
        self.ids_classes :  {1: 'Parade'}
        self.ids_new_old {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20}
        self.ids_old_new {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20}
        :return:
        '''
        # [{'id': 1, 'name': 'aeroplane'}, {'id': 2, 'name': 'bicycle'}, {'id': 3, 'name': 'bird'}, {'id': 4, 'name': 'boat'}, {'id': 5, 'name': 'bottle'}, {'id': 6, 'name': 'bus'}, {'id': 7, 'name': 'car'}, {'id': 8, 'name': 'cat'}, {'id': 9, 'name': 'chair'}, {'id': 10, 'name': 'cow'}, {'id': 11, 'name': 'diningtable'}, {'id': 12, 'name': 'dog'}, {'id': 13, 'name': 'horse'}, {'id': 14, 'name': 'motorbike'}, {'id': 15, 'name': 'person'}, {'id': 16, 'name': 'pottedplant'}, {'id': 17, 'name': 'sheep'}, {'id': 18, 'name': 'sofa'}, {'id': 19, 'name': 'train'}, {'id': 20, 'name': 'tvmonitor'}]
        categories = self.coco_obj.loadCats(ids_cat)
        categories.sort(key=lambda x: x['id'])  # 按id升序 [{'id': 1, 'name': 'Parade'},]

        # coco ids is not from 1, and not continue ,make a new index from 0 to 79, continuely
        # 重建index 从1-80
        # classes_ids:   {names:      new_index}
        # coco_ids:  {new_index:  coco_index}
        # coco_ids_inverse: {coco_index: new_index}

        self.classes_ids, self.classes_train2coco, self.classes_coco2train = {}, {}, {}
        self.ids_classes = {}
        # 解决中间有断格的情况
        for i, c in enumerate(categories, start=1):  # 修正从1开始
            self.classes_train2coco[i] = c['id']  # 验证时用这个
            self.classes_coco2train[c['id']] = i
            self.classes_ids[c['name']] = i  # 这个是 train 索引 {'Parade': 0,}
            self.ids_classes[i] = c['name']  # 这个是 train 索引 {0:'Parade',}
        pass


class HeightenCocoDataset(CustomCocoDataset):

    def __init__(self, file_json, path_img, mode, transform=None, is_debug=False, s_ids_cats=None, nums_cat=None,
                 is_ts_all=True, is_jump=False, size_hw_img=None, mode_balance_data=None, name='fname',
                 is_mosaic=False, is_mixup=False,
                 is_mosaic_filter=False, thr_wh=5, thr_area=25,
                 kps_seq=None,
                 ):
        super().__init__(file_json=file_json, path_img=path_img, mode=mode,
                         transform=transform, is_debug=is_debug,
                         s_ids_cats=s_ids_cats, nums_cat=nums_cat,
                         is_ts_all=is_ts_all, is_jump=is_jump,
                         size_hw_img=size_hw_img,
                         mode_balance_data=mode_balance_data, name=name,
                         kps_seq=kps_seq,
                         )
        # 这个用于 mosaic 的尺寸
        assert size_hw_img is not None, 'size_hw_img 不能为空'
        self.size_hw_img = size_hw_img
        self.is_mosaic = is_mosaic
        self.is_mixup = is_mixup

        # mosaic 过滤参数 如果 transform 不带过滤 则建议开启
        self.is_mosaic_filter = is_mosaic_filter
        self.thr_wh = thr_wh
        self.thr_area = thr_area

    def fgetitem(self, id_img):
        if self.is_mosaic:
            # 这里自动强制将 np.int 转成 int coco不报错
            ids_img = [id_img] + np.random.choice(self.ids_img, 3).tolist()
            imgs, targets = [], []
            for id_img in ids_img:
                img_np, target = super().fgetitem(id_img)
                imgs.append(img_np)
                targets.append(target)

            img_np, target = get_mosaic_img(imgs=imgs,
                                            targets=targets,
                                            size_hw_m=self.size_hw_img,
                                            is_filter=self.is_mosaic_filter,
                                            thr_wh=self.thr_wh,
                                            thr_area=self.thr_area,
                                            )
            # debug
            # from ftools.ai.picture.f_show import f_show_od_np4plt_v3
            # f_show_od_np4plt_v3(img_np, g_ltrb=target['boxes'],
            #                                 g_texts=target['labels'].astype(np.int).tolist())

        elif self.is_mixup:
            img_src, target_src = super().fgetitem(id_img)
            # _id_img = np.random.choice(self.ids_img, 1)[0]  # 这个返回的是np.int
            _id_img = random.randint(0, len(self.ids_img) - 1)
            img_det, target_det = super().fgetitem(_id_img)  # dataset 已确保有目标

            img_np, target = mixup(img_src=img_src, target_src=target_src,
                                   img_det=img_det, target_det=target_det,
                                   size_hw_m=self.size_hw_img,
                                   mixup_scale=(0.5, 1.5),
                                   )
            # debug
            # from ftools.ai.picture.f_show import f_show_od_np4plt_v3
            # f_show_od_np4plt_v3(img_np, g_ltrb=target['boxes'],
            #                     g_texts=target['labels'].astype(np.int).tolist())
        else:
            img_np, target = super().fgetitem(id_img)

        return img_np, target


if __name__ == '__main__':
    from ftools.ai.datas.data_factory import CLS4collate_fn
    from ftools.ai.datas.z_dataloader import get_data_cocomin, get_data_type3
    from ftools.ai.picture.f_show import f_show_od_np4plt_v3, f_show_od_np4cv
    import numpy as np


    class CFG:
        pass


    path_host = 'M:'
    mode = 'bbox'
    cfg = CFG()
    cfg.IS_TRAIN = True
    cfg.IS_VAL = False
    cfg.IS_TEST = False
    cfg.IS_MULTI_SCALE = False
    cfg.num_workers = 0

    # mosaic 必须传
    cfg.SIZE_WH_INPUT_TRAIN = (640, 640)

    cfg.IS_MOSAIC = True
    cfg.IS_MIXUP = True
    cfg.IS_MOSAIC_FILTER = False
    cfg.THR_WH = 5
    cfg.THR_AREA = 25

    data_info, dataloader_train, dataloader_test = get_data_type3(
        cfg,
        path_host=path_host,
        mode_train=mode, batch_train=10
    )

    dataset = dataloader_train.dataset

    for data in dataset:
        img_np, target = data
        text = [str(l) for l in target['labels']]
        # f_show_od_np4plt_v3(img_np, target['boxes'], g_texts=text, )
        f_show_od_np4cv(img_np, target['boxes'], g_texts=text, )
