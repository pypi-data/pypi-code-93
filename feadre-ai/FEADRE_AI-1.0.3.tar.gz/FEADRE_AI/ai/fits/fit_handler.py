import datetime
import os
import random
import sys
import time
from abc import abstractmethod

import cv2
import matplotlib
import numpy as np
import onnxruntime
import torch
from torch.backends import cudnn

from ftools.GLOBAL_LOG import flog
from ftools.ai.fits.f_fit_tools import SmoothedValue, FitExecutorBase, FitExecutor4OD, FitExecutor4KPS
from ftools.ai.picture.f_show import f_show_od_np4plt_v3, draw_text_chinese4cv
from ftools.f_general import get_img_file
from ftools.ai.fits.f_predictfun import batch_nms_v2
from ftools.general.fsys.fcamera import init_video


class DispatchTask:
    def __init__(self, fun_task_cfg=None) -> None:
        super().__init__()
        self.init_sys(None)
        self.fun_task_cfg = fun_task_cfg

    def init_sys(self, cfg):
        # -----------通用系统配置----------------
        # format short g, %precision=5
        torch.set_printoptions(linewidth=320, sci_mode=False, precision=5, profile='long')
        np.set_printoptions(linewidth=320, suppress=True, formatter={'float_kind': '{:11.5g}'.format})
        # 修改配置文件
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 设置matplotlib可以显示汉语
        matplotlib.rcParams['axes.unicode_minus'] = False
        matplotlib.rcParams['font.size'] = 11
        # matplotlib.rc('font', **{'size': 11})

        # try:
        #     # 对windwos进行限制防止出错  by yolox
        #     import resource  # 这个模块没有
        #     rlimit = resource.getrlimit(resource.RLIMIT_NOFILE)
        #     resource.setrlimit(resource.RLIMIT_NOFILE, (8192, rlimit[1]))
        # except Exception as e:
        #     # Exception might be raised in Windows OS or rlimit reaches max limit number.
        #     # However, set rlimit value might not be necessary.
        #     raise e

        # --- pytorch 系统加速 ---
        torch.multiprocessing.set_sharing_strategy('file_system')  # 多GPU必须开 实测加速
        os.environ["OPENCV_OPENCL_RUNTIME"] = "disabled"  # by yolox
        try:
            # by yolox
            cv2.setNumThreads(0)  # 加速 防止OpenCV进入多线程(使用PyTorch DataLoader)
            cv2.ocl.setUseOpenCL(False)
        except Exception as e:
            # cv2 version mismatch might rasie exceptions.
            raise e
        seed = 0
        # 随机种子
        np.random.seed(seed)
        random.seed(seed)
        # from yolo5 Speed-reproducibility tradeoff https://pytorch.org/docs/stable/notes/randomness.html
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            cudnn.deterministic = True
            if seed == 0:  # slower, more reproducible
                cudnn.benchmark, cudnn.deterministic = False, True
            else:  # faster, less reproducible
                cudnn.benchmark, cudnn.deterministic = True, False

    def show_args(self, cfg):
        '''
        重要参数显示
        本方法 参数在 cfg 中具备较强依赖  不适合通用

        :param cfg:
        :return:
        '''
        if cfg.IS_WRITER:
            if cfg.KEEP_WRITER is not None:
                tb_writer_info = cfg.KEEP_WRITER
            else:
                tb_writer_info = '开,随机目录'
        else:
            tb_writer_info = False

        if cfg.IS_WARMUP:
            warmup_info = cfg.NUM_WARMUP
        else:
            warmup_info = False

        if cfg.IS_MULTI_SCALE:
            size = '多尺度: ' + str(cfg.MULTI_SCALE_VAL)
        else:
            size = cfg.SIZE_WH_INPUT_TRAIN

        _text_dict = {
            'dataset_name': cfg.DATA_INFO.dataset_name,
            'tb_writer_info': tb_writer_info,
            'device': cfg.DEVICE,
            'num_vis_z': cfg.NUM_VIS_Z,
            'num_workers': cfg.NUM_WORKERS,
            'path_save_weight': cfg.PATH_SAVE_WEIGHT,
            'warmup_info': warmup_info,
            'is_visual': cfg.IS_VISUAL,
            'size': size,
            'batch_train': cfg.DATA_INFO.batch_train,
            'mode_train': cfg.DATA_INFO.mode_train,
            'ema': cfg.IS_EMA,
            'maps_def_max': cfg.MAPS_DEF_MAX,
            'is_mosaic': cfg.IS_MOSAIC,
            'is_mixup': cfg.IS_MIXUP,
        }

        separator = '  \n'
        for k, v in _text_dict.items():
            _text_dict[k] = str(v) + separator

        # 遍历转str + 分隔

        # _text = '--- 训练类 ---\n'.format(**_text_dict)

        _text1 = '----------------- 系统类 ---------------\n' \
                 '\t 当前数据集: {dataset_name}' \
                 '\t 当前设备: {device}' \
                 '\t 权重路径: {path_save_weight}' \
                 '\t tb_writer: {tb_writer_info}' \
                 '\t num_workers: {num_workers}' \
                 '\t WARMUP: {warmup_info}' \
                 '\t IS_VISUAL: {is_visual}' \
                 '\t size: {size}' \
                 '\t 上限AP: {maps_def_max}'

        _text2 = '----------------- 训练类 -----------------\n' \
                 '\t batch:{batch_train}' \
                 '\t mode_train:{mode_train}' \
                 '\t ema:{ema}' \
                 '\t IS_MOSAIC:{is_mosaic}' \
                 '\t IS_MIXUP:{is_mixup}'

        _text3 = '----------------- 测试类 -----------------\n' \
                 '\t NUM_VIS_Z:{num_vis_z}'

        show_text = (_text1 + _text2 + _text3).format(**_text_dict)
        print(show_text)

    def run_train(self):
        t00 = time.time()
        cfg, model, fun_loss, fun_test, dataloader_train, dataloader_test \
            = self.fun_task_cfg()

        self.show_args(cfg)

        ''' --------------- 启动 --------------------- '''
        # 'segm', 'bbox', 'keypoints'
        if cfg.DATA_INFO.mode_test == 'keypoints':
            executor = FitExecutor4KPS(cfg, model=model,
                                       fun_loss=fun_loss, fun_test=fun_test,
                                       dataloader_train=dataloader_train,
                                       dataloader_test=dataloader_test, )
            pass
        elif cfg.DATA_INFO.mode_test == 'bbox':
            executor = FitExecutor4OD(cfg, model=model,
                                      fun_loss=fun_loss, fun_test=fun_test,
                                      dataloader_train=dataloader_train,
                                      dataloader_test=dataloader_test,
                                      )
        elif cfg.DATA_INFO.mode_test == 'segm':
            raise Exception('暂不支持 %s' % cfg.DATA_INFO.mode_test)
        else:
            raise Exception('暂不支持 %s' % cfg.DATA_INFO.mode_test)

        executor.frun()

        time_text = str(datetime.timedelta(seconds=int(time.time() - t00)))
        return time_text


''' ----------------- 检测任务执行者 --------------------- '''


class DetectTaskBase:

    def __init__(self, mode_detect, data_transform, device, ids_classes,
                 model=None, path_pic=None, video_address=0, is_show_res=True,
                 ) -> None:
        '''

        :param mode_detect: video  pic  webcam
        :param data_transform:
        :param device:
        :param ids_classes:
        :param path_pic:
        :param video_address: 视频地址
        '''
        super().__init__()
        self.model = model
        self.mode_detect = mode_detect
        self.data_transform = data_transform
        self.device = device
        self.ids_classes = ids_classes
        self.path_pic = path_pic
        self.video_address = video_address
        self.is_show_res = is_show_res

        self._init_args()

    def detect(self):
        if self.mode_detect == 'pic':
            files_pic = self.examine_path_pic()
            for file in files_pic:
                # 在 reses 中处理返回值
                # 计时在里面单独计时从打开文件开始 因为显示时间除外
                reses = self.detect4pic(file=file)

        elif self.mode_detect == 'video':
            cap = init_video(det=self.video_address)
            self.is_show_res = False  # 视频时图形显示 必须关闭
            reses = self.detect4video(cap=cap)

        flog.info('%s 模式 detect 运行完成' % self.mode_detect)

    def examine_path_pic(self):
        if self.path_pic is not None and os.path.exists(self.path_pic):
            if os.path.isdir(self.path_pic):
                files_pic = get_img_file(self.path_pic)
            elif os.path.isfile(self.path_pic):
                files_pic = [self.path_pic]
            else:
                raise Exception('path_pic 有问题 %s' % self.path_pic)
        else:
            raise Exception('path_pic 不存在 %s' % self.path_pic)

        if len(files_pic) == 0:
            raise Exception('path_pic 路径没有图片 %s' % self.path_pic)

        return files_pic

    def _init_args(self):
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 设置matplotlib可以显示汉语
        matplotlib.rcParams['axes.unicode_minus'] = False
        matplotlib.rcParams['font.size'] = 11

    def get_reses_z(self, img_np_file, reses_detect):
        '''
        强关联  get_detect_reses 方法 否则复写
        :param reses_detect:
        :return:
        '''
        if reses_detect is None:
            # flog.debug('没有目标 %s', )
            # sys.exit(-1)
            return None
        else:
            # 一次只有一张 ids_batch 无用
            ids_batch, p_ltrb_one, p_labels, p_scores = reses_detect
            if len(p_labels) == 0:
                # 没有目标
                return None

            size_wh_file = np.array(img_np_file.shape[:2][::-1])
            size_wh_file_x2 = np.tile(size_wh_file, 2)
            # if isinstance(p_ltrb_one, torch.Tensor):
            #     size_wh_file_x2 = torch.tensor(size_wh_file_x2)
            p_boxes_ltrb_f = p_ltrb_one * size_wh_file_x2
            # 这个待后续可处理成json返回
            title_text, p_texts = self.cre_title_text(size_wh_file=size_wh_file,
                                                      p_boxes_ltrb_f=p_boxes_ltrb_f,
                                                      p_labels=p_labels,
                                                      p_scores=p_scores,
                                                      img_np_file=img_np_file,
                                                      )

        return p_boxes_ltrb_f, p_labels, p_scores, title_text, p_texts

    def cre_title_text(self, size_wh_file, p_boxes_ltrb_f, p_labels, p_scores, img_np_file, ):
        '''
        这个用于创建检测结果的文本
        :return:
        '''
        title_text = '%s x %s (num_pos = %s) max=%s' % (str(size_wh_file[0]),  # w
                                                        str(size_wh_file[1]),  # h
                                                        str(len(p_scores)),
                                                        str(round(p_scores.max().cpu().item(), 2))
                                                        )
        p_texts = []
        for i, p_label in enumerate(p_labels):
            s = self.ids_classes[str(p_label.long().item())] + ':' + str(round(p_scores[i].cpu().item(), 2))
            p_texts.append(str(s))

        if self.is_show_res:
            f_show_od_np4plt_v3(img_np_file, p_ltrb=p_boxes_ltrb_f,
                                title=title_text, p_texts=p_texts,
                                is_recover_size=False)
        return title_text, p_texts

    def print_time(self, t00, p_labels):
        t01 = time.time()
        _text_dict = {
            'time': t01 - t00,
            'num_pos': 0 if p_labels is None else len(p_labels)
        }
        print('检测时间: {time:0.4f} 共有 {num_pos} 个目标'.format(**_text_dict))

    @abstractmethod
    def detect4pic(self, file):
        pass

    def detect4video(self, cap):
        fps = 0.0
        count = 0
        num_out = 0
        while cap.isOpened():
            start_time = time.time()
            '''---------------数据加载及处理--------------'''
            ref, img_np_file = cap.read()  # 读取某一帧 ref是否成功
            if not ref:
                if num_out >= 3:
                    raise Exception('cap 读取出错~~~num_out=%s' % num_out)
                num_out += 1
                flog.error('cap 读取出错，再试')
                continue

            reses_detect = self.get_detect_reses(img_np_file)
            reses_z = self.get_reses_z(img_np_file, reses_detect)
            if reses_z is None:
                img_np = img_np_file
                title_text = 'no target!!!'
            else:
                p_boxes_ltrb_f, p_labels, p_scores, title_text, p_texts = reses_z
                if len(p_labels) == 0:
                    img_np = img_np_file
                    title_text = 'no target!!!'
                else:
                    # cv转码 乱码
                    # if isinstance(p_boxes_ltrb_f, torch.Tensor):
                    # ts -> np
                    p_boxes_ltrb_f = p_boxes_ltrb_f.numpy()

                    # 这里是画框
                    img_np = img_np_file
                    for box, text in zip(p_boxes_ltrb_f, p_texts):
                        box = box.astype(np.int)
                        cv2.rectangle(img_np, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)  # (l,t),(r,b),颜色.宽度
                        left = box[0]
                        top = box[1]  # putText 这个是文字中间
                        img_np = draw_text_chinese4cv(img_np, text, left, top)
                        # cv2.putText(img_np, text, (cx, cy), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), )

            # 这个 img_np 就是rgb 不用转
            # img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

            # print("fps= %.2f" % (fps))
            count += 1
            text_ = "%s fps= %.2f count=%s " % (title_text, fps, count)
            # 图片，添加的文字，左上角坐标，字体，字体大小，颜色，字体粗细
            img_np = cv2.putText(img_np, text_, (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                 (0, 255, 0), 1)
            # img_np=draw_text_chinese4cv(img_np, text_, 0, 40, )
            # 极小数
            fps = (fps + (1. / max(sys.float_info.min, time.time() - start_time))) / 2

            # cv2.imshow(title_text, img_np)
            # cv2.imshow('无效'.encode("gbk").decode(errors="ignore"), img_np) # 无效
            cv2.imshow(u'abc', img_np)

            c = cv2.waitKey(1) & 0xff  # 输入esc退出
            if c == 27:
                cap.release()
                cv2.destroyAllWindows()
                break

    @abstractmethod
    def get_detect_reses(self, img_np_file):
        '''
        必须返回以下内容
        :param img_np_file:
        :return:
            ids_batch, p_ltrbs, p_labels, p_scores = reses_detect
        '''
        pass


class DetectTaskFlowBase(DetectTaskBase):

    def __init__(self, mode_detect, data_transform, device, ids_classes,
                 path_pic=None,
                 pred_conf_thr=0.01,
                 pred_select_topk=500,
                 pred_nms_thr=0.65,
                 pred_nms_keep=9999,
                 is_show_res=True,
                 ) -> None:
        super(DetectTaskFlowBase, self).__init__(mode_detect=mode_detect,
                                                 data_transform=data_transform,
                                                 device=device,
                                                 ids_classes=ids_classes,
                                                 model=None,
                                                 path_pic=path_pic,
                                                 is_show_res=is_show_res,
                                                 )
        self.pred_conf_thr = pred_conf_thr
        self.pred_select_topk = pred_select_topk
        self.pred_nms_thr = pred_nms_thr
        self.pred_nms_keep = pred_nms_keep

    @abstractmethod
    def p_init(self, model_outs, targets):
        '''
        p_init 处理数据
        :param model_outs:
        :param targets: 这个需要处理  例如 to.显卡
        :return: 只需返回 model_outs
        '''
        return model_outs

    @abstractmethod
    def get_pscores(self, outs_init, targets):
        '''
        这个返回分数
        :param outs_init: p_init 处理后
        :param targets: 这个需要处理  例如 to.显卡
        :return:
            pscores : 这个用于判断 生成 mask_pos
            plabels : 这个用于二阶段
        '''
        pass

    @abstractmethod
    def get_stage_res(self, outs_init, imgs_ts_4d):
        '''

        :param outs_init:
        :return:  目标检测返回 这4个结果
            ids_batch2, p_boxes_ltrb2, p_labels2, p_scores2
        '''
        return None

    @abstractmethod
    def get_model_outs(self, imgs_ts_4d):
        '''
        模型输出的返回 这个由框架实现
        :param imgs_ts_4d:
        :return:
        '''
        pass

    def detect4pic(self, file):
        t00 = time.time()
        img_np_file = cv2.imread(file)  # h,w,c bgr

        reses_detect = self.get_detect_reses(img_np_file)
        reses_z = self.get_reses_z(img_np_file, reses_detect)
        if reses_z is None:
            return None

        p_boxes_ltrb_f, p_labels, p_scores, title_text, p_texts = reses_z
        self.print_time(t00, p_labels)
        return reses_z

    def get_detect_reses(self, img_np_file):
        '''

        :param img_np_file:
        :return:
            ids_batch, p_ltrbs, p_labels, p_scores = reses_detect
        '''
        # 这个必须返回一个target 这里返回的都是CPU值 框架会自动创建一个  这里
        img_ts_3d, target = self.data_transform(img_np_file)
        device = img_ts_3d.DEVICE

        # batch为1 一个图有一个 off_ltrb
        if target is not None and 'off_ltrb' in target:  # 多尺度归一
            off_ltrb_ts = torch.tensor(target['off_ltrb'], dtype=torch.float, device=device).unsqueeze(0)
        else:
            off_ltrb_ts = torch.zeros(1, 4, device=device, dtype=torch.float)

        # np只能用cpu()
        imgs_ts_4d = img_ts_3d.unsqueeze(0)
        model_outs = self.get_model_outs(imgs_ts_4d)

        # 转 tensor 保持一致
        reses_detect = self.postprocess(model_outs, imgs_ts_4d=imgs_ts_4d,
                                        targets=[target], off_ltrb_ts=off_ltrb_ts)

        return reses_detect

    def postprocess(self, model_outs, imgs_ts_4d, targets=None, off_ltrb_ts=None):
        outs = self.p_init(model_outs, targets)  # 1 -- 处理 np 转换
        pscores, plabels = self.get_pscores(outs, targets)  # 2 -- 处理 pscores, plabels
        mask_pos = pscores > self.pred_conf_thr
        if not torch.any(mask_pos):
            return None

        if pscores.shape[-1] > self.pred_select_topk:  # 并行取top100 与mask_pos 进行and操作
            # 每个批次取 topk 个
            ids_topk = pscores.topk(self.pred_select_topk, dim=-1)[1]  # torch.Size([32, 1000])
            mask_topk = torch.zeros_like(mask_pos)
            mask_topk[torch.arange(ids_topk.shape[0])[:, None], ids_topk] = True
            mask_pos = torch.logical_and(mask_pos, mask_topk)

        # 3 -- 处理 p_ltrb_input
        p_ltrb_input = self.get_stage_res(outs, imgs_ts_4d)

        size_hw_input = imgs_ts_4d.shape[-2:]
        device = imgs_ts_4d.DEVICE

        # off_ltrb_ts 实际归一化尺寸 偏移
        size_wh_input_ts = torch.tensor(list(size_hw_input)[::-1], device=device)
        # [2] ^^ [batch,4] ... [batch,2] ->  [batch,2] 实际可用图片尺寸
        size_wh_input_ts_x2 = (size_wh_input_ts - off_ltrb_ts[:, 2:] - off_ltrb_ts[:, :2]).repeat(1, 2)
        # [batch,dim,4] ^^ [batch,4] 平移选框只考虑lt           [batch,2] -> [batch,4] [batch,1,4]
        p_ltrb_one1 = (p_ltrb_input - off_ltrb_ts[:, :2].repeat(1, 2).unsqueeze(1)) / size_wh_input_ts_x2.unsqueeze(1)

        p_ltrb_one1 = p_ltrb_one1[mask_pos]
        p_ltrb_one1.clamp_(0, 1)

        ids_batch1, _ = torch.where(mask_pos)
        p_scores1 = pscores[mask_pos]
        p_labels1 = plabels[mask_pos]
        p_labels1 = p_labels1 + 1

        ids_batch2, p_ltrb_one2, p_labels2, p_scores2 = batch_nms_v2(
            ids_batch1=ids_batch1, p_ltrb1=p_ltrb_one1,
            p_labels1=p_labels1, p_scores1=p_scores1,
            threshold_nms=self.pred_nms_thr,
            num_max=self.pred_nms_keep,
        )
        return ids_batch2, p_ltrb_one2, p_labels2, p_scores2


class DetectTask_py(DetectTaskFlowBase):

    def __init__(self, mode_detect, data_transform, device, ids_classes, model,
                 path_pic=None,
                 pred_conf_thr=0.01,
                 pred_select_topk=500,
                 pred_nms_thr=0.65,
                 pred_nms_keep=9999,
                 is_show_res=True, ) -> None:
        super(DetectTask_py, self).__init__(mode_detect=mode_detect,
                                            data_transform=data_transform,
                                            device=device,
                                            ids_classes=ids_classes,
                                            path_pic=path_pic,
                                            pred_conf_thr=pred_conf_thr,
                                            pred_select_topk=pred_select_topk,
                                            pred_nms_thr=pred_nms_thr,
                                            pred_nms_keep=pred_nms_keep,
                                            is_show_res=is_show_res,
                                            )
        self.model = model

    def get_model_outs(self, imgs_ts_4d):
        self.model.eval()
        with torch.no_grad():
            model_outs = self.model(imgs_ts_4d)
        return model_outs


class DetectTaskONNX(DetectTaskFlowBase):

    def __init__(self, file_model, mode_detect, data_transform, device, ids_classes,
                 path_pic=None,
                 pred_conf_thr=0.01,
                 pred_select_topk=500,
                 pred_nms_thr=0.65,
                 pred_nms_keep=9999,
                 is_show_res=True,
                 ) -> None:
        '''
        暂时只支持CPU
        '''
        super(DetectTaskONNX, self).__init__(mode_detect=mode_detect,
                                             data_transform=data_transform,
                                             device=device,
                                             ids_classes=ids_classes,
                                             path_pic=path_pic,
                                             pred_conf_thr=pred_conf_thr,
                                             pred_select_topk=pred_select_topk,
                                             pred_nms_thr=pred_nms_thr,
                                             pred_nms_keep=pred_nms_keep,
                                             is_show_res=is_show_res,
                                             )
        self._init_model(file_model)
        self.file_model = file_model

    def _init_model(self, file_model):
        if not os.path.exists(file_model):
            raise Exception('file_model 不存在 {}'.format(file_model))

        onnx_session = onnxruntime.InferenceSession(file_model)
        self.output_names = [o.name for o in onnx_session.get_outputs()]
        self.input_names = [i.name for i in onnx_session.get_inputs()]
        self.model = onnx_session

    def get_model_outs(self, imgs_ts_4d):
        img_np_4d = imgs_ts_4d.numpy()
        model_outs = self.model.run(output_names=self.output_names,
                                    input_feed={self.input_names[0]: img_np_4d})
        return model_outs
