import tensorflow as tf
import numpy as np
import json

import readyml.utils.visualization_utils as viz_utils
from readyml.labels import labels_loader
from readyml.utils import fwks_init, model_utils

fwks_init.init_tensorflow()


class ObjectDetection():
    def __init__(self, model_name):
        self.labels = self._load_labels()
        self.model = model_utils.load(model_name)

    def _load_labels(self):
        raw_labels = labels_loader.get_labels('ms_coco')
        ids_labels = json.loads(raw_labels)
        final_labels = {v.get('id'): v for v in ids_labels.values()}
        return final_labels

    def infer(self, image_pil, threshold=30):
        image_np = np.array(image_pil)
        image_tensor = tf.expand_dims(image_np, axis=0)
        results = self.model(image_tensor)

        boxes = results.get('detection_boxes')[0].numpy()
        classes = results.get('detection_classes')[0].numpy().astype(np.int8)
        scores = results.get('detection_scores')[0].numpy()
        masks = results.get('detection_masks_reframed', None)

        new_image = self._draw_boxes(image_pil, boxes, classes, scores, masks, threshold)
        return self._format(image_pil, boxes, classes, scores, threshold), new_image

    def _format(self, image_pil, boxes, classes, scores, threshold):

        results = []
        im_width, im_height = image_pil.size

        for box, class_id, score \
                in zip(boxes, classes, scores):
            score = np.around(score.astype(np.float)*100, 2)
            if score >= threshold:
                ymin, xmin, ymax, xmax = box[0], box[1], box[2], box[3]

                # left, right, top, bottom
                edges = [int(i) for i in (xmin * im_width, xmax * im_width,
                                            ymin * im_height, ymax * im_height)]

                results.append({'label': self.labels.get(class_id).get('name'),
                                'score': score,
                                'box': edges})
        return json.dumps(results, sort_keys=True, indent=4)

    def _draw_boxes(self, image_pil, boxes, classes, scores, masks, threshold):

        image_np = np.array(image_pil)

        viz_utils.visualize_boxes_and_labels_on_image_array(
            image_np,
            boxes,
            (classes + 0),
            scores,
            self.labels,
            use_normalized_coordinates=True,
            max_boxes_to_draw=200,
            min_score_thresh=threshold/100,
            agnostic_mode=False,
            instance_masks=masks,
            line_thickness=8)
        return image_np


class HourGlass_512x512(ObjectDetection):
    def __init__(self):
        super().__init__("hourglass_512x512")


class HourGlass_1024x1024(ObjectDetection):
    def __init__(self):
        super().__init__("hourglass_1024x1024")


class Resnet50v1Fpn_512x512(ObjectDetection):
    def __init__(self):
        super().__init__("resnet50v1_fpn_512x512")


class Resnet101v1Fpn_512x512(ObjectDetection):
    def __init__(self):
        super().__init__("resnet101v1_fpn_512x512")


class Resnet50v2_512x512(ObjectDetection):
    def __init__(self):
        super().__init__("resnet50v2_512x512")


class EfficientdetD0(ObjectDetection):
    def __init__(self):
        super().__init__("efficientdet/d0")


class EfficientdetD1(ObjectDetection):
    def __init__(self):
        super().__init__("efficientdet/d1")


class EfficientdetD2(ObjectDetection):
    def __init__(self):
        super().__init__("efficientdet/d2")


class EfficientdetD3(ObjectDetection):
    def __init__(self):
        super().__init__("efficientdet/d3")


class EfficientdetD4(ObjectDetection):
    def __init__(self):
        super().__init__("efficientdet/d4")


class EfficientdetD5(ObjectDetection):
    def __init__(self):
        super().__init__("efficientdet/d5")


class EfficientdetD6(ObjectDetection):
    def __init__(self):
        super().__init__("efficientdet/d6")


class EfficientdetD7(ObjectDetection):
    def __init__(self):
        super().__init__("efficientdet/d7")


class SsdMobilenetv2(ObjectDetection):
    def __init__(self):
        super().__init__("ssd_mobilenet_v2")


class SsdMobilenetv1Fpn_640x640(ObjectDetection):
    def __init__(self):
        super().__init__("ssd_mobilenet_v1/fpn_640x640")


class SsdMobilenetv2FpnLite_320x320(ObjectDetection):
    def __init__(self):
        super().__init__("ssd_mobilenet_v2/fpnlite_320x320")


class Resnet50V1Fpn_640x640(ObjectDetection):
    def __init__(self):
        super().__init__("resnet50_v1_fpn_640x640")


class Resnet50v1Fpn_1024x1024(ObjectDetection):
    def __init__(self):
        super().__init__("resnet50_v1_fpn_1024x1024")


class Resnet101v1Fpn_640x640(ObjectDetection):
    def __init__(self):
        super().__init__("resnet101_v1_fpn_640x640")


class Resnet101v1Fpn_1024x1024(ObjectDetection):
    def __init__(self):
        super().__init__("resnet101_v1_fpn_1024x1024")


class Resnet152v1Fpn_640x640(ObjectDetection):
    def __init__(self):
        super().__init__("resnet152_v1_fpn_640x640")


class Resnet152v1Fpn_1024x1024(ObjectDetection):
    def __init__(self):
        super().__init__("resnet152_v1_fpn_1024x1024")


class FasterRcnnResnet50v1_640x640(ObjectDetection):
    def __init__(self):
        super().__init__("faster_rcnn/resnet50_v1_640x640")


class FasterRcnnResnet50v1_1024x1024(ObjectDetection):
    def __init__(self):
        super().__init__("faster_rcnn/resnet50_v1_1024x1024")


class FasterRcnnResnet50v1_800x1333(ObjectDetection):
    def __init__(self):
        super().__init__("faster_rcnn/resnet50_v1_800x1333")


class FasterRcnnResnet101v1_640x640(ObjectDetection):
    def __init__(self):
        super().__init__("faster_rcnn/resnet101_v1_640x640")


class FasterRcnnResnet101v1_1024x1024(ObjectDetection):
    def __init__(self):
        super().__init__("faster_rcnn/resnet101_v1_1024x1024")


class FasterRcnnResnet101v1_800x1333(ObjectDetection):
    def __init__(self):
        super().__init__("faster_rcnn/resnet101_v1_800x1333")


class FasterRcnnResnet152v1_640x640(ObjectDetection):
    def __init__(self):
        super().__init__("faster_rcnn/resnet152_v1_640x640")


class FasterRcnnResnet152v1_1024x1024(ObjectDetection):
    def __init__(self):
        super().__init__("faster_rcnn/resnet152_v1_1024x1024")


class FasterRcnnResnet152v1_800x1333(ObjectDetection):
    def __init__(self):
        super().__init__("faster_rcnn/resnet152_v1_800x1333")


class FasterRcnnInceptionResnetv2_640x640(ObjectDetection):
    def __init__(self):
        super().__init__("faster_rcnn/inception_resnet_v2_640x640")


class FasterRcnnInceptionResnetv2_1024x1024(ObjectDetection):
    def __init__(self):
        super().__init__("faster_rcnn/inception_resnet_v2_1024x1024")


class MaskRcnnInceptionResnetv2_1024x1024(ObjectDetection):
    def __init__(self):
        super().__init__("mask_rcnn/inception_resnet_v2_1024x1024")
