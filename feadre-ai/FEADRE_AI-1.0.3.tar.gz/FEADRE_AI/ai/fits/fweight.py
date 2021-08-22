import os

import torch

from ftools.GLOBAL_LOG import flog

'''
filter(lambda p: p.requires_grad, model.parameters()) 过滤优化器的迭代器
'''


def save_weight(path_save, model, name, loss=None, optimizer=None,
                lr_scheduler=None, epoch=1, maps_val=None,
                ema_model=None, ):
    if path_save and os.path.exists(path_save):

        if ema_model is not None:
            model = ema_model.ema

        sava_dict = {
            'model': model.state_dict(),
            'optimizer': optimizer.state_dict() if optimizer else None,
            'lr_scheduler': lr_scheduler.state_dict() if lr_scheduler else None,
            'epoch': epoch}

        if loss is not None:
            l = round(loss, 2)
        else:
            l = ''

        if maps_val is not None:
            file_weight = os.path.join(path_save, (name + '_{}_{}_{}_{}.pth')
                                       .format(epoch,
                                               l,
                                               'p' + str(round(maps_val[0] * 100, 1)),
                                               'r' + str(round(maps_val[1] * 100, 1)),
                                               ))
        else:
            file_weight = os.path.join(path_save, (name + '_{}_{}.pth').format(epoch, l))
        torch.save(sava_dict, file_weight)
        flog.info('保存成功 %s', file_weight)


def load_weight(file_weight, model, optimizer=None, lr_scheduler=None,
                device=torch.device('cpu'), is_mgpu=False, ffun=None):
    start_epoch = 1
    if file_weight and os.path.exists(file_weight):
        checkpoint = torch.load(file_weight, map_location=device)

        '''对多gpu的k进行修复'''
        if 'model' in checkpoint:
            pretrained_dict_y = checkpoint['model']
        else:
            pretrained_dict_y = checkpoint

        '''重组权重回调'''
        if ffun is not None:
            pretrained_dict = ffun(pretrained_dict_y)
        else:
            pretrained_dict = pretrained_dict_y

        dd = {}
        # # 多GPU处理
        ss = 'module.'
        for k, v in pretrained_dict.items():
            if is_mgpu:
                if ss not in k:
                    dd[ss + k] = v
                else:
                    dd = pretrained_dict_y
                    break
                    # dd[k] = v
            else:
                dd[k.replace(ss, '')] = v

        keys_missing, keys_unexpected = model.load_state_dict(dd, strict=False)
        if len(keys_missing) > 0 or len(keys_unexpected):
            flog.error('missing_keys %s', keys_missing)  # 这个是 model 的属性
            flog.error('unexpected_keys %s', keys_unexpected)  # 这个是 pth 的属性
        if optimizer and 'optimizer' in checkpoint and checkpoint['optimizer'] is not None:
            optimizer.load_state_dict(checkpoint['optimizer'])
        if lr_scheduler and 'lr_scheduler' in checkpoint and checkpoint['lr_scheduler'] is not None:
            lr_scheduler.load_state_dict(checkpoint['lr_scheduler'])

        if 'epoch' in checkpoint:
            start_epoch = checkpoint['epoch'] + 1


        flog.warning('已加载 feadre 权重文件为 %s', file_weight)
    else:
        flog.error('权重文件加载失败 %s', file_weight)
    return start_epoch
