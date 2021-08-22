import copy
import datetime
import json
import math
import os
import sys
import tempfile
import time
from abc import abstractmethod
from collections import deque

import cv2
import numpy as np
import torch
import torch.nn as nn
from pycocotools.cocoeval import COCOeval
from torch.cuda.amp import GradScaler, autocast

from ftools.GLOBAL_LOG import flog
from ftools.ai.fits.fweight import save_weight
from ftools.ai.object_detection.boxes.f_boxes import ltrb2ltwh
from ftools.ai.datas.coco.fcocoeval import FCOCOeval
from ftools.ai.fmodels.tools.ema import ModelEMA
from ftools.ai.object_detection.boxes.f_kps import fsplit_kps
from ftools.ai.picture.f_show import f_show_od_np4plt_v3, f_show_kp_np4cv

from ftools.f_general import get_path_root


class FModelBase(nn.Module):
    def __init__(self, net, losser, preder, is_val, is_test):
        super(FModelBase, self).__init__()
        self.net = net
        self.losser = losser
        self.preder = preder
        self.is_val = is_val
        self.is_test = is_test

    def forward(self, datas_batch):
        if isinstance(datas_batch, (tuple, list)):
            imgs_ts_4d, targets = datas_batch
        else:
            imgs_ts_4d = datas_batch
            targets = [{}]

        # ''' 尺寸偏移 '''
        # device = imgs_ts_4d.device  # 在这里还没有进行to显卡操作
        device = self.fdevice  # 在这里还没有进行to显卡操作
        batch, c, h, w = imgs_ts_4d.shape
        imgs_ts_4d = imgs_ts_4d.to(self.fdevice)  # 图片设备赋值
        off_ltrb_ts = []  # (batch,4)
        if targets is not None and 'off_ltrb' in targets[0]:  # 多尺度归一
            for target in targets:
                off_ltrb_ts.append(torch.tensor(target['off_ltrb'], dtype=torch.float, device=device))
            off_ltrb_ts = torch.stack(off_ltrb_ts, 0)
        else:
            off_ltrb_ts = torch.zeros(batch, 4, device=device, dtype=torch.float)

        if self.training:
            if targets is None:
                raise ValueError("In training mode, targets should be passed")
            # model.fdevice 这里模型自动转显卡 单显卡
            outs = self.net(imgs_ts_4d)
            loss_total, log_dict = self.losser(outs, targets, imgs_ts_4d, off_ltrb_ts)
            return loss_total, log_dict
        else:
            # reses, loss_total, log_dict = [torch.tensor(math.nan)] * 3
            reses, loss_total, log_dict = None, None, {}
            with torch.no_grad():  # 这个没用
                if (self.is_val is not None and self.is_val) or (self.is_test is not None and self.is_test):
                    outs = self.net(imgs_ts_4d)
                    if self.is_val:
                        loss_total, log_dict = self.losser(outs, targets, imgs_ts_4d, off_ltrb_ts)

                    if self.is_test:
                        # outs模型输出  返回 ids_batch, p_boxes_ltrb, p_keypoints, p_labels, p_scores
                        reses = self.preder(outs, imgs_ts_4d, targets, off_ltrb_ts)

            return reses, imgs_ts_4d, targets, off_ltrb_ts, loss_total, log_dict


''' 以下是训练执行者 '''


class InfoRes4test:
    # 根据功能自定义

    def __init__(self) -> None:
        # 记录每一张图的情况
        self.ids_img = []
        self.nums_pos = []
        # self.loss = [] # 这个在 log_dict 中
        self.scores_max = []
        self.scores_mean = []
        self.scores_min = []

    def clear(self):
        self.__init__()


class FitExecutorBase:

    def __init__(self, cfg, model,
                 fun_loss=None, fun_test=None,
                 dataloader_train=None,
                 dataloader_test=None, ) -> None:
        self.cfg = cfg
        self.model = model
        self.fun_loss = fun_loss
        self.fun_test = fun_test
        self.dataloader_train = dataloader_train
        self.dataloader_test = dataloader_test

        self.init_executor(cfg)

        self.num_vis_now = 0  # 已可视化的临时值

    def init_executor(self, cfg):
        # 校验
        assert os.path.exists(cfg.PATH_SAVE_WEIGHT), \
            'path_save_weight 不存在 %s' % cfg.PATH_SAVE_WEIGHT
        if cfg.IS_WRITER:
            from torch.utils.tensorboard import SummaryWriter
            if cfg.KEEP_WRITER:
                _dir = cfg.KEEP_WRITER
            else:
                _dir = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))

            _path = os.path.join(get_path_root(), 'logs', _dir)
            os.makedirs(_path, exist_ok=True)
            flog.debug('---- use tensorboard ---\ntensorboard --host=192.168.0.199 --logdir=\\\n%s\n', _path)
            self.tb_writer = SummaryWriter(_path)
        else:
            self.tb_writer = None

        if self.cfg.IS_EMA and self.model is not None and self.dataloader_train is not None:
            self.ema_model = ModelEMA(self.model, 0.9998)
            # 开始 * max_iter数
            self.ema_model.updates = int(self.cfg.START_EPOCH * len(self.dataloader_train) / self.cfg.FORWARD_COUNT)
        else:
            self.ema_model = None

    def frun(self):

        # 重新训练时 继续冻结
        if self.cfg.NUMS_LOCK_WEIGHT_DICT is not None:
            n_time = len(self.cfg.NUMS_LOCK_WEIGHT_DICT[::-1])
            for s in self.cfg.NUMS_LOCK_WEIGHT_DICT[::-1]:
                if self.cfg.START_EPOCH >= s:
                    self.cfg.FUN_LOCK(self.model, n_time)
                else:
                    n_time -= 1

        # epoch 迭代
        for epoch in range(self.cfg.START_EPOCH, self.cfg.END_EPOCH + 1, 1):  # epoch从1开始
            save_val = None  # loss 值 用于保存weight 时记录
            ''' ------------------- 训练代码  --------------------- '''
            if self.dataloader_train is not None and self.cfg.IS_TRAIN:
                self.model.train()
                if self.cfg.NUMS_LOCK_WEIGHT_DICT is not None:
                    _mask = self.cfg.NUMS_LOCK_WEIGHT_DICT == epoch  # 这里只用结果的第一个
                    if _mask.any():
                        self.cfg.FUN_LOCK(self.model, np.where(_mask)[0][0] + 1)

                t0_test = time.time()
                loss_val_obj = self.ftrain(epoch)  # 调用训练
                save_val = loss_val_obj.avg

                if self.cfg.IS_EMA:
                    self.ema_model.update_attr(model=self.model)

                print(' ----- 训练用时 %s ----- \n\n' % str(datetime.timedelta(seconds=int(time.time() - t0_test))))

            if self.dataloader_train is not None \
                    and self.is_open(epoch, self.cfg.NUM_WEIGHT_SAVE_DICT):
                print('训练完成正在保存模型...')
                save_weight(
                    path_save=self.cfg.PATH_SAVE_WEIGHT,
                    model=self.model,
                    name=self.cfg.SAVE_WEIGHT_NAME,
                    loss=save_val,  # 这个正常是一样的有的
                    optimizer=self.cfg.OPTIMIZER,
                    lr_scheduler=self.cfg.LR_SCHEDULER,
                    epoch=epoch,
                    ema_model=self.ema_model,
                )

            ''' ------------------- 测试代码  --------------------- '''
            if self.dataloader_test is not None and self.is_open(epoch, self.cfg.NUMS_TEST_DICT):

                if self.cfg.IS_TEST is None and self.cfg.IS_VAL is None:
                    flog.warning('cfg.IS_TEST,cfg.IS_VAL 均为空')
                    return

                t0_test = time.time()
                maps_val = self.ftest(epoch)  # 调用测试

                torch.cuda.empty_cache()

                if maps_val is not None and self.cfg.MAPS_DEF_MAX is not None:
                    # 更新 self.cfg.MAPS_DEF_MAX 值
                    if maps_val[0] > self.cfg.MAPS_DEF_MAX[0]:
                        self.cfg.MAPS_DEF_MAX[0] = maps_val[0]
                        self.cfg.MAPS_DEF_MAX[1] = max(self.cfg.MAPS_DEF_MAX[1], maps_val[1])
                    elif maps_val[1] > self.cfg.MAPS_DEF_MAX[1]:
                        self.cfg.MAPS_DEF_MAX[0] = max(self.cfg.MAPS_DEF_MAX[0], maps_val[0])
                        self.cfg.MAPS_DEF_MAX[1] = maps_val[1]
                    else:
                        print(' ----- 测试总用时 %s ----- \n\n'
                              % str(datetime.timedelta(seconds=int(time.time() - t0_test))))
                        continue
                    save_weight(
                        path_save=self.cfg.PATH_SAVE_WEIGHT,
                        model=self.model,
                        name=self.cfg.SAVE_WEIGHT_NAME,
                        loss=save_val,  # 这个正常是一样的有的
                        optimizer=self.cfg.OPTIMIZER,
                        lr_scheduler=self.cfg.LR_SCHEDULER,
                        epoch=epoch,
                        maps_val=maps_val,
                    )
                print(' ----- 测试总用时 %s ----- \n\n' % str(datetime.timedelta(seconds=int(time.time() - t0_test))))
        flog.debug('frun 完成 start_epoch = %s' % self.cfg.START_EPOCH)

    def ftrain(self, epoch):
        cfg = self.cfg

        # 这个在 epoch 中
        loss_val_obj = SmoothedValue()
        print('-------------------- '
              '训练 ftrain 开始 {}，IS_TRAIN={}，IS_VAL={}，IS_TEST={}，IS_DEBUG={}'
              '-------------------------'.format(
            epoch, cfg.IS_TRAIN, cfg.IS_VAL, cfg.IS_TEST, cfg.IS_DEBUG
        ))
        epoch_size = len(self.dataloader_train)
        batch = self.dataloader_train.batch_size
        title_tb_writer = 'loss_iter_train:(batch = %d，epoch_size = %d)' % (batch, epoch_size)

        scaler = GradScaler(enabled=cfg.IS_MIXTURE_FIT)

        t0 = time.time()
        for i, datas_batch in enumerate(self.dataloader_train):
            # 这里输出的是CPU 数据 dataloader 之前是多进程使用CPU兼容性好 这里需要转换
            if epoch < cfg.NUM_WARMUP and cfg.IS_WARMUP:
                now_lr = cfg.LR_BASE * pow((i + epoch * epoch_size) * 1. / (cfg.NUM_WARMUP * epoch_size), 4)
                self.update_lr(cfg.OPTIMIZER, now_lr)
            elif epoch == cfg.NUM_WARMUP:
                self.update_lr(cfg.OPTIMIZER, cfg.LR_BASE)

            with autocast(enabled=cfg.IS_MIXTURE_FIT):
                t1 = time.time()  # 前置任务完成, 数据及初始化 这个不包括进入显卡的时间
                if self.fun_loss is not None:  # 这个优先
                    # 这里是回调 多返回一个 数据时间
                    loss_total, log_dict = self.fun_loss(cfg, datas_batch, self.model)
                else:
                    # datas_batch = fun_datas_l2(datas_batch, model.fdevice)
                    loss_total, log_dict = self.model(datas_batch)

                if not math.isfinite(loss_total):  # 当计算的损失为无穷大时停止训练
                    flog.critical("Loss is {}, stopping training".format(loss_total))
                    flog.critical(log_dict)
                    sys.exit(1)
                loss_total *= 1. / cfg.FORWARD_COUNT

            # 统一添加 loss_total
            l_total_val = loss_total.item()
            log_dict['l_total'] = l_total_val
            loss_val_obj.update(l_total_val)

            scaler.scale(loss_total).backward()

            if ((i + 1) % cfg.FORWARD_COUNT) == 0:
                scaler.step(cfg.OPTIMIZER)
                scaler.update()
                if self.ema_model is not None:
                    self.ema_model.update(self.model)
                cfg.OPTIMIZER.zero_grad()

            if i % cfg.PRINT_FREQ == 0:
                self.print_log(end_epoch=cfg.END_EPOCH, epoch=epoch,
                               epoch_size=epoch_size, iter_i=i, log_dict=log_dict,
                               l_val=loss_val_obj.value, l_avg=loss_val_obj.avg,
                               lr=cfg.OPTIMIZER.param_groups[0]['lr'],
                               t0=t0, t1=t1, title='train',
                               device=self.model.fdevice, )
                pass

            if self.tb_writer is not None:
                self.tb_writing_train(tb_writer=self.tb_writer, log_dict=log_dict,
                                      iter_i=epoch_size * (epoch - 1) + i + 1,
                                      title=title_tb_writer,
                                      lr=cfg.OPTIMIZER.param_groups[0]['lr'])
                pass

            # 更新时间用于获取 data 时间
            t0 = time.time()

        if cfg.LR_SCHEDULER is not None:  # 这个必须与梯度代码在一个地方
            cfg.LR_SCHEDULER.step(epoch)  # 更新学习
        return loss_val_obj

    def update_lr(self, optimizer, now_lr):
        for param_group in optimizer.param_groups:
            param_group['lr'] = now_lr

    def print_log(self, end_epoch, epoch,
                  epoch_size, iter_i, log_dict, l_val, l_avg,
                  t0, t1, lr=math.nan, title='title',
                  device=torch.device('cpu')):
        '''

        :param end_epoch:
        :param epoch:
        :param epoch_size: 一个 epoch 需迭代的次数
        :param iter_i:  当前迭代次数
        :param log_dict:
        :param l_val:
        :param l_avg:
        :param lr: 当前学习率
        :param t0: 最开始的时间 这个是秒
        :param t1:  数据加载完成时间
        :param title:  标题
        :return:
        '''
        s = '[{title} {epoch}/{end_epoch}] ' \
            '[Iter {iter_i}/{iter_epoch}/{iter_z}] ' \
            '[lr: {lr:.6f}] (Loss:({val:.2f} /{avg:.2f} )|| {loss_str}) ' \
            '[time: d{data_time:.2f}/i{iter_time:.2f}/{residue_time}] {memory:.0f}'
        MB = 1024.0 * 1024.0

        show_loss_str = []
        for k, v, in log_dict.items():
            show_loss_str.append(
                "{}: {:.4f} ||".format(k, v)
            )

        iter_time = time.time() - t0
        residue_time = iter_time * (epoch_size - iter_i + 1)  # 剩余时间

        d = {
            'title': title,
            'epoch': epoch,
            'end_epoch': end_epoch,
            'iter_i': iter_i + 1,
            'iter_epoch': epoch_size,
            'iter_z': (epoch - 1) * epoch_size + iter_i + 1,
            'lr': lr,
            'val': l_val,
            'avg': l_avg,
            'loss_str': str(show_loss_str),
            'data_time': t1 - t0,  # 数据
            'iter_time': iter_time,  # 迭代时间
            'residue_time': str(datetime.timedelta(seconds=int(residue_time))),  # 剩余时间
            'memory': torch.cuda.max_memory_allocated() / MB if device.type == 'cuda' else math.nan,  # 只能取第一个显卡
        }

        print(s.format(**d))

    def is_open(self, epoch, nums_dict):
        '''
        是否开启 验证或测试
        :param epoch:
        :param nums_dict: NUMS_TEST_DICT = {2: 1, 35: 1, 50: 1}
        :return:
        '''

        #  {2: 1, 35: 1, 50: 1}  -> 2,35,50 ->  50,35,2
        s_keys = sorted(list(nums_dict), reverse=True)
        for s_key in s_keys:
            if epoch < s_key:
                continue
            else:
                eval_interval = nums_dict[s_key]
                if epoch % eval_interval != 0:
                    # 满足epoch 无需验证退出
                    break
                return True

    def tb_writing_train(self, tb_writer, log_dict, iter_i, title, lr=None):
        # 主进程写入   不验证时写  用于 train 和 verify
        for k, v, in log_dict.items():
            tb_writer.add_scalar('%s/%s' % (title, k), v, iter_i)
        if lr is not None:
            tb_writer.add_scalar('%s/lr' % title, lr, iter_i)

    @abstractmethod
    def ftest(self, epoch):
        # 返回 一个tuple map 和 mrp 不一定是coco
        return (0, 0)


class FitExecutorCOCO_t(FitExecutorBase):

    def __init__(self, cfg, model, fun_loss=None, fun_test=None, dataloader_train=None, dataloader_test=None) -> None:
        super().__init__(cfg, model, fun_loss, fun_test, dataloader_train, dataloader_test)
        # 这个可用于对每次 检测结果进行分析(例如找出loss高的图片) 检测过多时容易 爆内容 预留 需单独去实现
        self.is_debug = False

    def ftest(self, epoch):
        cfg = self.cfg
        print('-------------------- '
              '测试 ftest 开始 {}，IS_TRAIN={}，IS_VAL={}，IS_TEST={}，IS_DEBUG={} '
              '-------------------------'.format(
            epoch, cfg.IS_TRAIN, cfg.IS_VAL, cfg.IS_TEST, cfg.IS_DEBUG
        ))
        self.model.eval()
        loss_val_obj = SmoothedValue()
        batch = self.dataloader_test.batch_size
        epoch_size = len(self.dataloader_test)  # 迭代次数
        # tb title
        title_tb_writer = 'loss_iter_val:(batch = %d，epoch_size = %d)' % (batch, epoch_size)

        info_res4test = InfoRes4test()
        res_z = {}  # 保存 全部的coco结果

        t0 = time.time()
        for i, datas_batch in enumerate(self.dataloader_test):
            t1 = time.time()
            if self.fun_test is not None:
                # 这里的
                reses, imgs_ts_4d, targets, off_ltrb_ts, loss_total, log_dict \
                    = self.fun_test(cfg, datas_batch, self.model)
            else:
                # 由模型 FModelBase 处理数据后输出 返回的已进行完整归一化
                reses, imgs_ts_4d, targets, off_ltrb_ts, loss_total, log_dict \
                    = self.model(datas_batch)

            # 校验
            if reses is None:
                raise Exception('模型返回为空 reses')

            if cfg.IS_VAL:
                # 只要 is_val loss_val_obj 才有效
                loss_val_obj.update(loss_total.item())
                if self.tb_writer is not None:
                    self.tb_writing_train(tb_writer=self.tb_writer, log_dict=log_dict,
                                          iter_i=epoch_size * (epoch - 1) + i + 1,
                                          title=title_tb_writer, lr=None)

                if not cfg.IS_TEST:
                    # 如果没有test则 就在这里完结
                    if i % cfg.PRINT_FREQ == 0:
                        self.print_log(end_epoch=cfg.END_EPOCH, epoch=epoch,
                                       epoch_size=epoch_size, iter_i=i, log_dict=log_dict,
                                       l_val=loss_val_obj.value, l_avg=loss_val_obj.avg,
                                       t0=t0, t1=t1, title='val',
                                       device=self.model.fdevice, )
                    t0 = time.time()
                    continue

            if not cfg.IS_TEST:
                # 如果没有test
                continue

            device = imgs_ts_4d.device
            size_wh_input_ts = torch.tensor(imgs_ts_4d.shape[-2:][::-1], device=device)

            ''' 抽象方法 6个参数  res_z, log_dict, info_res4test  指针传入无需返回 '''
            self._ftest_impl(reses, batch, targets, off_ltrb_ts,
                             size_wh_input_ts, device,
                             res_z, log_dict, info_res4test)  # 具体实现

            if i % cfg.PRINT_FREQ == 0:
                self.print_log(end_epoch=cfg.END_EPOCH, epoch=epoch,
                               epoch_size=epoch_size, iter_i=i, log_dict=log_dict,
                               l_val=loss_val_obj.value, l_avg=loss_val_obj.avg,
                               t0=t0, t1=t1, title='test|val',
                               device=self.model.fdevice, )
            t0 = time.time()

        if not cfg.IS_TEST:
            return None

        if self.is_debug:  # 分析预留
            raise Exception('需要自行去实现')

        ''' 抽象方法 '''
        res_coco_standard = self.convert_coco(res_z)

        if len(res_coco_standard) > 0:  # 有 coco 结果
            ''' 抽象方法 '''
            maps_val, coco_stats = self.run_cocoeval(
                dataloader_test=self.dataloader_test,
                ids_data_all=info_res4test.ids_img,
                res_coco_standard=res_coco_standard,
                kpt_oks_sigmas=cfg.KPT_OKS_SIGMAS,
            )
        else:
            # 没有 coco 结果
            maps_val = [0, 0]
            coco_stats = None

        if self.tb_writer is not None:
            nums_pos_np = np.array(info_res4test.nums_pos)
            num_no_pos = (nums_pos_np == 0).sum()
            _d = {
                'num_no_pos': num_no_pos,  # 未检出的图片数量
            }
            ''' 抽象方法 '''
            self.tr_writing_test4coco(epoch=epoch, log_dict=_d,
                                      tb_writer=self.tb_writer,
                                      coco_stats=coco_stats)
        # 返回 一个tuple map 和 mrp
        return maps_val

    @abstractmethod
    def _ftest_impl(self, reses, batch, targets, off_ltrb_ts,
                    size_wh_input_ts, device,
                    res_z, log_dict, info_res4test):
        # 这个无需返回  核心参数 用的是指针
        pass

    @abstractmethod
    def convert_coco(self, res_z):
        # 这里转换 res_coco_standard 格式 返回 res_coco_standard FitExecutor4OD
        return []

    @abstractmethod
    def run_cocoeval(self, dataloader_test, ids_data_all, res_coco_standard, kpt_oks_sigmas):
        # maps_val, coco_stats:size(12)  参考 FitExecutor4OD
        return [0, 0], []

    @abstractmethod
    def tr_writing_test4coco(self, epoch, log_dict, tb_writer, coco_stats):
        # 测试完成 写记录
        pass


class FitExecutor4OD(FitExecutorCOCO_t):

    def __init__(self, cfg, model, fun_loss=None, fun_test=None, dataloader_train=None, dataloader_test=None) -> None:
        super().__init__(cfg, model, fun_loss, fun_test, dataloader_train, dataloader_test)

    def set_info_res4test(self, info_res4test, log_dict, id_img, is_no_pos=False, **kargs):
        info_res4test.ids_img.append(id_img)  # 全局
        if is_no_pos:
            info_res4test.nums_pos.append(0)
            info_res4test.scores_max.append(0)
            info_res4test.scores_mean.append(0)
            info_res4test.scores_min.append(0)
        else:
            info_res4test.nums_pos.append(kargs['num_pos'])
            info_res4test.scores_max.append(kargs['score_max'])
            info_res4test.scores_mean.append(kargs['score_mean'])
            info_res4test.scores_min.append(kargs['score_min'])

        if log_dict is None:
            return

        # 一批的loss是一样的
        for k, v in log_dict.items():
            info_res4test.__setattr__(k, v)

    def _ftest_impl(self, reses, batch, targets, off_ltrb_ts,
                    size_wh_input_ts, device,
                    res_z, log_dict, info_res4test):
        '''
        这里是每一批迭代中
        :param reses:
        :param batch:
        :param targets:
        :param off_ltrb_ts:
        :param size_wh_input_ts:
        :param device:
        :param log_dict: 共享内存
        :return:
        '''
        cfg = self.cfg
        num_no_pos_batch = 0  # 这个需要返回

        # 这里在dataloader 的迭代之中
        # 这里输出的都是归一化尺寸
        ids_batch, p_ltrbs, p_kps, p_labels, p_scores = reses

        # if log_dict is None:
        #     log_dict = {}

        ''' 整批没有目标 提示和处理 '''
        if p_labels is None or len(p_labels) == 0:
            for target in targets:  # 通过target 提取ID 和 size
                # ids_img_batch.append(target['image_id'])
                self.set_info_res4test(info_res4test, log_dict,
                                       target['image_id'], is_no_pos=True)

            # 这里可以加整批检测失败的次数 进行退出
            return

        res_batch = {}  # 每一批的coco 结果
        # 每一张图的 id 与批次顺序保持一致 选出匹配
        for j, target in enumerate(targets):
            # 取出该批第j张图所有的 POS
            mask = ids_batch == j  # 构建 batch 次的mask
            ''' 单张图没有目标 计数提示 '''
            if not torch.any(mask):
                # flog.warning('没有预测出框 %s', files_txt)
                num_no_pos_batch += 1
                self.set_info_res4test(info_res4test, log_dict,
                                       target['image_id'], is_no_pos=True)
            else:
                ''' 已检出 是否可视化逻辑 '''
                if cfg.IS_VISUAL or self.num_vis_now < cfg.NUM_VIS_Z:
                    self.num_vis_now += 1
                    if 'boxes' not in target:
                        flog.warning('该图没有GT,但是被检出 %s' % targets[j])
                        self.show_pic(dataloader_test=self.dataloader_test,
                                      size_wh_input_ts=size_wh_input_ts.cpu(),
                                      off_ltrb_ts_f=off_ltrb_ts[j].cpu(),
                                      gltrb_f=None,
                                      image_id=target['image_id'],
                                      p_labels_pos=p_labels[mask].cpu(),
                                      p_ltrbs_pos=p_ltrbs[mask].cpu(),
                                      p_scores_pos=p_scores[mask].cpu())
                    else:
                        self.show_pic(dataloader_test=self.dataloader_test,
                                      size_wh_input_ts=size_wh_input_ts.cpu(),
                                      off_ltrb_ts_f=off_ltrb_ts[j].cpu(),
                                      gltrb_f=targets[j]['boxes'].cpu(),
                                      image_id=target['image_id'],
                                      p_labels_pos=p_labels[mask].cpu(),
                                      p_ltrbs_pos=p_ltrbs[mask].cpu(),
                                      p_scores_pos=p_scores[mask].cpu())

                # size_wh_f_ts_batch = []  # 用于修复box
                # for target in targets:  # 通过target 提取ID 和 size
                #     size_wh_f_ts_batch.append(target['size'].to(device))  # tnesor
                size_wh_f_ts = target['size'].to(device)
                # 归一化->file尺寸  coco需要 ltwh
                boxes_ltwh = ltrb2ltwh(p_ltrbs[mask] * size_wh_f_ts.repeat(2)[None])
                res_batch[target['image_id']] = {
                    'boxes': boxes_ltwh.cpu(),  # coco loadRes 会对ltwh 转换成 ltrb
                    'labels': p_labels[mask].cpu(),
                    'scores': p_scores[mask].cpu(),
                }

                p_scores_j = p_scores[mask]
                _d = {
                    'num_pos': len(boxes_ltwh),
                    'score_max': p_scores_j.max().item(),
                    'score_mean': p_scores_j.mean().item(),
                    'score_min': p_scores_j.min().item(),
                }
                self.set_info_res4test(info_res4test, log_dict,
                                       target['image_id'], False,
                                       **_d)

        res_z.update(res_batch)
        return

    def run_cocoeval(self, dataloader_test, ids_data_all, res_coco_standard, kpt_oks_sigmas=None):
        maps_val = []

        coco_gt = dataloader_test.dataset.coco_obj
        # 第一个元素指示操作该临时文件的安全级别，第二个元素指示该临时文件的路径
        _, tmp = tempfile.mkstemp()  # 创建临时文件
        json.dump(res_coco_standard, open(tmp, 'w'))
        coco_dt = coco_gt.loadRes(tmp)
        '''
                    _summarizeDets()->_summarize()
                        _summarizeDets 函数中调用了12次 _summarize
                        结果在 self.eval['precision'] , self.eval['recall']中
                    '''
        coco_eval_obj = FCOCOeval(copy.deepcopy(coco_gt), copy.deepcopy(coco_dt), 'bbox')  # 这个添加了每个类别的map分
        # coco_eval_obj = COCOeval(coco_gt, coco_dt, ann_type)
        coco_eval_obj.params.imgIds = ids_data_all  # 多显卡id合并更新
        coco_eval_obj.evaluate()
        coco_eval_obj.accumulate()
        coco_stats, print_coco = coco_eval_obj.summarize()
        coco_eval_obj.stats = coco_stats
        print(print_coco)
        clses_name = list(dataloader_test.dataset.classes_ids)
        coco_eval_obj.print_clses(clses_name)
        maps_val.append(coco_eval_obj.stats[1])  # 添加ap50
        maps_val.append(coco_eval_obj.stats[7])
        coco_stats = coco_eval_obj.stats
        return maps_val, coco_stats

    def show_pic(self, dataloader_test, size_wh_input_ts,
                 off_ltrb_ts_f, gltrb_f,
                 image_id,
                 p_labels_pos, p_ltrbs_pos, p_scores_pos):
        '''

        :param dataloader_test:
        :param size_wh_input_ts:
        :param off_ltrb_ts_f:  这个是1D [4]
        :param gltrb_f:
        :param image_id:
        :return:
        '''

        coco = dataloader_test.dataset.coco_obj
        img_info = coco.loadImgs([image_id])
        file_img = os.path.join(dataloader_test.dataset.path_img, img_info[0]['file_name'])
        img_np_file = cv2.imread(file_img)
        img_np_file = cv2.cvtColor(img_np_file, cv2.COLOR_BGR2RGB)
        # import skimage.io as io
        # h,w,c
        # img_np = io.imread(file_img)

        # p归一化
        size_wh_f_ts = torch.tensor(img_np_file.shape[:2][::-1])
        size_wh_f_ts_x2 = size_wh_f_ts.repeat(2)  # 图片真实尺寸
        p_boxes_ltrb_f = p_ltrbs_pos * size_wh_f_ts_x2

        # g归一化
        size_wh_toone_ts = size_wh_input_ts - off_ltrb_ts_f[:2] - off_ltrb_ts_f[2:]
        # 平移 [nn,4]  [4] -> [1,4]
        if gltrb_f is None:
            # 有没有标注的图片情况
            gltrb_ = gltrb_f
        else:
            gltrb_ = gltrb_f - off_ltrb_ts_f.view(1, -1)
            gltrb_ = gltrb_ / size_wh_toone_ts.repeat(2).squeeze(0) * size_wh_f_ts.repeat(2).squeeze(0)

        p_texts = []
        for i, p_label in enumerate(p_labels_pos):
            name_cat = dataloader_test.dataset.ids_classes[(p_label.long()).item()]
            s = name_cat + ':' + str(round(p_scores_pos[i].item(), 2))
            p_texts.append(s)

        title_text = '%s x %s (num_pos = %s) max=%s' % (str(img_np_file.shape[1]),  # w
                                                        str(img_np_file.shape[0]),  # h
                                                        str(len(p_boxes_ltrb_f)),
                                                        str(round(p_scores_pos.max().item(), 2))
                                                        )

        f_show_od_np4plt_v3(
            img_np_file, p_ltrb=p_boxes_ltrb_f,
            title=title_text,
            g_ltrb=gltrb_,
            p_texts=p_texts,
            is_recover_size=False,
        )

    def convert_coco(self, res_z):
        # 标准化coco结果数据
        res_coco_standard = []  # 最终的 coco 标准格式 一个ID可能 有多个目标
        # res_z 每一个ID可能有多个目标 每个目标形成一条 id对应数据
        for i, (image_id, g_target) in enumerate(res_z.items()):
            labels = g_target['labels'].type(torch.int).tolist()
            boxes_ltwh = g_target['boxes'].tolist()
            score = g_target['scores'].tolist()
            for i in range(len(labels)):
                # catid转换
                category_id = self.dataloader_test.dataset.classes_train2coco[labels[i]]
                res_coco_standard.append(
                    {"image_id": image_id, "category_id": category_id, "bbox": boxes_ltwh[i], "score": score[i]})
        return res_coco_standard

    def tr_writing_test4coco(self, epoch, log_dict, tb_writer, coco_stats):
        # 一个图只有一个值
        title = 'mAP'

        if coco_stats is not None:
            _d = {
                'IoU=0.50:0.95': coco_stats[0],
                'IoU=0.50': coco_stats[1],
                'IoU=0.75': coco_stats[2],
            }
            tb_writer.add_scalars(title + '/Precision_iou', _d, epoch)
            # Recall_iou
            _d = {
                'maxDets=  1': coco_stats[6],
                'maxDets= 10': coco_stats[7],
                'maxDets=100': coco_stats[8],
            }
            tb_writer.add_scalars(title + '/Recall_iou', _d, epoch)
            # 小中大
            _d = {
                'p_large': coco_stats[5],
                'r_large': coco_stats[11],
            }
            tb_writer.add_scalars(title + '/large', _d, epoch)
            _d = {
                'p_medium': coco_stats[4],
                'r_medium': coco_stats[10],
            }
            tb_writer.add_scalars(title + '/medium', _d, epoch)
            _d = {
                'p_small': coco_stats[3],
                'r_small': coco_stats[9],
            }
            tb_writer.add_scalars(title + '/small', _d, epoch)

        for k, v, in log_dict.items():
            tb_writer.add_scalar('%s/%s' % (title, k), v, epoch)


class FitExecutor4KPS(FitExecutorCOCO_t):

    def __init__(self, cfg, model, fun_loss=None, fun_test=None, dataloader_train=None, dataloader_test=None) -> None:
        super().__init__(cfg, model, fun_loss, fun_test, dataloader_train, dataloader_test)

    def set_info_res4test(self, info_res4test, log_dict, id_img, is_no_pos=False, **kargs):
        info_res4test.ids_img.append(id_img)  # 全局
        if is_no_pos:
            info_res4test.nums_pos.append(0)
            info_res4test.scores_max.append(0)
            info_res4test.scores_mean.append(0)
            info_res4test.scores_min.append(0)
        else:
            info_res4test.nums_pos.append(kargs['num_pos'])
            info_res4test.scores_max.append(kargs['score_max'])
            info_res4test.scores_mean.append(kargs['score_mean'])
            info_res4test.scores_min.append(kargs['score_min'])

        if log_dict is None:
            return

        # 一批的loss是一样的
        for k, v in log_dict.items():
            info_res4test.__setattr__(k, v)

    def _ftest_impl(self, reses, batch, targets, off_ltrb_ts,
                    size_wh_input_ts, device,
                    res_z, log_dict, info_res4test):
        '''

        :param reses:
        :param batch:
        :param targets:
        :param off_ltrb_ts:
        :param size_wh_input_ts: input尺寸
        :param device:
        :param log_dict: 共享内存
        :return:
        '''
        cfg = self.cfg
        num_no_pos_batch = 0  # 这个需要返回

        # 这里在dataloader 的迭代之中
        # 这里输出的都是归一化尺寸
        ids_batch, p_ltrbs, p_kps, p_labels, p_scores = reses

        # if log_dict is None:
        #     log_dict = {}

        ''' 整批没有目标 提示和处理 '''
        if p_labels is None or len(p_labels) == 0:
            for target in targets:  # 通过target 提取ID 和 size
                # ids_img_batch.append(target['image_id'])
                self.set_info_res4test(info_res4test, log_dict,
                                       target['image_id'], is_no_pos=True)

            # 这里可以加整批检测失败的次数 进行退出
            return

        res_batch = {}  # 每一批的coco 结果
        # 每一张图的 id 与批次顺序保持一致 选出匹配
        for j, target in enumerate(targets):
            # 取出该批第j张图所有的 POS
            mask = ids_batch == j  # 构建 batch 次的mask
            ''' 单张图没有目标 计数提示 '''
            if not torch.any(mask):
                # flog.warning('没有预测出框 %s', files_txt)
                num_no_pos_batch += 1
                self.set_info_res4test(info_res4test, log_dict,
                                       target['image_id'], is_no_pos=True)
            else:
                ''' 已检出 是否可视化逻辑 '''
                if cfg.IS_VISUAL or self.num_vis_now < cfg.NUM_VIS_Z:
                    self.num_vis_now += 1
                    self.show_pic(dataloader_test=self.dataloader_test,
                                  size_wh_input_ts=size_wh_input_ts.cpu(),
                                  off_ltrb_ts=off_ltrb_ts[j].cpu(),
                                  target=target,
                                  p_labels_pos=p_labels[mask].cpu(),
                                  p_ltrbs_pos=p_ltrbs[mask].cpu() if p_ltrbs is not None else None,
                                  p_scores_pos=p_scores[mask].cpu(),
                                  p_kps_pos=p_kps[mask].cpu(),
                                  kps_seq=cfg.DATA_INFO.kps_seq,
                                  )

                # size_wh_f_ts_batch = []  # 用于修复box
                # for target in targets:  # 通过target 提取ID 和 size
                #     size_wh_f_ts_batch.append(target['size'].to(device))  # tnesor
                size_wh_f_ts = target['size'].to(device)
                # 归一化->file尺寸  coco需要 ltwh [3, 14, 3] -> [1, 14, 3]
                p_kps_f = p_kps[mask]
                p_kps_f[..., :2] = p_kps_f[..., :2] * size_wh_f_ts
                res_batch[target['image_id']] = {
                    'category_id': p_labels[mask].cpu(),  # coco loadRes 会对ltwh 转换成 ltrb
                    'keypoints': p_kps_f.reshape(p_kps_f.shape[0], -1).cpu(),  # 转 kps_l
                    'scores': p_scores[mask].cpu(),
                }

                p_scores_j = p_scores[mask]
                _d = {
                    'num_pos': len(p_kps_f),
                    'score_max': p_scores_j.max().item(),
                    'score_mean': p_scores_j.mean().item(),
                    'score_min': p_scores_j.min().item(),
                }
                self.set_info_res4test(info_res4test, log_dict,
                                       target['image_id'], False,
                                       **_d)

        res_z.update(res_batch)
        return

    def show_pic(self, dataloader_test, size_wh_input_ts,
                 off_ltrb_ts, target,
                 p_labels_pos, p_ltrbs_pos, p_scores_pos, p_kps_pos,
                 kps_seq=None,
                 ):
        '''

        :param dataloader_test:
        :param size_wh_input_ts:
        :param off_ltrb_ts:
        :param p_labels_pos:
        :param p_ltrbs_pos: 这里是归一化尺寸
        :param p_scores_pos:
        :param p_kps_pos:
        :return:
        '''
        # 通过coco读取file图片
        coco = dataloader_test.dataset.coco_obj
        img_info = coco.loadImgs(target['image_id'])
        file_img = os.path.join(dataloader_test.dataset.path_img, img_info[0]['file_name'])
        img_np_file = cv2.imread(file_img)
        img_np_file = cv2.cvtColor(img_np_file, cv2.COLOR_BGR2RGB)

        p_kps_f = p_kps_pos.clone()

        # 尺寸归一化恢复
        size_wh_f_ts = torch.tensor(img_np_file.shape[:2][::-1])  # [2]
        if p_ltrbs_pos is not None:
            size_wh_f_ts_x2 = size_wh_f_ts.repeat(2)  # 图片真实尺寸
            p_ltrb_f = p_ltrbs_pos * size_wh_f_ts_x2
        else:
            p_ltrb_f = None
        p_kps_f[..., :2] = p_kps_pos[..., :2] * size_wh_f_ts

        # GT 归一化真实尺寸
        size_wh_input2one_ts = size_wh_input_ts - off_ltrb_ts[:2] - off_ltrb_ts[2:]
        # 平移 [nn,4]  [4] -> [1,4]
        if 'boxes' not in target:
            # 有没有标注的图片情况
            gltrb_f = None
        else:
            gltrb_f = target['boxes'] - off_ltrb_ts[:2].repeat(2).view(1, -1)
            gltrb_f = gltrb_f / size_wh_input2one_ts.repeat(2).squeeze(0) \
                      * size_wh_f_ts.repeat(2).squeeze(0)
        if 'kps' not in target:
            g_kps_f = None
        else:
            _kps, mask = fsplit_kps(target['kps'])
            _kps = torch.tensor(_kps)
            g_kps_f = _kps.clone()
            g_kps_f[..., :2] = (_kps[..., :2] - off_ltrb_ts[:2].view(1, -1)) \
                               / size_wh_input2one_ts \
                               * size_wh_f_ts

        p_texts = []
        for i, p_label in enumerate(p_labels_pos):
            name_cat = dataloader_test.dataset.ids_classes[(p_label.long()).item()]
            s = name_cat + ':' + str(round(p_scores_pos[i].item(), 2))
            p_texts.append(s)

        title_text = '%s x %s (num_pos = %s) max=%s' % (str(img_np_file.shape[1]),  # w
                                                        str(img_np_file.shape[0]),  # h
                                                        str(len(p_kps_f[p_kps_f[..., 2] != 0])),
                                                        str(round(p_scores_pos.max().item(), 2))
                                                        )
        f_show_kp_np4cv(img_np_file,
                        p_kps_l=p_kps_f.reshape(p_kps_f.shape[0], -1).numpy(),  # 转换 kps_l
                        g_kps_l=g_kps_f.reshape(g_kps_f.shape[0], -1).numpy(),  # 转换 kps_l
                        kps_seq=kps_seq,
                        title=title_text,
                        g_ltrb=gltrb_f,
                        p_ltrb=p_ltrb_f,
                        p_texts=p_texts,
                        is_color_same=True,
                        )

    def convert_coco(self, res_z):
        # 标准化coco结果数据  一个图片可能 有多个 coco
        res_coco_standard = []  # 最终的 coco 标准格式 一个ID可能 有多个目标
        # res_z 每一个ID可能有多个目标 每个目标形成一条 id对应数据
        for i, (image_id, g_target) in enumerate(res_z.items()):
            labels = g_target['category_id'].type(torch.int).tolist()
            kps_ls = g_target['keypoints'].tolist()
            score = g_target['scores'].tolist()
            for i in range(len(labels)):
                # catid转换
                category_id = labels[i]  # 这里无需转换
                res_coco_standard.append(
                    {"image_id": image_id,
                     "category_id": category_id,
                     "keypoints": kps_ls[i],
                     "score": score[i]})
        return res_coco_standard

    def run_cocoeval(self, dataloader_test, ids_data_all, res_coco_standard, kpt_oks_sigmas):
        maps_val = []
        mode_test = 'keypoints'  # 'segm', 'bbox', 'keypoints'

        coco_gt = dataloader_test.dataset.coco_obj
        # 第一个元素指示操作该临时文件的安全级别，第二个元素指示该临时文件的路径
        _, tmp = tempfile.mkstemp()  # 创建临时文件
        json.dump(res_coco_standard, open(tmp, 'w'))
        coco_dt = coco_gt.loadRes(tmp)
        '''
                    _summarizeDets()->_summarize()
                        _summarizeDets 函数中调用了12次 _summarize
                        结果在 self.eval['precision'] , self.eval['recall']中
                    '''
        # coco_eval_obj = FCOCOeval(copy.deepcopy(coco_gt), copy.deepcopy(coco_dt), mode_test)  # 这个添加了每个类别的map分
        coco_eval_obj = COCOeval(coco_gt, coco_dt, mode_test)
        coco_eval_obj.params.imgIds = ids_data_all  # 多显卡id合并更新
        coco_eval_obj.params.kpt_oks_sigmas = kpt_oks_sigmas
        # coco_eval_obj.params.kpt_oks_sigmas = np.array([.26, .25, .25, .26, .26, ]) / 10.0

        coco_eval_obj.evaluate()
        coco_eval_obj.accumulate()
        coco_eval_obj.summarize()
        maps_val.append(coco_eval_obj.stats[1])  # 添加ap50
        maps_val.append(coco_eval_obj.stats[6])
        coco_stats = coco_eval_obj.stats
        return maps_val, coco_stats

    def tr_writing_test4coco(self, epoch, log_dict, tb_writer, coco_stats):
        # 一个图只有一个值
        title = 'mAP'

        if coco_stats is not None:
            _d = {
                'IoU=0.50:0.95': coco_stats[0],
                'IoU=0.50': coco_stats[1],
                'IoU=0.75': coco_stats[2],
            }
            tb_writer.add_scalars(title + '/Precision_iou', _d, epoch)
            # Recall_iou
            _d = {
                'maxDets=  1': coco_stats[5],
                'maxDets= 10': coco_stats[6],
                'maxDets=100': coco_stats[7],
            }
            tb_writer.add_scalars(title + '/Recall_iou', _d, epoch)
            # 小中大
            _d = {
                'p_large': coco_stats[4],
                'r_large': coco_stats[9],
            }
            tb_writer.add_scalars(title + '/large', _d, epoch)
            _d = {
                'p_medium': coco_stats[3],
                'r_medium': coco_stats[8],
            }
            tb_writer.add_scalars(title + '/medium', _d, epoch)

        for k, v, in log_dict.items():
            tb_writer.add_scalar('%s/%s' % (title, k), v, epoch)


class SmoothedValue:
    """
    记录一系列统计量
    Track a series of values and provide access to smoothed values over a
    window or the global series average.
    """

    def __init__(self, window_size=20, fmt=None):
        if fmt is None:
            fmt = "{median:.4f} ({global_avg:.4f})"
        self.deque = deque(maxlen=window_size)  # deque简单理解成加强版list
        self.total = 0.0
        self.count = 0
        self.fmt = fmt

    def update(self, value, n=1):
        self.deque.append(value)
        self.count += n
        self.total += value * n

    # def synchronize_between_processes(self):
    #     """
    #     Warning: does not synchronize the deque!
    #     """
    #     if not fis_mgpu():
    #         return
    #     t = torch.tensor([self.count, self.total], dtype=torch.float64, device="cuda")
    #     dist.barrier()
    #     dist.all_reduce(t)
    #     t = t.tolist()
    #     self.count = int(t[0])
    #     self.total = t[1]

    @property
    def median(self):  # @property 是装饰器，这里可简单理解为增加median属性(只读)
        d = torch.tensor(list(self.deque))
        return d.median().item()

    @property
    def avg(self):
        if len(self.deque) == 0:
            return math.nan
        d = torch.tensor(list(self.deque), dtype=torch.float32)
        return d.mean().item()

    @property
    def global_avg(self):
        return self.total / self.count

    @property
    def max(self):
        if len(self.deque) == 0:
            return math.nan
        return max(self.deque)

    @property
    def value(self):
        if len(self.deque) == 0:
            return math.nan
        return self.deque[-1]

    def __str__(self):
        return self.fmt.format(
            median=self.median,
            avg=self.avg,
            global_avg=self.global_avg,
            max=self.max,
            value=self.value)
