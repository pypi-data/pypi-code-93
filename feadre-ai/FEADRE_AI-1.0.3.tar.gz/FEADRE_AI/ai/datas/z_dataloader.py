import os

from ftools.ai.datas.coco.coco_api import f_look_coco_type, f_coco_verify_info
from ftools.ai.datas.data_factory import fcre_dataload
from ftools.ai.gpu.webapi.translate import translate_baidu

KEYPOINTS_Mirror = {  # 水平翻转 这个要和数据遍历对起
    'face98': {
        0: 32, 1: 31, 2: 30, 3: 29, 4: 28, 5: 27, 6: 26, 7: 25, 8: 24, 9: 23, 10: 22, 11: 21, 12: 20,
        13: 19,
        14: 18,
        15: 17,
        16: 16, 17: 15, 18: 14, 19: 13, 20: 12, 21: 11, 22: 10, 23: 9, 24: 8, 25: 7, 26: 6, 27: 5,
        28: 4, 29: 3,
        30: 2,
        31: 1, 32: 0,
        33: 46, 34: 45, 35: 44, 36: 43, 37: 42, 38: 50, 39: 49, 40: 48, 41: 47,
        46: 33, 45: 34, 44: 35, 43: 36, 42: 37, 50: 38, 49: 39, 48: 40, 47: 41,
        60: 72, 61: 71, 62: 70, 63: 69, 64: 68, 65: 75, 66: 74, 67: 73,
        72: 60, 71: 61, 70: 62, 69: 63, 68: 64, 75: 65, 74: 66, 73: 67,
        96: 97, 97: 96,
        51: 51, 52: 52, 53: 53, 54: 54,
        55: 59, 56: 58, 57: 57, 58: 56, 59: 55,
        76: 82, 77: 81, 78: 80, 79: 79, 80: 78, 81: 77, 82: 76,
        87: 83, 86: 84, 85: 85, 84: 86, 83: 87,
        88: 92, 89: 91, 90: 90, 91: 89, 92: 88,
        95: 93, 94: 94, 93: 95
    },
    'face5': [[0, 5], [3, 4]],  # widerface
    'lsp': [[0, 5], [1, 4], [2, 3], [6, 11], [7, 10], [8, 9]],  # 14个关键点
}

KEYPOINTS_SEQ = {
    'LSP': [[13, 12], [12, 9], [12, 8], [9, 10], [8, 7], [10, 11],
            [7, 6], [12, 3], [12, 2], [2, 1], [1, 0], [3, 4], [4, 5]],
}


class DataInfo:

    def __init__(self, dataset_name, path_root,
                 mode_train, batch_train, path_img_train, file_json_train,
                 mode_test, batch_test, path_img_test, file_json_test,
                 kps_seq=None,
                 ) -> None:
        '''

        '''
        super().__init__()
        self.dataset_name = dataset_name  # 数据集的通用名称不能区分是train 还是test
        self.path_root = path_root
        self.kps_seq = kps_seq

        self.mode_train = mode_train
        self.batch_train = batch_train
        self.path_img_train = path_img_train
        self.file_json_train = file_json_train

        self.mode_test = mode_train if mode_test is None else mode_test
        self.batch_test = batch_train if batch_test is None else batch_test
        self.path_img_test = path_img_test
        self.file_json_test = file_json_test


def get_dataloader(cfg, data_info, transform_train, transform_test, kps_seq, ):
    dataloader_train, dataloader_test = None, None
    if cfg.IS_TRAIN and data_info.file_json_train is not None:
        dataloader_train = fcre_dataload(is_multi_scale=cfg.IS_MULTI_SCALE,
                                         num_workers=cfg.NUM_WORKERS,
                                         mode=data_info.mode_train,
                                         batch=data_info.batch_train,
                                         file_json=data_info.file_json_train,
                                         path_img=data_info.path_img_train,
                                         transform=transform_train,
                                         is_jump=cfg.IS_JUMP,
                                         name=data_info.dataset_name + '_train',
                                         size_hw_img=cfg.SIZE_WH_INPUT_TRAIN,
                                         is_mosaic=cfg.IS_MOSAIC,
                                         is_mixup=cfg.IS_MIXUP,
                                         is_mosaic_filter=cfg.IS_MOSAIC_FILTER,
                                         thr_wh=cfg.THR_WH,
                                         thr_area=cfg.THR_AREA,
                                         kps_seq=kps_seq,
                                         is_debug=cfg.IS_DEBUG,
                                         )

        f_look_coco_type(dataloader_train.dataset.coco_obj,
                         ids_cats_ustom=None,
                         name=dataloader_train.dataset.name)

    if (cfg.IS_VAL or cfg.IS_TEST) and data_info.file_json_test is not None:
        dataloader_test = fcre_dataload(is_multi_scale=cfg.IS_MULTI_SCALE,
                                        num_workers=cfg.NUM_WORKERS,
                                        mode=data_info.mode_test,
                                        batch=data_info.batch_test,
                                        file_json=data_info.file_json_test,
                                        path_img=data_info.path_img_test,
                                        transform=transform_test,
                                        is_jump=False,
                                        name=data_info.dataset_name + '_test',
                                        kps_seq=kps_seq,
                                        is_debug=cfg.IS_DEBUG,
                                        )
        f_look_coco_type(dataloader_test.dataset.coco_obj,
                         ids_cats_ustom=None,
                         name=dataloader_test.dataset.name)
    return dataloader_train, dataloader_test


def get_data_cocomin(cfg, path_host,
                     mode_train, batch_train, transform_train=None,
                     mode_test=None, batch_test=None, transform_test=None
                     ):
    ''' 这个可用于COCO测试 '''
    cfg.NUMS_VAL_DICT = {55: 3, 66: 1, 77: 1}  # 验证起始和频率
    cfg.NUMS_TEST_DICT = {1: 1, 100: 1, 200: 1}  # 测试的起始和频率
    cfg.NUM_WEIGHT_SAVE_DICT = {1: 1, 35: 1, 50: 1}
    cfg.PRINT_FREQ = 30
    cfg.VAL_FREQ = 20
    cfg.NUM_CLASSES = 80  # 这个根据数据集要改

    dataset_name = 'cocomin'
    path_root = os.path.join(path_host, '/AI/datas/coco2017')
    path_img_train = os.path.join(path_root, 'imgs/train2017_118287')
    file_json_train = os.path.join(path_root, 'annotations/instances_coco_min_train_16000.json')
    path_img_test = os.path.join(path_root, 'imgs/val2017_5000')
    file_json_test = os.path.join(path_root, 'annotations/instances_coco_min_val_3200.json')
    # file_json_test = os.path.join(path_root, 'annotations/instances_val2017_4952.json')
    kps_seq = None

    data_info = DataInfo(dataset_name, path_root,
                         mode_train, batch_train, path_img_train, file_json_train,
                         mode_test, batch_test, path_img_test, file_json_test,
                         kps_seq=kps_seq,
                         )

    dataloader_train, dataloader_test = get_dataloader(
        cfg, data_info,
        transform_train, transform_test,
        kps_seq=kps_seq,
    )

    return data_info, dataloader_train, dataloader_test


def get_data_coco2017(cfg, path_host,
                      mode_train, batch_train, transform_train=None,
                      mode_test=None, batch_test=None, transform_test=None
                      ):
    ''' 这个可用于COCO测试 '''
    cfg.NUMS_VAL_DICT = {55: 3, 66: 1, 77: 1}  # 验证起始和频率
    cfg.NUMS_TEST_DICT = {1: 1, 100: 1, 200: 1}  # 测试的起始和频率
    cfg.NUM_WEIGHT_SAVE_DICT = {1: 1, 35: 1, 50: 1}
    cfg.PRINT_FREQ = 40
    cfg.VAL_FREQ = 40
    cfg.NUM_CLASSES = 80  # 这个根据数据集要改

    dataset_name = 'coco2017'
    path_root = os.path.join(path_host, '/AI/datas/coco2017')
    path_img_train = os.path.join(path_root, 'imgs/train2017_118287')
    file_json_train = os.path.join(path_root, 'annotations/instances_train2017_117266.json')
    path_img_test = os.path.join(path_root, 'imgs/val2017_5000')
    file_json_test = os.path.join(path_root, 'annotations/instances_val2017_4952.json')
    # file_json_test = os.path.join(path_root, 'annotations/instances_val2017_4952.json')
    kps_seq = None

    data_info = DataInfo(dataset_name, path_root,
                         mode_train, batch_train, path_img_train, file_json_train,
                         mode_test, batch_test, path_img_test, file_json_test,
                         kps_seq=kps_seq,
                         )

    dataloader_train, dataloader_test = get_dataloader(
        cfg, data_info,
        transform_train, transform_test,
    )

    return data_info, dataloader_train, dataloader_test


def get_data_type3(cfg, path_host,
                   mode_train, batch_train, transform_train=None,
                   mode_test=None, batch_test=None, transform_test=None
                   ):
    cfg.NUMS_VAL_DICT = {55: 3, 66: 1, 77: 1}  # 验证起始和频率
    cfg.NUMS_TEST_DICT = {20: 1, 100: 1, 200: 1}  # 测试的起始和频率
    cfg.NUM_WEIGHT_SAVE_DICT = {15: 10, 35: 1, 50: 1}  # 25轮记录
    cfg.PRINT_FREQ = 8
    cfg.NUM_CLASSES = 3  # ** 这里要改

    dataset_name = 'type3'  # ** 这里要改
    path_root = os.path.join(path_host, '/AI/datas/VOC2007')
    path_img_train = os.path.join(path_root, 'train/JPEGImages')
    file_json_train = os.path.join(path_root, 'annotations/instances_type3_train_1066.json')
    path_img_test = os.path.join(path_root, 'val/JPEGImages')
    # instances_type3_val_413.json
    file_json_test = os.path.join(path_root, 'annotations/instances_type3_test_637.json')
    kps_seq = None

    # 这里不变
    data_info = DataInfo(dataset_name, path_root,
                         mode_train, batch_train, path_img_train, file_json_train,
                         mode_test, batch_test, path_img_test, file_json_test,
                         kps_seq=kps_seq,
                         )
    kps_seq = None

    dataloader_train, dataloader_test = get_dataloader(
        cfg, data_info,
        transform_train, transform_test,
        kps_seq=kps_seq,
    )

    return data_info, dataloader_train, dataloader_test


def get_data_type4(cfg, path_host,
                   mode_train, batch_train, transform_train=None,
                   mode_test=None, batch_test=None, transform_test=None
                   ):
    cfg.NUMS_VAL_DICT = {55: 3, 66: 1, 77: 1}  # 验证起始和频率
    cfg.NUMS_TEST_DICT = {20: 1, 100: 1, 200: 1}  # 测试的起始和频率
    cfg.NUM_WEIGHT_SAVE_DICT = {15: 10, 35: 1, 50: 1}  # 25轮记录
    cfg.PRINT_FREQ = 8
    cfg.NUM_CLASSES = 4  # ** 这里要改

    dataset_name = 'type4'  # ** 这里要改
    path_root = os.path.join(path_host, '/AI/datas/VOC2007')
    path_img_train = os.path.join(path_root, 'train/JPEGImages')
    file_json_train = os.path.join(path_root, 'annotations/instances_type4_train_994.json')
    path_img_test = os.path.join(path_root, 'val/JPEGImages')
    # instances_type4_test_550.json
    file_json_test = os.path.join(path_root, 'annotations/instances_type4_test_550.json')
    kps_seq = None

    # 这里不变
    data_info = DataInfo(dataset_name, path_root,
                         mode_train, batch_train, path_img_train, file_json_train,
                         mode_test, batch_test, path_img_test, file_json_test,
                         kps_seq=kps_seq,
                         )

    dataloader_train, dataloader_test = get_dataloader(
        cfg, data_info,
        transform_train, transform_test,
        kps_seq=kps_seq,
    )

    return data_info, dataloader_train, dataloader_test


def get_data_face5(cfg, path_host,
                   mode_train, batch_train, transform_train=None,
                   mode_test=None, batch_test=None, transform_test=None
                   ):
    cfg.NUMS_VAL_DICT = {55: 3, 66: 1, 77: 1}  # 验证起始和频率
    cfg.NUMS_TEST_DICT = {1: 1, 100: 1, 200: 1}  # 测试的起始和频率
    cfg.NUM_WEIGHT_SAVE_DICT = {15: 10, 35: 1, 50: 1}  # 25轮记录
    cfg.PRINT_FREQ = 20
    cfg.NUM_CLASSES = 1  # ** 这里要改

    dataset_name = 'face5'  # ** 这里要改
    path_root = os.path.join(path_host, '/AI/datas/kps/face_5')
    path_img_train = os.path.join(path_root, 'images_13466')
    file_json_train = os.path.join(path_root, 'annotations/keypoints_train_10000_10000.json')
    path_img_test = os.path.join(path_root, 'images_13466')
    file_json_test = os.path.join(path_root, 'annotations/keypoints_test_3466_3466.json')

    kps_seq = None
    # 这里不变
    data_info = DataInfo(dataset_name, path_root,
                         mode_train, batch_train, path_img_train, file_json_train,
                         mode_test, batch_test, path_img_test, file_json_test,
                         kps_seq=kps_seq,
                         )

    dataloader_train, dataloader_test = get_dataloader(
        cfg, data_info,
        transform_train, transform_test,
        kps_seq=kps_seq,
    )

    return data_info, dataloader_train, dataloader_test


def get_data_face98(cfg, path_host,
                    mode_train, batch_train, transform_train=None,
                    mode_test=None, batch_test=None, transform_test=None
                    ):
    cfg.NUMS_VAL_DICT = {55: 3, 66: 1, 77: 1}  # 验证起始和频率
    cfg.NUMS_TEST_DICT = {1: 1, 100: 1, 200: 1}  # 测试的起始和频率
    cfg.NUM_WEIGHT_SAVE_DICT = {15: 10, 35: 1, 50: 1}  # 25轮记录
    cfg.PRINT_FREQ = 10
    cfg.NUM_CLASSES = 1  # ** 这里要改

    dataset_name = 'face98'  # ** 这里要改
    path_root = os.path.join(path_host, '/AI/datas/kps/face_98')
    path_img_train = os.path.join(path_root, 'images_train_5316')
    file_json_train = os.path.join(path_root, 'annotations/keypoints_train_7500_5316.json')
    path_img_test = os.path.join(path_root, 'images_test_2118')
    file_json_test = os.path.join(path_root, 'annotations/keypoints_test_2500_2118.json')

    kps_seq = None
    # 这里不变
    data_info = DataInfo(dataset_name, path_root,
                         mode_train, batch_train, path_img_train, file_json_train,
                         mode_test, batch_test, path_img_test, file_json_test,
                         kps_seq=kps_seq,
                         )

    dataloader_train, dataloader_test = get_dataloader(
        cfg, data_info,
        transform_train, transform_test,
        kps_seq=kps_seq,
    )

    return data_info, dataloader_train, dataloader_test


def get_data_voc2007(cfg, path_host,
                     mode_train, batch_train, transform_train=None,
                     mode_test=None, batch_test=None, transform_test=None
                     ):
    cfg.NUMS_VAL_DICT = {55: 3, 66: 1, 77: 1}  # 验证起始和频率
    cfg.NUMS_TEST_DICT = {1: 1, 100: 1, 200: 1}  # 测试的起始和频率
    cfg.NUM_WEIGHT_SAVE_DICT = {15: 10, 35: 1, 50: 1}  # 25轮记录
    cfg.PRINT_FREQ = 20
    cfg.NUM_CLASSES = 20  # ** 这里要改

    dataset_name = 'voc2007'  # ** 这里要改
    path_root = os.path.join(path_host, '/AI/datas/VOC2007')
    path_img_train = os.path.join(path_root, 'train/JPEGImages')
    file_json_train = os.path.join(path_root, 'annotations/instances_train_5011.json')
    path_img_test = os.path.join(path_root, 'val/JPEGImages')
    file_json_test = os.path.join(path_root, 'annotations/instances_val_1980.json')
    kps_seq = None

    # 这里不变
    data_info = DataInfo(dataset_name, path_root,
                         mode_train, batch_train, path_img_train, file_json_train,
                         mode_test, batch_test, path_img_test, file_json_test,
                         kps_seq=kps_seq,
                         )

    dataloader_train, dataloader_test = get_dataloader(
        cfg, data_info,
        transform_train, transform_test,
        kps_seq=kps_seq,
    )

    return data_info, dataloader_train, dataloader_test


def get_data_voc2012(cfg, path_host,
                     mode_train, batch_train, transform_train=None,
                     mode_test=None, batch_test=None, transform_test=None
                     ):
    cfg.NUMS_VAL_DICT = {55: 3, 66: 1, 77: 1}  # 验证起始和频率
    cfg.NUMS_TEST_DICT = {1: 1, 100: 1, 200: 1}  # 测试的起始和频率
    cfg.NUM_WEIGHT_SAVE_DICT = {15: 10, 35: 1, 50: 1}  # 25轮记录
    cfg.PRINT_FREQ = 30
    cfg.NUM_CLASSES = 20  # ** 这里要改

    dataset_name = 'voc2012'  # ** 这里要改
    path_root = os.path.join(path_host, '/AI/datas/VOC2012')
    path_img_train = os.path.join(path_root, 'train/JPEGImages')
    file_json_train = os.path.join(path_root, 'annotations/instances_train_17125.json')
    path_voc2007 = cfg.PATH_HOST + '/AI/datas/VOC2007'
    path_img_test = os.path.join(path_voc2007, 'val/JPEGImages')
    file_json_test = os.path.join(path_voc2007, 'annotations/instances_test_2972.json')

    kps_seq = None
    # 这里不变
    data_info = DataInfo(dataset_name, path_root,
                         mode_train, batch_train, path_img_train, file_json_train,
                         mode_test, batch_test, path_img_test, file_json_test,
                         kps_seq=kps_seq,
                         )

    dataloader_train, dataloader_test = get_dataloader(
        cfg, data_info,
        transform_train, transform_test,
        kps_seq=kps_seq,
    )

    return data_info, dataloader_train, dataloader_test


def get_data_widerface(cfg, path_host,
                       mode_train, batch_train, transform_train=None,
                       mode_test=None, batch_test=None, transform_test=None
                       ):
    cfg.NUMS_VAL_DICT = {55: 3, 66: 1, 77: 1}  # 验证起始和频率
    cfg.NUMS_TEST_DICT = {1: 1, 100: 1, 200: 1}  # 测试的起始和频率
    cfg.NUM_WEIGHT_SAVE_DICT = {15: 10, 35: 1, 50: 1}  # 25轮记录
    cfg.PRINT_FREQ = 30
    cfg.NUM_CLASSES = 1  # ** 这里要改

    dataset_name = 'widerface'  # ** 这里要改
    path_root = os.path.join(path_host, '/AI/datas/widerface')
    path_img_train = os.path.join(path_root, 'images/train2017')
    file_json_train = os.path.join(path_root, 'annotations/person_keypoints_train2017.json')
    path_img_test = os.path.join(path_root, 'images/val2017')
    file_json_test = os.path.join(path_root, 'annotations/instances_val2017.json')

    kps_seq = None
    # 这里不变
    data_info = DataInfo(dataset_name, path_root,
                         mode_train, batch_train, path_img_train, file_json_train,
                         mode_test, batch_test, path_img_test, file_json_test,
                         kps_seq=kps_seq,
                         )

    dataloader_train, dataloader_test = get_dataloader(
        cfg, data_info,
        transform_train, transform_test,
        kps_seq=kps_seq,
    )

    return data_info, dataloader_train, dataloader_test


def get_data_lsp(cfg, path_host,
                 mode_train, batch_train, transform_train=None,
                 mode_test=None, batch_test=None, transform_test=None
                 ):
    cfg.NUMS_VAL_DICT = {55: 3, 66: 1, 77: 1}  # 验证起始和频率
    cfg.NUMS_TEST_DICT = {1: 1, 100: 1, 200: 1}  # 测试的起始和频率
    cfg.NUM_WEIGHT_SAVE_DICT = {15: 10, 35: 1, 50: 1}  # 25轮记录
    cfg.PRINT_FREQ = 30
    cfg.NUM_CLASSES = 1  # ** 这里要改

    dataset_name = 'lsp'  # ** 这里要改
    path_root = os.path.join(path_host, '/AI/datas/kps/Leeds_Sports_Pose')
    path_img_train = os.path.join(path_root, 'data/lsp_dataset/images')
    file_json_train = os.path.join(path_root, 'annotations/keypoints_train_1600_1600.json')
    path_img_test = os.path.join(path_root, 'data/lsp_dataset/images')
    file_json_test = os.path.join(path_root, 'annotations/keypoints_test_400_400.json')

    kps_seq = KEYPOINTS_SEQ['LSP']
    # 这里不变
    data_info = DataInfo(dataset_name, path_root,
                         mode_train, batch_train, path_img_train, file_json_train,
                         mode_test, batch_test, path_img_test, file_json_test,
                         kps_seq=kps_seq,
                         )

    dataloader_train, dataloader_test = get_dataloader(
        cfg, data_info,
        transform_train, transform_test,
        kps_seq=kps_seq,
    )

    return data_info, dataloader_train, dataloader_test


def get_data_raccoon(cfg, path_host,
                     mode_train, batch_train, transform_train=None,
                     mode_test=None, batch_test=None, transform_test=None
                     ):
    cfg.NUMS_VAL_DICT = {55: 3, 66: 1, 77: 1}  # 验证起始和频率
    cfg.NUMS_TEST_DICT = {1: 1, 100: 1, 200: 1}  # 测试的起始和频率
    cfg.NUM_WEIGHT_SAVE_DICT = {15: 10, 35: 1, 50: 1}  # 25轮记录
    cfg.PRINT_FREQ = 10
    cfg.NUM_CLASSES = 1  # ** 这里要改

    dataset_name = 'raccoon'  # ** 这里要改
    path_root = os.path.join(path_host, '/AI/datas/raccoon200')
    path_img_train = os.path.join(path_root, 'VOCdevkit/JPEGImages')
    file_json_train = os.path.join(path_root, 'annotations/instances_train2017.json')
    path_img_test = os.path.join(path_root, 'VOCdevkit/JPEGImages')
    file_json_test = os.path.join(path_root, 'annotations/instances_val2017.json')

    # 这里不变
    data_info = DataInfo(dataset_name, path_root,
                         mode_train, batch_train, path_img_train, file_json_train,
                         mode_test, batch_test, path_img_test, file_json_test,
                         kps_seq=None,
                         )

    dataloader_train, dataloader_test = get_dataloader(
        cfg, data_info,
        transform_train, transform_test,
        kps_seq=None,
    )

    return data_info, dataloader_train, dataloader_test


def cre_id_classes():
    ids_classes_china = {}
    for k, v in ids_classes.items():
        ids_classes_china[k] = translate_baidu(v)
        time.sleep(1)
    # 创建id class文件
    file_json = os.path.join(data_info.path_root, 'ids_classes_%s.json' % data_info.dataset_name)
    with open(file_json, 'w', encoding='utf-8') as f:
        json.dump(ids_classes, f, ensure_ascii=False, )
    file_json = os.path.join(data_info.path_root, 'classes_ids_%s.json' % data_info.dataset_name)
    with open(file_json, 'w', encoding='utf-8') as f:
        json.dump(dataset.classes_ids, f, ensure_ascii=False, )
    # 创建中文的id class文件
    file_json = os.path.join(data_info.path_root, 'ids_classes_%s_china.json' % data_info.dataset_name)
    with open(file_json, 'w', encoding='utf-8') as f:
        json.dump(ids_classes_china, f, ensure_ascii=False, )
    print('创建成功 ', file_json)


if __name__ == '__main__':
    '''
    这里为每一个数据集创建 class id文件
    '''
    import json
    import time


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
    mode_train = 'keypoints'  # bbox segm keypoints caption
    # get_data_widerface 数据中自带校验方法
    data_info, dataloader_train, dataloader_test = get_data_lsp(cfg, path_host=path_host,
                                                                mode_train=mode_train,
                                                                batch_train=10)

    dataset = dataloader_train.dataset
    ids_classes = dataset.ids_classes

    for data in dataset:
        data1 = data
        pass

    ''' ------------------------------- 创建文件 ------------------------------- '''
    # 创建3个 id_classes 的 josn
    # cre_id_classes()
    #
    ''' ------------------------------- 简单测试数据集 ------------------------------- '''
    # print('dataloader_test')
    # f_coco_verify_info(dataloader_test.dataset.coco_obj, data_info.path_img_train)
    #
    # print('dataloader_train')
    # f_coco_verify_info(dataloader_train.dataset.coco_obj, data_info.path_img_test)
