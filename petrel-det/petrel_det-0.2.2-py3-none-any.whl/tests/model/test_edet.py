from effdet.bench import DetBenchPredict, DetBenchTrain
from unittest import TestCase

from petrel.model import load_edet, DetBenchTrainVal


class TestEnet(TestCase):
    def test_classes(self):
        model = load_edet(config_name="tf_efficientdet_d0",
                          image_size=(512, 512),
                          num_classes=100)
        assert model.num_classes == 100
        assert model.num_levels == 5
        assert model.max_det_per_image == 1000
        assert model.max_detection_points == 5000
        assert not model.soft_nms
        assert model.__class__ == DetBenchTrainVal

    def test_det_per_image(self):
        model = load_edet(config_name="tf_efficientdet_d0",
                          image_size=(512, 512),
                          max_det_per_image=100)
        assert model.num_classes == 1
        assert model.num_levels == 5
        assert model.max_det_per_image == 100
        assert model.max_detection_points == 5000
        assert not model.soft_nms
        assert model.__class__ == DetBenchTrainVal

    def test_enet(self):
        model = load_edet(config_name="tf_efficientdet_d0",
                          image_size=(512, 512))
        assert model.num_classes == 1
        assert model.num_levels == 5
        assert model.max_det_per_image == 1000
        assert model.max_detection_points == 5000
        assert not model.soft_nms
        assert model.__class__ == DetBenchTrainVal

    def test_image_int(self):
        model = load_edet(config_name="tf_efficientdet_d0",
                          image_size=512,
                          num_classes=100)
        assert model.num_classes == 100
        assert model.num_levels == 5
        assert model.max_det_per_image == 1000
        assert model.max_detection_points == 5000
        assert not model.soft_nms
        assert model.__class__ == DetBenchTrainVal
        assert model.config.image_size == [512, 512]

    def test_image_size(self):
        model = load_edet(config_name="tf_efficientdet_d0",
                          image_size=(256, 256),
                          num_classes=100)
        assert model.num_classes == 100
        assert model.num_levels == 5
        assert model.max_det_per_image == 1000
        assert model.max_detection_points == 5000
        assert not model.soft_nms
        assert model.__class__ == DetBenchTrainVal
        assert model.config.image_size == [256, 256]

    def test_soft_nms(self):
        model = load_edet(config_name="tf_efficientdet_d0",
                          image_size=(512, 512),
                          soft_nms=True)
        assert model.num_classes == 1
        assert model.num_levels == 5
        assert model.max_det_per_image == 1000
        assert model.max_detection_points == 5000
        assert model.soft_nms
        assert model.__class__ == DetBenchTrainVal

    def test_train(self):
        model = load_edet(config_name="tf_efficientdet_d0",
                          image_size=(512, 512),
                          train=False)
        assert model.num_classes == 1
        assert model.num_levels == 5
        assert model.max_det_per_image == 1000
        assert model.max_detection_points == 5000
        assert not model.soft_nms
        assert model.__class__ == DetBenchPredict

    def test_checkout(self):
        model = load_edet(config_name="tf_efficientdet_d1",
                          image_size=(640, 640),
                          num_classes=90,
                          checkpoint_path="tests/tf_efficientdet_d1_40-a30f94af.pth",
                          train=True)
        assert model.num_classes == 90
        assert model.num_levels == 5
        assert model.max_det_per_image == 1000
        assert model.max_detection_points == 5000
        assert not model.soft_nms
        assert model.__class__ == DetBenchTrainVal

    def test_detection(self):
        model = load_edet(config_name="tf_efficientdet_d0",
                          image_size=(512, 512),
                          detection=True)
        assert model.num_classes == 1
        assert model.num_levels == 5
        assert model.max_det_per_image == 1000
        assert model.max_detection_points == 5000
        assert not model.soft_nms
        assert model.__class__ == DetBenchTrain
