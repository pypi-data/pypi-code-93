import argparse
import os

import cv2
import numpy as np

import onnxruntime
import torch

from ftools.ai.datas.dta_heighten.f_data_heighten4target import ftransform_ssd_test
from ftools.ai.datas.z_dataloader import get_data_type3

if __name__ == '__main__':
    file_onnx = ''
    path_root_weight = r'M:\AI\weights\feadre\zz'
    _file_read_weight = os.path.join(path_root_weight, 'nanodet_coco_p34r29_1' + '.pth')
    device = torch.device('cpu')
    size_wh_input = (320, 320)

    class CFG:
        pass


    path_host = 'M:'
    mode = 'bbox'
    cfg = CFG()
    cfg.IS_TRAIN = False
    cfg.IS_VAL = False
    cfg.IS_TEST = True
    cfg.IS_MULTI_SCALE = False
    cfg.num_workers = 0
    data_transform = ftransform_ssd_test(size_wh_input)

    data_info, dataloader_train, dataloader_test = get_data_type3(
        cfg,
        path_host=path_host,
        mode_train=mode, batch_train=1
    )


    # session = onnxruntime.InferenceSession(file_onnx)
    # ort_inputs = {session.get_inputs()[0].name: img[None, :, :, :]}
    # output = session.run(None, ort_inputs)

    # predictions = demo_postprocess(output[0], input_shape, p6=args.with_p6)[0]

    # boxes = predictions[:, :4]
    # scores = predictions[:, 4:5] * predictions[:, 5:]
    #
    # boxes_xyxy = np.ones_like(boxes)
    # boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2.
    # boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2.
    # boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2.
    # boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2.
    # boxes_xyxy /= ratio
    # dets = multiclass_nms(boxes_xyxy, scores, nms_thr=0.65, score_thr=0.1)
    #
    # if dets is not None:
    #     final_boxes, final_scores, final_cls_inds = dets[:, :4], dets[:, 4], dets[:, 5]
    #     origin_img = vis(origin_img, final_boxes, final_scores, final_cls_inds,
    #                      conf=args.score_thr, class_names=COCO_CLASSES)
    #
    # mkdir(args.output_dir)
    # output_path = os.path.join(args.output_dir, args.image_path.split("/")[-1])
    # cv2.imwrite(output_path, origin_img)
