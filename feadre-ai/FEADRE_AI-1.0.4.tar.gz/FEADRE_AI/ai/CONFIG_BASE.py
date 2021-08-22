from collections import defaultdict


class FCFG_BASE:
    # 训练验证
    IS_MIXTURE_FIT = True  # 半精度训练 *
    FORWARD_COUNT = 1  # 多次前向一次反向 *
    IS_TRAIN = True  # 开启训练 *
    IS_VAL = False  # 开启验证 *
    IS_WARMUP = True  # 是否热身 *
    NUM_WARMUP = 2  # WARMUP 的轮数  n-1 *
    IS_EMA = False  # 参数平滑 *

    IS_TEST = True  # 开启测试 *
    IS_VISUAL = False  # 可视化模式 关联训练 和测试
    # MODE_VIS = 'bbox'  # 验证的 计算模式 'kps','bbox' 关系到 可视化 nms等 *
    NUM_VIS_Z = 3  # 测试时可视化的图片数 超过就不再可视 *

    IS_WRITER = False  # 使用CPU时有BUG 不能创建目录
    KEEP_WRITER = None  # 指定目录名称 FitExecutorBase 转换为 self.tb_writer

    IS_DEBUG = False  # 调试模式

    # 预测参数
    PRED_CONF_THR = 0.05  # 用于预测的阀值 *
    PRED_NMS_THR = 0.5  # 提高 conf 提高召回, 越小框越少 *
    PRED_SELECT_TOPK = 500  # 预测时topk *
    PRED_NMS_KEEP = 9999  # NMS每张图保留的个数 这个设置为100 有可能加速

    MAP_RECORD = defaultdict(lambda: [0.5, 0.5])
    MAP_RECORD.update({
        'type3': [0.762, 0.675],
        'type4': [0.732, 0.542],  # ema p542r368
        'face5': [0.988, 0.754],
        'face98': [0.470, 0.56],
        'widerface': [0.6, 0.5],
        'coco2017': [0.4, 0.4],
        'cocomin': [0.5, 0.5],
        'raccoon': [0.859, 0.672],
        'lsp': [0.859, 0.875],
    })
    MAPS_DEF_MAX = [0.5, 0.5]  # MAP的最大值 触发保存
    '''
    np.array([.26, .25, .25, .35, .35, 
                .79, .79, .72, .72, .62, .62, 
                1.07, 1.07, .87, .87, .89, .89])/10.0
    嘴眼 .25
    耳朵 .35
    肩 手关节 手腕 .79 .72 .62
    屁 脚关节 脚腕 1.07 .87 .89
    '''
    KPT_OKS_SIGMAS = None  # kps 验证必须 脸部25

    # 频率参数
    PRINT_FREQ = 1  # 打印频率 与 batch * PRINT_FREQ
    NUMS_TEST_DICT = {2: 1, 35: 1, 50: 1}  # 测试的起始和频率
    NUM_WEIGHT_SAVE_DICT = {2: 1, 35: 1, 50: 1}  # 保存频率

    # 数据集
    # BATCH_TRAIN = 3
    # BATCH_VAL = 1

    # 数据增强
    IS_MULTI_SCALE = False  # 开启多尺寸训练 只要用数据增强必须有
    MULTI_SCALE_VAL = [200, 300]  # 多尺寸训练的尺寸范围
    SIZE_WH_INPUT_TRAIN = (320, 320)
    SIZE_WH_INPUT_TEST = (320, 320)

    # MOSAIC 参数
    IS_MOSAIC = False
    IS_MIXUP = False
    IS_MOSAIC_FILTER = False
    THR_WH = 5
    THR_AREA = 25

    # 其它动态参数
    PATH_SAVE_WEIGHT = ''  # ***
    SAVE_WEIGHT_NAME = ''  # ***
    PATH_HOST = 'nan'  # 用于多环境切换主机
    NUM_WORKERS = 4
    FUN_LOCK = None  # 冻结训练参数
    NUMS_LOCK_WEIGHT_DICT = None  # np.array([1, 5, 12]) 锁定权重分段训练  [1, 10] epoch 与 FUN_LOCK 匹配 必须由小到大
    LR_BASE = 1e-3
    START_EPOCH = 1
    END_EPOCH = 300
    TRANSFORM_TRAIN = None
    TRANSFORM_TEST = None
    DATA_INFO = None  # 这个用于存一些data信息 DATA_INFO对象
    IS_JUMP = False  # 当coco数据集有没有目标的GT时 默认可参与训练 不跳过  boxes为空需要处理

    # 可调参数 这个要在 fun_get_data 的后面

    def __str__(self) -> str:
        s = '---------------- CFG参数 ------------------\n'
        for name in dir(self):  # 显示对象的所有属性
            if not name.startswith('__'):  # 过滤掉系统自带的
                s += ('\t' + name + ' : ' + str(getattr(self, name)) + '\n')
        return s


if __name__ == '__main__':
    print(str(FCFG_BASE()))
