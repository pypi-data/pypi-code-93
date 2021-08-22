import sys

import torch

from ftools.GLOBAL_LOG import flog
from ftools.ai.fits.fweight import save_weight


def init_weight4nanodet(model, device, path_host):
    '''
    421个
    'model.head.distribution_project.project'
    'model.fpn.lateral_convs.0.conv.weight'
    'model.head.gfl_reg.2.bias'
    'model.head.cls_convs.2.1.pointwise.weight'
    '''
    file_weight = path_host + '/AI/weights/nanodet/nanodet_m.ckpt'
    # file_weight = 'M:/AI/weights/feadre/nanodet_50_57.765.pth'
    checkpoint = torch.load(file_weight, map_location=device)
    pretrained_dict_y = checkpoint['state_dict']
    s_backbone = 'net.backbone.'  # lrelu
    # s_backbone = 'net.backbone.model_hook.'  # relu
    s_fpn = ['net.fpn.prj_5.', 'net.fpn.prj_4.', 'net.fpn.prj_3.', ]
    # s_fpn = ['net.fpn.lateral_convs.2.conv.', 'net.fpn.lateral_convs.1.conv.', 'net.fpn.lateral_convs.0.conv.', ]
    s_gfl_head_convs_front = 'net.gfl_head.convs_front.'
    s_gfl_head_cls_reg = 'net.gfl_head.cls_reg.'
    dd = {}
    for k, v in pretrained_dict_y.items():
        split_key = k.split(".")
        if 'backbone' in split_key:
            det = '.'.join(split_key[2:])
            dd[s_backbone + det] = v
        elif 'fpn' in split_key:
            det = '.'.join(split_key[-1:])
            if '0' in split_key:
                dd[s_fpn[2] + det] = v
            elif '1' in split_key:
                dd[s_fpn[1] + det] = v
            elif '2' in split_key:
                dd[s_fpn[0] + det] = v
        elif 'head' in split_key:
            if 'distribution_project' in split_key:
                # 这个是 tensor([0., 1., 2., 3., 4., 5., 6., 7.]) 没用
                pass
            elif 'cls_convs' in split_key:
                det = '.'.join(split_key[3:])
                dd[s_gfl_head_convs_front + det] = v
            elif 'gfl_cls' in split_key:  # 迁移学习改这里
                det = '.'.join(split_key[-2:])
                dd[s_gfl_head_cls_reg + det] = v
            elif 'gfl_reg' in split_key:
                pass

    keys_missing, keys_unexpected = model.load_state_dict(dd, strict=False)
    if len(keys_missing) > 0 or len(keys_unexpected):
        flog.error('missing_keys %s', keys_missing)  # 这个是 model 的属性
        flog.error('unexpected_keys %s', keys_unexpected)  # 这个是 pth 的属性
    flog.debug('权重加载完成 %s', file_weight)

    # path_root_weight = r'M:\AI\weights\feadre\zz'
    # save_weight(path_root_weight, model=model, name='nanodet_coco_p34r29')
    sys.exit(-1)


def init_weight4yolox(model, device, path_host):
    '''

    '''
    file_weight = path_host + '/AI/weights/yolox/yolox_nano.pth.tar'
    checkpoint = torch.load(file_weight, map_location=device)
    start_epoch = 1
    if 'start_epoch' in checkpoint:
        start_epoch = checkpoint['start_epoch'] + 1
    pretrained_dict_y = checkpoint['model']

    s_backbone = 'net.'
    s_head = s_backbone
    dd = {}
    for k, v in pretrained_dict_y.items():
        split_key = k.split(".")
        if 'backbone' in split_key:
            det = '.'.join(split_key[1:])
            dd[s_backbone + det] = v
        elif 'head' in split_key:
            dd[s_head + k] = v
        else:
            dd[k] = v

    keys_missing, keys_unexpected = model.load_state_dict(dd, strict=False)
    if len(keys_missing) > 0 or len(keys_unexpected):
        flog.error('missing_keys %s', keys_missing)  # 这个是 model 的属性
        print()
        flog.error('unexpected_keys %s', keys_unexpected)  # 这个是 pth 的属性
    flog.debug('权重加载完成 %s', file_weight)

    path_root_weight = r'M:\AI\weights\feadre\zz'
    save_weight(path_root_weight, epoch=start_epoch,
                model=model, name='yolox_coco_pxxrxx_y')
    sys.exit(-1)
