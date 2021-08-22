import copy
import json
import tempfile

from pycocotools.cocoeval import COCOeval
import numpy as np

from ftools.ai.datas.z_dataloader import get_data_face5

'''
https://blog.csdn.net/u014734886/article/details/78831382
'segm', 'bbox', 'keypoints'
---------- OD  bbox --------------
[{
    "image_id": int,
    "category_id": int,
    "bbox": [x,y,width,height],
    "score": float,

}]

---------- OD  segm --------------
[{
    "image_id": int,
    "category_id": int,
    "segmentation": RLE,
    "score": float,

}]

---------- KP  keypoints --------------
[{
    "image_id": int,
    "category_id": int,
    "keypoints": [x1,y1,v1,...,xk,yk,vk],
    "score": float,
}]

---------- Stuff segmentation --------------
[{
    "image_id": int,
    "category_id": int,
    "segmentation": RLE,
}]

---------- Caption generation --------------
[{
    "image_id": int,
    "caption": str,
}]
'''


class FCOCOeval(COCOeval):
    '''
    添加了每一个类的得分
    原装生成运行后自动赋值 coco_eval_obj.stats
    '''

    def __init__(self, cocoGt=None, cocoDt=None, iouType='segm'):
        super().__init__(cocoGt, cocoDt, iouType)

    def summarize(self, catId=None):
        """
        Compute and display summary metrics for evaluation results.
        Note this functin can *only* be applied on the default parameter setting
        """

        def _summarize(ap=1, iouThr=None, areaRng='all', maxDets=100):
            p = self.params
            iStr = ' {:<18} {} @[ IoU={:<9} | area={:>6s} | maxDets={:>3d} ] = {:0.3f}'
            titleStr = 'Average Precision' if ap == 1 else 'Average Recall'
            typeStr = '(AP)' if ap == 1 else '(AR)'
            iouStr = '{:0.2f}:{:0.2f}'.format(p.iouThrs[0], p.iouThrs[-1]) \
                if iouThr is None else '{:0.2f}'.format(iouThr)

            aind = [i for i, aRng in enumerate(p.areaRngLbl) if aRng == areaRng]
            mind = [i for i, mDet in enumerate(p.maxDets) if mDet == maxDets]

            if ap == 1:
                # dimension of precision: [TxRxKxAxM]
                s = self.eval['precision']
                # IoU
                if iouThr is not None:
                    t = np.where(iouThr == p.iouThrs)[0]
                    s = s[t]

                ''' 这里是添加的代码 判断是否传入catId，如果传入就计算指定类别的指标 '''
                if isinstance(catId, int):
                    s = s[:, :, catId, aind, mind]
                else:
                    s = s[:, :, :, aind, mind]

            else:
                # dimension of recall: [TxKxAxM]
                s = self.eval['recall']
                if iouThr is not None:
                    t = np.where(iouThr == p.iouThrs)[0]
                    s = s[t]

                ''' 这里是添加的代码 判断是否传入catId，如果传入就计算指定类别的指标 '''
                if isinstance(catId, int):
                    s = s[:, catId, aind, mind]
                else:
                    s = s[:, :, aind, mind]

            if len(s[s > -1]) == 0:
                mean_s = -1
            else:
                mean_s = np.mean(s[s > -1])

            ''' 这里是修改 原始只有一个返回值 '''
            # print(iStr.format(titleStr, typeStr, iouStr, areaRng, maxDets, mean_s))
            # return mean_s
            print_string = iStr.format(titleStr, typeStr, iouStr, areaRng, maxDets, mean_s)
            return mean_s, print_string

        stats, print_list = [0] * 12, [""] * 12
        stats[0], print_list[0] = _summarize(1)
        stats[1], print_list[1] = _summarize(1, iouThr=.5, maxDets=self.params.maxDets[2])
        stats[2], print_list[2] = _summarize(1, iouThr=.75, maxDets=self.params.maxDets[2])
        stats[3], print_list[3] = _summarize(1, areaRng='small', maxDets=self.params.maxDets[2])
        stats[4], print_list[4] = _summarize(1, areaRng='medium', maxDets=self.params.maxDets[2])
        stats[5], print_list[5] = _summarize(1, areaRng='large', maxDets=self.params.maxDets[2])
        stats[6], print_list[6] = _summarize(0, maxDets=self.params.maxDets[0])
        stats[7], print_list[7] = _summarize(0, maxDets=self.params.maxDets[1])
        stats[8], print_list[8] = _summarize(0, maxDets=self.params.maxDets[2])
        stats[9], print_list[9] = _summarize(0, areaRng='small', maxDets=self.params.maxDets[2])
        stats[10], print_list[10] = _summarize(0, areaRng='medium', maxDets=self.params.maxDets[2])
        stats[11], print_list[11] = _summarize(0, areaRng='large', maxDets=self.params.maxDets[2])

        print_info = "\n".join(print_list)

        if not self.eval:
            raise Exception('Please run accumulate() first')

        # if len(self.stats)==0:
        #     self.stats = stats  # 与原装只写一次保持一致

        return stats, print_info

    def print_clses(self, clses_name):
        # calculate COCO info for all classes
        # coco_stats, print_coco = self.summarize()

        # calculate voc info for every classes(IoU=0.5)
        voc_map_info_list = []
        for i in range(len(clses_name)):
            stats, _ = self.summarize(catId=i)
            voc_map_info_list.append(" {:15}: {:.3f} {:.3f}".format(clses_name[i], stats[1], stats[7]))

        print_voc = "\n".join(voc_map_info_list)
        print(print_voc)

        # # 将验证结果保存至txt文件中
        # with open("record_mAP.txt", "w") as f:
        #     record_lines = ["COCO results:",
        #                     print_coco,
        #                     "",
        #                     "mAP(IoU=0.5) for each category:",
        #                     print_voc]
        #     f.write("\n".join(record_lines))


if __name__ == '__main__':
    annType = ['segm', 'bbox', 'keypoints']
    mode_test = annType[2]


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
    cfg.IS_JUMP = True
    cfg.IS_DEBUG = False

    data_info, dataloader_train, dataloader_test = get_data_face5(
        cfg, path_host=path_host,
        mode_train=mode_test, batch_train=10)

    dataset = dataloader_train.dataset
    coco_obj_gt = dataset.coco_obj
    # imgIds = sorted(coco_obj_gt.getImgIds())
    imgIds = coco_obj_gt.getImgIds()
    # imgIds = imgIds[0:100]
    res_coco_kps = []  # 标准结果文档
    for id in imgIds:
        info_img = coco_obj_gt.loadImgs(id)[0]
        # file = os.path.join(path_img, info_img['file_name'])
        info_anns = coco_obj_gt.loadAnns(coco_obj_gt.getAnnIds(id))
        for ann in info_anns:
            if mode_test == 'bbox':
                _d = {
                    "image_id": id,
                    "category_id": ann['category_id'],
                    "bbox": ann['bbox'],
                    "score": 0.9,

                }
            elif mode_test == 'keypoints':
                _d = {
                    "image_id": id,
                    "category_id": ann['category_id'],
                    "keypoints": ann['keypoints'],  # kps_l
                    "score": 0.9,
                }
            else:
                raise Exception('暂不支持 mode_test=%s' % mode_test)

            res_coco_kps.append(_d)

    _, tmp = tempfile.mkstemp()  # 创建临时文件
    json.dump(res_coco_kps, open(tmp, 'w'))
    coco_dt = coco_obj_gt.loadRes(tmp)

    cocoEval = COCOeval(coco_obj_gt, coco_dt, mode_test)
    cocoEval.params.imgIds = imgIds

    '''
    # 标注效果 归一化因子 眼睛鼻子 .25 ~ 臀部 1.07 
    "nose",    "left_eye",    "right_eye",    "left_ear",臂    "right_ear",
    "left_shoulder", 肩   "right_shoulder",    "left_elbow",肘    "right_elbow",
    "left_wrist", 手腕   "right_wrist",    "left_hip",臀部    "right_hip",   
     "left_knee", 膝盖   "right_knee",    "left_ankle", 踝(89)   "right_ankle" 
    '''
    # cocoEval.params.kpt_oks_sigmas = np.array([.26, .25, .25, .35, .35, .
    # 79, .79, .72, .72, .62,.62,
    # 1.07, 1.07, .
    # 87, .87, .89, .89])/10.0
    cocoEval.params.kpt_oks_sigmas = np.array([.26, .25, .25, .26, .26, ]) / 10.0
    cocoEval.evaluate()
    cocoEval.accumulate()
    summarize = cocoEval.summarize()
    print(cocoEval.stats)
